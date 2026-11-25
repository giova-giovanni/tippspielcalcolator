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
