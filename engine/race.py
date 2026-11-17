"""Race to the end of the season: how likely is it to finish first?

Monte Carlo over the remaining game days of the season. Every simulated day is a *whole* real day of
the current season drawn at random (day bootstrap): the points of all players on that day plus the
walk-forward backtest points of the model. Drawing whole days keeps the correlation between the
players (same menu, often the same favourite dishes) – a day on which everybody hits the Vorspeise
does not change the gaps. Only scores are used, never the dishes the others tipped (rule 6).

Scenarios for ``me``:
* ``model`` – I tip what the model recommends (my daily points = the model's backtest points),
* ``own``   – I keep tipping like so far this season (my own daily points).

Players with fewer than ``MIN_DAYS`` tipping days this season (e.g. Lorenz, joined 2026-11-02) get,
on each simulated day, the points of a randomly chosen regular player of that day (= an average
player; their own few days say little).

Standings = official points (workbook value where present, start points included).

    python -m engine.race            # prints the race for today
"""
from __future__ import annotations

import datetime as dt
from collections import defaultdict

import numpy as np

from .dates import season_end

MIN_DAYS = 30
N_SIMS = 20000
TWO_WEEKS = 10   # game days


def _official(t) -> float:
    return t.points_sheet if t.points_sheet is not None else (t.points or 0.0)


def compute(ds, model_rec: list[dict], today: dt.date, n_sims: int = N_SIMS, seed: int = 7) -> dict | None:
    cfg = ds.config
    year = today.year
    end = season_end(year, cfg.get("season_end_mmdd", "12-23"))
    served = [m.date for m in ds.served if m.date.year == year and m.date <= today]
    if not served:
        return None
    last = max(served)
    remaining = [m.date for m in ds.menus
                 if m.status == "pending" and last < m.date <= end and m.date.weekday() < 5]
    me = ds.me
    standings: dict[str, float] = defaultdict(float)
    daily: dict[str, dict[dt.date, float]] = defaultdict(dict)
    for t in ds.tips:
        if t.date.year != year or t.date > last:
            continue
        standings[t.player] += _official(t)
        if not t.is_adjustment and ds.menus_by_date.get(t.date) and ds.menus_by_date[t.date].status == "served":
            daily[t.player][t.date] = _official(t)
    players = [p for p in ds.players if p in standings]
    if me not in players or len(players) < 2:
        return None
    model_pts = {r["date"]: r["points"] for r in model_rec if r.get("served") and r["date"].year == year}
    pool = [d for d in served if d in model_pts]
    if len(pool) < 20:
        return None
    regular = [p for p in players if len(daily[p]) >= MIN_DAYS]
    newbies = [p for p in players if p not in regular]
    others = [p for p in players if p != me]
    P = np.array([[daily[p].get(d, 0.0) for d in pool] for p in players])          # players x days
    M = np.array([model_pts[d] for d in pool])
    idx = {p: i for i, p in enumerate(players)}
    reg_rows = np.array([idx[p] for p in regular if p != me]) if any(p != me for p in regular) else np.array([idx[me]])

    n_rem = len(remaining)
    rng = np.random.default_rng(seed)
    draw = rng.integers(0, len(pool), size=(n_sims, n_rem))
    base = np.array([standings[p] for p in players])

    def simulate(me_daily: np.ndarray) -> dict:
        # (n_sims, n_rem, players) daily points
        pts = P.T[draw]                                    # sims x rem x players
        pts[:, :, idx[me]] = me_daily[draw]
        for p in newbies:
            if p == me:
                continue
            pick = reg_rows[rng.integers(0, len(reg_rows), size=(n_sims, n_rem))]
            pts[:, :, idx[p]] = P[pick, draw]
        out = {}
        for tag, k in (("end", n_rem), ("two_weeks", min(TWO_WEEKS, n_rem))):
            tot = base + pts[:, :k, :].sum(axis=1)          # sims x players
            mine = tot[:, idx[me]]
            best_other = np.max(np.delete(tot, idx[me], axis=1), axis=1)
            top = tot.max(axis=1, keepdims=True)
            n_top = (np.abs(tot - top) < 1e-9).sum(axis=1)
            first = np.abs(tot - top) < 1e-9
            win_share = (first / n_top[:, None]).mean(axis=0)    # ties split
            out[tag] = {
                "days": int(k),
                "p_first": round(float((mine > best_other + 1e-9).mean()), 4),
                "p_first_or_tied": round(float((mine >= best_other - 1e-9).mean()), 4),
                "p_ahead_of": {p: round(float((mine > tot[:, idx[p]] + 1e-9).mean()), 4) for p in others},
                "win_share": {p: round(float(win_share[idx[p]]), 4) for p in players},
                "expected": {p: round(float(tot[:, idx[p]].mean()), 2) for p in players},
                "q10_q90_me": [round(float(np.percentile(mine, 10)), 1), round(float(np.percentile(mine, 90)), 1)],
            }
        return out

    leader = max((p for p in players if p != me), key=lambda p: standings[p])
    gap = standings[leader] - standings[me]
    ppd = {p: round(float(P[idx[p]][[d in daily[p] for d in pool]].mean()), 4) if daily[p] else None
           for p in players}
    res = {
        "season": year,
        "as_of": last.isoformat(),
        "season_end": end.isoformat(),
        "remaining_days": n_rem,
        "remaining_dates": [d.isoformat() for d in remaining],
        "pool_days": len(pool),
        "n_sims": n_sims,
        "me": me,
        "standings": {p: round(standings[p], 2) for p in sorted(players, key=lambda p: -standings[p])},
        "leader": leader,
        "gap_to_leader": round(gap, 2),
        "ppd": ppd,
        "ppd_model": round(float(M.mean()), 4),
        "newbies": newbies,
        # points per day I need on top of the leader's usual rate to pass him (strictly) by the end
        "needed_ppd_vs_leader": (round(float(ppd[leader] + (gap + 0.5) / n_rem), 3)
                                 if n_rem and ppd.get(leader) is not None else None),
        "scenarios": {"model": simulate(M), "own": simulate(P[idx[me]])},
    }
    return res


def summary(r: dict, lang: str = "de") -> str:
    if not r:
        return ""
    sm, so = r["scenarios"]["model"], r["scenarios"]["own"]
    pct = lambda x: f"{100 * x:.0f} %"
    num = lambda x: f"{x:g}".replace(".", ",")
    if lang == "it":
        return (f"Mancano {r['remaining_days']} giorni di gioco. {r['leader']} è in testa con "
                f"{num(r['standings'][r['leader']])} punti, {num(r['gap_to_leader'])} più di {r['me']}. "
                f"Seguendo il modello ({num(round(r['ppd_model'], 2))} punti/giorno nel backtest) la probabilità di "
                f"finire primo è {pct(sm['end']['p_first'])} (in testa fra due settimane: {pct(sm['two_weeks']['p_first'])}); "
                f"giocando come finora {pct(so['end']['p_first'])}. Per superare {r['leader']} servono in media "
                f"{num(round(r['needed_ppd_vs_leader'], 2))} punti/giorno.")
    return (f"Noch {r['remaining_days']} Spieltage. {r['leader']} führt mit {num(r['standings'][r['leader']])} Punkten, "
            f"{num(r['gap_to_leader'])} vor {r['me']}. Mit den Tipps des Modells ({num(round(r['ppd_model'], 2))} Punkte/Tag "
            f"im Backtest) liegt die Siegchance bei {pct(sm['end']['p_first'])} (in zwei Wochen vorne: "
            f"{pct(sm['two_weeks']['p_first'])}); mit der bisherigen eigenen Form bei {pct(so['end']['p_first'])}. "
            f"Zum Überholen von {r['leader']} braucht es im Schnitt {num(round(r['needed_ppd_vs_leader'], 2))} Punkte/Tag.")


def main(argv=None) -> int:
    import json
    import zoneinfo

    from . import model as Mo
    from .backtest import START, Sim, play
    from .config import load_config
    from .data import load_dataset

    cfg = load_config()
    today = dt.datetime.now(zoneinfo.ZoneInfo(cfg.get("timezone", "Europe/Rome"))).date()
    ds = load_dataset()
    best, params = Mo.load_params()
    sim = Sim(ds, params, START, today)
    sc = sim.ml_scorers(params) if best in ("ml", "ensemble") else None
    rec = play(sim, best, params, sc, strategies=(Mo.load_strategy(),))[Mo.load_strategy()]
    r = compute(ds, rec, today)
    print(json.dumps({k: v for k, v in r.items() if k != "remaining_dates"}, indent=1, ensure_ascii=False))
    print(summary(r, "it"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
