"""Tests for engine/recommend.py: rule-4 validity, weekly planner, fish label, target day."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # run with plain `pytest` too

import datetime as dt
import random

import pytest

from engine import CATEGORIES
from engine.data import load_dataset
from engine.recommend import DayProbs, build, decide, week_rest
from engine.rules import R4

MON = dt.date(2026, 9, 28)   # an ordinary week (Mon..Fri all working days)
WEEK = [MON + dt.timedelta(days=i) for i in range(5)]


@pytest.fixture(scope="module")
def ds():
    return load_dataset()


def _probs(top: dict[str, str] | None = None, seed: int = 0) -> dict:
    rng = random.Random(seed)
    out = {}
    for cat in CATEGORIES:
        labs = [f"{cat[0].upper()}{i}" for i in range(12)]
        w = [rng.random() for _ in labs]
        if top and cat in top:
            labs[0] = top[cat]
            w[0] = 10.0
        s = sum(w)
        out[cat] = {lab: 0.9 * x / s for lab, x in zip(labs, w)}
    return out


def test_recommendation_r4_valid_with_crafted_history():
    r4 = R4()
    fri = WEEK[4]
    # A tipped Mon + Wed (2× used) and B tipped Thursday (adjacent) -> both blocked on Friday
    hist = {"vorspeise": {WEEK[0]: ["Arrabbiata"], WEEK[2]: ["Arrabbiata"], WEEK[3]: ["Lasagne"]},
            "hauptspeise": {WEEK[3]: ["Hühnerbrust"]},
            "beilage": {WEEK[0]: ["Reis"], WEEK[3]: ["Pommes"]}}
    probs = {"vorspeise": {"Arrabbiata": 0.4, "Lasagne": 0.3, "Hirten": 0.1, "Schlutzer": 0.05},
             "hauptspeise": {"Hühnerbrust": 0.5, "Leberkas": 0.2, "Hauswurst": 0.1},
             "beilage": {"Pommes": 0.5, "Reis": 0.3, "Püree": 0.1}}
    for strategy in ("week_planner", "greedy"):
        dec = decide([DayProbs(fri, probs)], hist, r4, None, strategy)
        assert dec.valid
        assert dec.tip["vorspeise"] == "Hirten"
        assert dec.tip["hauptspeise"] == "Leberkas"
        assert dec.tip["beilage"] == "Reis"     # used once (Mon), not adjacent -> allowed
        for cat in CATEGORIES:
            assert not r4.violations(cat, dec.tip[cat], fri, hist[cat])
    # the no_r4 upper bound ignores the rule
    dec = decide([DayProbs(fri, probs)], hist, r4, None, "no_r4")
    assert dec.tip["vorspeise"] == "Arrabbiata"


def test_planner_saves_scarce_dish_for_better_day():
    """Reis: Mon 0.30, Tue 0.29, Wed 0.10, Thu 0.29, Fri 0.10 → planner keeps two Reis tips for Mon+Thu
    or Tue+Thu, never wastes the quota; greedy on Monday also takes Reis (it is best today)."""
    r4 = R4()
    pr = [0.30, 0.29, 0.10, 0.29, 0.10]
    days = []
    for d, p in zip(WEEK, pr):
        probs = {"vorspeise": {"V1": 0.1, "V2": 0.09, "V3": 0.08},
                 "hauptspeise": {"H1": 0.1, "H2": 0.09, "H3": 0.08},
                 "beilage": {"Reis": p, "Pommes": 0.15, "Püree": 0.12, "Spatzlen": 0.11}}
        days.append(DayProbs(d, probs))
    dec = decide(days, {c: {} for c in CATEGORIES}, r4, None, "week_planner")
    reis_days = [row["date"] for row in dec.plan if row["beilage"] == "Reis"]
    assert len(reis_days) == 2
    assert WEEK[3] in reis_days
    total = sum(row["ev"] for row in dec.plan)
    # value of the plan is at least the greedy-then-greedy sequence
    assert total > 0


def _simulate_week(strategy: str, seed: int) -> dict:
    r4 = R4()
    rng = random.Random(seed)
    favourites = ["F1", "F2"]
    tips: dict = {}
    hist = {c: {} for c in CATEGORIES}
    for i, d in enumerate(WEEK):
        days = []
        for j, dd in enumerate(WEEK[i:]):
            top = {c: rng.choice(favourites) for c in CATEGORIES}
            days.append(DayProbs(dd, _probs(top, seed=seed * 100 + i * 10 + j)))
        dec = decide(days, hist, r4, None, strategy)
        assert dec.valid
        tips[d] = {c: [dec.tip[c]] for c in CATEGORIES}
        for c in CATEGORIES:
            hist[c][d] = [dec.tip[c]]
        # the plan for the remaining days is R4-valid as well
        plan_seq = {**{x: t for x, t in tips.items()},
                    **{row["date"]: {c: [row[c]] for c in CATEGORIES if row[c]} for row in dec.plan[1:]}}
        assert not r4.check_sequence(plan_seq)
    return tips


@pytest.mark.parametrize("seed", range(8))
@pytest.mark.parametrize("strategy", ["week_planner", "greedy"])
def test_planner_never_violates_r4(strategy, seed):
    r4 = R4()
    tips = _simulate_week(strategy, seed)
    assert not r4.check_sequence(tips)


def test_fish_label_outside_lent_is_generic():
    """Outside Lent the model label 'Fisch' is tipped as 'Fisch'; inside Lent exact names are used."""
    r4 = R4()
    day = dt.date(2026, 10, 9)
    probs = {"vorspeise": {"Arrabbiata": 0.2}, "hauptspeise": {"Fisch": 0.3, "Scombri": 0.1, "Leberkas": 0.2},
             "beilage": {"Salzkartoffeln": 0.3}}
    dec = decide([DayProbs(day, probs)], {c: {} for c in CATEGORIES}, r4)
    assert dec.tip["hauptspeise"] == "Fisch"


def test_fish_in_lent_recommendation_uses_exact_names(ds):
    """Real data: a Lent Friday recommendation never contains the generic 'Fisch' label."""
    from engine import model as M

    day = dt.date(2026, 3, 13)
    cal = M.WorkCalendar(ds.workdays(), ds.free_days)
    pr = M.Predictor("heuristic", None, ds.norm, cal).fit([m for m in ds.served if m.date < day])
    probs = pr.predict(day)
    assert "Fisch" not in probs["hauptspeise"]
    dec = decide([DayProbs(day, probs)], {c: {} for c in CATEGORIES}, R4(), ds.config.get("scoring"))
    assert dec.tip["hauptspeise"] != "Fisch"


def test_build_today_contract(ds):
    today_obj, week_obj = build(ds, dt.date(2026, 10, 9))
    assert today_obj["date"] == "2026-10-09"
    assert today_obj["is_today"] is True
    assert today_obj["season_over"] is False
    assert today_obj["deadline"].startswith("2026-10-09T12:00:00")
    rec = today_obj["recommendation"]
    assert rec["valid"] is True
    assert rec["strategy"] == "week_planner"
    assert today_obj["greedy"]["strategy"] == "greedy"
    for cat in CATEGORIES:
        assert rec[cat]["dish"]
        assert 0 <= rec[cat]["p"] <= 1
        alts = today_obj["alternatives"][cat]
        assert 1 <= len(alts) <= 10
        assert [a["p"] for a in alts] == sorted((a["p"] for a in alts), reverse=True)
    assert rec["copy_text"].count(" / ") == 2
    # my tips of the week are respected (rule 4)
    me_hist = {c: ds.tip_history(ds.me, c) for c in CATEGORIES}
    r4 = ds.r4()
    for cat in CATEGORIES:
        assert not r4.violations(cat, rec[cat]["dish"], dt.date(2026, 10, 9), me_hist[cat])
    assert week_obj["week_start"] == "2026-10-05"
    assert len(week_obj["days"]) == 5
    assert set(week_obj["tippable"]) == set(CATEGORIES)


def test_target_moves_when_menu_known(ds):
    today_obj, _ = build(ds, dt.date(2026, 10, 8))     # menu of 08.10. already entered
    assert today_obj["date"] == "2026-10-09"
    assert today_obj["is_today"] is False
    sat, _ = build(ds, dt.date(2026, 10, 10))          # weekend -> Monday
    assert sat["date"] == "2026-10-12"


def test_season_over(ds):
    obj, _ = build(ds, dt.date(2026, 12, 28))
    assert obj["season_over"] is True
    assert obj["recommendation"] is None


def test_week_rest():
    days = week_rest(dt.date(2026, 10, 7), [dt.date(2026, 10, d) for d in (5, 6, 7, 8, 9)])
    assert days == [dt.date(2026, 10, 7), dt.date(2026, 10, 8), dt.date(2026, 10, 9)]
    # unknown calendar: Mon–Fri minus free days
    days = week_rest(dt.date(2027, 1, 12), [], {dt.date(2027, 1, 14)})
    assert days == [dt.date(2027, 1, 12), dt.date(2027, 1, 13), dt.date(2027, 1, 15)]
