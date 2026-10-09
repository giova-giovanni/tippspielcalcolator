"""Descriptive analysis of the menu history and of the players' tips.

Writes
  * ``docs/data/stats.json``          (contract: see SPEC "stats.json")
  * ``reports/analysis.md``           (German report, Italian summary on top)
  * ``reports/alias_candidates.md``   (normalisation proposals, :func:`engine.normalize.write_alias_report`)

    python -m engine.analyze                       # analyse everything up to today
    python -m engine.analyze --today 2026-10-09    # pretend another day
    python -m engine.analyze --no-write            # only print the key findings

Conventions
  * only *served* menus with ``date <= today``; frequencies, gaps, weekday, pairs and
    seasonality use the *primary* (first announced) option of each category;
    "first/last served" and the trends (new/gone) use every announced option
  * gaps / lags are counted in **working days** = position in ``ds.workdays()``
    (free days and the breaks between seasons do not count); pairs that cross a
    season boundary (different years) are ignored
  * players: only tips with ``date < today`` (rule 6) on served days, points as
    recomputed by the engine (``Tip.points``)
"""
from __future__ import annotations

import argparse
import datetime as dt
import math
import random
import statistics
from collections import Counter, defaultdict

from . import CATEGORIES
from .config import REPORTS
from .data import Dataset, load_dataset
from .dates import WEEKDAYS_DE, WEEKDAYS_DE_LONG, is_lent, lent_range, week_key
from .normalize import write_alias_report
from .output import write_site_json

CAT_DE = {"vorspeise": "Vorspeise", "hauptspeise": "Hauptspeise", "beilage": "Beilage"}
CAT_IT = {"vorspeise": "primo", "hauptspeise": "secondo", "beilage": "contorno"}
MONTHS_DE = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
WEEKDAYS_IT_LONG = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì"]
MAX_LAG = 30
TOP_WEEKDAY = 20
TOP_MONTH = 15
TOP_SHARE_BY_YEAR = 25
RECENT_WD = 5              # "recently served" = within the last 5 working days
GAP_BINS = [(1, 2), (3, 5), (6, 10), (11, 20), (21, 40), (41, 10_000)]
WARMUP = 20                # tip-level strategy stats skip the first 20 served days (no history yet)
HALF_LIVES = [30, 60, 90, 180, 365, None]   # calendar days, None = no decay
N_PERM = 300


# ======================================================================= helpers
def _log_pmf(i: int, n: int, p: float) -> float:
    return math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1) + i * math.log(p) + (n - i) * math.log1p(-p)


def binom_sf(k: int, n: int, p: float) -> float:
    """P(X >= k) for X ~ Bin(n, p)."""
    if k <= 0:
        return 1.0
    if k > n or p <= 0:
        return 0.0
    if p >= 1:
        return 1.0
    return min(1.0, sum(math.exp(_log_pmf(i, n, p)) for i in range(k, n + 1)))


def binom_cdf(k: int, n: int, p: float) -> float:
    """P(X <= k) for X ~ Bin(n, p)."""
    if k < 0:
        return 0.0
    if k >= n or p <= 0:
        return 1.0
    if p >= 1:
        return 0.0
    return min(1.0, sum(math.exp(_log_pmf(i, n, p)) for i in range(0, k + 1)))


def entropy_bits(counter: Counter) -> float:
    n = sum(counter.values())
    if not n:
        return 0.0
    return -sum(v / n * math.log2(v / n) for v in counter.values() if v)


def mutual_info(xs: list, ys: list) -> float:
    n = len(xs)
    if not n:
        return 0.0
    cx, cy, cxy = Counter(xs), Counter(ys), Counter(zip(xs, ys))
    return sum(v / n * math.log2(v * n / (cx[a] * cy[b])) for (a, b), v in cxy.items())


def pearson(xs: list[float], ys: list[float]) -> float | None:
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx == 0 or sy == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


def _r(x, nd: int = 4):
    return None if x is None else round(float(x), nd)


def _num(x, nd: int = 1) -> str:
    """German number formatting (decimal comma)."""
    if x is None:
        return "–"
    return f"{x:.{nd}f}".replace(".", ",")


def _pct(x, nd: int = 0) -> str:
    if x is None:
        return "–"
    return _num(100 * x, nd) + " %"


def _pval(p) -> str:
    if p is None:
        return "–"
    if p < 0.001:
        return "< 0,001"
    return _num(p, 3)


def _peq(p) -> str:
    """'p < 0,001' / 'p = 0,017' for running text."""
    s = _pval(p)
    return "p " + s if s.startswith("<") else "p = " + s


def _esc(s) -> str:
    return str(s).replace("|", "\\|")


def _table(header: list[str], rows: list[list]) -> list[str]:
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(_esc(x) for x in r) + " |" for r in rows]
    return out


# ======================================================================= context
class _Ctx:
    """Pre-computed views on the dataset shared by all analyses."""

    def __init__(self, ds: Dataset, today: dt.date):
        self.ds, self.today, self.norm = ds, today, ds.norm
        self.served = [m for m in ds.served if m.date <= today]
        self.years = sorted({m.date.year for m in self.served})
        self.wd = {d: i for i, d in enumerate(ds.workdays())}
        self.prim: dict[str, list[tuple[dt.date, str]]] = {
            c: [(m.date, m.options[c][0]) for m in self.served if m.options.get(c)] for c in CATEGORIES}
        self.prim_by_date = {c: dict(self.prim[c]) for c in CATEGORIES}
        self.n = {c: len(self.prim[c]) for c in CATEGORIES}
        self.totals = {c: Counter(d for _, d in self.prim[c]) for c in CATEGORIES}
        self.by_year = {c: {y: Counter(d for day, d in self.prim[c] if day.year == y) for y in self.years}
                        for c in CATEGORIES}
        self.n_year = {c: {y: sum(self.by_year[c][y].values()) for y in self.years} for c in CATEGORIES}
        self.share = {c: {d: v / self.n[c] for d, v in self.totals[c].items()} if self.n[c] else {} for c in CATEGORIES}
        self.prim_dates: dict[str, dict[str, list[dt.date]]] = {c: defaultdict(list) for c in CATEGORIES}
        for c in CATEGORIES:
            for day, d in self.prim[c]:
                self.prim_dates[c][d].append(day)
        self.any_dates: dict[str, dict[str, list[dt.date]]] = {c: defaultdict(list) for c in CATEGORIES}
        for m in self.served:
            for c in CATEGORIES:
                for o in m.options.get(c, []):
                    if not self.any_dates[c][o] or self.any_dates[c][o][-1] != m.date:
                        self.any_dates[c][o].append(m.date)
        # within-season expectation of "same dish" for two random days of the same year
        self.s2_year = {c: {y: sum((v / self.n_year[c][y]) ** 2 for v in self.by_year[c][y].values())
                            if self.n_year[c][y] else 0.0 for y in self.years} for c in CATEGORIES}

    def top(self, cat: str, k: int) -> list[str]:
        return [d for d, _ in sorted(self.totals[cat].items(), key=lambda kv: (-kv[1], kv[0]))[:k]]

    def is_fish_menu(self, m) -> bool:
        return any(self.norm.is_fish(o) for o in m.options.get("hauptspeise", []))


# ================================================================= 1 frequencies
def frequencies(c: _Ctx) -> tuple[dict, dict]:
    out, facts = {}, {}
    for cat in CATEGORIES:
        rows = []
        for d in set(c.totals[cat]) | set(c.any_dates[cat]):
            tot = c.totals[cat][d]
            dates = c.any_dates[cat].get(d, [])
            rows.append({"dish": d, "total": tot, "share": _r(tot / c.n[cat] if c.n[cat] else 0.0),
                         "by_year": {str(y): c.by_year[cat][y][d] for y in c.years},
                         "first_served": dates[0].isoformat() if dates else None,
                         "last_served": dates[-1].isoformat() if dates else None})
        rows.sort(key=lambda r: (-r["total"], r["dish"]))
        out[cat] = rows
        facts[cat] = {
            "distinct": sum(1 for r in rows if r["total"] > 0),
            "only_option": [r["dish"] for r in rows if r["total"] == 0],
            "rare": [r["dish"] for r in rows if 0 < r["total"] <= 2],
            "top_share5": sum(r["total"] for r in rows[:5]) / c.n[cat] if c.n[cat] else 0.0,
            "entropy": entropy_bits(c.totals[cat]),
            "distinct_year": {y: len(c.by_year[cat][y]) for y in c.years},
        }
    return out, facts


# ============================================================ 2 repetitiveness
def repeat_intervals(c: _Ctx) -> tuple[dict, dict]:
    out, facts = {}, {}
    for cat in CATEGORIES:
        rows, pooled, cross = [], [], 0
        for dish, dates in c.prim_dates[cat].items():
            if len(dates) < 2:
                continue
            gaps = []
            for a, b in zip(dates, dates[1:]):
                if a.year == b.year:
                    gaps.append(c.wd[b] - c.wd[a])
                else:
                    cross += 1
            weeks = Counter(week_key(d) for d in dates)
            pooled += gaps
            rows.append({"dish": dish, "n": len(dates),
                         "mean": _r(statistics.mean(gaps), 2) if gaps else None,
                         "median": _r(statistics.median(gaps), 1) if gaps else None,
                         "min": min(gaps) if gaps else None,
                         "max": max(gaps) if gaps else None,
                         "same_week_repeats": sum(v - 1 for v in weeks.values() if v > 1)})
        rows.sort(key=lambda r: (-r["n"], r["dish"]))
        out[cat] = rows
        # same ISO week: observed pairs vs expectation under independent daily draws
        weeks: dict[tuple, list[str]] = defaultdict(list)
        for day, d in c.prim[cat]:
            weeks[week_key(day)].append(d)
        obs_pairs = sum(math.comb(v, 2) for ds_ in weeks.values() for v in Counter(ds_).values())
        exp_pairs = sum(math.comb(len(ds_), 2) * c.s2_year[cat][wk[0] if wk[0] in c.s2_year[cat] else c.years[-1]]
                        for wk, ds_ in weeks.items())
        n_pairs = sum(math.comb(len(ds_), 2) for ds_ in weeks.values())
        p_week = binom_cdf(obs_pairs, n_pairs, exp_pairs / n_pairs) if n_pairs else None
        facts[cat] = {
            "gaps": pooled, "cross_season": cross,
            "min_gap": min(pooled) if pooled else None,
            "median_gap": statistics.median(pooled) if pooled else None,
            "le": {k: (sum(1 for g in pooled if g <= k) / len(pooled) if pooled else None) for k in (2, 5, 10, 20)},
            "same_week_pairs": obs_pairs, "same_week_expected": exp_pairs, "same_week_p": p_week,
            "weeks_with_repeat": sum(1 for ds_ in weeks.values() if len(set(ds_)) < len(ds_)),
            "n_weeks": len(weeks),
        }
    return out, facts


def refractory(c: _Ctx) -> tuple[dict, dict]:
    out, facts = {}, {}
    for cat in CATEGORIES:
        by_idx = {c.wd[day]: (day.year, d) for day, d in c.prim[cat]}
        base = sum(p * p for p in c.share[cat].values())
        lags, rates, cnts, sames, base_y = [], [], [], [], []
        for L in range(1, MAX_LAG + 1):
            cnt = same = 0
            exp = 0.0
            for i, (y, d) in by_idx.items():
                j = by_idx.get(i + L)
                if j is None or j[0] != y:
                    continue
                cnt += 1
                same += j[1] == d
                exp += c.s2_year[cat][y]
            lags.append(L)
            rates.append(same / cnt if cnt else None)
            cnts.append(cnt)
            sames.append(same)
            base_y.append(exp / cnt if cnt else base)
        out[cat] = {"lags": lags, "same_rate": [_r(x) for x in rates], "baseline": _r(base)}
        # "avoid within N working days": every lag <= N has a rate <= 25 % of the within-season baseline
        n_avoid = 0
        for L, r, b in zip(lags, rates, base_y):
            if r is not None and r <= 0.25 * b:
                n_avoid = L
            else:
                break
        first_repeat = next((L for L, s in zip(lags, sames) if s > 0), None)
        peaks = []
        for L, r, n_, s, b in zip(lags, rates, cnts, sames, base_y):
            if r is not None and r > 1.3 * b:
                p = binom_sf(s, n_, b)
                if p < 0.05:
                    peaks.append({"lag": L, "rate": r, "baseline": b, "same": s, "n": n_, "p": p})
        cum = {}
        for N in (5, 10):
            s_obs = sum(sames[:N])
            s_exp = sum(n_ * b for n_, b in zip(cnts[:N], base_y[:N]))
            cum[N] = (s_obs, s_exp)
        # weekly rhythm: lags 10..30 that are multiples of 5 (same weekday if no holiday) vs the other lags
        wk = [i for i, L in enumerate(lags) if L >= 10 and L % 5 == 0]
        ot = [i for i, L in enumerate(lags) if L >= 10 and L % 5 != 0]
        s_wk, n_wk = sum(sames[i] for i in wk), sum(cnts[i] for i in wk)
        s_ot, n_ot = sum(sames[i] for i in ot), sum(cnts[i] for i in ot)
        weekly = {"rate_wk": s_wk / n_wk if n_wk else None, "rate_other": s_ot / n_ot if n_ot else None,
                  "s_wk": s_wk, "n_wk": n_wk, "s_ot": s_ot, "n_ot": n_ot,
                  "p": binom_sf(s_wk, n_wk, s_ot / n_ot) if n_wk and n_ot and s_ot else None}
        facts[cat] = {"rates": rates, "counts": cnts, "sames": sames, "base_year": base_y, "baseline": base,
                      "baseline_season": sum(base_y[-10:]) / 10, "n_avoid": n_avoid,
                      "first_repeat": first_repeat, "peaks": peaks, "cum": cum, "weekly": weekly}
    return out, facts


# ================================================================ 3 weekday
def _weekday_profile(menus, cat: str, pred) -> dict:
    """Counts per weekday of days where ``pred(menu)`` holds (served days with cat present)."""
    n_wd = [0] * 5
    k_wd = [0] * 5
    for m in menus:
        if not m.options.get(cat) or m.weekday > 4:
            continue
        n_wd[m.weekday] += 1
        k_wd[m.weekday] += bool(pred(m))
    N, K = sum(n_wd), sum(k_wd)
    best = max(range(5), key=lambda w: (k_wd[w] / n_wd[w] if n_wd[w] else 0))
    p0 = n_wd[best] / N if N else 0
    return {"counts": k_wd, "n_wd": n_wd, "n": K, "best": best,
            "share_best": k_wd[best] / K if K else 0.0, "expected_share": p0,
            "lift": (k_wd[best] / K) / p0 if K and p0 else None,
            "p": binom_sf(k_wd[best], K, p0) if K else None}


def weekday(c: _Ctx) -> tuple[dict, dict]:
    out, facts = {}, {"notable": [], "absent": [], "hypotheses": [], "n_tests": 0}
    for cat in CATEGORIES:
        n_wd = [0] * 5
        cnt: dict[str, list[int]] = defaultdict(lambda: [0] * 5)
        for day, d in c.prim[cat]:
            if day.weekday() < 5:
                n_wd[day.weekday()] += 1
                cnt[d][day.weekday()] += 1
        N = sum(n_wd)
        dishes = c.top(cat, TOP_WEEKDAY)
        matrix, counts, lift = [], [], []
        for d in dishes:
            row = cnt[d]
            share = c.totals[cat][d] / N if N else 0
            counts.append(list(row))
            matrix.append([_r(row[w] / n_wd[w]) if n_wd[w] else 0.0 for w in range(5)])
            lift.append([_r((row[w] / n_wd[w]) / share, 3) if n_wd[w] and share else None for w in range(5)])
        out[cat] = {"dishes": dishes, "matrix": matrix, "counts": counts, "lift": lift}
        facts.setdefault("n_wd", {})[cat] = n_wd
        # scan every dish with n >= 5 for weekday preferences / avoidances
        for d, row in cnt.items():
            n = sum(row)
            if n < 5:
                continue
            for w in range(5):
                p0 = n_wd[w] / N
                k = row[w]
                facts["n_tests"] += 1
                lift_w = (k / n) / p0
                if k >= 3 and lift_w >= 1.5:
                    p = binom_sf(k, n, p0)
                    if p < 0.05:
                        facts["notable"].append({"cat": cat, "dish": d, "wd": w, "k": k, "n": n,
                                                 "share": k / n, "exp": p0, "lift": lift_w, "p": p})
                if n >= 10 and lift_w <= 0.35:
                    p = binom_cdf(k, n, p0)
                    if p < 0.05:
                        facts["absent"].append({"cat": cat, "dish": d, "wd": w, "k": k, "n": n,
                                                "share": k / n, "exp": p0, "lift": lift_w, "p": p})
    facts["notable"].sort(key=lambda x: x["p"])
    facts["absent"].sort(key=lambda x: x["p"])
    has = lambda cat, name: (lambda m: name.casefold() in {o.casefold() for o in m.options.get(cat, [])})
    not_lent = [m for m in c.served if not m.lent]
    hyps = [  # (menus, category, label DE, label IT, predicate) – hypotheses named in advance
        (c.served, "hauptspeise", "Fisch (alle Fischgerichte)", "pesce (tutti)", c.is_fish_menu),
        (not_lent, "hauptspeise", "Fisch außerhalb Fastenzeit", "pesce fuori Quaresima", c.is_fish_menu),
        (c.served, "hauptspeise", "Scombri", "Scombri", has("hauptspeise", "Scombri")),
        (c.served, "beilage", "Plent", "Plent (polenta)", has("beilage", "Plent")),
        (c.served, "hauptspeise", "Leberkas", "Leberkas", has("hauptspeise", "Leberkas")),
        (c.served, "hauptspeise", "Hauswurst", "Hauswurst", has("hauptspeise", "Hauswurst")),
    ]
    for menus, cat, label_de, label_it, pred in hyps:
        prof = _weekday_profile(menus, cat, pred)
        if prof["n"]:
            facts["hypotheses"].append({"label_de": label_de, "label_it": label_it, **prof})
    return out, facts


# ================================================================== 4 pairs
def pairs(c: _Ctx) -> tuple[list, list, dict]:
    hv = c.prim_by_date
    days = [m.date for m in c.served]
    # ---- Hauptspeise -> Beilage
    hb = [(hv["hauptspeise"][d], hv["beilage"][d]) for d in days if d in hv["hauptspeise"] and d in hv["beilage"]]
    by_h: dict[str, Counter] = defaultdict(Counter)
    for h, b in hb:
        by_h[h][b] += 1
    pairs_hb = []
    for h, ctr in by_h.items():
        n = sum(ctr.values())
        if n < 3:
            continue
        pairs_hb.append({"hauptspeise": h, "n": n,
                         "beilagen": [{"dish": b, "n": k, "p": _r(k / n)}
                                      for b, k in sorted(ctr.items(), key=lambda kv: (-kv[1], kv[0]))]})
    pairs_hb.sort(key=lambda r: (-r["n"], r["hauptspeise"]))
    b_tot = Counter(b for _, b in hb)
    top_b, top_b_n = b_tot.most_common(1)[0] if b_tot else ("", 0)
    # leave-one-out accuracy of "predict the most frequent Beilage of this Hauptspeise"
    loo_hit = 0
    for h, b in hb:
        ctr = by_h[h].copy()
        ctr[b] -= 1
        ctr = +ctr
        if ctr:
            mx = max(ctr.values())
            cands = sorted(x for x, v in ctr.items() if v == mx)
            guess = cands[0]
        else:
            g = b_tot.copy()
            g[b] -= 1
            guess = g.most_common(1)[0][0]
        loo_hit += guess == b
    h_b = entropy_bits(b_tot)
    h_b_given_h = sum(sum(ctr.values()) / len(hb) * entropy_bits(ctr) for ctr in by_h.values()) if hb else 0.0
    # ---- Vorspeise <-> Hauptspeise
    vh = [(hv["vorspeise"][d], hv["hauptspeise"][d]) for d in days if d in hv["vorspeise"] and d in hv["hauptspeise"]]
    nv, nh, nvh = Counter(v for v, _ in vh), Counter(h for _, h in vh), Counter(vh)
    N = len(vh)
    pairs_vh, vh_facts = [], []
    for (v, h), k in nvh.items():
        if k < 3:
            continue
        lift = k * N / (nv[v] * nh[h])
        pairs_vh.append({"vorspeise": v, "hauptspeise": h, "n": k, "lift": _r(lift, 3)})
        vh_facts.append({"v": v, "h": h, "n": k, "lift": lift, "nv": nv[v], "nh": nh[h],
                         "p": binom_sf(k, nv[v], nh[h] / N)})
    pairs_vh.sort(key=lambda r: (-r["lift"], -r["n"], r["vorspeise"]))
    vh_facts.sort(key=lambda r: r["p"])
    # ---- mutual information vs permutation
    rng = random.Random(0)
    mi = {}
    for name, (a, b) in {"V–H": ("vorspeise", "hauptspeise"), "H–B": ("hauptspeise", "beilage"),
                         "V–B": ("vorspeise", "beilage")}.items():
        xy = [(hv[a][d], hv[b][d]) for d in days if d in hv[a] and d in hv[b]]
        xs, ys = [x for x, _ in xy], [y for _, y in xy]
        obs = mutual_info(xs, ys)
        perm = []
        ys2 = list(ys)
        for _ in range(N_PERM):
            rng.shuffle(ys2)
            perm.append(mutual_info(xs, ys2))
        mi[name] = {"mi": obs, "perm_mean": statistics.mean(perm),
                    "p": (1 + sum(1 for x in perm if x >= obs)) / (1 + N_PERM)}
    facts = {"n_hb": len(hb), "top_b": top_b, "top_b_share": top_b_n / len(hb) if hb else 0.0,
             "loo_acc": loo_hit / len(hb) if hb else 0.0, "h_b": h_b, "h_b_given_h": h_b_given_h,
             "vh": vh_facts, "mi": mi, "n_vh": N}
    return pairs_hb, pairs_vh, facts


# ============================================================== 5 seasonality
def _contrast(c: _Ctx, cat: str, in_a, min_total: int = 3, fish_group: bool = False) -> list[dict]:
    """Shares of each dish on days with in_a(day) vs the other days."""
    na = nb = 0
    ka, kb = Counter(), Counter()
    fa = fb = 0
    menus = {m.date: m for m in c.served}
    for day, d in c.prim[cat]:
        a = in_a(day)
        if a:
            na += 1
            ka[d] += 1
        else:
            nb += 1
            kb[d] += 1
        if fish_group and c.is_fish_menu(menus[day]):
            if a:
                fa += 1
            else:
                fb += 1
    rows = []
    for d in c.totals[cat]:
        if c.totals[cat][d] < min_total and ka[d] < 2:
            continue
        pa = ka[d] / na if na else 0.0
        pb = kb[d] / nb if nb else 0.0
        rows.append({"dish": d, "ka": ka[d], "kb": kb[d], "pa": pa, "pb": pb,
                     "lift": pa / pb if pb else None,
                     "p": binom_sf(ka[d], ka[d] + kb[d], na / (na + nb)) if (na + nb) else None})
    if fish_group:
        pa, pb = fa / na if na else 0.0, fb / nb if nb else 0.0
        rows.append({"dish": c.norm.fish_label, "ka": fa, "kb": fb, "pa": pa, "pb": pb,
                     "lift": pa / pb if pb else None,
                     "p": binom_sf(fa, fa + fb, na / (na + nb)) if (na + nb) else None})
    for r in rows:
        r["na"], r["nb"] = na, nb
    return rows


def seasonality(c: _Ctx) -> tuple[dict, dict]:
    by_month, lent, sw, facts = {}, {}, {}, {"lent": {}, "sw": {}, "xmas": {}, "month_n": {}}
    for cat in CATEGORIES:
        n_m = [0] * 12
        cnt: dict[str, list[int]] = defaultdict(lambda: [0] * 12)
        for day, d in c.prim[cat]:
            n_m[day.month - 1] += 1
            cnt[d][day.month - 1] += 1
        dishes = c.top(cat, TOP_MONTH)
        by_month[cat] = {"dishes": dishes,
                         "matrix": [[_r(cnt[d][i] / n_m[i]) if n_m[i] else 0.0 for i in range(12)] for d in dishes]}
        facts["month_n"][cat] = n_m
        # Lent
        rows = _contrast(c, cat, is_lent, fish_group=(cat == "hauptspeise"))
        rows.sort(key=lambda r: (-(r["lift"] if r["lift"] is not None else 1e9), -r["pa"], r["dish"]))
        lent[cat] = [{"dish": r["dish"], "p_lent": _r(r["pa"]), "p_other": _r(r["pb"]),
                      "lift": _r(r["lift"], 3)} for r in rows]
        facts["lent"][cat] = rows
        # summer (Jun-Aug) vs winter (Dec-Feb); other months ignored
        ns = sum(1 for day, _ in c.prim[cat] if day.month in (6, 7, 8))
        nw = sum(1 for day, _ in c.prim[cat] if day.month in (12, 1, 2))
        ks = Counter(d for day, d in c.prim[cat] if day.month in (6, 7, 8))
        kw = Counter(d for day, d in c.prim[cat] if day.month in (12, 1, 2))
        srows = []
        for d in c.totals[cat]:
            if c.totals[cat][d] < 3:
                continue
            ps, pw = (ks[d] / ns if ns else 0.0), (kw[d] / nw if nw else 0.0)
            # two-sided-ish: probability of the observed summer count among summer+winter appearances
            k_tot = ks[d] + kw[d]
            p = None
            if k_tot and ns + nw:
                q = ns / (ns + nw)
                p = min(1.0, 2 * min(binom_sf(ks[d], k_tot, q), binom_cdf(ks[d], k_tot, q)))
            srows.append({"dish": d, "ps": ps, "pw": pw, "ks": ks[d], "kw": kw[d], "p": p})
        srows.sort(key=lambda r: (-(r["ps"] - r["pw"]), r["dish"]))
        sw[cat] = [{"dish": r["dish"], "p_summer": _r(r["ps"]), "p_winter": _r(r["pw"])} for r in srows]
        facts["sw"][cat] = {"rows": srows, "ns": ns, "nw": nw}
        # Christmas period: 1-23 December
        xrows = _contrast(c, cat, lambda day: day.month == 12 and day.day <= 23, min_total=2)
        xrows = [r for r in xrows if r["ka"] >= 2]
        xrows.sort(key=lambda r: (-(r["lift"] if r["lift"] is not None else 1e9), -r["ka"]))
        facts["xmas"][cat] = xrows
    # last served menu before Christmas, per year
    last = {}
    for m in c.served:
        if m.date.month == 12:
            last[m.date.year] = m
    facts["xmas_last"] = last
    # Lent ranges in data
    facts["lent_ranges"] = {y: lent_range(y) for y in c.years
                            if any(m.lent for m in c.served if m.date.year == y)}
    return {"by_month": by_month, "lent": lent, "summer_winter": sw}, facts


# =================================================================== 6 trends
def trends(c: _Ctx) -> tuple[dict, dict]:
    cur = max(c.years)
    prev_years = [y for y in c.years if y < cur]
    new, gone, sby, facts = {}, {}, {}, {"cur": cur, "prev": prev_years, "risers": {}, "fallers": {}, "halflife": {}}
    for cat in CATEGORIES:
        any_year: dict[str, Counter] = defaultdict(Counter)
        for d, dates in c.any_dates[cat].items():
            for day in dates:
                any_year[d][day.year] += 1
        prev = {d for d, ctr in any_year.items() if any(ctr[y] for y in prev_years)}
        now = {d for d, ctr in any_year.items() if ctr[cur]}
        new[cat] = sorted(now - prev, key=lambda d: (-any_year[d][cur], d))
        gone[cat] = sorted(prev - now, key=lambda d: (-sum(any_year[d].values()), d))
        dishes = c.top(cat, TOP_SHARE_BY_YEAR)
        for d in new[cat]:
            if d not in dishes and c.totals[cat][d] >= 3:
                dishes.append(d)
        sby[cat] = [{"dish": d, "by_year": {str(y): _r(c.by_year[cat][y][d] / c.n_year[cat][y]) if c.n_year[cat][y] else 0.0
                                            for y in c.years}} for d in dishes]
        facts.setdefault("counts", {})[cat] = {d: dict(any_year[d]) for d in new[cat] + gone[cat]}
        if prev_years:
            py = prev_years[-1]
            diffs = []
            for d in c.totals[cat]:
                if c.totals[cat][d] < 5:
                    continue
                a = c.by_year[cat][py][d] / c.n_year[cat][py] if c.n_year[cat][py] else 0.0
                b = c.by_year[cat][cur][d] / c.n_year[cat][cur] if c.n_year[cat][cur] else 0.0
                diffs.append((d, a, b))
            diffs.sort(key=lambda x: x[2] - x[1])
            facts["risers"][cat] = [x for x in reversed(diffs[-5:]) if x[2] > x[1]]
            facts["fallers"][cat] = [x for x in diffs[:5] if x[2] < x[1]]
            facts["prev_year"] = py
        facts["halflife"][cat] = _halflife_logloss(c, cat, cur)
    return {"new_2026": new, "gone_2026": gone, "share_by_year": sby}, facts


def _halflife_logloss(c: _Ctx, cat: str, test_year: int, alpha: float = 0.5) -> dict:
    """Mean log-loss of an exp-decay frequency forecast for every served day of ``test_year``."""
    hist = c.prim[cat]
    res = {}
    for hl in HALF_LIVES:
        ll, n = 0.0, 0
        for i, (day, d) in enumerate(hist):
            if day.year != test_year:
                continue
            w: dict[str, float] = defaultdict(float)
            for pday, pd in hist[:i]:
                w[pd] += 1.0 if hl is None else 0.5 ** ((day - pday).days / hl)
            W = sum(w.values())
            K = len(w) + 1
            p = (w.get(d, 0.0) + alpha) / (W + alpha * K)
            ll -= math.log(p)
            n += 1
        res["inf" if hl is None else str(hl)] = ll / n if n else None
    return res


# ================================================================== 7 players
def _label(c: _Ctx, name: str, cat: str, day: dt.date) -> str:
    return c.norm.model_label(name, cat, is_lent(day))


def players(c: _Ctx) -> tuple[list, dict]:
    ds = c.ds
    r4 = ds.r4()
    served_dates = sorted(m.date for m in c.served)
    served_pos = {d: i for i, d in enumerate(served_dates)}
    menus = {m.date: m for m in c.served}
    # rolling top-5 (model labels) and last-served index per label, both strictly before each served day
    top5_before: dict[str, dict[dt.date, set]] = {cat: {} for cat in CATEGORIES}
    last_before: dict[str, dict[dt.date, dict]] = {cat: {} for cat in CATEGORIES}
    for cat in CATEGORIES:
        run_cnt: Counter = Counter()
        last_idx: dict[str, int] = {}
        for day in served_dates:
            top5_before[cat][day] = {d for d, _ in sorted(run_cnt.items(), key=lambda kv: (-kv[1], kv[0]))[:5]}
            last_before[cat][day] = dict(last_idx)
            m = menus[day]
            if m.options.get(cat):
                run_cnt[_label(c, m.options[cat][0], cat, day)] += 1
                for o in m.options[cat]:
                    last_idx[_label(c, o, cat, day)] = c.wd[day]
                    if cat == "hauptspeise" and c.norm.is_generic_fish_ok(o):
                        last_idx[c.norm.fish_label] = c.wd[day]

    tips = [t for t in ds.tips if t.date < c.today]
    rows, facts = [], {"tiplevel": {}, "strategy": [], "sheet_diff": {}, "points_check": {}}
    tl_top = {cat: {True: [0, 0], False: [0, 0]} for cat in CATEGORIES}
    tl_gap = {cat: defaultdict(lambda: [0, 0]) for cat in CATEGORIES}
    per_py: dict[tuple, dict] = {}
    for p in ds.players:
        for y in c.years:
            ptips = [t for t in tips if t.player == p and t.date.year == y]
            if not ptips:
                continue
            st = [t for t in ptips if t.date in menus and t.points is not None and any(t.options.values())]
            if not st:
                continue
            days = len(st)
            pts = sum(t.points for t in st)
            wrong = sum(1 for t in st if t.points == 0)
            right = sum(1 for t in st if t.points >= 3)
            acc, fav = {}, {}
            m_top5 = m_recent = m_n = 0
            ent = []
            for cat in CATEGORIES:
                scorable = [t for t in st if t.options.get(cat) and menus[t.date].options.get(cat)]
                acc[cat] = _r(sum(1 for t in scorable if t.hits.get(cat)) / len(scorable)) if scorable else None
                ctr = Counter(o for t in ptips for o in t.options.get(cat, []))
                fav[cat] = [{"dish": d, "n": k} for d, k in sorted(ctr.items(), key=lambda kv: (-kv[1], kv[0]))[:5]]
                ent.append(entropy_bits(Counter(t.options[cat][0] for t in st if t.options.get(cat))))
                for t in scorable:
                    if served_pos[t.date] < WARMUP:
                        continue  # too little history for "top-5" / "days since last served"
                    lab = _label(c, t.options[cat][0], cat, t.date)
                    in_top = lab in top5_before[cat].get(t.date, set())
                    li = last_before[cat].get(t.date, {}).get(lab)
                    gap = c.wd[t.date] - li if li is not None else None
                    hit = bool(t.hits.get(cat))
                    m_n += 1
                    m_top5 += in_top
                    m_recent += gap is not None and gap <= RECENT_WD
                    tl_top[cat][in_top][0] += hit
                    tl_top[cat][in_top][1] += 1
                    key = "nie" if gap is None else next(f"{a}–{b}" if b < 10_000 else f"> {a - 1}"
                                                         for a, b in GAP_BINS if a <= gap <= b)
                    tl_gap[cat][key][0] += hit
                    tl_gap[cat][key][1] += 1
            hist = {t.date: t.options for t in ptips}
            viol = r4.check_sequence(hist)
            sheet = [t for t in st if t.points_sheet is not None]
            facts["sheet_diff"][(p, y)] = sum(1 for t in sheet if abs(t.points - t.points_sheet) > 1e-9)
            facts["points_check"][(p, y)] = (pts, sum(t.points_sheet for t in sheet))
            row = {"player": p, "year": y, "days": days, "points": _r(pts, 2), "ppd": _r(pts / days, 4),
                   "all_wrong": wrong, "all_wrong_rate": _r(wrong / days), "all_right": right,
                   "acc": acc, "fav": fav, "r4_violations": len(viol),
                   "strategy_note_de": "", "strategy_note_it": ""}
            rows.append(row)
            per_py[(p, y)] = {"top5": m_top5 / m_n if m_n else 0.0, "recent": m_recent / m_n if m_n else 0.0,
                              "entropy": statistics.mean(ent) if ent else 0.0, "viol": viol}
    # ranks + notes
    for y in c.years:
        yr = sorted((r for r in rows if r["year"] == y), key=lambda r: -r["ppd"])
        for rank, r in enumerate(yr, 1):
            m = per_py[(r["player"], y)]
            best = max((cat for cat in CATEGORIES if r["acc"].get(cat) is not None), key=lambda k: r["acc"][k],
                       default=None)
            de = (f"{_num(r['ppd'], 2)} Punkte/Tag (Rang {rank}/{len(yr)} in {y}). "
                  f"Top-5-Anteil der Tipps {_pct(m['top5'])}, Vielfalt {_num(m['entropy'], 1)} bit, "
                  f"{_pct(m['recent'])} Tipps auf Gerichte, die in den letzten {RECENT_WD} Arbeitstagen serviert wurden.")
            it = (f"{_num(r['ppd'], 2)} punti/giorno (posizione {rank}/{len(yr)} nel {y}). "
                  f"Quota tipp sui top-5 {_pct(m['top5'])}, varietà {_num(m['entropy'], 1)} bit, "
                  f"{_pct(m['recent'])} dei tipp su piatti serviti negli ultimi {RECENT_WD} giorni lavorativi.")
            if best:
                de += f" Stärkste Kategorie: {CAT_DE[best]} ({_pct(r['acc'][best])} Treffer)."
                it += f" Categoria migliore: {CAT_IT[best]} ({_pct(r['acc'][best])} centrati)."
            if r["r4_violations"]:
                de += f" Regel-4-Verstöße: {r['r4_violations']}."
                it += f" Violazioni regola 4: {r['r4_violations']}."
            r["strategy_note_de"], r["strategy_note_it"] = de, it
            m["rank"] = rank
    rows.sort(key=lambda r: (-r["year"], -r["ppd"]))
    # strategy correlation across player-years with enough days
    big = [r for r in rows if r["days"] >= 100]
    corr = {}
    for key in ("top5", "entropy", "recent"):
        corr[key] = pearson([per_py[(r["player"], r["year"])][key] for r in big], [r["ppd"] for r in big])
    corr["acc_v"] = pearson([r["acc"]["vorspeise"] or 0 for r in big], [r["ppd"] for r in big])
    facts.update({"per_py": per_py, "corr": corr, "n_big": len(big), "tl_top": tl_top,
                  "tl_gap": {cat: dict(v) for cat, v in tl_gap.items()}})
    return rows, facts


# ===================================================================== report
def _report(c: _Ctx, stats: dict, F: dict) -> str:
    L: list[str] = []
    nyear = {y: sum(1 for m in c.served if m.date.year == y) for y in c.years}
    last_menu = max(m.date for m in c.served) if c.served else None
    fr, rep, rf, wk, pr, se, tr, pl = (F[k] for k in ("freq", "rep", "refr", "wday", "pairs", "season", "trends", "players"))
    cur = tr["cur"]

    # ---------------------------------------------------------------- headline numbers
    hb_loo, hb_top = pr["loo_acc"], pr["top_b_share"]
    fish_lent = next((r for r in se["lent"]["hauptspeise"] if r["dish"] == c.norm.fish_label), None)
    best_cur = max((r for r in stats["players"] if r["year"] == cur), key=lambda r: r["ppd"], default=None)
    tl_recent = {}
    for cat in CATEGORIES:
        g = pl["tl_gap"][cat]
        rec = [g.get(k, [0, 0]) for k in ("1–2", "3–5")]
        old = [v for k, v in g.items() if k not in ("1–2", "3–5")]
        tl_recent[cat] = (sum(x[0] for x in rec) / max(1, sum(x[1] for x in rec)), sum(x[1] for x in rec),
                          sum(x[0] for x in old) / max(1, sum(x[1] for x in old)))
    bonf = 0.05 / max(1, wk["n_tests"])
    strong_wd = [x for x in wk["notable"] if x["p"] < bonf]
    det_pairs = [(r["hauptspeise"], r["beilagen"][0]) for r in stats["pairs_hb"]
                 if r["n"] >= 5 and r["beilagen"] and r["beilagen"][0]["p"] >= 0.6]
    hyp_ok = [h for h in wk["hypotheses"] if h["p"] is not None and h["p"] < 0.01]
    hyp_no = [h for h in wk["hypotheses"] if h["p"] is None or h["p"] >= 0.05]
    sw_sig = {cat: [r for r in se["sw"][cat]["rows"] if r["p"] is not None and r["p"] < 0.05] for cat in CATEGORIES}
    rv, rh, rb = rf["vorspeise"], rf["hauptspeise"], rf["beilage"]
    sv, sh, sb = rep["vorspeise"], rep["hauptspeise"], rep["beilage"]
    best_gap = {}
    for cat in CATEGORIES:
        g = {k: v for k, v in pl["tl_gap"][cat].items() if v[1] >= 50 and k != "nie"}
        if g:
            k = max(g, key=lambda k: g[k][0] / g[k][1])
            best_gap[cat] = (k, g[k][0] / g[k][1], g[k][1])

    def week_phrase(s, lang):
        if s["same_week_pairs"] == 0:
            return ("nie zweimal in derselben Kalenderwoche" if lang == "de" else "mai due volte nella stessa settimana")
        return (f"nur {s['same_week_pairs']}× doppelt in derselben Woche" if lang == "de"
                else f"solo {s['same_week_pairs']} doppioni nella stessa settimana")

    L += ["# Analyse Tippspiel Essen Wies", "",
          f"_Automatisch erzeugt von `engine/analyze.py` am {stats['generated_at'][:16].replace('T', ' ')} UTC "
          f"(Stichtag {c.today.isoformat()}). Datenstand: {len(c.served)} servierte Menüs "
          f"({', '.join(f'{y}: {n}' for y, n in nyear.items())}), letztes Menü {last_menu}._", ""]

    # ---------------------------------------------------------------- Riassunto
    L += ["## Riassunto (IT)", ""]
    it = []
    it.append(f"**Dati**: {len(c.served)} menù serviti ({', '.join(f'{y}: {n}' for y, n in nyear.items())}); "
              f"piatti distinti: primo {fr['vorspeise']['distinct']}, secondo {fr['hauptspeise']['distinct']}, "
              f"contorno {fr['beilage']['distinct']}.")
    for cat in CATEGORIES:
        top3 = ", ".join(f"{r['dish']} ({r['total']})" for r in stats["frequencies"][cat][:3])
        it.append(f"**{CAT_IT[cat].capitalize()} più frequenti**: {top3}; i primi 5 coprono {_pct(fr[cat]['top_share5'])} dei giorni.")
    it.append(f"**Ripetizioni**: la cucina evita le ripetizioni. Primo e secondo: {week_phrase(sv, 'it')} "
              f"({sv['same_week_pairs']} e {sh['same_week_pairs']} coppie contro "
              f"{_num(sv['same_week_expected'], 0)} e {_num(sh['same_week_expected'], 0)} attese per caso, {_peq(sv['same_week_p'])}); "
              f"quasi nessuna ripetizione entro {rv['n_avoid']} (primo) / {rh['n_avoid']} (secondo) giorni lavorativi; "
              f"intervallo mediano {_num(sv['median_gap'], 0)} / {_num(sh['median_gap'], 0)} giorni lavorativi. "
              f"Il contorno si ripete molto di più ({sb['same_week_pairs']} coppie nella stessa settimana). "
              f"→ Non tippare primo/secondo serviti negli ultimi giorni o già serviti questa settimana.")
    if wk["notable"]:
        top = (strong_wd or wk["notable"])[:4]
        it.append("**Giorno della settimana**: " + "; ".join(
            f"{x['dish']} ({CAT_IT[x['cat']]}) il {WEEKDAYS_IT_LONG[x['wd']]} {x['k']}/{x['n']} "
            f"(atteso {_pct(x['exp'])}, {_peq(x['p'])})" for x in top)
            + (f". {len(strong_wd)} effetti restano significativi anche con correzione di Bonferroni: il giorno della "
               f"settimana conta." if strong_wd else ". Nessun effetto supera la correzione di Bonferroni: usare con cautela."))
    hyp_it = [f"{h['label_it']} il {WEEKDAYS_IT_LONG[h['best']]} {h['counts'][h['best']]}/{h['n']}" for h in hyp_ok]
    if hyp_it:
        it.append("**Ipotesi confermate**: " + "; ".join(hyp_it) + "."
                  + (" Non confermate: " + ", ".join(h["label_it"] for h in hyp_no) + "." if hyp_no else ""))
    it.append(f"**Contorno ↔ secondo**: conoscendo il secondo, il contorno più tipico è giusto nel {_pct(hb_loo)} dei casi "
              f"(leave-one-out) contro {_pct(hb_top)} tippando sempre {pr['top_b']}"
              + (" (es. " + ", ".join(f"{h} → {b['dish']} {_pct(b['p'])}" for h, b in det_pairs[:4]) + ")" if det_pairs else "")
              + f". Primo e secondo invece sono quasi indipendenti (MI {_num(pr['mi']['V–H']['mi'], 2)} bit vs "
              f"{_num(pr['mi']['V–H']['perm_mean'], 2)} per caso, {_peq(pr['mi']['V–H']['p'])}).")
    if fish_lent:
        it.append(f"**Quaresima / pesce**: pesce in Quaresima nel {_pct(fish_lent['pa'])} dei giorni contro {_pct(fish_lent['pb'])} "
                  f"fuori ({fish_lent['ka']} vs {fish_lent['kb']} giorni). Nessuna differenza significativa estate/inverno"
                  + ("" if not any(sw_sig.values()) else " tranne " + ", ".join(r["dish"] for v in sw_sig.values() for r in v))
                  + ".")
    it.append(f"**Trend {cur}**: nuovi primi {len(stats['trends']['new_2026']['vorspeise'])}, nuovi secondi "
              f"{len(stats['trends']['new_2026']['hauptspeise'])}; spariti primi {len(stats['trends']['gone_2026']['vorspeise'])}, "
              f"secondi {len(stats['trends']['gone_2026']['hauptspeise'])} (quasi tutti piatti rari). " + _halflife_sentence(tr, "it"))
    if best_cur:
        it.append(f"**Giocatori {cur}**: miglior media {best_cur['player']} con {_num(best_cur['ppd'], 2)} punti/giorno. "
                  f"Tipp su piatti serviti negli ultimi 5 giorni lavorativi: primo centrato solo nel "
                  f"{_pct(tl_recent['vorspeise'][0], 1)} (n={tl_recent['vorspeise'][1]}) contro {_pct(tl_recent['vorspeise'][2], 1)} "
                  f"per gli altri tipp"
                  + (f"; il momento migliore per tippare un primo è {best_gap['vorspeise'][0]} giorni lavorativi dopo "
                     f"l'ultima volta ({_pct(best_gap['vorspeise'][1], 1)})" if "vorspeise" in best_gap else "") + ".")
    L += [f"- {x}" for x in it] + [""]

    # ---------------------------------------------------------------- Kernaussagen DE
    L += ["## Kernaussagen", ""]
    de = []
    de.append(f"**Keine Wiederholung in derselben Woche**: Vorspeise {week_phrase(sv, 'de')} ({sv['same_week_pairs']} Paare, "
              f"Zufall {_num(sv['same_week_expected'], 1)}, {_peq(sv['same_week_p'])}), Hauptspeise {week_phrase(sh, 'de')} "
              f"({sh['same_week_pairs']} Paare, Zufall {_num(sh['same_week_expected'], 1)}). Beilage dagegen "
              f"{sb['same_week_pairs']} Paare (Zufall {_num(sb['same_week_expected'], 1)}), v. a. {pr['top_b']}.")
    de.append(f"**Mindestabstand**: Vorspeise frühestens wieder nach {rv['first_repeat']} Arbeitstagen, Hauptspeise nach "
              f"{rh['first_repeat']}; innerhalb von {rv['n_avoid']} bzw. {rh['n_avoid']} AT praktisch nie (< 25 % der "
              f"Zufallsrate). Median-Abstand {_num(sv['median_gap'], 1)} (V), {_num(sh['median_gap'], 1)} (H), "
              f"{_num(sb['median_gap'], 1)} (B) Arbeitstage.")
    wv, wh = rv["weekly"], rh["weekly"]
    if wv["rate_wk"] is not None and wh["rate_wk"] is not None:
        de.append(f"**Wochenrhythmus**: Bei Abständen von 10, 15, … 30 AT (gleicher Wochentag) ist dieselbe Speise "
                  f"häufiger als bei anderen Abständen – V {_pct(wv['rate_wk'], 1)} vs {_pct(wv['rate_other'], 1)} "
                  f"({_peq(wv['p'])}), H {_pct(wh['rate_wk'], 1)} vs {_pct(wh['rate_other'], 1)} ({_peq(wh['p'])}). "
                  + "; ".join(f"Spitze {CAT_DE[cat]} L={pk['lag']}: {_pct(pk['rate'], 1)} vs {_pct(pk['baseline'], 1)} ({_peq(pk['p'])})"
                              for cat in CATEGORIES for pk in rf[cat]["peaks"][:1]) + ".")
    for x in (strong_wd or wk["notable"])[:6]:
        de.append(f"**Wochentag**: {x['dish']} ({CAT_DE[x['cat']]}) am {WEEKDAYS_DE_LONG[x['wd']]} {x['k']}/{x['n']} "
                  f"({_pct(x['share'])}, erwartet {_pct(x['exp'])}, Lift {_num(x['lift'], 1)}, {_peq(x['p'])}"
                  f"{', Bonferroni-signifikant' if x['p'] < bonf else ''}).")
    for h in wk["hypotheses"]:
        verdict = "bestätigt" if h["p"] is not None and h["p"] < 0.01 else ("Tendenz" if h["p"] is not None and h["p"] < 0.05
                                                                              else "nicht bestätigt")
        de.append(f"**Hypothese {h['label_de']}**: häufigster Tag {WEEKDAYS_DE_LONG[h['best']]} "
                  f"{h['counts'][h['best']]}/{h['n']} (Mo–Fr: {'/'.join(str(x) for x in h['counts'])}, {_peq(h['p'])}) → {verdict}.")
    de.append(f"**Beilage hängt an der Hauptspeise**: mit bekannter Hauptspeise trifft die typische Beilage in "
              f"{_pct(hb_loo)} der Fälle (Leave-one-out), ohne nur {_pct(hb_top)} ({pr['top_b']}); Entropie "
              f"{_num(pr['h_b'], 2)} → {_num(pr['h_b_given_h'], 2)} bit. Feste Paare: "
              + ", ".join(f"{h} → {b['dish']} {_pct(b['p'])} ({b['n']})" for h, b in det_pairs) + ".")
    de.append(f"**Vorspeise ↔ Hauptspeise**: kaum Zusammenhang (MI {_num(pr['mi']['V–H']['mi'], 3)} vs Zufall "
              f"{_num(pr['mi']['V–H']['perm_mean'], 3)} bit, {_peq(pr['mi']['V–H']['p'])}); einzelne Paare mit hohem Lift "
              f"entstehen v. a. über den gemeinsamen Wochentag.")
    if fish_lent:
        de.append(f"**Fisch & Fastenzeit**: Fisch an {_pct(fish_lent['pa'])} der Fastentage ({fish_lent['ka']}) vs "
                  f"{_pct(fish_lent['pb'])} sonst ({fish_lent['kb']}; {_peq(fish_lent['p'])}). Sommer/Winter: "
                  + ("keine signifikanten Unterschiede." if not any(sw_sig.values()) else
                     ", ".join(f"{r['dish']} ({'Sommer' if r['ps'] > r['pw'] else 'Winter'})" for v in sw_sig.values() for r in v) + "."))
    de.append(_halflife_sentence(tr, "de"))
    if best_gap:
        de.append("**Tipp-Timing (alle Spieler)**: Tipps auf Gerichte, die vor 1–5 AT serviert wurden, treffen bei V nur "
                  f"{_pct(tl_recent['vorspeise'][0], 1)} (sonst {_pct(tl_recent['vorspeise'][2], 1)}), bei H "
                  f"{_pct(tl_recent['hauptspeise'][0], 1)} (sonst {_pct(tl_recent['hauptspeise'][2], 1)}). Beste Abstandsklasse: "
                  + ", ".join(f"{CAT_DE[cat]} {k} AT ({_pct(r, 1)}, n={n})" for cat, (k, r, n) in best_gap.items()) + ".")
    if best_cur:
        de.append(f"**Spieler {cur}**: beste Quote {best_cur['player']} mit {_num(best_cur['ppd'], 3)} Punkten/Tag; "
                  f"alle Spieler liegen eng beieinander (" + ", ".join(
                      f"{r['player']} {_num(r['ppd'], 3)}" for r in stats["players"] if r["year"] == cur) + ").")
    L += [f"- {x}" for x in de] + [""]

    # ---------------------------------------------------------------- 1 frequencies
    L += ["## 1. Häufigkeiten", "",
          "Gezählt wird die erste angesagte Option (bei „A / B“ zählt A). „zuletzt“ berücksichtigt alle Optionen.", ""]
    L += _table(["Kategorie", "verschiedene Gerichte"] + [str(y) for y in c.years] + ["Top-5-Anteil", "Entropie (bit)"],
                [[CAT_DE[cat], fr[cat]["distinct"]] + [fr[cat]["distinct_year"][y] for y in c.years]
                 + [_pct(fr[cat]["top_share5"]), _num(fr[cat]["entropy"], 2)] for cat in CATEGORIES])
    L.append("")
    for cat in CATEGORIES:
        rows = stats["frequencies"][cat]
        L += [f"### {CAT_DE[cat]} – Top 20", ""]
        L += _table(["#", "Gericht", "gesamt", "Anteil"] + [str(y) for y in c.years] + ["zuletzt"],
                    [[i + 1, r["dish"], r["total"], _pct(r["share"], 1)] + [r["by_year"][str(y)] for y in c.years]
                     + [r["last_served"]] for i, r in enumerate([x for x in rows if x["total"] > 0][:20])])
        L.append("")
        rare = fr[cat]["rare"]
        L += [f"**Selten (n ≤ 2, {len(rare)} Gerichte):** " + (", ".join(rare) if rare else "_keine_"), ""]
        if fr[cat]["only_option"]:
            L += ["**Nur als Alternative angesagt:** " + ", ".join(fr[cat]["only_option"]), ""]

    # ---------------------------------------------------------------- 2 repetitions
    L += ["## 2. Wiederholungen und Refraktärzeit", "",
          "Abstände in **Arbeitstagen** (Position im Spielkalender; freie Tage und Saisonpausen zählen nicht). "
          "Abstände über eine Saisongrenze hinweg werden ignoriert. „Zufall“ = Erwartung, wenn die Küche jeden Tag "
          "unabhängig nach den Jahreshäufigkeiten wählen würde.", ""]
    L += _table(["Kategorie", "kleinster Abstand", "Median", "≤ 2 AT", "≤ 5 AT", "≤ 10 AT", "≤ 20 AT",
                 "gleiche Woche (Paare)", "Zufall", "p (weniger als Zufall)", "keine Wdh. innerhalb"],
                [[CAT_DE[cat], rep[cat]["min_gap"], _num(rep[cat]["median_gap"], 1)]
                 + [_pct(rep[cat]["le"][k]) for k in (2, 5, 10, 20)]
                 + [rep[cat]["same_week_pairs"], _num(rep[cat]["same_week_expected"], 1), _pval(rep[cat]["same_week_p"]),
                    f"{rf[cat]['n_avoid']} AT"] for cat in CATEGORIES])
    L.append("")
    for cat in CATEGORIES:
        r = rf[cat]
        s5, e5 = r["cum"][5]
        s10, e10 = r["cum"][10]
        verdict = ("**vermeidet** Wiederholungen" if s5 <= 0.25 * e5 else
                   "wiederholt **seltener** als Zufall" if s5 < 0.75 * e5 else "zeigt **keine** klare Vermeidung")
        L.append(f"- **{CAT_DE[cat]}**: Die Küche {verdict} innerhalb von 5 Arbeitstagen ({s5} gleiche Paare, Zufall "
                 f"{_num(e5, 1)}); innerhalb von 10 Arbeitstagen {s10} vs {_num(e10, 1)}. Erste Wiederholung frühestens "
                 f"nach {r['first_repeat']} AT.")
    L.append("")
    L += ["### Refraktärkurve P(gleiches Gericht im Abstand L)", "",
          "Basis = Σ p² (globale Anteile, wie in `stats.json`); Saison-Basis = Erwartung für zwei Tage derselben Saison.", ""]
    hdr = ["L (AT)"] + [f"{CAT_DE[cat]}" for cat in CATEGORIES]
    rows = []
    for i in range(MAX_LAG):
        rows.append([i + 1] + [f"{_pct(rf[cat]['rates'][i], 1)} ({rf[cat]['sames'][i]}/{rf[cat]['counts'][i]})"
                               for cat in CATEGORIES])
    rows.append(["Basis Σp²"] + [_pct(rf[cat]["baseline"], 1) for cat in CATEGORIES])
    rows.append(["Saison-Basis"] + [_pct(rf[cat]["baseline_season"], 1) for cat in CATEGORIES])
    L += _table(hdr, rows) + [""]
    pk_lines = [f"- {CAT_DE[cat]}: L={pk['lag']} → {_pct(pk['rate'], 1)} vs {_pct(pk['baseline'], 1)} "
                f"({pk['same']}/{pk['n']}, {_peq(pk['p'])})" for cat in CATEGORIES for pk in rf[cat]["peaks"]]
    L += ["**Auffällige Spitzen (Rate > 1,3 × Saison-Basis, p < 0,05; L=5 ≈ 1 Woche, L=20 ≈ 4 Wochen):**", ""]
    L += (pk_lines or ["_keine_"]) + [""]
    L += ["**Wochenrhythmus** – gleiche Speise bei Abständen L = 10, 15, 20, 25, 30 AT (meist gleicher Wochentag) "
          "vs. allen anderen Abständen 10–30 AT:", ""]
    L += _table(["Kategorie", "L = 5·k", "andere L", "p"],
                [[CAT_DE[cat], f"{_pct(rf[cat]['weekly']['rate_wk'], 1)} ({rf[cat]['weekly']['s_wk']}/{rf[cat]['weekly']['n_wk']})",
                  f"{_pct(rf[cat]['weekly']['rate_other'], 1)} ({rf[cat]['weekly']['s_ot']}/{rf[cat]['weekly']['n_ot']})",
                  _pval(rf[cat]["weekly"]["p"])] for cat in CATEGORIES])
    L += ["", "→ Der Wochentag-Effekt (Abschnitt 3) erzeugt einen schwachen Wochenrhythmus; die Refraktärzeit "
          "dominiert aber die ersten 1–2 Wochen.", ""]
    for cat in ("vorspeise", "hauptspeise"):
        L += [f"### Abstände je Gericht – {CAT_DE[cat]} (n ≥ 8)", ""]
        L += _table(["Gericht", "n", "Mittel", "Median", "min", "max", "Wdh. gleiche Woche"],
                    [[r["dish"], r["n"], _num(r["mean"], 1), _num(r["median"], 1), r["min"], r["max"], r["same_week_repeats"]]
                     for r in stats["repeat_intervals"][cat] if r["n"] >= 8])
        L.append("")
    L += ["### Abstände je Gericht – Beilage", ""]
    L += _table(["Gericht", "n", "Mittel", "Median", "min", "max", "Wdh. gleiche Woche"],
                [[r["dish"], r["n"], _num(r["mean"], 1), _num(r["median"], 1), r["min"], r["max"], r["same_week_repeats"]]
                 for r in stats["repeat_intervals"]["beilage"] if r["n"] >= 5])
    L.append("")

    # ---------------------------------------------------------------- 3 weekday
    L += ["## 3. Wochentage", "",
          f"Servierte Tage je Wochentag (Hauptspeise): "
          + ", ".join(f"{WEEKDAYS_DE[w]} {wk['n_wd']['hauptspeise'][w]}" for w in range(5)) + ". "
          f"Getestet wurden {wk['n_tests']} Kombinationen (Gericht mit n ≥ 5 × Wochentag) mit einem einseitigen "
          f"Binomialtest; bei so vielen Tests sind einzelne p < 0,05 auch zufällig zu erwarten "
          f"(Bonferroni-Schwelle ≈ {_num(0.05 / max(1, wk['n_tests']), 4)}).", ""]
    L += ["### Gezielte Hypothesen", ""]
    L += _table(["Merkmal", "n Tage", "Mo", "Di", "Mi", "Do", "Fr", "häufigster Tag", "Anteil (erwartet)", "p"],
                [[h["label_de"], h["n"]] + h["counts"] + [WEEKDAYS_DE[h["best"]],
                 f"{_pct(h['share_best'])} ({_pct(h['expected_share'])})", _pval(h["p"])] for h in wk["hypotheses"]])
    L.append("")
    L += ["### Auffällige Wochentag-Vorlieben (Lift ≥ 1,5, mind. 3×, p < 0,05)", ""]
    L += _table(["Kategorie", "Gericht", "Tag", "an diesem Tag", "Anteil", "erwartet", "Lift", "p", "Bonferroni"],
                [[CAT_DE[x["cat"]], x["dish"], WEEKDAYS_DE[x["wd"]], f"{x['k']}/{x['n']}", _pct(x["share"]),
                  _pct(x["exp"]), _num(x["lift"], 2), _pval(x["p"]), "✔" if x["p"] < 0.05 / max(1, wk["n_tests"]) else ""]
                 for x in wk["notable"][:25]]) if wk["notable"] else ["_keine_"]
    L.append("")
    if wk["absent"]:
        L += ["### Gerichte, die an einem Wochentag (fast) nie kommen (n ≥ 10, p < 0,05)", ""]
        L += _table(["Kategorie", "Gericht", "Tag", "an diesem Tag", "erwartet", "p"],
                    [[CAT_DE[x["cat"]], x["dish"], WEEKDAYS_DE[x["wd"]], f"{x['k']}/{x['n']}",
                      _num(x["exp"] * x["n"], 1), _pval(x["p"])] for x in wk["absent"][:15]])
        L.append("")
    for cat in CATEGORIES:
        w = stats["weekday"][cat]
        L += [f"### {CAT_DE[cat]}: Anzahl je Wochentag (Top 12)", ""]
        L += _table(["Gericht", "Mo", "Di", "Mi", "Do", "Fr", "max. Lift"],
                    [[d] + w["counts"][i] + [_num(max((x for x in w["lift"][i] if x is not None), default=None), 2)]
                     for i, d in enumerate(w["dishes"][:12])])
        L.append("")

    # ---------------------------------------------------------------- 4 pairs
    L += ["## 4. Kombinationen", "", "### Beilage | Hauptspeise (Hauptspeisen mit n ≥ 3)", "",
          f"Wer die Hauptspeise kennt (bzw. richtig schätzt), sollte die dazu typische Beilage tippen: "
          f"Treffer {_pct(hb_loo)} (Leave-one-out) statt {_pct(hb_top)} mit der global häufigsten Beilage ({pr['top_b']}).", ""]
    L += _table(["Hauptspeise", "n", "Beilage 1", "Beilage 2", "Beilage 3"],
                [[r["hauptspeise"], r["n"]] + [f"{b['dish']} {_pct(b['p'])} ({b['n']})" for b in r["beilagen"][:3]]
                 + [""] * (3 - min(3, len(r["beilagen"]))) for r in stats["pairs_hb"]])
    L.append("")
    L += ["### Vorspeise ↔ Hauptspeise (n ≥ 3)", "",
          f"Mutual Information zwischen den Kategorien vs. Erwartung bei zufälliger Zuordnung ({N_PERM} Permutationen):", ""]
    L += _table(["Paar", "MI (bit)", "Zufall (bit)", "p"],
                [[k, _num(v["mi"], 3), _num(v["perm_mean"], 3), _pval(v["p"])] for k, v in pr["mi"].items()])
    L.append("")
    L += _table(["Vorspeise", "Hauptspeise", "zusammen", "n(V)", "n(H)", "Lift", "p"],
                [[x["v"], x["h"], x["n"], x["nv"], x["nh"], _num(x["lift"], 2), _pval(x["p"])] for x in pr["vh"][:25]])
    L.append("")

    # ---------------------------------------------------------------- 5 seasonality
    L += ["## 5. Saisonalität", ""]
    lr = se["lent_ranges"]
    L += ["### Fastenzeit (Aschermittwoch – Ostersonntag)", "",
          "Fastenzeiten in den Daten: " + ", ".join(f"{y}: {a.strftime('%d.%m.')}–{b.strftime('%d.%m.')}" for y, (a, b) in lr.items())
          + ". Fisch = jede Hauptspeise, die als Fisch gilt (inkl. Scombri).", ""]
    for cat in ("hauptspeise", "vorspeise", "beilage"):
        rows = [r for r in se["lent"][cat] if r["ka"] >= 2 or r["dish"] == c.norm.fish_label]
        rows.sort(key=lambda r: (-(r["lift"] if r["lift"] is not None else 1e9), -r["pa"]))
        if not rows:
            continue
        L += [f"**{CAT_DE[cat]}** (Fastentage n={rows[0]['na']}, sonst n={rows[0]['nb']}; Gerichte mit ≥ 2 Fastentagen):", ""]
        L += _table(["Gericht", "Fastenzeit", "sonst", "Lift", "p"],
                    [[r["dish"], f"{_pct(r['pa'], 1)} ({r['ka']})", f"{_pct(r['pb'], 1)} ({r['kb']})",
                      _num(r["lift"], 2) if r["lift"] is not None else "nur Fastenzeit", _pval(r["p"])] for r in rows[:12]])
        L.append("")
    L += ["### Sommer (Jun–Aug) vs Winter (Dez–Feb)", ""]
    for cat in CATEGORIES:
        s = se["sw"][cat]
        rows = s["rows"]
        sig = [r for r in rows if r["p"] is not None and r["p"] < 0.05]
        L += [f"**{CAT_DE[cat]}** (Sommertage n={s['ns']}, Wintertage n={s['nw']}):", ""]
        sel = rows[:6] + [r for r in rows[-6:] if r not in rows[:6]]
        L += _table(["Gericht", "Sommer", "Winter", "p (zweiseitig)"],
                    [[r["dish"], f"{_pct(r['ps'], 1)} ({r['ks']})", f"{_pct(r['pw'], 1)} ({r['kw']})", _pval(r["p"])]
                     for r in sel])
        L += ["", "Signifikant (p < 0,05): " + (", ".join(
            f"{r['dish']} ({'Sommer' if r['ps'] > r['pw'] else 'Winter'})" for r in sig) if sig else "_keine_"), ""]
    L += ["### Monate (Anteil der servierten Tage, Top 10)", ""]
    for cat in CATEGORIES:
        bm = stats["seasonality"]["by_month"][cat]
        L += [f"**{CAT_DE[cat]}** (Tage je Monat: " + ", ".join(
            f"{MONTHS_DE[i]} {n}" for i, n in enumerate(se["month_n"][cat]) if n) + ")", ""]
        L += _table(["Gericht"] + MONTHS_DE,
                    [[d] + [(_num(100 * x, 0) if x else "·") for x in bm["matrix"][i]] for i, d in enumerate(bm["dishes"][:10])])
        L.append("")
    L += ["### Weihnachtszeit (1.–23. Dezember)", ""]
    any_x = False
    for cat in CATEGORIES:
        rows = [r for r in se["xmas"][cat] if (r["lift"] is None or r["lift"] >= 1.5)][:6]
        if rows:
            any_x = True
            L.append(f"- **{CAT_DE[cat]}** (Dezembertage n={rows[0]['na']}): " + "; ".join(
                f"{r['dish']} {r['ka']}× ({_pct(r['pa'])} vs {_pct(r['pb'])} sonst, {_peq(r['p'])})" for r in rows))
    if not any_x:
        L.append("- _keine auffälligen Dezember-Gerichte_")
    for y, m in sorted(se["xmas_last"].items()):
        L.append(f"- Letztes Menü vor Weihnachten {y} ({m.date.strftime('%d.%m.')}): "
                 + " / ".join(m.options[c_][0] if m.options.get(c_) else "–" for c_ in CATEGORIES))
    L.append("")

    # ---------------------------------------------------------------- 6 trends
    L += [f"## 6. Trends ({cur} vs. {', '.join(str(y) for y in tr['prev'])})", ""]
    for cat in CATEGORIES:
        cnts = tr["counts"][cat]
        new = stats["trends"]["new_2026"][cat]
        gone = stats["trends"]["gone_2026"][cat]
        L.append(f"- **{CAT_DE[cat]} neu {cur}** ({len(new)}): "
                 + (", ".join(f"{d} ({cnts[d].get(cur, 0)}×)" for d in new) if new else "_keine_"))
        L.append(f"- **{CAT_DE[cat]} verschwunden {cur}** ({len(gone)}): "
                 + (", ".join(f"{d} ({sum(cnts[d].values())}×)" for d in gone) if gone else "_keine_"))
    L.append("")
    if tr.get("prev_year"):
        py = tr["prev_year"]
        L += [f"**Aufsteiger / Absteiger** (Anteil {py} → {cur}, Gerichte mit n ≥ 5):", ""]
        rows = []
        for cat in CATEGORIES:
            for d, a, b in tr["risers"][cat]:
                rows.append([CAT_DE[cat], d, "↑", _pct(a, 1), _pct(b, 1)])
            for d, a, b in tr["fallers"][cat]:
                rows.append([CAT_DE[cat], d, "↓", _pct(a, 1), _pct(b, 1)])
        L += _table(["Kategorie", "Gericht", "", str(py), str(cur)], rows) + [""]
    L += ["### Gewichtung nach Aktualität", "",
          f"Mittlerer Log-Loss einer reinen Häufigkeitsprognose für jeden Tag {cur} (nur Vergangenheit, Gewicht "
          f"0,5^(Alter/Halbwertszeit), Glättung 0,5; kleiner = besser). Zeigt, ob jüngere Menüs mehr zählen sollten "
          f"(Refraktärzeit und Wochentag sind hier bewusst nicht enthalten).", ""]
    hls = [("30", "30 T"), ("60", "60 T"), ("90", "90 T"), ("180", "180 T"), ("365", "365 T"), ("inf", "∞ (ungewichtet)")]
    L += _table(["Kategorie"] + [h for _, h in hls],
                [[CAT_DE[cat]] + [_num(tr["halflife"][cat].get(k), 3) for k, _ in hls] for cat in CATEGORIES])
    L += ["", _halflife_sentence(tr, "de"), ""]
    L += ["### Anteile je Jahr (Top-Gerichte)", ""]
    for cat in CATEGORIES:
        L += [f"**{CAT_DE[cat]}**", ""]
        L += _table(["Gericht"] + [str(y) for y in c.years],
                    [[r["dish"]] + [_pct(r["by_year"][str(y)], 1) for y in c.years]
                     for r in stats["trends"]["share_by_year"][cat][:15]])
        L.append("")

    # ---------------------------------------------------------------- 7 players
    L += ["## 7. Spieler", "",
          "Punkte = Neuberechnung der Engine (`tips.points`; identisch mit dem Excel bis auf dokumentierte manuelle "
          "Korrekturen). Nur servierte Tage vor dem Stichtag. „Alles falsch“ = 0 Punkte, „Alles richtig“ = 3 Punkte.", ""]
    L += _table(["Jahr", "Spieler", "Tage", "Punkte", "P./Tag", "Alles falsch", "Alles richtig", "V", "H", "B", "R4-Verstöße",
                 "Abw. Excel"],
                [[r["year"], r["player"], r["days"], _num(r["points"], 1), _num(r["ppd"], 3),
                  f"{r['all_wrong']} ({_pct(r['all_wrong_rate'])})", r["all_right"]]
                 + [_pct(r["acc"][cat]) for cat in CATEGORIES]
                 + [r["r4_violations"], pl["sheet_diff"].get((r["player"], r["year"]), 0)] for r in stats["players"]])
    L.append("")
    L += ["### Lieblingstipps", ""]
    L += _table(["Jahr", "Spieler", "Vorspeise", "Hauptspeise", "Beilage"],
                [[r["year"], r["player"]] + [", ".join(f"{f['dish']} {f['n']}" for f in r["fav"][cat][:3]) for cat in CATEGORIES]
                 for r in stats["players"]])
    L.append("")
    L += ["### Was funktioniert? (alle Spieler, Ebene Einzeltipp)", "",
          "Trefferquote je Kategorie, je nachdem ob der getippte Name zu den 5 bis dahin häufigsten gehörte, "
          "und je nach Arbeitstagen seit dem letzten Servieren des getippten Gerichts (Fisch außerhalb der Fastenzeit "
          f"als Gruppe „Fisch“). Die ersten {WARMUP} servierten Tage sind ausgenommen (noch keine Historie).", ""]
    rows = []
    for cat in CATEGORIES:
        t = pl["tl_top"][cat]
        rows.append([CAT_DE[cat], f"{_pct(t[True][0] / t[True][1] if t[True][1] else None, 1)} (n={t[True][1]})",
                     f"{_pct(t[False][0] / t[False][1] if t[False][1] else None, 1)} (n={t[False][1]})"])
    L += _table(["Kategorie", "Tipp in Top-5", "Tipp außerhalb Top-5"], rows) + [""]
    keys = [f"{a}–{b}" if b < 10_000 else f"> {a - 1}" for a, b in GAP_BINS] + ["nie"]
    rows = []
    for cat in CATEGORIES:
        g = pl["tl_gap"][cat]
        rows.append([CAT_DE[cat]] + [f"{_pct(g[k][0] / g[k][1], 1)} ({g[k][1]})" if k in g and g[k][1] else "–" for k in keys])
    L += _table(["Kategorie"] + [f"{k} AT" if k != "nie" else "nie serviert" for k in keys], rows) + [""]
    for cat in CATEGORIES:
        t = pl["tl_top"][cat]
        if t[True][1] and t[False][1]:
            a, b = t[True][0] / t[True][1], t[False][0] / t[False][1]
            L.append(f"- {CAT_DE[cat]}: Top-5-Tipps treffen {_pct(a, 1)} vs {_pct(b, 1)} "
                     f"({'besser' if a > b else 'schlechter'}, Faktor {_num(a / b if b else None, 2)}).")
    L.append("")
    L.append(f"→ Tipps auf Gerichte, die erst vor 1–5 Arbeitstagen serviert wurden, treffen bei der Vorspeise nur "
             f"{_pct(tl_recent['vorspeise'][0], 1)} (n={tl_recent['vorspeise'][1]}) gegenüber {_pct(tl_recent['vorspeise'][2], 1)} "
             f"sonst; Hauptspeise {_pct(tl_recent['hauptspeise'][0], 1)} vs {_pct(tl_recent['hauptspeise'][2], 1)}; "
             f"Beilage {_pct(tl_recent['beilage'][0], 1)} vs {_pct(tl_recent['beilage'][2], 1)}.")
    L.append("")
    corr = pl["corr"]
    L += [f"### Strategie-Kennzahlen je Spieler und Jahr", "",
          "Top-5-Anteil = Anteil der Tipps auf die 5 bis dahin häufigsten Gerichte; Vielfalt = mittlere Entropie der "
          f"eigenen Tipps (bit); kürzlich = Anteil der Tipps auf Gerichte der letzten {RECENT_WD} Arbeitstage.", ""]
    L += _table(["Jahr", "Spieler", "P./Tag", "Rang", "Top-5-Anteil", "Vielfalt", "kürzlich"],
                [[r["year"], r["player"], _num(r["ppd"], 3), pl["per_py"][(r["player"], r["year"])].get("rank", ""),
                  _pct(pl["per_py"][(r["player"], r["year"])]["top5"]), _num(pl["per_py"][(r["player"], r["year"])]["entropy"], 2),
                  _pct(pl["per_py"][(r["player"], r["year"])]["recent"])] for r in stats["players"]])
    L += ["", f"Korrelation mit Punkten/Tag über {pl['n_big']} Spieler-Jahre mit ≥ 100 Tagen (sehr kleine Stichprobe, nur Hinweis): "
          f"Top-5-Anteil r={_num(corr['top5'], 2)}, Vielfalt r={_num(corr['entropy'], 2)}, kürzlich r={_num(corr['recent'], 2)}, "
          f"V-Trefferquote r={_num(corr['acc_v'], 2)}. Die Vorspeise zählt doppelt so viel wie H oder B – wer bei der "
          f"Vorspeise besser trifft, gewinnt.", ""]
    L += ["### Notizen je Spieler", ""]
    L += [f"- **{r['player']} {r['year']}**: {r['strategy_note_de']}" for r in stats["players"]] + [""]

    # ---------------------------------------------------------------- method
    L += ["## Methodik", "",
          "- Datenbasis: `data/menus.csv` (Status `served`), `data/tips.csv`; Namen kanonisch nach `data/aliases.json` "
          "(siehe `reports/alias_candidates.md`).",
          "- Häufigkeiten, Abstände, Wochentage, Paare, Saison: erste angesagte Option. Neu/verschwunden: alle Optionen.",
          "- Arbeitstage = alle Spieltage (serviert/unbekannt/offen) ohne freie Tage; Saisonpausen zählen nicht.",
          "- p-Werte: exakter Binomialtest (einseitig, außer Sommer/Winter), ohne Korrektur für Mehrfachtests – "
          "kleine p-Werte bei vielen Tests sind Hinweise, keine Beweise.",
          "- Spieler: nur Tipps vor dem Stichtag (Regel 6), Punkte aus der Engine-Neuberechnung.", ""]
    return "\n".join(L) + "\n"


def _halflife_sentence(tr: dict, lang: str) -> str:
    best = {}
    for cat in CATEGORIES:
        hl = {k: v for k, v in tr["halflife"][cat].items() if v is not None}
        if hl:
            best[cat] = min(hl, key=hl.get)
    if not best:
        return ""
    fmt = lambda k: ("∞" if k == "inf" else f"{k}")
    if lang == "it":
        return ("Pesatura per recenza (emivita migliore in giorni, log-loss): " +
                ", ".join(f"{CAT_IT[c]} {fmt(k)}" for c, k in best.items()) + ".")
    return ("Aktualitätsgewichtung: beste Halbwertszeit (Log-Loss, Tage) – " +
            ", ".join(f"{CAT_DE[c]} {fmt(k)}" for c, k in best.items()) + ".")


# ======================================================================== run
def raw_counts(ds: Dataset) -> dict[str, Counter]:
    """Raw cell strings of served menus + all tips, per category (for the alias report)."""
    out = {cat: Counter() for cat in CATEGORIES}
    for m in ds.served:
        for cat, raw in zip(CATEGORIES, m.raw):
            if raw:
                out[cat][raw] += 1
    for t in ds.tips:
        for cat, raw in zip(CATEGORIES, t.raw):
            if raw:
                out[cat][raw] += 1
    return out


def compute(ds: Dataset, today: dt.date | None = None) -> tuple[dict, dict, _Ctx]:
    today = today or dt.date.today()
    c = _Ctx(ds, today)
    F = {}
    freq, F["freq"] = frequencies(c)
    rep, F["rep"] = repeat_intervals(c)
    refr, F["refr"] = refractory(c)
    wday, F["wday"] = weekday(c)
    phb, pvh, F["pairs"] = pairs(c)
    seas, F["season"] = seasonality(c)
    trd, F["trends"] = trends(c)
    pls, F["players"] = players(c)
    stats = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "n_menus": len(c.served),
        "years": c.years,
        "frequencies": freq,
        "repeat_intervals": rep,
        "refractory": refr,
        "weekday": wday,
        "pairs_hb": phb,
        "pairs_vh": pvh,
        "seasonality": seas,
        "trends": trd,
        "players": pls,
    }
    return stats, F, c


def _write(ds: Dataset, c: _Ctx, stats: dict, F: dict) -> str:
    write_site_json("stats", stats)
    REPORTS.mkdir(parents=True, exist_ok=True)
    md = _report(c, stats, F)
    (REPORTS / "analysis.md").write_text(md, encoding="utf-8")
    write_alias_report(REPORTS / "alias_candidates.md", raw_counts(ds), ds.norm)
    return md


def run(ds: Dataset, today: dt.date | None = None, write: bool = True) -> dict:
    """Compute stats.json; with ``write`` also the two Markdown reports. Returns the stats dict."""
    stats, F, c = compute(ds, today)
    if write:
        _write(ds, c, stats, F)
    return stats


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--today", type=dt.date.fromisoformat)
    ap.add_argument("--no-write", action="store_true", help="nur Kernaussagen ausgeben, nichts schreiben")
    a = ap.parse_args(argv)
    ds = load_dataset()
    today = a.today or dt.date.today()
    stats, F, c = compute(ds, today)
    md = _write(ds, c, stats, F) if not a.no_write else _report(c, stats, F)
    print(md[md.index("## Riassunto"):md.index("## 1.")].strip())
    if not a.no_write:
        print(f"\n-> docs/data/stats.json, reports/analysis.md, reports/alias_candidates.md geschrieben "
              f"({len(c.served)} Menüs, Stichtag {today}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
