"""Walk-forward backtest and hyper-parameter tuning.

For every working day from 2025-01-13 on (2024 = warm-up only) the models are trained on the
served menus strictly before that day, the tip is chosen with the decision code of
:mod:`engine.recommend` (EV maximisation, rule 4 w.r.t. the model's OWN simulated tips of the
same ISO week, strategy from data/model_params.json) and scored with :func:`engine.rules.score_tip`
against all announced options (fish rule included).

Leakage guards (tested in tests/test_model.py): one online feature pass where the features of a day
with prefix n only use the served menus 0..n-1; ML scorers for prefix n are fitted on rows j < n only;
the tuning simulations end at the validation split (no 2026 features, rows or metrics).

Splits: tune 2025-01-13..2025-08-31 · validation 2025-09-01..2025-12-19 · test 2026 (never tuned).

    python -m engine.backtest            # tune (if data/model_params.json is missing) + backtest
    python -m engine.backtest --tune     # force re-tuning
"""
from __future__ import annotations

import datetime as dt
import math
import time
from collections import defaultdict

import numpy as np

from . import CATEGORIES
from . import model as M
from .config import MODEL_PARAMS_JSON, REPORTS, load_json, save_json
from .dates import season_end, week_key, week_monday
from .recommend import DayProbs, decide, week_rest
from .rules import score_tip

START = dt.date(2025, 1, 13)
SPLITS = {
    "tune": (dt.date(2025, 1, 13), dt.date(2025, 8, 31)),
    "validation": (dt.date(2025, 9, 1), dt.date(2025, 12, 19)),
    "test": (dt.date(2026, 1, 12), dt.date(2026, 12, 23)),
}
STRATEGIES = ("week_planner", "greedy", "no_r4")
CAL_EDGES = [0.0, 0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 1.0001]
CAT_W = {"vorspeise": 1.0, "hauptspeise": 0.5, "beilage": 0.5}


def split_of(d: dt.date) -> str | None:
    for k, (a, b) in SPLITS.items():
        if a <= d <= b:
            return k
    if d >= SPLITS["test"][0]:  # later seasons (2027 …) are out-of-sample too
        return "test"
    return None


# ------------------------------------------------------------------ simulation
class Sim:
    """Shared precomputation for one parameter set."""

    def __init__(self, ds, params: dict, start: dt.date = START, end: dt.date | None = None,
                 week_targets: bool = True, with_ml: bool = True):
        self.ds = ds
        self.params = M.merge_params(params)
        self.cal = M.WorkCalendar(ds.workdays(), ds.free_days)
        self.enc = M.Encoded(ds.served, ds.norm, self.cal)
        last = max(m.date for m in ds.served)
        self.end = min(end or last, last)
        self.eval_days = [m.date for m in ds.menus
                          if m.status in ("served", "unknown") and start <= m.date <= self.end]
        self.weeks: dict = {}
        targets = set()
        wdays = ds.workdays()
        for t in self.eval_days:
            n = self.enc.prefix_len(t)
            if week_targets:
                days = week_rest(t, wdays, ds.free_days, season_end(t.year))
            else:
                days = [t]
            self.weeks[t] = (n, days)
            for d in days:
                targets.add((d, n))
        j0 = int(self.params["ml_min_day"])
        # ML training rows: only served days that precede some evaluation day (the scorer of an
        # evaluation day with prefix n is fitted on rows j < n) – nothing after ``end`` is touched
        self.n_max = max((n for n, _ in self.weeks.values()), default=0)
        if with_ml:
            for j in range(j0, self.n_max):
                targets.add((self.enc.dates[j], j))
        self.with_ml = with_ml
        self.feats = M.walk(self.enc, sorted(targets, key=lambda x: (x[1], x[0])), self.params, with_ml=with_ml)
        # training labels for every served day
        self.labels = []
        for j, m in enumerate(self.enc.menus):
            lb = M.menu_labels(m, ds.norm, m.lent)
            self.labels.append({c: (lb[c][0] if lb[c] else None) for c in CATEGORIES})
        self._ml_cache: dict = {}

    def ml_scorers(self, params: dict | None = None) -> dict:
        """prefix length -> fitted MLScorer (refit every ``ml_refit_every`` served days)."""
        p = M.merge_params({**self.params, **(params or {})})
        key = (p["ml_C"], p["ml_kind"], p["ml_refit_every"])
        if key in self._ml_cache:
            return self._ml_cache[key]
        j0 = int(p["ml_min_day"])
        every = int(p["ml_refit_every"])
        out = {}
        cur, last_n = None, None
        for t in self.eval_days:
            n = self.weeks[t][0]
            if cur is None or n - last_n >= every:
                days = [self.feats[(self.enc.dates[j], j)] for j in range(j0, n)]
                labs = [self.labels[j] for j in range(j0, n)]
                cur = M.MLScorer(p).fit(days, labs)
                last_n = n
            out[n] = cur
        self._ml_cache[key] = out
        return out

    def day_probs(self, name: str, t: dt.date, params: dict | None = None, scorers: dict | None = None,
                  arrays: bool = False):
        p = M.merge_params({**self.params, **(params or {})})
        n, days = self.weeks[t]
        ml = scorers.get(n) if scorers else None
        res = []
        for d in days:
            df = self.feats[(d, n)]
            res.append((df, M.probs_from_features(name, df, p, ml)))
        return res


def _actual(menu, norm, lent):
    return M.menu_labels(menu, norm, lent)


def prob_metrics(sim: Sim, name: str, params: dict | None = None, scorers: dict | None = None) -> dict:
    """Log-loss / top-k / calibration per split and category on the served eval days."""
    ds = sim.ds
    acc = {sp: {c: [] for c in CATEGORIES} for sp in SPLITS}
    cal = {c: [[0.0, 0.0, 0] for _ in range(len(CAL_EDGES) - 1)] for c in CATEGORIES}
    for t in sim.eval_days:
        m = ds.menus_by_date[t]
        if m.status != "served":
            continue
        sp = split_of(t)
        df, arr = sim.day_probs(name, t, params, scorers)[0]
        act = _actual(m, ds.norm, df.lent)
        for c in CATEGORIES:
            if not act[c] or df.chans.get(c) is None:
                continue
            cf = df.chans[c]
            a = arr[c]
            pd = dict(zip(cf.labels, a))
            p = pd.get(act[c][0], cf.p_new)
            order = np.argsort(-a)
            top = [cf.labels[i] for i in order[:3]]
            acc[sp][c].append((-math.log(max(p, 1e-6)), any(x in act[c] for x in top[:1]),
                               any(x in act[c] for x in top[:3])))
            if sp == "test" or sp is None:
                continue
            hits = np.array([lab in act[c] for lab in cf.labels])
            bins = np.searchsorted(CAL_EDGES, a, side="right") - 1
            for b, pp, h in zip(bins, a, hits):
                cal[c][b][0] += float(pp)
                cal[c][b][1] += float(h)
                cal[c][b][2] += 1
    out = {}
    for sp in SPLITS:
        r = {}
        for c in CATEGORIES:
            v = np.array(acc[sp][c], dtype=float)
            if v.size == 0:
                r[c] = None
                continue
            r[c] = {"logloss": float(v[:, 0].mean()), "top1": float(v[:, 1].mean()),
                    "top3": float(v[:, 2].mean()), "n": int(len(v))}
        if all(r[c] for c in CATEGORIES):
            r["wll"] = sum(CAT_W[c] * r[c]["logloss"] for c in CATEGORIES) / sum(CAT_W.values())
        out[sp] = r
    out["calibration"] = {c: [{"p_mean": (b[0] / b[2]) if b[2] else None, "hit_rate": (b[1] / b[2]) if b[2] else None,
                               "n": b[2], "bin": [CAL_EDGES[i], min(CAL_EDGES[i + 1], 1.0)]}
                              for i, b in enumerate(cal[c])] for c in CATEGORIES}
    return out


def calibration_all(sim: Sim, name: str, params=None, scorers=None) -> dict:
    """Calibration bins over every served eval day (all splits)."""
    ds = sim.ds
    cal = {c: [[0.0, 0.0, 0] for _ in range(len(CAL_EDGES) - 1)] for c in CATEGORIES}
    for t in sim.eval_days:
        m = ds.menus_by_date[t]
        if m.status != "served":
            continue
        df, arr = sim.day_probs(name, t, params, scorers)[0]
        act = _actual(m, ds.norm, df.lent)
        for c in CATEGORIES:
            if not act[c] or df.chans.get(c) is None:
                continue
            a = arr[c]
            hits = [lab in act[c] for lab in df.chans[c].labels]
            bins = np.searchsorted(CAL_EDGES, a, side="right") - 1
            for b, pp, h in zip(bins, a, hits):
                cal[c][b][0] += float(pp)
                cal[c][b][1] += float(h)
                cal[c][b][2] += 1
    return {c: [{"p_mean": round(b[0] / b[2], 4) if b[2] else None,
                 "hit_rate": round(b[1] / b[2], 4) if b[2] else None, "n": b[2],
                 "bin": [CAL_EDGES[i], min(CAL_EDGES[i + 1], 1.0)]}
                for i, b in enumerate(cal[c]) if b[2]] for c in CATEGORIES}


def play(sim: Sim, name: str, params: dict | None = None, scorers: dict | None = None,
         strategies=STRATEGIES, plan_discount: float | None = None) -> dict:
    """Simulated tipping with every strategy. Returns per-strategy daily records."""
    ds = sim.ds
    p = M.merge_params({**sim.params, **(params or {})})
    r4 = ds.r4()
    scoring = ds.config.get("scoring", {})
    hist = {s: {c: {} for c in CATEGORIES} for s in strategies}
    out = {s: [] for s in strategies}
    cross_week = r4.mode != "workday_adjacent_same_week"
    discount = float(p.get("plan_discount", 1.0)) if plan_discount is None else float(plan_discount)
    for t in sim.eval_days:
        lst = sim.day_probs(name, t, p, scorers)
        dicts = [M.as_dict(df, arr) for df, arr in lst]
        df0 = lst[0][0]
        rho = {c: (df0.chans[c].week_factor if df0.chans.get(c) else 1.0) for c in CATEGORIES}
        probs = M.week_correction(dicts, rho)
        pairs = M.full_pair_lookup(df0)
        days = sim.weeks[t][1]
        dps = [DayProbs(d, pb, pairs if i == 0 else None) for i, (d, pb) in enumerate(zip(days, probs))]
        m = ds.menus_by_date[t]
        for s in strategies:
            # rule-4 history = the model's OWN simulated tips of the same ISO week (plus the previous
            # working days only when the configured adjacency crosses week boundaries)
            # (same window as recommend.my_week_history: a long weekend/holiday gap can make
            # Friday -> Wednesday "adjacent" in the cross-week modes)
            h = {c: {d: o for d, o in hist[s][c].items() if d < t and (week_key(d) == week_key(t)
                     or (cross_week and d >= week_monday(t) - dt.timedelta(days=7)))} for c in CATEGORIES}
            dec = decide(dps, h, r4, scoring, s, discount=discount)
            tip = {c: [dec.tip[c]] if dec.tip[c] else [] for c in CATEGORIES}
            for c in CATEGORIES:
                if dec.tip[c]:
                    hist[s][c][t] = [dec.tip[c]]
            if m.status == "served":
                pts, hits = score_tip(tip, m.options, t, ds.norm, scoring)
            else:
                pts, hits = 0.0, {c: False for c in CATEGORIES}
            out[s].append({"date": t, "tip": dec.tip, "points": pts, "hits": hits, "served": m.status == "served",
                           "ev": dec.ev, "valid": dec.valid})
    # verify rule 4 on the simulated sequences
    for s in strategies:
        if s == "no_r4":
            continue
        seq = {r["date"]: {c: [r["tip"][c]] for c in CATEGORIES} for r in out[s]}
        viol = r4.check_sequence(seq)
        for r in out[s]:
            r["r4_ok"] = True
        if viol:
            bad = {d for d, _ in viol}
            for r in out[s]:
                if r["date"] in bad:
                    r["r4_ok"] = False
    return out


def summarize(records: list, key=lambda r: r["date"].year) -> dict:
    agg = defaultdict(lambda: {"days": 0, "points": 0.0, "hits": {c: 0 for c in CATEGORIES}, "full_hits": 0,
                               "r4_ok": True, "ev": 0.0})
    for r in records:
        k = key(r)
        if k is None:
            continue
        a = agg[k]
        a["points"] += r["points"]
        a["ev"] += r.get("ev", 0.0)
        if r.get("r4_ok") is False:
            a["r4_ok"] = False
        if not r["served"]:
            continue
        a["days"] += 1
        for c in CATEGORIES:
            a["hits"][c] += int(bool(r["hits"].get(c)))
        if all(r["hits"].values()):
            a["full_hits"] += 1
    out = {}
    for k, a in agg.items():
        d = max(a["days"], 1)
        out[str(k)] = {"days": a["days"], "points": round(a["points"], 2), "ppd": round(a["points"] / d, 4),
                       "acc": {c: round(a["hits"][c] / d, 4) for c in CATEGORIES}, "full_hits": a["full_hits"],
                       "r4_ok": a["r4_ok"], "expected_points": round(a["ev"], 2)}
    return out


def player_stats(ds, until: dt.date | None = None) -> dict:
    """Real players per year (points recomputed by the engine; days = served days with a tip <= ``until``)."""
    out: dict = {}
    for t in ds.tips:
        if until is not None and t.date > until:
            continue
        m = ds.menus_by_date.get(t.date)
        if m is None or m.status not in ("served", "unknown") or t.points is None:
            continue
        y = str(t.date.year)
        a = out.setdefault(y, {}).setdefault(t.player, {"days": 0, "points": 0.0, "hits": {c: 0 for c in CATEGORIES},
                                                         "full_hits": 0, "first": t.date})
        a["points"] += t.points
        if m.status == "served":
            a["days"] += 1
            for c in CATEGORIES:
                a["hits"][c] += int(bool(t.hits.get(c)))
            if t.hits and all(t.hits.values()):
                a["full_hits"] += 1
    res = {}
    for y, players in out.items():
        res[y] = {}
        for pl, a in players.items():
            d = max(a["days"], 1)
            res[y][pl] = {"days": a["days"], "points": round(a["points"], 2), "ppd": round(a["points"] / d, 4),
                          "acc": {c: round(a["hits"][c] / d, 4) for c in CATEGORIES}, "full_hits": a["full_hits"],
                          "first_tip": a["first"].isoformat()}
    return res


# ------------------------------------------------------------------ tuning
HEUR_GRID = {
    "half_life": [60.0, 150.0, 400.0, 1000.0],
    "hazard_mode": ["abs", "rel"],
    "hazard_kappa": [0.3, 1.0, 3.0],
    "hazard_smooth": [0.0, 0.25],
    "weekday_beta": [4.0, 12.0, 30.0, 80.0],
    "season_beta": [0.0, 15.0, 40.0, 120.0],
    "week_kappa": [0.5, 2.0, 8.0],
    "temperature": [1.0, 1.2, 1.4, 1.7],
}


def tune(ds, n_sweeps: int = 2, verbose: bool = True) -> dict:
    """Hyper-parameter search: coordinate descent on the tune split, selection on validation.

    2026 is never looked at. Writes data/model_params.json and returns it.
    """
    t0 = time.time()
    end = SPLITS["validation"][1]
    log = []

    def say(msg):
        log.append(msg)
        if verbose:
            print(f"[tune {time.time() - t0:6.1f}s] {msg}", flush=True)

    # ---- stage 1: heuristic factors – coordinate descent per category on the tune split,
    #      the number of sweeps (0 = defaults, 1, 2) is chosen per category on the validation split
    cur = {k: dict(v) for k, v in M.DEFAULT_PARAMS.items() if k in HEUR_GRID}
    cache: dict = {}

    def evaluate(cfg):
        key = repr(sorted((k, sorted(v.items())) for k, v in cfg.items()))
        if key not in cache:
            # B|H mixing off in stage 1 so that the categories are independent
            sim = Sim(ds, {**cfg, "beilage_mix": 0.0}, START, end, week_targets=False, with_ml=False)
            cache[key] = prob_metrics(sim, "heuristic")
        return cache[key]

    pm0 = evaluate(cur)
    best_loss = {c: pm0["tune"][c]["logloss"] for c in CATEGORIES}
    snapshots = [({k: dict(v) for k, v in cur.items()}, pm0)]
    for sweep in range(n_sweeps):
        for k, vals in HEUR_GRID.items():
            for v in vals:
                if all(cur[k][c] == v for c in CATEGORIES):
                    continue
                cfg = {kk: dict(vv) for kk, vv in cur.items()}
                cfg[k] = {c: v for c in CATEGORIES}
                # other params stay per-category: evaluate with the candidate value for all cats
                pm = evaluate(cfg)
                for c in CATEGORIES:
                    if pm["tune"][c]["logloss"] < best_loss[c] - 1e-6:
                        best_loss[c] = pm["tune"][c]["logloss"]
                        cur[k][c] = v
            say(f"sweep {sweep + 1} {k}: " + ", ".join(f"{c[0]}={cur[k][c]}" for c in CATEGORIES)
                + "  tune ll " + ", ".join(f"{c[0]}={best_loss[c]:.4f}" for c in CATEGORIES))
        snapshots.append(({k: dict(v) for k, v in cur.items()}, evaluate(cur)))
    chosen: dict = {k: {} for k in HEUR_GRID}
    for c in CATEGORIES:
        i_best = min(range(len(snapshots)), key=lambda i: snapshots[i][1]["validation"][c]["logloss"])
        for k in HEUR_GRID:
            chosen[k][c] = snapshots[i_best][0][k][c]
        say(f"heuristic {c}: {i_best} sweeps chosen on validation (val ll "
            + ", ".join(f"{snapshots[i][1]['validation'][c]['logloss']:.4f}" for i in range(len(snapshots))) + ")")
    params = M.merge_params(chosen)
    n_configs = len(cache)

    # ---- stage 2: Beilage given Hauptspeise mixing
    best_b = None
    for mix in (0.0, 0.3, 0.6, 0.9):
        for gamma, phl in ((1.0, 250.0), (0.3, 500.0), (3.0, 120.0)):
            if mix == 0.0 and gamma != 1.0:
                continue
            p2 = {**params, "beilage_mix": mix, "pair_gamma": gamma, "pair_half_life": phl}
            sim = Sim(ds, p2, START, end, week_targets=False, with_ml=False)
            pm = prob_metrics(sim, "heuristic")
            key = (pm["tune"]["beilage"]["logloss"], pm["validation"]["beilage"]["logloss"])
            say(f"beilage_mix={mix} gamma={gamma} pair_hl={phl}: tune {key[0]:.4f} val {key[1]:.4f}")
            if best_b is None or key[1] < best_b[0][1]:
                best_b = (key, mix, gamma, phl)
    params.update({"beilage_mix": best_b[1], "pair_gamma": best_b[2], "pair_half_life": best_b[3]})

    # ---- frequency baseline half-life
    best_f = None
    for hl in (0.0, 100.0, 250.0, 500.0):
        p3 = {**params, "freq_half_life": hl}
        sim = Sim(ds, p3, START, end, week_targets=False, with_ml=False)
        pm = prob_metrics(sim, "frequency")
        v = pm["validation"]["wll"]
        say(f"frequency half_life={hl or 'inf'}: val wll {v:.4f}")
        if best_f is None or v < best_f[0]:
            best_f = (v, hl)
    params["freq_half_life"] = best_f[1]

    # ---- stage 3: ML regularisation and ensemble weight (shared feature pass)
    sim = Sim(ds, params, START, end, week_targets=False, with_ml=True)
    best_ml = None
    for kind, C in (("lr", 0.01), ("lr", 0.03), ("lr", 0.1), ("clogit", 0.03), ("clogit", 0.1)):
        sc = sim.ml_scorers({"ml_C": C, "ml_kind": kind})
        pm = prob_metrics(sim, "ml", {"ml_C": C, "ml_kind": kind}, sc)
        say(f"ml {kind} C={C}: tune wll {pm['tune']['wll']:.4f} val wll {pm['validation']['wll']:.4f}")
        if best_ml is None or pm["validation"]["wll"] < best_ml[0]:
            best_ml = (pm["validation"]["wll"], kind, C)
    params.update({"ml_kind": best_ml[1], "ml_C": best_ml[2]})
    sc = sim.ml_scorers(params)
    best_e = None
    for w in (0.3, 0.5, 0.7):
        pm = prob_metrics(sim, "ensemble", {**params, "ensemble_w": w}, sc)
        say(f"ensemble w={w}: val wll {pm['validation']['wll']:.4f}")
        if best_e is None or pm["validation"]["wll"] < best_e[0]:
            best_e = (pm["validation"]["wll"], w)
    params["ensemble_w"] = best_e[1]

    # ---- model selection on validation (weighted log-loss; points reported for information)
    sel = {}
    simw = Sim(ds, params, START, end, week_targets=True, with_ml=True)
    scw = simw.ml_scorers(params)
    for name in M.MODEL_NAMES:
        pm = prob_metrics(simw, name, params, scw if name in ("ml", "ensemble") else None)
        recs = play(simw, name, params, scw if name in ("ml", "ensemble") else None, strategies=("week_planner",))
        pts = summarize(recs["week_planner"], key=lambda r: split_of(r["date"]))
        sel[name] = {"tune_wll": pm["tune"]["wll"], "val_wll": pm["validation"]["wll"],
                     "tune_points": pts.get("tune", {}).get("points"), "val_points": pts.get("validation", {}).get("points"),
                     "val_ppd": pts.get("validation", {}).get("ppd")}
        say(f"model {name}: val wll {sel[name]['val_wll']:.4f} val points {sel[name]['val_points']} "
            f"(tune points {sel[name]['tune_points']})")
    best_model = min(sel, key=lambda k: sel[k]["val_wll"])
    say(f"best model (validation log-loss): {best_model}")

    # ---- decision strategy for the chosen model: greedy vs weekly planner (discount grid),
    #      chosen on the validation split by EXPECTED points (sum of the model's EV of the chosen tips;
    #      far less noisy than realised points). 2026 is not looked at.
    strategy, strat_sel = select_strategy(simw, best_model, params,
                                          scw if best_model in ("ml", "ensemble") else None, say)
    params["plan_discount"] = strat_sel["chosen_discount"]
    obj = {
        "best_model": best_model,
        "strategy": strategy,
        "strategy_selection": strat_sel,
        "params": params,
        "selection": sel,
        "selection_rule": "heuristic: coordinate descent per category on tune-split log-loss, number of sweeps "
                          "(0/1/2) chosen per category on validation log-loss; B|H mixing, ML regularisation and "
                          "ensemble weight chosen on validation; model = lowest validation weighted log-loss "
                          "(V 1, H 0.5, B 0.5); strategy (greedy vs. weekly planner with discount) = highest "
                          "validation expected points of the chosen model. 2026 never used.",
        "splits": {k: f"{a.isoformat()}..{b.isoformat()}" for k, (a, b) in SPLITS.items()},
        "n_configs": n_configs + 10 + 4 + 5 + 3,
        "tuned_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "tuning_seconds": round(time.time() - t0, 1),
        "log": log,
    }
    save_json(MODEL_PARAMS_JSON, obj)
    return obj


PLAN_DISCOUNTS = (0.5, 0.7, 0.85, 1.0)


def select_strategy(sim: Sim, name: str, params: dict, scorers: dict | None = None, say=print) -> tuple[str, dict]:
    """Greedy vs. weekly planner (discount grid) by expected points on the VALIDATION split."""
    cands = [("greedy", 1.0)] + [("week_planner", d) for d in PLAN_DISCOUNTS]
    res = {}
    for strat, disc in cands:
        recs = play(sim, name, params, scorers, strategies=(strat,), plan_discount=disc)[strat]
        val = [r for r in recs if split_of(r["date"]) == "validation"]
        tun = [r for r in recs if split_of(r["date"]) == "tune"]
        key = strat if strat == "greedy" else f"week_planner@{disc:g}"
        res[key] = {"strategy": strat, "discount": disc,
                    "val_expected": round(sum(r["ev"] for r in val), 3),
                    "val_points": round(sum(r["points"] for r in val), 2),
                    "tune_expected": round(sum(r["ev"] for r in tun), 3),
                    "tune_points": round(sum(r["points"] for r in tun), 2)}
        say(f"strategy {key}: val expected {res[key]['val_expected']:.2f} (realised {res[key]['val_points']:g}), "
            f"tune expected {res[key]['tune_expected']:.2f}")
    # highest validation expected points; ties (< 0.01) -> the simpler greedy / the smaller discount
    best_key = max(res, key=lambda k: (round(res[k]["val_expected"], 2), k == "greedy", -res[k]["discount"]))
    strat = res[best_key]["strategy"]
    say(f"strategy chosen on validation expected points: {best_key}")
    return strat, {"candidates": res, "chosen": best_key,
                   "chosen_discount": res[best_key]["discount"] if strat == "week_planner" else 1.0,
                   "rule": "max expected points (sum of EV) on the validation split 2025-09-01..2025-12-19"}


# ------------------------------------------------------------------ run
def run(ds, today: dt.date | None = None, verbose: bool = True) -> dict:
    """Full backtest with the tuned parameters; writes backtest.json, leaderboard.json, reports/backtest.md."""
    from .output import write_site_json

    t0 = time.time()
    best_model, params = M.load_params()
    strategy = M.load_strategy()
    stored = load_json(MODEL_PARAMS_JSON, {}) or {}
    # The backtest runs through ``today``: a day's simulated tip only uses the menus before it, so
    # once today's menu is entered (on-data run after lunch) today is scored like any other day.
    # Ending at yesterday made the leaderboard compare the players through today with the model
    # through yesterday until the next data push.
    end = today
    sim = Sim(ds, params, START, end, week_targets=True, with_ml=True)
    sc = sim.ml_scorers(params)
    if verbose:
        print(f"[backtest {time.time() - t0:5.1f}s] features + ML fits ready ({len(sim.eval_days)} days)", flush=True)
    models = []
    plays = {}
    metrics = {}
    calib = {}
    for name in M.MODEL_NAMES:
        s = sc if name in ("ml", "ensemble") else None
        pm = prob_metrics(sim, name, params, s)
        metrics[name] = pm
        calib[name] = calibration_all(sim, name, params, s)
        rec = play(sim, name, params, s)
        plays[name] = rec
        yr = summarize(rec[strategy])
        planner = summarize(rec["week_planner"])
        greedy = summarize(rec["greedy"])
        nor4 = summarize(rec["no_r4"])
        by_split = summarize(rec[strategy], key=lambda r: split_of(r["date"]))
        by_split_p = summarize(rec["week_planner"], key=lambda r: split_of(r["date"]))
        by_split_g = summarize(rec["greedy"], key=lambda r: split_of(r["date"]))
        test = pm["test"]
        models.append({
            "name": name, "label_de": M.MODEL_LABELS[name][0], "label_it": M.MODEL_LABELS[name][1],
            "strategy": strategy,
            "years": yr,
            "week_planner": {y: {"points": v["points"], "ppd": v["ppd"], "expected_points": v["expected_points"]}
                             for y, v in planner.items()},
            "greedy": {y: {"points": v["points"], "ppd": v["ppd"], "expected_points": v["expected_points"]}
                       for y, v in greedy.items()},
            "no_r4": {y: {"points": v["points"], "ppd": v["ppd"]} for y, v in nor4.items()},
            "splits": {k: {"points": v["points"], "ppd": v["ppd"], "days": v["days"],
                           "expected_points": v["expected_points"],
                           "planner_points": by_split_p.get(k, {}).get("points"),
                           "planner_expected": by_split_p.get(k, {}).get("expected_points"),
                           "greedy_points": by_split_g.get(k, {}).get("points"),
                           "greedy_expected": by_split_g.get(k, {}).get("expected_points")}
                       for k, v in by_split.items()},
            "logloss": {c: test[c]["logloss"] for c in CATEGORIES if test.get(c)},
            "top1": {c: test[c]["top1"] for c in CATEGORIES if test.get(c)},
            "top3": {c: test[c]["top3"] for c in CATEGORIES if test.get(c)},
            "metrics_by_split": {sp: pm[sp] for sp in SPLITS},
        })
        if verbose:
            print(f"[backtest {time.time() - t0:5.1f}s] {name}: "
                  + ", ".join(f"{y}: {v['points']} P ({v['days']} Tage, greedy {greedy[y]['points']}, ohne R4 {nor4[y]['points']})"
                              for y, v in sorted(yr.items())), flush=True)
    players = player_stats(ds, today)
    comparison = _compare(ds, plays[best_model][strategy])
    best_rec = plays[best_model][strategy]
    daily = defaultdict(list)
    for r in best_rec:
        m = ds.menus_by_date[r["date"]]
        daily[str(r["date"].year)].append({
            "date": r["date"].isoformat(),
            "model_tip": {"v": r["tip"]["vorspeise"], "h": r["tip"]["hauptspeise"], "b": r["tip"]["beilage"]},
            "actual": ({"v": " / ".join(m.options.get("vorspeise", [])), "h": " / ".join(m.options.get("hauptspeise", [])),
                        "b": " / ".join(m.options.get("beilage", []))} if m.status == "served" else None),
            "points": r["points"], "ev": round(r["ev"], 4),
        })
    last = sim.end
    obj = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "split": {"tune": "2025-01-13..2025-08-31", "validation": "2025-09-01..2025-12-19",
                  "test": f"2026-01-12..{last.isoformat()}"},
        "models": models,
        "players": players,
        "best_model": best_model,
        "strategy": strategy,
        "params": params,
        "selection": stored.get("selection"),
        "strategy_selection": stored.get("strategy_selection"),
        "calibration": calib,
        "daily": dict(daily),
        "comparison": comparison,
    }
    obj["summary_de"], obj["summary_it"] = _summaries(obj, ds)
    write_site_json("backtest", obj)
    write_site_json("leaderboard", _leaderboard(ds, best_rec, best_model, today))
    _write_report(obj, ds)
    if verbose:
        print(f"[backtest {time.time() - t0:5.1f}s] fertig", flush=True)
    return obj


def _compare(ds, model_rec, n_boot: int = 4000, seed: int = 11) -> dict:
    """Paired day-bootstrap of (model − player) season points: 95 % interval and P(model ahead).

    Days = served backtest days; a day a player did not tip counts 0 for that player.
    """
    rng = np.random.default_rng(seed)
    by_day = {r["date"]: r["points"] for r in model_rec if r["served"]}
    tips = defaultdict(dict)
    for t in ds.tips:
        if t.points is not None:
            tips[t.player][t.date] = t.points
    out: dict = {}
    for y in sorted({d.year for d in by_day}):
        days = sorted(d for d in by_day if d.year == y)
        mv = np.array([by_day[d] for d in days])
        res = {}
        for pl in ds.players:
            if not any(d.year == y for d in tips[pl]):
                continue
            first = min(d for d in tips[pl] if d.year == y)
            pv = np.array([tips[pl].get(d, 0.0) for d in days])
            diff = mv - pv
            idx = rng.integers(0, len(days), size=(n_boot, len(days)))
            boot = diff[idx].sum(axis=1)
            # same comparison restricted to the days since the player's first tip of the year
            mask = np.array([d >= first for d in days])
            # skill comparison: only the days the player actually tipped
            tipped = np.array([d in tips[pl] for d in days])
            dt_ = diff[tipped]
            if dt_.size:
                idx_t = rng.integers(0, dt_.size, size=(n_boot, dt_.size))
                boot_t = dt_[idx_t].sum(axis=1)
                ci_t = [round(float(np.percentile(boot_t, 2.5)), 1), round(float(np.percentile(boot_t, 97.5)), 1)]
                pa_t = round(float((boot_t > 0).mean()), 3)
            else:
                ci_t, pa_t = [0.0, 0.0], 0.0
            res[pl] = {"diff": round(float(diff.sum()), 2), "ci95": [round(float(np.percentile(boot, 2.5)), 1),
                                                                     round(float(np.percentile(boot, 97.5)), 1)],
                       "p_model_ahead": round(float((boot > 0).mean()), 3),
                       "diff_since_first_tip": round(float(diff[mask].sum()), 2), "days": len(days),
                       "player_points": round(float(pv.sum()), 2), "model_points": round(float(mv.sum()), 2),
                       "tipped_days": int(tipped.sum()), "diff_tipped_days": round(float(dt_.sum()), 2),
                       "ci95_tipped_days": ci_t, "p_model_ahead_tipped_days": pa_t}
        out[str(y)] = res
    return out


def _leaderboard(ds, model_rec, model_name, until: dt.date | None = None) -> dict:
    by_year_days = defaultdict(set)
    pts = defaultdict(lambda: defaultdict(float))
    for t in ds.tips:
        if until is not None and t.date > until:
            continue
        m = ds.menus_by_date.get(t.date)
        if m is None or m.status not in ("served", "unknown") or t.points is None:
            continue
        by_year_days[t.date.year].add(t.date)
        pts[t.player][t.date] += t.points
    mpts = {}
    for r in model_rec:
        mpts[r["date"]] = r["points"]
        by_year_days[r["date"].year].add(r["date"])
    years = {}
    for y in sorted(by_year_days):
        dates = sorted(by_year_days[y])
        series, totals = {}, {}
        players = [p for p in ds.players if any(d.year == y for d in pts[p])]
        for p in players:
            cum, s = [], 0.0
            for d in dates:
                s += pts[p].get(d, 0.0)
                cum.append(round(s, 2))
            series[p] = cum
            totals[p] = round(s, 2)
        if any(d in mpts for d in dates):
            cum, s = [], 0.0
            for d in dates:
                s += mpts.get(d, 0.0)
                cum.append(round(s, 2))
            series["Modell"] = cum
            totals["Modell"] = round(s, 2)
        years[str(y)] = {"dates": [d.isoformat() for d in dates], "series": series, "totals": totals}
    return {"years": years, "model_name": model_name}


STRAT_DE = {"week_planner": "Wochenplaner", "greedy": "Greedy (nur heute)"}
STRAT_IT = {"week_planner": "pianificatore settimanale", "greedy": "greedy (solo oggi)"}


def _num(x) -> str:
    return f"{x:g}"


def _headline(obj: dict, ds, lang: str = "de") -> list[str]:
    """Honest verdict lines (markdown bullets) for the top of the report."""
    models, players, best = obj["models"], obj["players"], obj["best_model"]
    strategy = obj.get("strategy", "week_planner")
    bm = next(m for m in models if m["name"] == best)
    comp = obj.get("comparison") or {}
    de = lang == "de"
    out = []
    ss = obj.get("strategy_selection") or {}
    if de:
        out.append(f"* **Modell:** *{best}* (auf der Validierung 2025 nach Log-Loss gewählt), **Strategie:** "
                   f"{STRAT_DE.get(strategy, strategy)} (auf der Validierung nach *erwarteten* Punkten gewählt). "
                   "Regel 4 gilt gegen die eigenen simulierten Tipps der Woche; gewertet wird mit `rules.score_tip`.")
        out.append("* **2026 ist echter Test (out-of-sample):** keine Hyperparameter, keine Modell- oder "
                   "Strategiewahl hat 2026 gesehen; für jeden Tag wird nur mit den Menüs *davor* trainiert.")
    else:
        out.append(f"* **Modello:** *{best}* (scelto sulla validazione 2025 per log-loss), **strategia:** "
                   f"{STRAT_IT.get(strategy, strategy)} (scelta sulla validazione per punti *attesi*). "
                   "Regola 4 rispettata rispetto ai propri tip simulati della settimana; punteggio con `rules.score_tip`.")
        out.append("* **Il 2026 è un vero test (fuori campione):** nessun iperparametro, nessuna scelta di modello o "
                   "strategia ha visto il 2026; ogni giorno il modello usa solo i menù *precedenti*.")
    for y in ("2026", "2025"):
        v = bm["years"].get(y)
        pl = players.get(y, {})
        if not v or not pl:
            continue
        ranking = sorted(pl.items(), key=lambda kv: -kv[1]["points"])
        top_name, top = ranking[0]
        beaten = [n for n, x in ranking if v["points"] > x["points"]]
        c = (comp.get(y) or {}).get(top_name)
        tag = ("Test, out-of-sample" if y == "2026" else "teilweise in-sample: Tuning/Validierung") if de else \
              ("test, fuori campione" if y == "2026" else "in parte nel campione: tuning/validazione")
        others = ", ".join(f"{n} {_num(x['points'])}" for n, x in ranking)
        if de:
            pos = ("vor **allen** Spielern" if len(beaten) == len(ranking) else
                   f"vor {len(beaten)} von {len(ranking)} Spielern" if beaten else "hinter allen Spielern")
            line = (f"* **{y}** ({tag}, mit Regel 4): Modell **{_num(v['points'])} Punkte** an {v['days']} Spieltagen "
                    f"({v['ppd']:.3f}/Tag; laut Modell erwartet {v.get('expected_points', 0):.1f}) → {pos}. "
                    f"Spieler: {others}.")
        else:
            pos = ("davanti a **tutti** i giocatori" if len(beaten) == len(ranking) else
                   f"davanti a {len(beaten)} giocatori su {len(ranking)}" if beaten else "dietro a tutti i giocatori")
            line = (f"* **{y}** ({tag}, con regola 4): modello **{_num(v['points'])} punti** in {v['days']} giorni "
                    f"({v['ppd']:.3f}/giorno; attesi secondo il modello {v.get('expected_points', 0):.1f}) → {pos}. "
                    f"Giocatori: {others}.")
        out.append(line)
        if c:
            sig = c["ci95"][0] > 0 or c["ci95"][1] < 0
            sig_t = c["ci95_tipped_days"][0] > 0 or c["ci95_tipped_days"][1] < 0
            if de:
                out.append(f"  * Gegen den Besten ({top_name}): {c['diff']:+g} Punkte, 95 %-Bootstrap-Intervall "
                           f"[{c['ci95'][0]:+g}, {c['ci95'][1]:+g}], P(Modell vorne) {c['p_model_ahead']:.0%} → "
                           + ("**statistisch gesichert**." if sig else "**statistisch nicht gesichert** (Intervall enthält 0)."))
                out.append(f"  * Nur an den {c['tipped_days']} Tagen, an denen {top_name} getippt hat: "
                           f"{c['diff_tipped_days']:+g} [{c['ci95_tipped_days'][0]:+g}, {c['ci95_tipped_days'][1]:+g}]"
                           + (" (gesichert)." if sig_t else " (nicht gesichert)."))
            else:
                out.append(f"  * Contro il migliore ({top_name}): {c['diff']:+g} punti, intervallo bootstrap 95 % "
                           f"[{c['ci95'][0]:+g}, {c['ci95'][1]:+g}], P(modello davanti) {c['p_model_ahead']:.0%} → "
                           + ("**statisticamente significativo**." if sig else "**non statisticamente significativo** (l'intervallo contiene 0)."))
                out.append(f"  * Solo nei {c['tipped_days']} giorni in cui {top_name} ha tippato: "
                           f"{c['diff_tipped_days']:+g} [{c['ci95_tipped_days'][0]:+g}, {c['ci95_tipped_days'][1]:+g}]"
                           + (" (significativo)." if sig_t else " (non significativo)."))
        me = ds.me
        cm = (comp.get(y) or {}).get(me)
        if cm and me != top_name:
            if de:
                out.append(f"  * Gegen {me} (ich): {cm['diff']:+g} [{cm['ci95'][0]:+g}, {cm['ci95'][1]:+g}], "
                           f"nur meine {cm['tipped_days']} Tipptage {cm['diff_tipped_days']:+g} "
                           f"[{cm['ci95_tipped_days'][0]:+g}, {cm['ci95_tipped_days'][1]:+g}].")
            else:
                out.append(f"  * Contro {me} (io): {cm['diff']:+g} [{cm['ci95'][0]:+g}, {cm['ci95'][1]:+g}], "
                           f"solo i miei {cm['tipped_days']} giorni tippati {cm['diff_tipped_days']:+g} "
                           f"[{cm['ci95_tipped_days'][0]:+g}, {cm['ci95_tipped_days'][1]:+g}].")
        if y == "2026":
            oth = ", ".join(f"{m['name']} {_num(m['years'][y]['points'])}" for m in models
                            if m["name"] != best and y in m["years"])
            out.append(("  * Andere Modelle 2026 (gleiche Strategie, nur zur Information – nicht zur Auswahl benutzt): "
                        if de else "  * Altri modelli 2026 (stessa strategia, solo informativo – non usati per la scelta): ") + oth + ".")
    # strategy
    cand = ss.get("candidates") or {}
    g = cand.get("greedy")
    pk = [k for k in cand if k != "greedy"]
    if g and pk:
        bp = max(pk, key=lambda k: cand[k]["val_expected"])
        y26p = bm.get("week_planner", {}).get("2026", {}).get("points")
        y26g = bm.get("greedy", {}).get("2026", {}).get("points")
        if de:
            out.append(f"* **Wochenplaner vs. Greedy:** Validierung erwartete Punkte {cand[bp]['val_expected']:.2f} "
                       f"({bp}) vs. {g['val_expected']:.2f} (Greedy) → gewählt: {STRAT_DE.get(strategy, strategy)}. "
                       f"Der Unterschied ist klein ({cand[bp]['val_expected'] - g['val_expected']:+.2f} erwartete Punkte "
                       f"auf der Validierung); 2026 realisiert: Planer {_num(y26p)} vs. Greedy {_num(y26g)} – "
                       "innerhalb des Zufallsrauschens.")
        else:
            out.append(f"* **Pianificatore vs. greedy:** punti attesi sulla validazione {cand[bp]['val_expected']:.2f} "
                       f"({bp}) vs. {g['val_expected']:.2f} (greedy) → scelto: {STRAT_IT.get(strategy, strategy)}. "
                       f"Differenza piccola ({cand[bp]['val_expected'] - g['val_expected']:+.2f} punti attesi sulla "
                       f"validazione); 2026 realizzato: pianificatore {_num(y26p)} vs. greedy {_num(y26g)} – "
                       "dentro il rumore casuale.")
    if de:
        out.append("* Eine Saison hat ~180 Spieltage mit stark schwankenden Tagespunkten (0–3): Unterschiede von "
                   "wenigen Punkten sind Zufall. Das Modell tippt jeden Tag; Spieler haben einzelne Tage ausgelassen "
                   "(zählen 0) – deshalb auch der Vergleich nur über die getippten Tage.")
    else:
        out.append("* Una stagione ha ~180 giorni con punti giornalieri molto variabili (0–3): differenze di pochi "
                   "punti sono casuali. Il modello tippa ogni giorno; i giocatori hanno saltato alcuni giorni "
                   "(contano 0) – per questo anche il confronto solo sui giorni tippati.")
    return out


def _summaries(obj: dict, ds) -> tuple[str, str]:
    """One-paragraph summaries (backtest.json summary_de / summary_it)."""
    models, players, best = obj["models"], obj["players"], obj["best_model"]
    bm = next(m for m in models if m["name"] == best)
    comp = obj.get("comparison") or {}
    strategy = obj.get("strategy", "week_planner")
    parts_de, parts_it = [], []
    for y in ("2026", "2025"):
        v = bm["years"].get(y)
        pl = players.get(y, {})
        if not v or not pl:
            continue
        top_name, top = max(pl.items(), key=lambda kv: kv[1]["points"])
        c = (comp.get(y) or {}).get(top_name) or {}
        ci = c.get("ci95", [0, 0])
        sig = ci[0] > 0 or ci[1] < 0
        diff = v["points"] - top["points"]
        tag_de = "Test, nie getunt" if y == "2026" else "teilweise getunt"
        tag_it = "test, mai ottimizzato" if y == "2026" else "parzialmente ottimizzato"
        parts_de.append(f"{y} ({tag_de}): Modell {_num(v['points'])} Punkte vs. bester Spieler {top_name} "
                        f"{_num(top['points'])} ({diff:+g}; 95 %-Intervall [{ci[0]:+g}, {ci[1]:+g}], "
                        f"{'gesichert' if sig else 'nicht gesichert'})")
        parts_it.append(f"{y} ({tag_it}): modello {_num(v['points'])} punti vs. miglior giocatore {top_name} "
                        f"{_num(top['points'])} ({diff:+g}; intervallo 95 % [{ci[0]:+g}, {ci[1]:+g}], "
                        f"{'significativo' if sig else 'non significativo'})")
    de = (f"Bestes Modell (auf Validierung gewählt): {best}, Strategie {STRAT_DE.get(strategy, strategy)}. "
          + "; ".join(parts_de) + ". Mit Regel 4, gleiche Entscheidungslogik wie die Tagesempfehlung.")
    it = (f"Modello migliore (scelto sulla validazione): {best}, strategia {STRAT_IT.get(strategy, strategy)}. "
          + "; ".join(parts_it) + ". Con la regola 4, stessa logica della raccomandazione giornaliera.")
    return de, it


def _fmt(x, nd=1):
    return "–" if x is None else f"{x:.{nd}f}"


def _write_report(obj: dict, ds) -> None:
    models = obj["models"]
    players = obj["players"]
    best = obj["best_model"]
    bm = next(m for m in models if m["name"] == best)
    L = ["# Backtest – Tippspiel Essen Wies", "",
         f"_Automatisch erzeugt von `engine/backtest.py` am {obj['generated_at']}._", "",
         "## Kurzfassung", ""] + _headline(obj, ds, "de") + ["", "## Riassunto (italiano)", ""] + \
        _headline(obj, ds, "it") + ["",
         "## Methode", "",
         "* **Walk-forward**: für jeden Arbeitstag ab 13.01.2025 wird nur mit den Menüs *vor* diesem Tag trainiert "
         "(2024 = Aufwärmphase). Keine Tipps anderer Spieler als Eingabe (Regel 6).",
         "* **Entscheidung** exakt wie in der Tagesempfehlung (`engine/recommend.py::decide`): Erwartungswert "
         "EV = 1·P(V) + 0,5·P(H) + 0,5·P(B) + 1·P(V∧H∧B) mit P(V∧H∧B) = P(V)·P(H)·P(B|H), Regel 4 gegen die "
         "*eigenen simulierten* Tipps derselben ISO-Woche. Strategien: Wochenplaner (Receding Horizon über die "
         "restlichen Arbeitstage der Woche, spätere Tage mit Faktor discount^k gewichtet, „anderes Gericht“ als "
         "Ausweichoption) oder Greedy (bester gültiger Tipp nur für heute). "
         f"Verwendet: **{STRAT_DE.get(obj.get('strategy'), obj.get('strategy'))}**, gewählt nach erwarteten Punkten "
         "auf der Validierung (Regel vorab festgelegt, nicht nach 2026).",
         "* **Wertung** mit `rules.score_tip`: jede angesagte Option zählt, „Fisch“-Regel außerhalb der Fastenzeit.",
         "* **Splits**: Tuning 13.01.–31.08.2025 · Validierung 01.09.–19.12.2025 · **Test 2026 (nie getunt)**. "
         "2025 ist damit *teilweise in-sample* (Hyperparameter), 2026 ist ehrlich out-of-sample.",
         f"* Bestes Modell (Auswahl nach Validierungs-Log-Loss, nicht nach 2026): **{best}**.",
         "* Modellentwicklung (Features, Suchgitter, Entscheidungslogik) nur mit 2024/2025; 2026 wurde erst mit "
         "eingefrorenem Modell ausgewertet. Einzige Ausnahme: ein früher Diagnoselauf mit *ungetunten* "
         "Standardparametern zeigte einmal den 2026-Log-Loss; daraus wurde nichts abgeleitet.", "",
         f"## Punkte pro Jahr (mit Regel 4, {STRAT_DE.get(obj.get('strategy'), obj.get('strategy'))})", ""]
    years = ["2025", "2026"]
    L += ["| Wer | " + " | ".join(f"{y} Punkte | {y} Tage | {y} Pkt/Tag" for y in years) + " |",
          "|---|" + "---|---|---|" * len(years)]
    for m in models:
        cells = []
        for y in years:
            v = m["years"].get(y)
            cells += [_fmt(v["points"]) if v else "–", str(v["days"]) if v else "–", _fmt(v["ppd"], 3) if v else "–"]
        L.append(f"| Modell **{m['name']}** | " + " | ".join(cells) + " |")
    for p in ds.players:
        cells = []
        for y in years:
            v = players.get(y, {}).get(p)
            cells += [_fmt(v["points"]) if v else "–", str(v["days"]) if v else "–", _fmt(v["ppd"], 3) if v else "–"]
        L.append(f"| {p} | " + " | ".join(cells) + " |")
    L += ["", "Spieler: Tage = servierte Tage mit eigenem Tipp (nicht getippte Tage zählen 0 Punkte). "
          "Modell: tippt jeden Arbeitstag.", ""]
    # verdict
    L += ["## Fazit", ""]
    for y in years:
        v = bm["years"].get(y)
        pl = players.get(y, {})
        if not v or not pl:
            continue
        ranking = sorted(pl.items(), key=lambda kv: -kv[1]["points"])
        top = ranking[0]
        diff = v["points"] - top[1]["points"]
        tag = "Testjahr, out-of-sample" if y == "2026" else "teilweise getunt"
        ppd_best = max(x["ppd"] for _, x in ranking)
        verdict = "schlägt" if diff > 0 else ("gleichauf mit" if diff == 0 else "verliert gegen")
        L.append(f"* **{y}** ({tag}): Modell *{best}* {v['points']:g} Punkte → {verdict} den besten Spieler "
                 f"{top[0]} ({top[1]['points']:g}), Differenz {diff:+g}. Punkte pro getipptem Tag: Modell "
                 f"{v['ppd']:.3f} vs. bester Spieler {ppd_best:.3f}.")
        me = ds.me
        cm = (obj.get("comparison") or {}).get(y, {}).get(me)
        if cm and me in pl:
            L.append(f"  Gegen {me} (ich): {cm['diff']:+g} Punkte (ab meinem ersten Tipp {cm['diff_since_first_tip']:+g}); "
                     f"pro getipptem Tag {pl[me]['ppd']:.3f} (ich) vs. {v['ppd']:.3f} (Modell).")
        others = [m for m in models if m["name"] != best and y in m["years"]]
        if others:
            L.append("  Andere Modelle: " + ", ".join(f"{m['name']} {m['years'][y]['points']:g}" for m in others) + ".")
    L.append("")
    comp = obj.get("comparison") or {}
    if comp:
        L += ["### Wie sicher ist der Vorsprung? (gepaarter Bootstrap über Tage, 4000 Ziehungen)", "",
              "| Jahr | gegen | Modell | Spieler | Differenz | 95 %-Intervall | P(Modell vorne) | nur getippte Tage (n) | 95 %-Intervall |",
              "|---|---|---|---|---|---|---|---|---|"]
        for y in years:
            for pl, v in (comp.get(y) or {}).items():
                L.append(f"| {y} | {pl} | {v['model_points']:g} | {v['player_points']:g} | {v['diff']:+g} | "
                         f"[{v['ci95'][0]:+g}, {v['ci95'][1]:+g}] | {v['p_model_ahead']:.0%} | "
                         f"{v['diff_tipped_days']:+g} ({v['tipped_days']}) | "
                         f"[{v['ci95_tipped_days'][0]:+g}, {v['ci95_tipped_days'][1]:+g}] |")
        L += ["", "Eine Saison hat nur ~180 Spieltage; die Tagespunkte schwanken stark (0 / 0,5 / 1 / 1,5 / 2 / 3). "
              "Ein Vorsprung von wenigen Punkten ist daher statistisch nicht gesichert.", ""]
    L += ["## Wochenplaner vs. Greedy vs. ohne Regel 4", "",
          "| Modell | Jahr | Wochenplaner | Greedy | ohne R4 (Obergrenze nur im Erwartungswert) | erwartete Punkte Planer | erwartete Punkte Greedy |",
          "|---|---|---|---|---|---|---|"]
    for m in models:
        for y in years:
            wp = m["week_planner"].get(y)
            if wp:
                L.append(f"| {m['name']} | {y} | {_fmt(wp['points'])} | {_fmt(m['greedy'].get(y, {}).get('points'))} | "
                         f"{_fmt(m['no_r4'].get(y, {}).get('points'))} | {_fmt(wp.get('expected_points'))} | "
                         f"{_fmt(m['greedy'].get(y, {}).get('expected_points'))} |")
    tot_p = sum(m["week_planner"][y]["points"] for m in models for y in years if y in m["week_planner"])
    tot_g = sum(m["greedy"][y]["points"] for m in models for y in years if y in m["greedy"])
    gain = [m["week_planner"][y].get("expected_points", 0) - m["greedy"][y].get("expected_points", 0)
            for m in models for y in years if y in m["week_planner"] and y in m["greedy"] and m["name"] != "frequency"]
    r4cost = [m["no_r4"][y]["points"] - m["years"][y]["points"] for m in models for y in years
              if y in m["years"] and m["name"] != "frequency"]
    vs = []
    for m in models:
        sp = m["splits"].get("validation") or {}
        if sp.get("planner_expected") is not None:
            vs.append(f"{m['name']} {sp['planner_expected']:.1f} vs. {sp['greedy_expected']:.1f}")
    L += ["", f"Summe über alle Modelle und Jahre: Wochenplaner {tot_p:g} vs. Greedy {tot_g:g} Punkte. "
          "„Erwartete Punkte“ = Summe der EV der gewählten Tipps laut Modell. Der Planer verteilt die knappen "
          "Regel-4-Kontingente (v. a. Reis, Montags-Favoriten) auf die Tage mit der höchsten Wahrscheinlichkeit; "
          f"sein erwarteter Vorteil laut Modell beträgt {min(gain):.1f}–{max(gain):.1f} Punkte pro Saison und ist im "
          "realisierten Ergebnis vom Zufall nicht zu unterscheiden. Erwartete Punkte auf der Validierung "
          f"(Planer vs. Greedy): {'; '.join(vs)}. Ohne Regel 4 hätten die Modelle (außer frequency) realisiert "
          f"{min(r4cost):g}–{max(r4cost):g} Punkte pro Saison mehr erzielt (ohne R4 ist nur der *erwartete* Wert eine "
          "Obergrenze – realisiert kann es auch weniger sein).", ""]
    ss = obj.get("strategy_selection") or {}
    if ss.get("candidates"):
        L += [f"Strategiewahl für *{best}* (Validierung, erwartete Punkte = Summe der EV): ", "",
              "| Kandidat | Val. erwartet | Val. realisiert | Tuning erwartet | Tuning realisiert |", "|---|---|---|---|---|"]
        for k, v in ss["candidates"].items():
            mark = " ✔" if k == ss.get("chosen") else ""
            L.append(f"| {k}{mark} | {v['val_expected']:.2f} | {v['val_points']:g} | {v['tune_expected']:.2f} | "
                     f"{v['tune_points']:g} |")
        L.append("")
    L += ["", f"## Punkte nach Split ({STRAT_DE.get(obj.get('strategy'), obj.get('strategy'))})", "",
          "| Modell | Tuning | Validierung | Test 2026 |", "|---|---|---|---|"]
    for m in models:
        s = m["splits"]
        L.append(f"| {m['name']} | {_fmt(s.get('tune', {}).get('points'))} | {_fmt(s.get('validation', {}).get('points'))} | "
                 f"{_fmt(s.get('test', {}).get('points'))} |")
    L += ["", "## Trefferquoten der gewählten Tipps (mit R4)", "", "| Modell | Jahr | V | H | B | volle Menüs |", "|---|---|---|---|---|---|"]
    for m in models:
        for y in years:
            v = m["years"].get(y)
            if v:
                L.append(f"| {m['name']} | {y} | {v['acc']['vorspeise']:.1%} | {v['acc']['hauptspeise']:.1%} | "
                         f"{v['acc']['beilage']:.1%} | {v['full_hits']} |")
    for p in ds.players:
        for y in years:
            v = players.get(y, {}).get(p)
            if v:
                L.append(f"| {p} | {y} | {v['acc']['vorspeise']:.1%} | {v['acc']['hauptspeise']:.1%} | "
                         f"{v['acc']['beilage']:.1%} | {v['full_hits']} |")
    L += ["", "## Wahrscheinlichkeitsgüte (Log-Loss, Top-1/Top-3 ohne R4)", "",
          "| Modell | Split | LL V | LL H | LL B | Top1 V | Top1 H | Top1 B | Top3 V | Top3 H | Top3 B |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for m in models:
        for sp in ("tune", "validation", "test"):
            r = m["metrics_by_split"].get(sp) or {}
            if not all(r.get(c) for c in CATEGORIES):
                continue
            L.append(f"| {m['name']} | {sp} | " + " | ".join(f"{r[c]['logloss']:.3f}" for c in CATEGORIES) + " | "
                     + " | ".join(f"{r[c]['top1']:.1%}" for c in CATEGORIES) + " | "
                     + " | ".join(f"{r[c]['top3']:.1%}" for c in CATEGORIES) + " |")
    L += ["", f"## Kalibrierung ({best}, alle Backtest-Tage)", "", "| Kategorie | p-Bereich | mittleres p | Trefferquote | n |", "|---|---|---|---|---|"]
    for c in CATEGORIES:
        for b in obj["calibration"][best][c]:
            L.append(f"| {c} | {b['bin'][0]:.2f}–{b['bin'][1]:.2f} | {_fmt(b['p_mean'], 3)} | {_fmt(b['hit_rate'], 3)} | {b['n']} |")
    L += ["", "## Gewählte Parameter", "", "```json"]
    import json
    L += [json.dumps(obj["params"], ensure_ascii=False, indent=1), "```", ""]
    if obj.get("selection"):
        L += ["Modellauswahl auf der Validierung:", "", "| Modell | Val-Log-Loss (gewichtet) | Val-Punkte | Tuning-Punkte |", "|---|---|---|---|"]
        for k, v in obj["selection"].items():
            L.append(f"| {k} | {v['val_wll']:.4f} | {_fmt(v['val_points'])} | {_fmt(v['tune_points'])} |")
        L.append("")
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "backtest.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    import argparse

    from .data import load_dataset

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tune", action="store_true", help="re-run the hyper-parameter search")
    ap.add_argument("--today", type=dt.date.fromisoformat)
    a = ap.parse_args(argv)
    ds = load_dataset()
    if a.tune or not MODEL_PARAMS_JSON.exists():
        tune(ds)
    run(ds, today=a.today)
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
