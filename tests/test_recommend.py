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


# ---------------------------------------------------------------- deadline / target day / robustness
import zoneinfo

from engine.data import Dataset, Menu, Tip
from engine.recommend import _target_day, deadline_passed, rollout

ROME = zoneinfo.ZoneInfo("Europe/Rome")


def _at(day: dt.date, hh: int, mm: int = 0) -> dt.datetime:
    return dt.datetime(day.year, day.month, day.day, hh, mm, tzinfo=ROME)


def _truncated(ds, day: dt.date, my_tips: dict | None = None, drop_my_tips: bool = False) -> Dataset:
    """Dataset as it looked on ``day`` morning: menus >= day pending (free days stay free), tips >= day
    removed. ``my_tips``: {date: {cat: dish}} replaces MY tips of those dates."""
    menus = []
    for m in ds.menus:
        if m.date >= day and m.status in ("served", "unknown"):
            menus.append(Menu(m.date, "pending", ["", "", ""], {c: [] for c in CATEGORIES}))
        else:
            menus.append(m)
    tips = [t for t in ds.tips if t.date < day and not (t.player == ds.me and (drop_my_tips or
                                                                             (my_tips and t.date in my_tips)))]
    for d, tip in (my_tips or {}).items():
        opts = {c: [tip[c]] if tip.get(c) else [] for c in CATEGORIES}
        tips.append(Tip(d, ds.me, [tip.get(c, "") for c in CATEGORIES], opts))
    return Dataset(menus, tips, ds.norm, ds.config)


def _check_today(ds, obj, week_obj, target: dt.date):
    assert obj["date"] == target.isoformat()
    assert obj["season_over"] is False
    rec = obj["recommendation"]
    assert rec["valid"] is True
    r4 = ds.r4()
    for cat in CATEGORIES:
        assert rec[cat]["dish"]
        assert not r4.violations(cat, rec[cat]["dish"], target, ds.tip_history(ds.me, cat))
    plan = obj["week_plan"]
    assert plan[0]["date"] == target.isoformat()
    from engine.dates import week_key
    assert all(week_key(dt.date.fromisoformat(r["date"])) == week_key(target) for r in plan)
    # the whole plan together with my tips of the week is rule-4 valid
    seq = {d: {c: o for c in CATEGORIES for o in [ds.tip_history(ds.me, c).get(d)] if o}
           for d in {t.date for t in ds.tips if t.player == ds.me}}
    for r in plan:
        seq[dt.date.fromisoformat(r["date"])] = {c: [r[c]] for c in CATEGORIES if r[c]}
    assert not r4.check_sequence({d: v for d, v in seq.items() if week_key(d) == week_key(target)})
    assert week_obj["week_start"] == (target - dt.timedelta(days=target.weekday())).isoformat()


def test_deadline_passed_helper(ds):
    d = dt.date(2026, 10, 9)
    assert not deadline_passed(d, _at(d, 11, 59), ds.config)
    assert deadline_passed(d, _at(d, 12, 0), ds.config)
    assert deadline_passed(d, dt.datetime(2026, 10, 9, 10, 30, tzinfo=dt.timezone.utc), ds.config)  # 12:30 Rome
    assert not deadline_passed(d, dt.datetime(2026, 10, 9, 9, 59, tzinfo=dt.timezone.utc), ds.config)
    assert not deadline_passed(d, None, ds.config)
    assert deadline_passed(d, dt.datetime(2026, 10, 9, 12, 5), ds.config)   # naive = local time


def test_deadline_friday_moves_to_next_week(ds):
    fri = dt.date(2026, 10, 9)
    before, _ = build(ds, fri, now=_at(fri, 11, 59))
    assert before["date"] == "2026-10-09" and before["is_today"] is True
    after, week_obj = build(ds, fri, now=_at(fri, 12, 0))
    assert after["is_today"] is False
    assert after["today_deadline_passed"] is True
    _check_today(ds, after, week_obj, dt.date(2026, 10, 12))
    assert after["my_week"] == []                      # nothing tipped yet in the new week
    assert after["deadline"].startswith("2026-10-12T12:00:00")
    assert [d["date"] for d in week_obj["days"]][0] == "2026-10-12"


def test_deadline_midweek_moves_to_tomorrow_and_forecasts_today(ds):
    wed = dt.date(2026, 10, 7)
    my = {dt.date(2026, 10, 5): {"vorspeise": "Arrabbiata", "hauptspeise": "Hühnerbrust", "beilage": "Reis"},
          dt.date(2026, 10, 6): {"vorspeise": "Hirten", "hauptspeise": "Leberkas", "beilage": "Pommes"},
          wed: {"vorspeise": "Lasagne", "hauptspeise": "Hauswurst", "beilage": "Reis"}}
    dst = _truncated(ds, wed, my_tips=my)
    obj, week_obj = build(dst, wed, now=_at(wed, 14, 0))
    _check_today(dst, obj, week_obj, dt.date(2026, 10, 8))
    assert obj["is_today"] is False
    rec = obj["recommendation"]
    # Reis tipped Mon + Wed -> quota used up; Lasagne/Hauswurst tipped Wed -> adjacent to Thu
    assert rec["beilage"]["dish"] != "Reis"
    assert rec["vorspeise"]["dish"] != "Lasagne" and rec["hauptspeise"]["dish"] != "Hauswurst"
    assert [x["date"] for x in obj["my_week"]] == ["2026-10-05", "2026-10-06", "2026-10-07"]
    days = {d["date"]: d for d in week_obj["days"]}
    assert days["2026-10-07"]["forecast"] is not None   # today's (unknown) menu is still forecast
    assert days["2026-10-05"]["forecast"] is None and days["2026-10-05"]["menu"] is not None
    # before the deadline the target is today
    obj2, _ = build(dst, wed, now=_at(wed, 9, 0))
    assert obj2["date"] == "2026-10-07" and obj2["is_today"] is True


def test_no_now_means_no_deadline(ds):
    obj, _ = build(ds, dt.date(2026, 10, 9), now=None)
    assert obj["date"] == "2026-10-09" and obj["is_today"] is True


def test_season_end_and_deadline(ds):
    d = dt.date(2026, 12, 22)
    assert _target_day(ds, d, _at(d, 13, 0)) == (dt.date(2026, 12, 23), False)
    last = dt.date(2026, 12, 23)
    obj, week_obj = build(ds, last, now=_at(last, 12, 1))
    assert obj["season_over"] is True and obj["recommendation"] is None and obj["date"] is None
    assert week_obj["days"] and week_obj["tippable"].keys() == set(CATEGORIES)
    for d in (dt.date(2026, 12, 24), dt.date(2026, 12, 31), dt.date(2027, 1, 1) - dt.timedelta(days=1)):
        obj, _ = build(ds, d, now=_at(d, 8, 0))
        assert obj["season_over"] is True


def test_no_more_working_days_is_season_over(ds):
    """All remaining days of the season free -> season over, no crash."""
    d = dt.date(2026, 12, 21)
    menus = [m if m.date < d else Menu(m.date, "free", ["frei", "", ""], {c: [] for c in CATEGORIES})
             for m in ds.menus]
    dsx = Dataset(menus, list(ds.tips), ds.norm, ds.config)
    obj, week_obj = build(dsx, d, now=_at(d, 8, 0))
    assert obj["season_over"] is True and obj["recommendation"] is None
    assert all(x["status"] == "free" for x in week_obj["days"] if x["date"] >= "2026-12-21")


def test_lent_day_uses_exact_fish_names(ds):
    day = dt.date(2026, 3, 11)                 # Wednesday in Lent
    dst = _truncated(ds, day)
    obj, week_obj = build(dst, day, now=_at(day, 9, 0))
    _check_today(dst, obj, week_obj, day)
    assert obj["is_lent"] is True and obj["fish"]["lent"] is True
    labels = [a["dish"] for a in obj["alternatives"]["hauptspeise"]]
    assert "Fisch" not in labels
    for r in obj["week_plan"]:
        assert r["hauptspeise"] != "Fisch"
    for d in week_obj["days"]:
        if d["forecast"]:
            assert all(x["dish"] != "Fisch" for x in d["forecast"]["hauptspeise"])


def test_week_with_free_days(ds):
    """Week of 01.06.2026: Mon + Tue free. Friday 29.05. after the deadline -> Wednesday 03.06."""
    fri = dt.date(2026, 5, 29)
    dst = _truncated(ds, fri)
    obj, week_obj = build(dst, fri, now=_at(fri, 12, 30))
    _check_today(dst, obj, week_obj, dt.date(2026, 6, 3))
    assert [r["date"] for r in obj["week_plan"]] == ["2026-06-03", "2026-06-04", "2026-06-05"]
    st = {d["date"]: d["status"] for d in week_obj["days"]}
    assert st["2026-06-01"] == "free" and st["2026-06-02"] == "free"
    for row in week_obj["tippable"]["beilage"]:
        assert not set(row["blocked_days"]) & {"2026-06-01", "2026-06-02"}


def test_week_with_unknown_menu_and_no_my_tips(ds):
    """Easter Monday 06.04.2026 has status 'unknown'; no tips of mine at all -> still a valid tip."""
    tue = dt.date(2026, 4, 7)
    dst = _truncated(ds, tue, drop_my_tips=True)
    dst.menus_by_date[dt.date(2026, 4, 6)] = ds.menus_by_date[dt.date(2026, 4, 6)]
    assert ds.menus_by_date[dt.date(2026, 4, 6)].status == "unknown"
    assert not dst.tips_of(ds.me)
    obj, week_obj = build(dst, tue, now=_at(tue, 10, 0))
    _check_today(dst, obj, week_obj, tue)
    assert obj["my_week"] == []
    st = {d["date"]: d["status"] for d in week_obj["days"]}
    assert st["2026-04-06"] == "unknown"
    # an 'unknown' day is not a target (its menu row exists) – the target moves on
    menus = [Menu(m.date, "unknown", ["-", "-", "-"], {c: [] for c in CATEGORIES}) if m.date == tue else m
             for m in dst.menus]
    dsu = Dataset(menus, list(dst.tips), ds.norm, ds.config)
    obj2, _ = build(dsu, tue, now=_at(tue, 10, 0))
    assert obj2["date"] == "2026-04-08" and obj2["is_today"] is False


def test_greedy_strategy_and_discount_zero_equal_greedy(ds):
    probs = [_probs({"beilage": "Reis"}, seed=i) for i in range(5)]
    days = [DayProbs(d, p) for d, p in zip(WEEK, probs)]
    hist = {c: {} for c in CATEGORIES}
    g = decide(days, hist, R4(), None, "greedy")
    z = decide(days, hist, R4(), None, "week_planner", discount=0.0)
    assert g.tip == z.tip and g.ev == pytest.approx(z.ev)
    plan = rollout(days, hist, R4(), None, "greedy")
    assert [r["date"] for r in plan] == WEEK
    seq = {r["date"]: {c: [r[c]] for c in CATEGORIES if r[c]} for r in plan}
    assert not R4().check_sequence(seq)
    obj, _ = build(ds, dt.date(2026, 10, 9), strategy="greedy")
    assert obj["recommendation"]["strategy"] == "greedy"
    assert obj["recommendation"]["copy_text"] == obj["greedy"]["copy_text"]
    assert obj["week_plan"][0]["vorspeise"] == obj["recommendation"]["vorspeise"]["dish"]


def test_ev_formula(ds):
    """EV = 1·P(V) + 0.5·P(H) + 0.5·P(B) + 1·P(V)·P(H)·P(B|H)."""
    import numpy as np

    day = WEEK[2]
    probs = {"vorspeise": {"V1": 0.3}, "hauptspeise": {"H1": 0.4, "H2": 0.1},
             "beilage": {"B1": 0.2, "B2": 0.1}}
    pair = {"P": np.array([[0.9, 0.1], [0.5, 0.5]]), "h": {"H1": 0, "H2": 1}, "b": {"B1": 0, "B2": 1}}
    dec = decide([DayProbs(day, probs, pair)], {c: {} for c in CATEGORIES}, R4())
    assert dec.tip == {"vorspeise": "V1", "hauptspeise": "H1", "beilage": "B1"}
    assert dec.p_full == pytest.approx(0.3 * 0.4 * 0.9)
    assert dec.ev == pytest.approx(0.3 + 0.5 * 0.4 + 0.5 * 0.2 + 0.3 * 0.4 * 0.9)
    from engine.rules import expected_value
    assert dec.ev == pytest.approx(expected_value(0.3, 0.4, 0.2, dec.p_full))


def test_backtest_and_recommend_make_the_same_decision(ds):
    """Same decision code: the backtest's simulated tip for a day equals the recommendation built from the
    data as it looked that morning, with the backtest's own earlier tips of the week as 'my tips'."""
    from engine import backtest as B
    from engine import model as M

    _, params = M.load_params()
    mon, wed = dt.date(2025, 11, 10), dt.date(2025, 11, 12)
    sim = B.Sim(ds, params, mon, dt.date(2025, 11, 14), with_ml=False)
    for name in ("heuristic", "frequency"):
        for strat in ("week_planner", "greedy"):
            rec = B.play(sim, name, params, None, strategies=(strat,))[strat]
            byd = {r["date"]: r for r in rec}
            my = {d: byd[d]["tip"] for d in (mon, dt.date(2025, 11, 11))}
            dst = _truncated(ds, wed, my_tips=my)
            obj, _ = build(dst, wed, model_name=name, params=params, strategy=strat)
            got = {c: obj["recommendation"][c]["dish"] for c in CATEGORIES}
            assert got == byd[wed]["tip"], (name, strat)
            assert obj["recommendation"]["ev"] == pytest.approx(byd[wed]["ev"], rel=1e-9)
            # backtest scoring = rules.score_tip against ALL announced options
            from engine.rules import score_tip
            for r in rec:
                m = ds.menus_by_date[r["date"]]
                exp = score_tip({c: [r["tip"][c]] for c in CATEGORIES}, m.options, r["date"], ds.norm,
                                ds.config.get("scoring"))[0]
                assert r["points"] == exp


@pytest.mark.parametrize("seed", range(12))
def test_best_future_matches_brute_force(seed):
    """The branch & bound of the weekly planner finds the optimal rule-4-valid plan (incl. the
    'other dish' fallback that uses no quota)."""
    import itertools

    from engine.recommend import _R4Fast, _best_future, _top

    rng = random.Random(seed)
    r4 = R4()
    pool = ["Reis", "Pommes", "Püree", "Spatzlen", "Plent"]
    start = rng.randrange(0, 3)
    days = WEEK[start + 1:]
    hist_days = WEEK[:start + 1]
    hist = {d: [rng.choice(pool)] for d in hist_days}
    k = 3
    cands, fb = [], []
    for d in days:
        pr = {lab: rng.random() for lab in pool}
        cands.append(_top(pr, k))
        fb.append(_top(pr, k + 1)[k][1])
    w = [0.5 * 0.9 ** i for i in range(len(days))]
    from engine.normalize import fold
    used = {}
    for d, x in hist.items():
        used.setdefault(fold(x[0]), []).append(d)
    val, plan = _best_future(days, cands, w, used, _R4Fast(r4), fb)
    best = 0.0
    for combo in itertools.product(*[[c[0] for c in cs] + [None] for cs in cands]):
        h = dict(hist)
        ok, v = True, 0.0
        for i, (d, lab) in enumerate(zip(days, combo)):
            if lab is None:
                v += w[i] * fb[i]
                continue
            if r4.violations("beilage", lab, d, h):
                ok = False
                break
            h[d] = [lab]
            v += w[i] * dict(cands[i])[lab]
        if ok:
            best = max(best, v)
    assert val == pytest.approx(best, abs=1e-12)
    # the returned plan realises the value and is valid
    h = dict(hist)
    v = 0.0
    for i, (d, lab) in enumerate(zip(days, plan)):
        if lab is None:
            v += w[i] * fb[i]
        else:
            assert not r4.violations("beilage", lab, d, h)
            h[d] = [lab]
            v += w[i] * dict(cands[i])[lab]
    assert v == pytest.approx(val, abs=1e-12)


def test_cli_past_today_pretends_that_morning_and_dry_run_writes_nothing(ds, capsys):
    """`python -m engine.recommend --today <past day>` recommends for that day (not for the first
    day whose menu is still unknown, months later); --dry-run leaves docs/data untouched."""
    import json

    from engine.config import SITE_DATA
    from engine.recommend import as_of, main

    assert as_of(ds, dt.date(2026, 10, 9)) is ds          # live day: nothing to hide
    past = as_of(ds, dt.date(2026, 3, 6))
    assert past.menus_by_date[dt.date(2026, 3, 6)].status == "pending"
    assert past.menus_by_date[dt.date(2026, 3, 5)].status == "served"
    assert not [t for t in past.tips if t.date >= dt.date(2026, 3, 6)]
    assert past.free_days == ds.free_days

    files = [SITE_DATA / "today.json", SITE_DATA / "week.json"]
    before = [f.stat().st_mtime_ns if f.exists() else None for f in files]
    assert main(["--today", "2026-03-06", "--dry-run", "--json"]) == 0
    obj = json.loads(capsys.readouterr().out)
    assert [f.stat().st_mtime_ns if f.exists() else None for f in files] == before
    assert obj["date"] == "2026-03-06" and obj["is_today"] is True and obj["is_lent"] is True
    assert "Fisch" not in [a["dish"] for a in obj["alternatives"]["hauptspeise"]]
    assert obj["recommendation"]["valid"] is True
