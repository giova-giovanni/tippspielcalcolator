"""Tests for engine/model.py: probability sanity, no leakage, Lent/fish labels, calendar."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # run with plain `pytest` too

import datetime as dt
import random

import numpy as np
import pytest

from engine import CATEGORIES
from engine import model as M
from engine.data import Menu, load_dataset


@pytest.fixture(scope="module")
def ds():
    return load_dataset()


@pytest.fixture(scope="module")
def cal(ds):
    return M.WorkCalendar(ds.workdays(), ds.free_days)


def _hist(ds, day):
    return [m for m in ds.served if m.date < day]


@pytest.mark.parametrize("name", M.MODEL_NAMES)
def test_probabilities_valid(ds, cal, name):
    day = dt.date(2025, 10, 15)
    pr = M.Predictor(name, None, ds.norm, cal).fit(_hist(ds, day))
    probs = pr.predict(day)
    for cat in CATEGORIES:
        p = np.array(list(probs[cat].values()))
        assert p.size > 5
        assert np.all(p >= 0)
        assert p.sum() <= 1 + 1e-9
        assert p.sum() > 0.8           # most mass on known dishes
    pn = pr.p_new(day)
    for cat in CATEGORIES:
        assert 0 < pn[cat] < 0.5
        assert abs(sum(probs[cat].values()) + pn[cat] - 1) < 1e-6


def test_p_beilage_given_haupt(ds, cal):
    day = dt.date(2026, 5, 6)
    pr = M.Predictor("heuristic", None, ds.norm, cal).fit(_hist(ds, day))
    table = pr.p_beilage_given_haupt(day)
    assert table
    for h, row in table.items():
        vals = np.array(list(row.values()))
        assert np.all(vals >= 0)
        assert abs(vals.sum() - 1) < 1e-6
    # strong learnt association: Champignonschnitzel -> Reis
    assert max(table["Champignonschnitzel"], key=table["Champignonschnitzel"].get) == "Reis"


def _scramble_future(ds, day, seed=1):
    """Copy of the served menus where every menu ON/AFTER ``day`` gets random other dishes."""
    rng = random.Random(seed)
    pool = {c: sorted({o for m in ds.served for o in m.options.get(c, [])}) for c in CATEGORIES}
    out = []
    for m in ds.served:
        if m.date >= day:
            opts = {c: [rng.choice(pool[c] + ["Brandneues Gericht X"])] for c in CATEGORIES}
            out.append(Menu(m.date, "served", [opts[c][0] for c in CATEGORIES], opts))
        else:
            out.append(m)
    return out


@pytest.mark.parametrize("name", M.MODEL_NAMES)
def test_no_leakage_predict(ds, cal, name):
    """Predicting day d must not depend on menus >= d (module-level predict filters the history)."""
    day = dt.date(2025, 11, 12)
    a = M.predict(day, ds.served, ds.norm, name=name, calendar=cal)
    b = M.predict(day, _scramble_future(ds, day), ds.norm, name=name, calendar=cal)
    for cat in CATEGORIES:
        assert a[cat].keys() == b[cat].keys()
        for k in a[cat]:
            assert a[cat][k] == pytest.approx(b[cat][k], abs=1e-12)


def test_no_leakage_walk(ds, cal):
    """The backtest feature pass over the FULL sequence gives the same features for prefix n
    whether or not the later menus are changed."""
    day = dt.date(2026, 3, 11)
    enc_a = M.Encoded(ds.served, ds.norm, cal)
    enc_b = M.Encoded(_scramble_future(ds, day, seed=5), ds.norm, cal)
    n = enc_a.prefix_len(day)
    assert n == enc_b.prefix_len(day)
    fa = M.walk(enc_a, [(day, n), (day + dt.timedelta(days=1), n)], {})
    fb = M.walk(enc_b, [(day, n), (day + dt.timedelta(days=1), n)], {})
    for key in fa:
        for cat in CATEGORIES:
            ca, cb = fa[key].chans[cat], fb[key].chans[cat]
            assert ca.labels == cb.labels
            assert np.allclose(ca.p_heur, cb.p_heur)
            assert np.allclose(ca.X, cb.X)


def test_predict_rejects_target_inside_history(ds, cal):
    day = dt.date(2025, 6, 4)
    pr = M.Predictor("heuristic", None, ds.norm, cal).fit(_hist(ds, day + dt.timedelta(days=3)))
    with pytest.raises(ValueError):
        pr.predict(day)


def test_fish_labels_outside_and_inside_lent(ds, cal):
    norm = ds.norm
    # outside Lent: generic fish grouped as "Fisch", Scombri stays exact
    day = dt.date(2026, 10, 9)
    ph = M.predict(day, ds.served, norm, name="heuristic", calendar=cal)["hauptspeise"]
    assert "Fisch" in ph
    assert "Scombri" in ph
    assert not any(norm.is_generic_fish_ok(lab) for lab in ph)
    # inside Lent (Friday 2026-03-13): exact fish names, no generic label
    lday = dt.date(2026, 3, 13)
    pl = M.predict(lday, ds.served, norm, name="heuristic", calendar=cal)["hauptspeise"]
    assert "Fisch" not in pl
    exact_fish = [lab for lab in pl if norm.is_generic_fish_ok(lab)]
    assert len(exact_fish) >= 3
    # fish is boosted on a Lent Friday compared with a non-Lent Friday
    p_fish_lent = sum(p for lab, p in pl.items() if norm.is_fish(lab))
    p_fish_out = sum(p for lab, p in ph.items() if norm.is_fish(lab))
    assert p_fish_lent > 2 * p_fish_out


def test_model_label_mapping(ds):
    norm = ds.norm
    assert norm.model_label("Forelle", "hauptspeise", False) == "Fisch"
    assert norm.model_label("Forelle", "hauptspeise", True) == "Forelle"
    assert norm.model_label("Scombri", "hauptspeise", False) == "Scombri"
    assert norm.model_label("Nudel mit Thunfischsoße", "vorspeise", False) == "Nudel mit Thunfischsoße"


def test_calendar_ordinals(ds, cal):
    w = ds.workdays()
    o = [cal.ord(d) for d in w]
    assert o == sorted(o)
    assert all(b - a == 1 for a, b in zip(o, o[1:]))
    # date beyond the known calendar: counted in Mon–Fri days
    small = M.WorkCalendar([dt.date(2026, 1, 5), dt.date(2026, 1, 6)])
    assert small.ord(dt.date(2026, 1, 8)) == 3       # Wed, Thu after Tue
    assert small.ord(dt.date(2026, 3, 2)) == 2        # long break counts as one day


def test_history_only_sum_and_unseen(ds, cal):
    """With a tiny history the model still returns a proper sub-distribution."""
    hist = ds.served[:8]
    day = ds.served[8].date
    for name in ("frequency", "heuristic"):
        probs = M.Predictor(name, None, ds.norm, cal).fit(hist).predict(day)
        for cat in CATEGORIES:
            s = sum(probs[cat].values())
            assert 0 < s <= 1


# ---------------------------------------------------------------- leakage audit (tuned params, all models)
def _perturb_menus(ds, day, seed=3):
    """Copy of ALL menus where every served menu ON/AFTER ``day`` gets random dishes (incl. a brand-new
    one) and some served days AFTER ``day`` become "unknown"."""
    rng = random.Random(seed)
    pool = {c: sorted({o for m in ds.served for o in m.options.get(c, [])}) for c in CATEGORIES}
    out = []
    for m in ds.menus:
        if m.date >= day and m.status == "served":
            if m.date > day and rng.random() < 0.15:
                out.append(Menu(m.date, "unknown", ["-", "-", "-"], {c: [] for c in CATEGORIES}))
                continue
            opts = {c: [rng.choice(pool[c] + ["Brandneues Gericht X"])] for c in CATEGORIES}
            out.append(Menu(m.date, "served", [opts[c][0] for c in CATEGORIES], opts))
        else:
            out.append(m)
    return out


def _dataset(ds, menus):
    from engine.data import Dataset

    return Dataset(list(menus), list(ds.tips), ds.norm, ds.config)


def _same(a: dict, b: dict):
    for cat in CATEGORIES:
        assert a[cat].keys() == b[cat].keys()
        for k in a[cat]:
            assert a[cat][k] == pytest.approx(b[cat][k], abs=1e-12)


@pytest.mark.parametrize("day", [dt.date(2026, 3, 11), dt.date(2026, 9, 18)])   # Lent Wednesday, normal Friday
@pytest.mark.parametrize("name", M.MODEL_NAMES)
def test_no_leakage_predictor_tuned_params(ds, name, day):
    """Recommendation path (Predictor, tuned params from data/model_params.json): perturbing every menu
    >= d changes nothing for d – probabilities, B|H table and week forecasts."""
    _, params = M.load_params()
    dsb = _dataset(ds, _perturb_menus(ds, day))
    res = []
    for x in (ds, dsb):
        cal = M.WorkCalendar(x.workdays(), x.free_days)
        pr = M.Predictor(name, params, x.norm, cal).fit([m for m in x.served if m.date < day])
        res.append((pr.predict(day), pr.p_beilage_given_haupt(day),
                    pr.predict_week([day, day + dt.timedelta(days=3), day + dt.timedelta(days=4)])))
    _same(res[0][0], res[1][0])
    assert res[0][1].keys() == res[1][1].keys()
    for h in res[0][1]:
        for b, v in res[0][1][h].items():
            assert v == pytest.approx(res[1][1][h][b], abs=1e-12)
    for wa, wb in zip(res[0][2], res[1][2]):
        _same(wa, wb)


def test_no_leakage_backtest_walk_forward(ds):
    """Backtest path (shared feature pass over the FULL sequence, cached ML refits, simulated R4 history):
    perturbing every menu >= d leaves all probabilities and all tips of the days <= d unchanged."""
    from engine import backtest as B

    _, params = M.load_params()
    day = dt.date(2025, 11, 12)
    start, end = dt.date(2025, 10, 20), dt.date(2025, 11, 21)
    sims = [B.Sim(x, params, start, end) for x in (ds, _dataset(ds, _perturb_menus(ds, day)))]
    scs = [s.ml_scorers(params) for s in sims]
    days = [t for t in sims[0].eval_days if t <= day]
    assert days == [t for t in sims[1].eval_days if t <= day] and day in days
    for name in M.MODEL_NAMES:
        sc = [s if name in ("ml", "ensemble") else None for s in scs]
        for t in days:
            la = sims[0].day_probs(name, t, params, sc[0])
            lb = sims[1].day_probs(name, t, params, sc[1])
            assert [df.day for df, _ in la] == [df.day for df, _ in lb]
            for (dfa, aa), (dfb, ab) in zip(la, lb):
                _same(M.as_dict(dfa, aa), M.as_dict(dfb, ab))
        ra = B.play(sims[0], name, params, sc[0], strategies=("week_planner", "greedy"))
        rb = B.play(sims[1], name, params, sc[1], strategies=("week_planner", "greedy"))
        for s in ("week_planner", "greedy"):
            ta = [(r["date"], r["tip"]) for r in ra[s] if r["date"] <= day]
            tb = [(r["date"], r["tip"]) for r in rb[s] if r["date"] <= day]
            assert ta == tb


def test_tuning_never_sees_2026(ds):
    """The simulations used by tune() (end = validation end) never build features or ML rows from 2026,
    and their tune/validation metrics are identical when every 2026 menu is perturbed."""
    from engine import backtest as B

    _, params = M.load_params()
    end = B.SPLITS["validation"][1]
    y2026 = dt.date(2026, 1, 1)
    sims = [B.Sim(x, params, B.START, end) for x in (ds, _dataset(ds, _perturb_menus(ds, y2026, seed=9)))]
    s0 = sims[0]
    assert max(d for d, _ in s0.feats) < y2026
    assert all(n == 0 or s0.enc.dates[n - 1] < y2026 for _, n in s0.feats)
    scs = [s.ml_scorers(params) for s in sims]
    for name in ("heuristic", "ensemble"):
        sc = [s if name in ("ml", "ensemble") else None for s in scs]
        pa = B.prob_metrics(sims[0], name, params, sc[0])
        pb = B.prob_metrics(sims[1], name, params, sc[1])
        for sp in ("tune", "validation"):
            assert pa[sp]["wll"] == pytest.approx(pb[sp]["wll"], abs=1e-12)
        ra = B.play(sims[0], name, params, sc[0], strategies=("week_planner",))["week_planner"]
        rb = B.play(sims[1], name, params, sc[1], strategies=("week_planner",))["week_planner"]
        assert [(r["date"], r["tip"], r["points"]) for r in ra] == [(r["date"], r["tip"], r["points"]) for r in rb]


def test_backtest_and_leaderboard_include_today_once_its_menu_is_known(ds, monkeypatch):
    """On-data run after lunch: today's menu and the players' points are entered. The backtest must
    then score the model on today too, otherwise the leaderboard compares the players through
    today with the model through yesterday (players get today's points, the model 0)."""
    from engine import backtest as B
    from engine.data import Dataset, Tip
    from engine.rules import score_tip

    day = dt.date(2026, 10, 9)
    opts = {"vorspeise": ["Nudel mit Pesto"], "hauptspeise": ["Leberkas"], "beilage": ["Pommes"]}
    menus = [m if m.date != day else Menu(day, "served", [o[0] for o in opts.values()], dict(opts))
             for m in ds.menus]
    tips = []
    for t in ds.tips:
        if t.date == day:
            pts, hits = score_tip(t.options, opts, day, ds.norm, ds.config.get("scoring"))
            t = Tip(t.date, t.player, list(t.raw), dict(t.options), points=pts, hits=hits)
        tips.append(t)
    dsx = Dataset(menus, tips, ds.norm, ds.config)
    assert any(t.date == day and t.points for t in dsx.tips)   # somebody scored today

    # run() simulates through ``today`` (captured without running the whole backtest)
    seen = {}

    class _Stop(Exception):
        pass

    def fake_sim(ds_, params, start, end=None, **kw):
        seen["end"] = end
        raise _Stop

    monkeypatch.setattr(B, "Sim", fake_sim)
    with pytest.raises(_Stop):
        B.run(dsx, today=day, verbose=False)
    assert seen["end"] == day
    monkeypatch.undo()

    _, params = M.load_params()
    sim = B.Sim(dsx, params, dt.date(2026, 9, 28), day, with_ml=False)
    assert sim.eval_days[-1] == day
    rec = B.play(sim, "heuristic", params, None, strategies=("greedy",))["greedy"]
    lb = B._leaderboard(dsx, rec, "heuristic", day)["years"]["2026"]
    assert lb["dates"][-1] == day.isoformat()
    model_today = next(r["points"] for r in rec if r["date"] == day)
    s = lb["series"]["Modell"]
    assert s[-1] - s[-2] == pytest.approx(model_today)
    # tips after ``until`` never enter the leaderboard / player stats
    lb_y = B._leaderboard(dsx, [r for r in rec if r["date"] < day], "heuristic", day - dt.timedelta(days=1))
    assert lb_y["years"]["2026"]["dates"][-1] == (day - dt.timedelta(days=1)).isoformat()
    full = B.player_stats(dsx, day)["2026"]
    prev = B.player_stats(dsx, day - dt.timedelta(days=1))["2026"]
    tipped_today = {t.player for t in dsx.tips if t.date == day}
    for pl in tipped_today:
        assert full[pl]["days"] == prev[pl]["days"] + 1
