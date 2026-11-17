"""Tests for engine/race.py (season race Monte Carlo) and recommend.missing_menus – synthetic data only."""
from __future__ import annotations

import datetime as dt

import pytest

from engine import CATEGORIES
from engine import race
from engine.data import Dataset, Menu, Tip
from engine.normalize import Normalizer
from engine.recommend import missing_menus

D = dt.date


def _workdays(start: dt.date, n: int) -> list[dt.date]:
    out, d = [], start
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d += dt.timedelta(days=1)
    return out


def _ds(points_a: float, points_b: float, n_served: int = 40, n_pending: int = 5, start_b: float = 0.0,
        newbie: bool = False) -> tuple[Dataset, list[dict]]:
    days = _workdays(D(2030, 9, 2), n_served + n_pending)
    served, pending = days[:n_served], days[n_served:]
    menus = [Menu(d, "served", ["Lasagne", "Gulasch", "Reis"], {c: ["x"] for c in CATEGORIES}) for d in served]
    menus += [Menu(d, "pending", ["", "", ""], {c: [] for c in CATEGORIES}) for d in pending]
    tips = []
    for d in served:
        tips.append(Tip(d, "A", ["Lasagne", "", ""], {}, points_a, points_a, {}, "xlsx"))
        tips.append(Tip(d, "B", ["Hirten", "", ""], {}, points_b, points_b, {}, "xlsx"))
    if start_b:
        tips.append(Tip(served[0], "B", ["", "", ""], {}, start_b, start_b, {}, "xlsx"))
    if newbie:   # joins late with start points, tips only 3 days
        tips.append(Tip(served[-4], "N", ["", "", ""], {}, 100.0, 100.0, {}, "xlsx"))
        for d in served[-3:]:
            tips.append(Tip(d, "N", ["Hirten", "", ""], {}, 0.0, 0.0, {}, "xlsx"))
    ds = Dataset(menus, tips, Normalizer(), {"me": "A", "season_end_mmdd": "12-23"})
    rec = [{"date": d, "points": 1.0, "served": True} for d in served]   # the model hits 1 point every day
    return ds, rec


def test_standings_remaining_days_and_probabilities():
    ds, rec = _ds(0.0, 0.5)
    r = race.compute(ds, rec, today=D(2030, 12, 1), n_sims=2000)
    assert r["standings"] == {"B": 20.0, "A": 0.0}
    assert r["remaining_days"] == 5 and r["leader"] == "B" and r["gap_to_leader"] == 20.0
    # 5 days cannot close a 20-point gap, whatever the scenario
    for s in ("model", "own"):
        assert r["scenarios"][s]["end"]["p_first"] == 0.0
        assert sum(r["scenarios"][s]["end"]["win_share"].values()) == pytest.approx(1.0)
    assert r["scenarios"]["model"]["end"]["expected"]["A"] == pytest.approx(5.0)
    assert r["ppd_model"] == pytest.approx(1.0)


def test_model_scenario_wins_when_close():
    ds, rec = _ds(0.0, 0.0, start_b=3.0)        # B leads by 3 start points, nobody scores; the model scores 1/day
    r = race.compute(ds, rec, today=D(2030, 12, 1), n_sims=2000)
    assert r["standings"]["B"] == 3.0
    sm, so = r["scenarios"]["model"], r["scenarios"]["own"]
    assert sm["end"]["p_first"] == 1.0           # +5 in 5 days > 3
    assert sm["two_weeks"]["days"] == 5          # fewer than 10 days left -> horizon = season end
    assert so["end"]["p_first"] == 0.0           # playing like so far (0 points) never catches up
    assert r["needed_ppd_vs_leader"] == pytest.approx(0.0 + 3.5 / 5)
    assert "Siegchance" in race.summary(r, "de") and "probabilità" in race.summary(r, "it")


def test_newbie_start_points_count_and_simulated_as_regular():
    ds, rec = _ds(0.0, 1.0, newbie=True)
    r = race.compute(ds, rec, today=D(2030, 12, 1), n_sims=2000)
    assert r["standings"]["N"] == 100.0 and r["newbies"] == ["N"]
    # N gets the points of a regular player of the drawn day: B (A is me) -> +1 per day
    assert r["scenarios"]["model"]["end"]["expected"]["N"] == pytest.approx(105.0)
    assert r["ppd"]["N"] == 0.0                  # own tipping days only, start points excluded


def test_no_race_without_history():
    ds, rec = _ds(0.0, 0.0, n_served=5)
    assert race.compute(ds, rec, today=D(2030, 12, 1)) is None     # < 20 pool days


def test_missing_menus():
    ds, _ = _ds(0.0, 0.0, n_served=10, n_pending=6)
    pend = [m.date for m in ds.menus if m.status == "pending"]
    target = pend[-1]
    miss = missing_menus(ds, target)
    assert miss == [d.isoformat() for d in pend[:-1]]
    assert missing_menus(ds, pend[0]) == []
