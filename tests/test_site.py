"""engine/site.py – rule 6 in tips.json: other players' tips of today only after the deadline.

Fictitious players and a temp dataset; the JSON writer is replaced, nothing is written to docs/data.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # run with plain `pytest` too

import datetime as dt
import zoneinfo

import pytest

from engine import site
from engine.data import load_dataset

ROME = zoneinfo.ZoneInfo("Europe/Rome")
DAY = dt.date(2026, 10, 7)  # Wednesday, outside Lent
CFG = {"me": "Ich", "timezone": "Europe/Rome", "deadline": "12:00"}

MENUS = """date,year,weekday,status,vorspeise,hauptspeise,beilage,vorspeise_norm,hauptspeise_norm,beilage_norm,source
2026-10-06,2026,Di,served,Lasagne,Leberkas,Pommes,,,,form
2026-10-07,2026,Mi,served,Hirten,Gulasch,Reis,,,,form
2026-10-08,2026,Do,pending,,,,,,,form
"""
TIPS = """date,player,vorspeise,hauptspeise,beilage,points,points_sheet,source
2026-10-06,Anna,Lasagne,Gulasch,Reis,,,form
2026-10-06,Ich,Hirten,Leberkas,Pommes,,,form
2026-10-07,Anna,Hirten,Gulasch,Reis,,,form
2026-10-07,Bruno,,,,,0.5,form
2026-10-07,Ich,Lasagne,Gulasch,Pommes,,,form
2026-10-08,Anna,Carbonara,Gulasch,Reis,,,form
2026-10-08,Ich,Carbonara,Leberkas,Reis,,,form
"""


@pytest.fixture()
def ds(tmp_path):
    (tmp_path / "menus.csv").write_text(MENUS, encoding="utf-8")
    (tmp_path / "tips.csv").write_text(TIPS, encoding="utf-8")
    return load_dataset(tmp_path / "menus.csv", tmp_path / "tips.csv", config=CFG)


def _published(ds, monkeypatch, now):
    out = {}
    monkeypatch.setattr(site, "write_site_json", lambda name, obj, *a, **k: out.__setitem__(name, obj))
    site.run(ds, today=DAY, now=now)
    return {(r["date"], r["player"]) for r in out["tips"]["rows"]}


def test_others_today_hidden_before_deadline(ds, monkeypatch):
    rows = _published(ds, monkeypatch, dt.datetime(2026, 10, 7, 11, 59, tzinfo=ROME))
    assert ("2026-10-06", "Anna") in rows                       # past days: everything
    assert ("2026-10-07", "Anna") not in rows                   # today, before 12:00
    assert ("2026-10-07", "Bruno") not in rows
    assert ("2026-10-08", "Anna") not in rows                   # future: never
    assert {("2026-10-07", "Ich"), ("2026-10-08", "Ich")} <= rows   # my own tips: always


def test_others_today_published_after_deadline(ds, monkeypatch):
    rows = _published(ds, monkeypatch, dt.datetime(2026, 10, 7, 12, 0, tzinfo=ROME))
    assert {("2026-10-07", "Anna"), ("2026-10-07", "Bruno")} <= rows
    assert ("2026-10-08", "Anna") not in rows                   # tomorrow is still open


def test_without_now_today_stays_hidden(ds, monkeypatch):
    rows = _published(ds, monkeypatch, None)
    assert ("2026-10-07", "Anna") not in rows
    assert ("2026-10-06", "Anna") in rows


# ---------------------------------------------------------------- today_alt.json (the second tip)
# Snapshot: the morning of Wednesday 07.10.2026 (menus/tips from that day on hidden), so a data update
# never changes these expectations.
WED = dt.date(2026, 10, 7)


def _at(day: dt.date, hh: int, mm: int = 0) -> dt.datetime:
    return dt.datetime(day.year, day.month, day.day, hh, mm, tzinfo=ROME)


@pytest.fixture(scope="module")
def snap():
    from engine.recommend import as_of

    return as_of(load_dataset(), WED)


@pytest.fixture(scope="module")
def morning(snap):
    from engine.recommend import build

    return build(snap, WED, now=_at(WED, 9, 0))[0]


@pytest.fixture(scope="module")
def afternoon(snap):
    from engine.recommend import build

    return build(snap, WED, now=_at(WED, 13, 0))[0]


def _rec(obj):
    return obj["recommendation"]["copy_text"]


def test_alt_before_deadline_is_the_provisional_next_tip(snap, morning):
    assert morning["date"] == "2026-10-07"
    now = _at(WED, 9, 0)
    alt = site.alt_tip(snap, WED, now, morning)
    assert (alt["role"], alt["date"], alt["provisional"], alt["source"]) == ("next", "2026-10-08", True, "computed")
    assert alt["generated_at"] == now.isoformat(timespec="seconds")   # not the pretended 12:00
    assert "2026-10-07" in alt["missing_menus"]                       # today's menu is not known yet
    assert alt["recommendation"]["valid"] is True


def test_alt_after_deadline_is_todays_tip_as_shown(snap, morning, afternoon):
    assert afternoon["date"] == "2026-10-08"
    now = _at(WED, 13, 0)
    # carried over from the previous today.json (the morning run)
    alt = site.alt_tip(snap, WED, now, afternoon, {"today": morning, "alt": None})
    assert (alt["role"], alt["date"], alt["source"], alt["provisional"]) == ("today", "2026-10-07", "carried", False)
    assert _rec(alt) == _rec(morning)
    assert morning.get("role") is None                                # the previous object is not changed
    # a later run: today.json is already tomorrow's, the previous today_alt.json keeps today's tip
    again = site.alt_tip(snap, WED, _at(WED, 14, 0), afternoon, {"today": afternoon, "alt": alt})
    assert (again["date"], again["source"], _rec(again)) == ("2026-10-07", "carried", _rec(morning))
    # nothing to carry over (e.g. first run of the day after lunch): recomputed as of this morning
    rec = site.alt_tip(snap, WED, now, afternoon, {"today": {"date": "2026-10-06", "recommendation": {"x": 1}}, "alt": None})
    assert (rec["role"], rec["date"], rec["source"]) == ("today", "2026-10-07", "recomputed")
    assert _rec(rec) == _rec(morning)


def test_alt_none_on_weekend_free_day_or_without_now(snap, afternoon):
    from engine.data import Dataset, Menu
    from engine.recommend import build

    sat = dt.date(2026, 10, 10)
    main, _ = build(snap, sat, now=_at(sat, 10, 0))
    assert main["date"] == "2026-10-12"
    assert site.alt_tip(snap, sat, _at(sat, 10, 0), main)["role"] is None
    assert site.alt_tip(snap, WED, None, afternoon)["role"] is None
    free = Dataset([Menu(m.date, "free", ["Frei", "Frei", "Frei"], {c: [] for c in ("vorspeise", "hauptspeise", "beilage")}, m.source)
                    if m.date == WED else m for m in snap.menus], list(snap.tips), snap.norm, snap.config)
    main_f, _ = build(free, WED, now=_at(WED, 9, 0))
    assert main_f["date"] == "2026-10-08"
    assert site.alt_tip(free, WED, _at(WED, 9, 0), main_f)["role"] is None


def test_write_alt_writes_today_alt(snap, afternoon, morning, monkeypatch):
    out = {}
    monkeypatch.setattr(site, "write_site_json", lambda name, obj, *a, **k: out.__setitem__(name, obj))
    obj = site.write_alt(snap, WED, _at(WED, 13, 0), afternoon, {"today": morning})
    assert out == {"today_alt": obj} and obj["role"] == "today"
