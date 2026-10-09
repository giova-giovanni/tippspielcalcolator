"""Prediction models for the daily menu (Vorspeise / Hauptspeise / Beilage).

All models share one *prefix-based* feature pass (:func:`walk`): for a target day ``t`` only the
served menus strictly before ``t`` are used (no leakage), every statistic – decayed frequencies,
the repeat hazard, weekday / season lifts, the "already served this ISO week" factor, the Lent/fish
factor, the rate of brand-new dishes and the Hauptspeise→Beilage pair table – is estimated online
from that prefix.

Labels are *model labels* (``norm.model_label(name, cat, lent_of_target_day)``): outside Lent all
generic fish dishes are grouped into "Fisch" (rule 9.6), inside Lent the exact names are kept,
Scombri is always exact. The primary option of a served menu is the training label; every announced
option counts as "served" for recency/frequency.

Models (common interface :class:`Predictor`):

* ``frequency``  – exponentially decayed frequency (baseline)
* ``heuristic``  – decayed frequency × repeat hazard h(working days since last) × weekday lift ×
  season lift × same-week factor × Lent/fish factor (all learnt from the history, smoothed)
* ``ml``         – sklearn logistic regression on per-(day, dish) rows, normalised per day
* ``ensemble``   – geometric blend of heuristic and ml

Probabilities per category sum to ``1 - p_new`` (``p_new`` = mass of a dish never seen before,
which cannot be tipped by name).
"""
from __future__ import annotations

import bisect
import copy
import datetime as dt
import math
from dataclasses import dataclass, field
from typing import Iterable, Sequence

import numpy as np

from . import CATEGORIES
from .dates import is_lent, week_key

MODEL_NAMES = ("frequency", "heuristic", "ml", "ensemble")
MODEL_LABELS = {
    "frequency": ("Häufigkeit (Basislinie)", "Frequenza (baseline)"),
    "heuristic": ("Heuristik (Bayes)", "Euristica (bayesiana)"),
    "ml": ("Machine Learning (LogReg)", "Machine learning (LogReg)"),
    "ensemble": ("Ensemble (Heuristik + ML)", "Ensemble (euristica + ML)"),
}

# Hyper-parameters. Per-category values are dicts {cat: value}; tune() may overwrite them.
DEFAULT_PARAMS: dict = {
    "half_life": {"vorspeise": 150.0, "hauptspeise": 150.0, "beilage": 100.0},  # working days
    "alpha": {"vorspeise": 0.5, "hauptspeise": 0.5, "beilage": 0.5},            # frequency floor (pseudo-appearances)
    "hazard_mode": {"vorspeise": "abs", "hauptspeise": "abs", "beilage": "abs"}, # abs | rel
    "hazard_kappa": {"vorspeise": 3.0, "hauptspeise": 3.0, "beilage": 3.0},
    "hazard_smooth": {"vorspeise": 0.25, "hauptspeise": 0.25, "beilage": 0.25},
    "weekday_beta": {"vorspeise": 4.0, "hauptspeise": 4.0, "beilage": 4.0},
    "season_beta": {"vorspeise": 12.0, "hauptspeise": 12.0, "beilage": 12.0},    # <=0 → off
    "week_kappa": {"vorspeise": 2.0, "hauptspeise": 2.0, "beilage": 2.0},
    "temperature": {"vorspeise": 1.0, "hauptspeise": 1.0, "beilage": 1.0},
    "fish_kappa": 1.0,
    "family_kappa": 0.0,         # shrinkage of the dish-family factors (<=0 → off; did not help on 2025)
    "new_half_life": 150.0,
    "freq_half_life": 250.0,
    "short_half_life": 15.0,
    "pair_half_life": 250.0,
    "pair_gamma": 1.0,
    "beilage_mix": 0.5,          # weight of Σ_h P(h)·P(b|h) in the Beilage distribution
    "ml_C": 0.3,
    "ml_kind": "lr",             # lr (sklearn LogisticRegression) | clogit (per-day softmax) | hgb
    "ml_refit_every": 5,
    "ml_min_day": 20,
    "ensemble_w": 0.5,           # weight of ml in the geometric blend
    "plan_discount": 1.0,        # weekly planner: weight discount^k of the k-th later day (decision, not model)
}

BREAK_DAYS = 14   # calendar gap counted as a season break (lag + 1 only)
SEASON_OF_MONTH = [0 if m in (12, 1, 2) else 1 if m in (3, 4, 5) else 2 if m in (6, 7, 8) else 3
                   for m in range(1, 13)]
REL_EDGES = np.array([0.15, 0.3, 0.45, 0.6, 0.75, 0.9, 1.05, 1.2, 1.4, 1.6, 1.8, 2.0, 2.5, 3.0, 4.0, 6.0])
N_ABS = 34
N_REL = len(REL_EDGES) + 1
COARSE_LAG = [(1, 2), (3, 4), (5, 5), (6, 9), (10, 10), (11, 14), (15, 15), (16, 19), (20, 20),
              (21, 29), (30, 59), (60, 10**9)]


# Dish families (domain knowledge: meat type / pasta type). Hypothesis: the kitchen avoids the same
# family on consecutive days. On 2024–2025 the effect vanished once the dish-level repeat hazard was
# in the model, so the heuristic factor is off by default (family_kappa = 0); the two family
# indicators stay available as ML features. Keyword rules on the casefolded name, first match wins.
FAMILY_RULES = {
    "vorspeise": [
        ("fishpasta", ["thunfisch", "lachs", "meeres", "scampi", "vongole"]),
        ("tomato", ["arrabbiata", "amatriciana", "putanesca", "puttanesca", "tomat", "ragu", "mammarosa",
                    "salsiccia", "bolognese"]),
        ("creamy", ["käse", "carbonara", "rahm", "pesto", "aglio", "hirten", "gorgonzola", "sahne", "butter"]),
        ("filled", ["lasagne", "cannelloni", "ravioli", "schlutzer", "tortellini", "strudel", "pizza"]),
        ("dumpling", ["knödel", "spatzlen", "gries", "plent", "gnocchi", "schupf", "omelett"]),
        ("rice", ["risotto", "reis"]),
        ("soup", ["suppe", "salat"]),
    ],
    "hauptspeise": [
        ("turkey", ["truthahn", "champignon", "pizzaiola", "zigeuner"]),
        ("chicken", ["hühner", "huhn", "hähnchen", "pollo"]),
        ("beef", ["rind", "gulasch", "chilli", "chili", "ossobuchi", "zwiebelrost", "kalb"]),
        ("pork", ["schwein", "leberkas", "wurst", "kotelett", "sparerips", "cordon", "wiener", "hackbraten",
                  "speck", "kassler"]),
    ],
    "beilage": [
        ("rice", ["reis", "risotto"]),
        ("fried", ["pommes", "kroketten", "wedges", "röst", "brat"]),
        ("oven", ["ofen", "gratin"]),
        ("mash", ["püree", "stampf"]),
        ("boiled", ["salz", "salat"]),
        ("flour", ["spatzlen", "plent", "knödel", "nudel"]),
    ],
}


def family(label: str, cat: str, norm=None) -> str:
    k = label.casefold()
    if cat == "hauptspeise" and norm is not None and norm.is_fish(label):
        return "fish"
    for fam, kws in FAMILY_RULES.get(cat, []):
        if any(kw in k for kw in kws):
            return fam
    return "other:" + k if cat != "hauptspeise" else "other"


def merge_params(params: dict | None) -> dict:
    out = copy.deepcopy(DEFAULT_PARAMS)
    for k, v in (params or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = {**out[k], **v}
        else:
            out[k] = v
    return out


def pcat(params: dict, key: str, cat: str):
    v = params[key]
    return v.get(cat, v.get("default")) if isinstance(v, dict) else v


def chan_key(cat: str, lent: bool) -> tuple[str, bool]:
    return (cat, bool(lent) and cat == "hauptspeise")


CHANNELS = [("vorspeise", False), ("hauptspeise", False), ("hauptspeise", True), ("beilage", False)]


# ------------------------------------------------------------------ calendar
class WorkCalendar:
    """Working-day ordinals. ``days`` = known working days (served / unknown / pending rows).

    ``ord(d)`` only depends on calendar days ``<= d``. Days outside the known list are placed
    after the last known day by counting Mon–Fri non-free days; gaps > BREAK_DAYS calendar days
    (season breaks, holidays missing from the sheet) count as a single working day.
    """

    def __init__(self, days: Iterable[dt.date] = (), free_days: Iterable[dt.date] = ()):
        self.free = set(free_days)
        self.days = sorted({d for d in days if d.weekday() < 5 and d not in self.free})
        self._ord = {}
        o = 0
        prev = None
        for d in self.days:
            o = 0 if prev is None else o + 1   # consecutive known working days
            self._ord[d] = o
            prev = d

    def _busdays(self, a: dt.date, b: dt.date) -> int:
        """Mon–Fri non-free days in (a, b]."""
        if b <= a:
            return 0
        hol = [x for x in self.free if a < x <= b]
        return int(np.busday_count(a + dt.timedelta(days=1), b + dt.timedelta(days=1),
                                   holidays=hol))

    def ord(self, d: dt.date) -> float:
        o = self._ord.get(d)
        if o is not None:
            return float(o)
        k = bisect.bisect_left(self.days, d)
        if k == 0:
            return -float(max(1, self._busdays(d, self.days[0]))) if self.days else 0.0
        last = self.days[k - 1]
        if k < len(self.days):          # between two known days: not a known working day
            return self._ord[last] + 0.5
        if (d - last).days > BREAK_DAYS:
            return float(self._ord[last] + 1)
        return float(self._ord[last] + max(1, self._busdays(last, d)))


# ------------------------------------------------------------------ encoding
@dataclass
class Channel:
    cat: str
    lent: bool
    labels: list[str]
    index: dict[str, int]
    Y: np.ndarray           # (N, L) multi-hot of all announced options
    prim: np.ndarray        # (N,) primary label index or -1
    fish: np.ndarray        # (L,) bool
    fam: np.ndarray         # (L,) family id


class Encoded:
    """Served menus encoded per channel (cat, lent-space)."""

    def __init__(self, menus: Sequence, norm, calendar: WorkCalendar | None = None):
        ms = sorted([m for m in menus if m.status == "served"], key=lambda m: m.date)
        self.menus = ms
        self.norm = norm
        self.dates = [m.date for m in ms]
        self.N = len(ms)
        self.cal = calendar or WorkCalendar(self.dates)
        self.ords = np.array([self.cal.ord(d) for d in self.dates], dtype=float)
        self.wd = np.array([d.weekday() for d in self.dates], dtype=int)
        self.season = np.array([SEASON_OF_MONTH[d.month - 1] for d in self.dates], dtype=int)
        self.weeks = [week_key(d) for d in self.dates]
        self.lent = np.array([is_lent(d) for d in self.dates], dtype=bool)
        self.ch: dict[tuple[str, bool], Channel] = {}
        for cat, lent in CHANNELS:
            labels: list[str] = []
            index: dict[str, int] = {}
            rows = []
            for m in ms:
                labs = []
                for o in m.options.get(cat, []):
                    lab = norm.model_label(o, cat, lent)
                    if lab not in labs:
                        labs.append(lab)
                    if lab not in index:
                        index[lab] = len(labels)
                        labels.append(lab)
                rows.append(labs)
            L = len(labels)
            Y = np.zeros((self.N, L), dtype=float)
            prim = np.full(self.N, -1, dtype=int)
            for j, labs in enumerate(rows):
                for k, lab in enumerate(labs):
                    Y[j, index[lab]] = 1.0
                    if k == 0:
                        prim[j] = index[lab]
            # fish handling (rule 9.6 / Lent) only concerns the Hauptspeise
            fish = np.array([cat == "hauptspeise" and norm.is_fish(x) for x in labels], dtype=bool)
            fams = [family(x, cat, norm) for x in labels]
            fid = {f: i for i, f in enumerate(sorted(set(fams)))}
            fam = np.array([fid[f] for f in fams], dtype=int)
            self.ch[(cat, lent)] = Channel(cat, lent, labels, index, Y[:, :L], prim, fish, fam)

    def prefix_len(self, day: dt.date) -> int:
        return bisect.bisect_left(self.dates, day)


# ------------------------------------------------------------------ features
@dataclass
class ChanFeat:
    labels: list[str]          # candidate labels (seen in prefix)
    idx: np.ndarray            # their indices in the channel
    p_heur: np.ndarray         # heuristic probabilities (sum = 1 - p_new)
    p_freq: np.ndarray         # frequency-baseline probabilities
    p_new: float
    X: np.ndarray              # ML features
    lag: np.ndarray            # working days since last appearance
    cnt: np.ndarray
    last_date: list
    factors: dict              # name -> array (for explanations)
    week_factor: float
    fish: np.ndarray


@dataclass
class DayFeatures:
    day: dt.date
    n: int
    lent: bool
    chans: dict                # cat -> ChanFeat
    pair: dict                 # {"h_labels","b_labels","P": (Lh,Lb) P(b|h)} over candidate labels
    mix_b: np.ndarray | None = None   # Σ_h p_heur(h) P(b|h) over B candidates


FEATURE_NAMES = (["log_base", "log_base_short", "log1p_cnt", "log_lagfac", "log_wdfac", "log_sfac",
                  "in_week", "fish", "fish_lent", "fish_fri", "rel_lag", "rare", "log_heur", "log_mix_b",
                  "fam_prev", "fam_week"]
                 + [f"lag_{a}_{b}" for a, b in COARSE_LAG])


def _abs_bucket(lag: np.ndarray) -> np.ndarray:
    lag = np.maximum(lag, 1)
    return np.where(lag <= 30, lag - 1,
                    np.where(lag <= 40, 30, np.where(lag <= 60, 31, np.where(lag <= 100, 32, 33)))).astype(int)


def _rel_bucket(u: np.ndarray) -> np.ndarray:
    return np.searchsorted(REL_EDGES, u, side="right").astype(int)


def _smooth(v: np.ndarray, s: float, n_lin: int) -> np.ndarray:
    if s <= 0:
        return v
    out = v.copy()
    a = v[:n_lin]
    sm = a.copy()
    sm[1:n_lin - 1] = (1 - 2 * s) * a[1:n_lin - 1] + s * a[:n_lin - 2] + s * a[2:n_lin]
    out[:n_lin] = sm
    return out


class _ChanState:
    """Online statistics of one channel over a growing prefix."""

    def __init__(self, ch: Channel, params: dict):
        cat = ch.cat
        self.ch = ch
        L = ch.Y.shape[1]
        self.L = L
        self.hls = {
            "main": float(pcat(params, "half_life", cat)),
            "short": float(params["short_half_life"]),
            "freq": float(params["freq_half_life"]),
        }
        self.lam = {k: (math.log(2) / v if v and v > 0 else 0.0) for k, v in self.hls.items()}
        self.S = {k: np.zeros(L) for k in self.hls}
        self.ord_ref = None
        self.cnt = np.zeros(L)
        self.last = np.full(L, -1e9)
        self.first = np.full(L, np.nan)
        self.last_date: list = [None] * L
        self.wdc = np.zeros((L, 5))
        self.tot_wd = np.zeros(5)
        self.sc = np.zeros((L, 4))
        self.tot_s = np.zeros(4)
        self.mode = pcat(params, "hazard_mode", cat)
        nb = N_ABS if self.mode == "abs" else N_REL
        self.hz_hit = np.zeros(nb)
        self.hz_exp = np.zeros(nb)
        self.wk_hit = 0.0
        self.wk_exp = 0.0
        self.fish_hit = np.zeros(2)
        self.fish_exp = np.zeros(2)
        self.new_dec = 0.0
        self.day_dec = 0.0
        self.ord_new = None
        self.lam_new = math.log(2) / float(params["new_half_life"])
        self.alpha = float(pcat(params, "alpha", cat))
        self.kappa = float(pcat(params, "hazard_kappa", cat))
        self.hsmooth = float(pcat(params, "hazard_smooth", cat))
        self.beta_w = float(pcat(params, "weekday_beta", cat))
        self.beta_s = float(pcat(params, "season_beta", cat))
        self.kappa_w = float(pcat(params, "week_kappa", cat))
        self.kappa_f = float(params["fish_kappa"])
        self.temp = float(pcat(params, "temperature", cat))
        self.n_obs = 0
        self.week_members: dict = {}   # week key -> set of label idx seen in that week
        self.recent: list = []         # [(ord, week key, set of family ids)] of the last menus
        self.fp_hit = 0.0
        self.fp_exp = 0.0
        self.fw_hit = 0.0
        self.fw_exp = 0.0
        self.kappa_fam = float(params.get("family_kappa", 3.0))

    # ---- quantities at a target (ord t, weekday, season, week, lent)
    def decayed(self, key: str, t: float) -> np.ndarray:
        if self.ord_ref is None:
            return self.S[key]
        return self.S[key] * math.exp(-self.lam[key] * (t - self.ord_ref))

    def p_new(self) -> float:
        a, prior = 1.0, 0.06
        return float((self.new_dec + a * prior) / (self.day_dec + a))

    def hazard(self) -> np.ndarray:
        nl = 30 if self.mode == "abs" else N_REL
        hit = _smooth(self.hz_hit, self.hsmooth, nl)
        exp = _smooth(self.hz_exp, self.hsmooth, nl)
        return (hit + self.kappa) / (exp + self.kappa)

    def week_factor(self) -> float:
        return float((self.wk_hit + self.kappa_w * 0.5) / (self.wk_exp + self.kappa_w))

    def family_factors(self) -> tuple[float, float]:
        k = self.kappa_fam
        if k <= 0:
            return 1.0, 1.0
        return (float((self.fp_hit + k) / (self.fp_exp + k)), float((self.fw_hit + k) / (self.fw_exp + k)))

    def family_context(self, t: float, wk) -> tuple[set, set]:
        prev, week = set(), set()
        for o, w, fs in self.recent:
            if abs(t - 1 - o) < 1e-9:
                prev |= fs
            elif w == wk and o < t:
                week |= fs
        return prev, week - prev

    def fish_factor(self, lent: bool) -> float:
        k = int(lent)
        return float((self.fish_hit[k] + self.kappa_f) / (self.fish_exp[k] + self.kappa_f))

    def evaluate(self, t: float, wd: int, season: int, wk, lent: bool, full: bool = True):
        """Return dict of arrays over the seen labels."""
        seen = np.flatnonzero(self.cnt > 0)
        if seen.size == 0:
            return None
        D = self.decayed("main", t)[seen]
        base = D + self.alpha
        base = base / base.sum()
        lag = t - self.last[seen]
        lag = np.maximum(np.round(lag), 1.0)
        if self.mode == "abs":
            b = _abs_bucket(lag.astype(int))
            relu = None
        else:
            span = t - self.first[seen]
            gbar = (span + 20.0) / (self.cnt[seen] + 1.0)
            relu = lag / gbar
            b = _rel_bucket(relu)
        hz = self.hazard()
        lagfac = hz[b]
        # weekday lift (fish pooled)
        tot = self.tot_wd.sum()
        q = (self.tot_wd[wd] + 1.0) / (tot + 5.0)
        wdc = self.wdc[seen, wd].copy()
        cnt = self.cnt[seen].copy()
        fish = self.ch.fish[seen]
        if fish.any():
            fmask = self.ch.fish
            wdc[fish] = self.wdc[fmask, wd].sum()
            cnt_f = cnt.copy()
            cnt_f[fish] = self.cnt[fmask].sum()
        else:
            cnt_f = cnt
        if self.beta_w > 0:
            wdfac = ((wdc + self.beta_w * q) / (cnt_f + self.beta_w)) / q
        else:
            wdfac = np.ones(seen.size)
        if self.beta_s > 0:
            tots = self.tot_s.sum()
            qs = (self.tot_s[season] + 1.0) / (tots + 4.0)
            sc = self.sc[seen, season]
            sfac = ((sc + self.beta_s * qs) / (cnt + self.beta_s)) / qs
        else:
            sfac = np.ones(seen.size)
        members = self.week_members.get(wk)
        in_week = np.zeros(seen.size)
        if members:
            in_week = np.isin(seen, list(members)).astype(float)
        wf = self.week_factor()
        weekfac = np.where(in_week > 0, wf, 1.0)
        fishfac = np.where(fish, self.fish_factor(lent), 1.0)
        prev_f, week_f = self.family_context(t, wk)
        fam = self.ch.fam[seen]
        fam_prev = np.isin(fam, list(prev_f)).astype(float) if prev_f else np.zeros(seen.size)
        fam_week = np.isin(fam, list(week_f)).astype(float) if week_f else np.zeros(seen.size)
        ffp, ffw = self.family_factors()
        famfac = np.where(fam_prev > 0, ffp, 1.0) * np.where(fam_week > 0, ffw, 1.0)
        score = base * lagfac * wdfac * sfac * weekfac * fishfac * famfac
        if self.temp != 1.0:
            score = score ** self.temp
        pn = self.p_new()
        p_heur = (1 - pn) * score / score.sum()
        out = {"seen": seen, "base": base, "lag": lag, "bucket": b, "lagfac": lagfac, "wdfac": wdfac,
               "sfac": sfac, "in_week": in_week, "weekfac": weekfac, "fishfac": fishfac,
               "p_heur": p_heur, "p_new": pn, "fish": fish, "week_factor": wf, "relu": relu,
               "fam_prev": fam_prev, "fam_week": fam_week, "famfac": famfac}
        if full:
            Df = self.decayed("freq", t)[seen] + self.alpha
            out["p_freq"] = (1 - pn) * Df / Df.sum()
            Ds = self.decayed("short", t)[seen] + 0.05
            out["base_short"] = Ds / Ds.sum()
            out["cnt"] = cnt
            if relu is None:
                span = t - self.first[seen]
                gbar = (span + 20.0) / (self.cnt[seen] + 1.0)
                out["relu"] = lag / gbar
        return out

    # ---- learning step: observe menu j (stats computed *before* adding it)
    def observe(self, j: int, t: float, wd: int, season: int, wk, lent: bool, date):
        ch = self.ch
        y = ch.Y[j]
        p = int(ch.prim[j])
        if p >= 0:
            ev = self.evaluate(t, wd, season, wk, lent, full=False)
            if ev is not None:
                seen = ev["seen"]
                pn = ev["p_new"]
                e = ev["base"] * (1 - pn)
                np.add.at(self.hz_exp, ev["bucket"], e)
                pos = np.flatnonzero(seen == p)
                if pos.size:
                    self.hz_hit[ev["bucket"][pos[0]]] += 1.0
                # week factor: expected under base*hazard*weekday (normalised)
                p0 = ev["base"] * ev["lagfac"] * ev["wdfac"] * ev["sfac"]
                p0 = (1 - pn) * p0 / p0.sum()
                inw = ev["in_week"] > 0
                if inw.any():
                    self.wk_exp += float(p0[inw].sum())
                    if pos.size and inw[pos[0]]:
                        self.wk_hit += 1.0
                fp, fw = ev["fam_prev"] > 0, ev["fam_week"] > 0
                pfam = ch.fam[p]
                if fp.any():
                    self.fp_exp += float(p0[fp].sum())
                    self.fp_hit += float(pfam in set(ch.fam[seen[fp]].tolist()))
                if fw.any():
                    self.fw_exp += float(p0[fw].sum())
                    self.fw_hit += float(pfam in set(ch.fam[seen[fw]].tolist()))
                fish = ev["fish"]
                if fish.any():
                    self.fish_exp[int(lent)] += float(p0[fish].sum())
                if ch.fish[p]:
                    self.fish_hit[int(lent)] += 1.0
            # new-dish rate
            dec = math.exp(-self.lam_new * (t - self.ord_new)) if self.ord_new is not None else 1.0
            self.new_dec = self.new_dec * dec + (1.0 if self.cnt[p] == 0 else 0.0)
            self.day_dec = self.day_dec * dec + 1.0
            self.ord_new = t
            self.tot_wd[wd] += 1
            self.tot_s[season] += 1
            self.n_obs += 1
        # add the menu
        for k in self.S:
            if self.ord_ref is not None:
                self.S[k] *= math.exp(-self.lam[k] * (t - self.ord_ref))
            self.S[k] += y
        self.ord_ref = t
        nz = np.flatnonzero(y)
        self.cnt[nz] += 1
        self.last[nz] = t
        newfirst = nz[np.isnan(self.first[nz])]
        self.first[newfirst] = t
        for i in nz:
            self.last_date[i] = date
        self.wdc[nz, wd] += 1
        self.sc[nz, season] += 1
        if nz.size:
            self.week_members.setdefault(wk, set()).update(int(i) for i in nz)
            self.recent.append((t, wk, {int(ch.fam[p])} if p >= 0 else set()))
            self.recent = self.recent[-6:]


class _PairState:
    """Decayed H→B pair counts for one H channel."""

    def __init__(self, ch_h: Channel, ch_b: Channel, params: dict):
        self.h = ch_h
        self.b = ch_b
        self.M = np.zeros((ch_h.Y.shape[1], ch_b.Y.shape[1]))
        self.lam = math.log(2) / float(params["pair_half_life"])
        self.ord_ref = None
        self.gamma = float(params["pair_gamma"])

    def observe(self, j: int, t: float):
        if self.ord_ref is not None:
            self.M *= math.exp(-self.lam * (t - self.ord_ref))
        self.ord_ref = t
        ph, pb = int(self.h.prim[j]), int(self.b.prim[j])
        if ph >= 0 and pb >= 0:
            self.M[ph, pb] += 1.0

    def conditional(self, h_idx: np.ndarray, b_idx: np.ndarray, pb_marg: np.ndarray) -> np.ndarray:
        """P(b | h) over candidate labels (rows sum to 1 over the B candidates)."""
        M = self.M[np.ix_(h_idx, b_idx)]
        pm = pb_marg / max(pb_marg.sum(), 1e-12)
        P = (M + self.gamma * pm[None, :]) / (M.sum(axis=1, keepdims=True) + self.gamma)
        return P / P.sum(axis=1, keepdims=True)


def _ml_matrix(ev: dict, cat: str, wd: int, lent: bool, mix_b: np.ndarray | None) -> np.ndarray:
    n = ev["seen"].size
    lag = ev["lag"]
    cols = [
        np.log(ev["base"]),
        np.log(ev["base_short"]),
        np.log1p(ev["cnt"]),
        np.log(ev["lagfac"]),
        np.log(ev["wdfac"]),
        np.log(ev["sfac"]),
        ev["in_week"],
        ev["fish"].astype(float),
        ev["fish"].astype(float) * float(lent),
        ev["fish"].astype(float) * float(wd == 4),
        np.clip(ev["relu"], 0, 4),
        (ev["cnt"] <= 1).astype(float),
        np.log(np.maximum(ev["p_heur"], 1e-9)),
        np.log(np.maximum(mix_b, 1e-9)) if mix_b is not None else np.zeros(n),
        ev["fam_prev"],
        ev["fam_week"],
    ]
    for a, b in COARSE_LAG:
        cols.append(((lag >= a) & (lag <= b)).astype(float))
    return np.column_stack(cols)


def walk(enc: Encoded, targets: Sequence[tuple[dt.date, int]], params: dict,
         with_ml: bool = True, keep_state: dict | None = None) -> dict[tuple[dt.date, int], DayFeatures]:
    """One online pass over ``enc``; returns features for every ``(day, prefix_len)`` target.

    The features of a target with prefix ``n`` use menus ``0..n-1`` only. ``keep_state`` (a dict)
    receives the final online states (prefix = all of ``enc``) for later targets.
    """
    params = merge_params(params)
    states = {key: _ChanState(enc.ch[key], params) for key in CHANNELS}
    pairs = {lent: _PairState(enc.ch[("hauptspeise", lent)], enc.ch[("beilage", False)], params)
             for lent in (False, True)}
    by_n: dict[int, list[dt.date]] = {}
    for day, n in targets:
        by_n.setdefault(n, []).append(day)
    out: dict[tuple[dt.date, int], DayFeatures] = {}
    for j in range(enc.N + 1):
        for day in by_n.get(j, []):
            out[(day, j)] = _target_features(enc, states, pairs, day, j, params, with_ml)
        if j == enc.N:
            break
        t, wd, s, wk, lent, date = (enc.ords[j], int(enc.wd[j]), int(enc.season[j]), enc.weeks[j],
                                    bool(enc.lent[j]), enc.dates[j])
        for key, st in states.items():
            st.observe(j, t, wd, s, wk, lent, date)
        for p in pairs.values():
            p.observe(j, t)
    if keep_state is not None:
        keep_state.update({"states": states, "pairs": pairs, "params": params})
    return out


def _target_features(enc, states, pairs, day, n, params, with_ml) -> DayFeatures:
    t = enc.cal.ord(day)
    wd = min(day.weekday(), 4)
    s = SEASON_OF_MONTH[day.month - 1]
    wk = week_key(day)
    lent = is_lent(day)
    chans = {}
    evs = {}
    for cat in CATEGORIES:
        key = chan_key(cat, lent)
        st = states[key]
        ev = st.evaluate(t, wd, s, wk, lent, full=True)
        evs[cat] = ev
    # pair table and Beilage mixture
    pair = {}
    mix_b = None
    evh, evb = evs["hauptspeise"], evs["beilage"]
    if evh is not None and evb is not None:
        ps = pairs[lent]
        P = ps.conditional(evh["seen"], evb["seen"], evb["base"])
        pair = {"h_idx": evh["seen"], "b_idx": evb["seen"], "P": P}
        mix_b = evh["p_heur"] @ P + evh["p_new"] * evb["base"]
    for cat in CATEGORIES:
        ev = evs[cat]
        key = chan_key(cat, lent)
        ch = enc.ch[key]
        st = states[key]
        if ev is None:
            chans[cat] = None
            continue
        X = _ml_matrix(ev, cat, wd, lent, mix_b if cat == "beilage" else None) if with_ml else None
        chans[cat] = ChanFeat(
            labels=[ch.labels[i] for i in ev["seen"]], idx=ev["seen"], p_heur=ev["p_heur"],
            p_freq=ev["p_freq"], p_new=ev["p_new"], X=X, lag=ev["lag"], cnt=ev["cnt"],
            last_date=[st.last_date[i] for i in ev["seen"]],
            factors={"base": ev["base"], "lagfac": ev["lagfac"], "wdfac": ev["wdfac"], "sfac": ev["sfac"],
                     "weekfac": ev["weekfac"], "fishfac": ev["fishfac"], "in_week": ev["in_week"],
                     "famfac": ev["famfac"]},
            week_factor=ev["week_factor"], fish=ev["fish"])
    if pair:
        pair["h_labels"] = chans["hauptspeise"].labels
        pair["b_labels"] = chans["beilage"].labels
    return DayFeatures(day, n, lent, chans, pair, mix_b)


# ------------------------------------------------------------------ models
def _mix_beilage(df: DayFeatures, p_h: np.ndarray, p_b: np.ndarray, lam: float) -> np.ndarray:
    if lam <= 0 or not df.pair or df.chans.get("beilage") is None:
        return p_b
    cb = df.chans["beilage"]
    ch = df.chans["hauptspeise"]
    mix = p_h @ df.pair["P"] + ch.p_new * (p_b / max(p_b.sum(), 1e-12)) * (1 - cb.p_new)
    # keep total mass 1 - p_new(B)
    mix = mix / max(mix.sum(), 1e-12) * (1 - cb.p_new)
    return (1 - lam) * p_b + lam * mix


class _CLogit:
    def __init__(self, beta: np.ndarray):
        self.coef_ = beta[None, :]
        self.beta = beta

    def decision_function(self, X: np.ndarray) -> np.ndarray:
        return X @ self.beta


def _fit_clogit(X: np.ndarray, y: np.ndarray, sizes: np.ndarray, C: float) -> np.ndarray:
    """Conditional (per-day softmax) logit with L2 penalty 1/(2C)·|β|², fitted with L-BFGS."""
    from scipy.optimize import minimize

    starts = np.concatenate([[0], np.cumsum(sizes)[:-1]])
    g = np.repeat(np.arange(len(sizes)), sizes)
    D = float(len(sizes))
    lam = 1.0 / (C * D) if C > 0 else 0.0
    ypos = np.flatnonzero(y > 0)
    Xy = X[ypos].sum(axis=0)

    def f(beta):
        z = X @ beta
        zmax = np.maximum.reduceat(z, starts)
        e = np.exp(z - zmax[g])
        s = np.add.reduceat(e, starts)
        lse = np.log(s) + zmax
        loss = (lse.sum() - z[ypos].sum()) / D + 0.5 * lam * beta @ beta
        p = e / s[g]
        grad = (X.T @ p - Xy) / D + lam * beta
        return loss, grad

    res = minimize(f, np.zeros(X.shape[1]), jac=True, method="L-BFGS-B", options={"maxiter": 300})
    return res.x


class MLScorer:
    """Logistic regression (or HistGradientBoosting) on per-(day, dish) rows, per category."""

    def __init__(self, params: dict):
        self.params = params
        self.models: dict = {}

    def fit(self, days: Sequence[DayFeatures], labels: Sequence[dict]) -> "MLScorer":
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler

        kind = self.params.get("ml_kind", "lr")
        for cat in CATEGORIES:
            Xs, ys = [], []
            for df, lab in zip(days, labels):
                cf = df.chans.get(cat)
                y = lab.get(cat)
                if cf is None or cf.X is None or not y or y not in cf.labels:
                    continue
                Xs.append(cf.X)
                v = np.zeros(len(cf.labels))
                v[cf.labels.index(y)] = 1.0
                ys.append(v)
            if len(Xs) < 10:
                self.models[cat] = None
                continue
            X = np.vstack(Xs)
            y = np.concatenate(ys)
            if kind == "clogit":
                sc = StandardScaler().fit(X)
                sizes = np.array([len(v) for v in ys])
                beta = _fit_clogit(sc.transform(X), y, sizes, float(self.params.get("ml_C", 0.3)))
                self.models[cat] = (sc, _CLogit(beta))
                continue
            if kind == "hgb":
                from sklearn.ensemble import HistGradientBoostingClassifier
                m = HistGradientBoostingClassifier(max_iter=120, learning_rate=0.05, max_leaf_nodes=15,
                                                   min_samples_leaf=40, l2_regularization=1.0, random_state=0)
                m.fit(X, y)
                self.models[cat] = (None, m)
            else:
                sc = StandardScaler().fit(X)
                m = LogisticRegression(C=float(self.params.get("ml_C", 0.3)), max_iter=500)
                m.fit(sc.transform(X), y)
                self.models[cat] = (sc, m)
        return self

    def probs(self, df: DayFeatures, cat: str) -> np.ndarray | None:
        cf = df.chans.get(cat)
        mm = self.models.get(cat)
        if cf is None or mm is None or cf.X is None:
            return None
        sc, m = mm
        X = cf.X if sc is None else sc.transform(cf.X)
        if sc is None:
            z = m.predict_proba(X)[:, 1]
            z = np.maximum(z, 1e-9)
        else:
            z = np.exp(np.clip(m.decision_function(X), -30, 30))
        return (1 - cf.p_new) * z / z.sum()


def probs_from_features(name: str, df: DayFeatures, params: dict, ml: MLScorer | None = None) -> dict:
    """{cat: np.ndarray over df.chans[cat].labels} for the given model."""
    params = merge_params(params)
    out: dict = {}
    for cat in CATEGORIES:
        cf = df.chans.get(cat)
        if cf is None:
            out[cat] = None
            continue
        if name == "frequency":
            out[cat] = cf.p_freq
        elif name == "heuristic":
            out[cat] = cf.p_heur
        elif name in ("ml", "ensemble"):
            pm = ml.probs(df, cat) if ml is not None else None
            if pm is None:
                pm = cf.p_heur
            if name == "ml":
                out[cat] = pm
            else:
                w = float(params["ensemble_w"])
                g = np.exp((1 - w) * np.log(np.maximum(cf.p_heur, 1e-12)) + w * np.log(np.maximum(pm, 1e-12)))
                out[cat] = (1 - cf.p_new) * g / g.sum()
        else:
            raise ValueError(f"unknown model {name}")
    if name in ("heuristic", "ensemble") and out.get("beilage") is not None and out.get("hauptspeise") is not None:
        out["beilage"] = _mix_beilage(df, out["hauptspeise"], out["beilage"], float(params["beilage_mix"]))
    return out


def as_dict(df: DayFeatures, arrs: dict) -> dict[str, dict[str, float]]:
    res = {}
    for cat in CATEGORIES:
        cf = df.chans.get(cat)
        a = arrs.get(cat)
        if cf is None or a is None:
            res[cat] = {}
            continue
        res[cat] = {lab: float(p) for lab, p in zip(cf.labels, a)}
    return res


def week_correction(prob_list: Sequence[dict], rho: dict) -> list[dict]:
    """Forecasts for later days of the week, accounting for earlier (still unknown) days.

    ``prob_list[k][cat]`` = {label: p} for the k-th remaining day (all computed from the same history).
    A dish served on an earlier day of the week is much less likely again (factor ``rho[cat]``);
    p_k(x) ∝ p'_k(x) · Π_{i<k} (1 - (1-rho)·p_i(x)), renormalised to the same total mass.
    """
    out = [dict(prob_list[0])] if prob_list else []
    for k in range(1, len(prob_list)):
        day = {}
        for cat in CATEGORIES:
            pk = prob_list[k].get(cat) or {}
            mass = sum(pk.values())
            r = float(rho.get(cat, 1.0))
            adj = {}
            for lab, p in pk.items():
                f = 1.0
                for i in range(k):
                    f *= 1 - (1 - r) * out[i].get(cat, {}).get(lab, 0.0)
                adj[lab] = p * max(f, 0.0)
            s = sum(adj.values())
            day[cat] = {lab: v * mass / s for lab, v in adj.items()} if s > 0 else pk
        out.append(day)
    return out


def pair_dict(df: DayFeatures, p_h: dict | None = None, top_h: int = 8, top_b: int = 6) -> dict:
    """{H: {B: P(B|H)}} for the top Hauptspeise candidates."""
    if not df.pair:
        return {}
    P = df.pair["P"]
    hl, bl = df.pair["h_labels"], df.pair["b_labels"]
    order = range(len(hl))
    if p_h:
        order = sorted(range(len(hl)), key=lambda i: -p_h.get(hl[i], 0.0))[:top_h]
    res = {}
    for i in order:
        row = P[i]
        top = np.argsort(-row)[:top_b]
        res[hl[i]] = {bl[k]: float(row[k]) for k in top}
    return res


def full_pair_lookup(df: DayFeatures) -> dict:
    """(H label, B label) -> P(B|H) for all candidates."""
    if not df.pair:
        return {}
    P = df.pair["P"]
    hl, bl = df.pair["h_labels"], df.pair["b_labels"]
    bi = {b: k for k, b in enumerate(bl)}
    hi = {h: k for k, h in enumerate(hl)}
    return {"P": P, "h": hi, "b": bi}


# ------------------------------------------------------------------ public interface
def menu_labels(menu, norm, lent: bool | None = None) -> dict[str, list[str]]:
    """Model labels of a served menu (all options) for the target-day Lent state."""
    lent = menu.lent if lent is None else lent
    out = {}
    for cat in CATEGORIES:
        labs = []
        for o in menu.options.get(cat, []):
            lab = norm.model_label(o, cat, lent)
            if lab not in labs:
                labs.append(lab)
        out[cat] = labs
    return out


class Predictor:
    """Common interface of all models.

    >>> pr = Predictor("heuristic", params, ds.norm, calendar=WorkCalendar(ds.workdays(), ds.free_days))
    >>> pr.fit(history)                     # served menus strictly before the first target day
    >>> pr.predict(day)                     # {cat: {label: p}}   (sum ≤ 1)
    >>> pr.p_beilage_given_haupt(day)       # {H: {B: p}}
    """

    def __init__(self, name: str = "heuristic", params: dict | None = None, norm=None,
                 calendar: WorkCalendar | None = None):
        if name not in MODEL_NAMES:
            raise ValueError(f"unknown model {name!r}")
        self.name = name
        self.params = merge_params(params)
        self.norm = norm
        self.calendar = calendar
        self.enc: Encoded | None = None
        self.ml: MLScorer | None = None
        self._cache: dict = {}
        self._state: dict | None = None
        self.history_end: dt.date | None = None

    def fit(self, history: Sequence) -> "Predictor":
        hist = sorted([m for m in history if m.status == "served"], key=lambda m: m.date)
        cal = self.calendar
        if cal is None:
            cal = WorkCalendar([m.date for m in hist])
        self.enc = Encoded(hist, self.norm, cal)
        self.history_end = hist[-1].date if hist else None
        self._cache = {}
        self._state = None
        self.ml = None
        if self.name in ("ml", "ensemble") and self.enc.N > 0:
            j0 = int(self.params["ml_min_day"])
            tg = [(self.enc.dates[j], j) for j in range(j0, self.enc.N)]
            feats = walk(self.enc, tg, self.params, with_ml=True)
            days, labels = [], []
            for d, j in tg:
                df = feats[(d, j)]
                labs = menu_labels(self.enc.menus[j], self.norm, df.lent)
                days.append(df)
                labels.append({c: (labs[c][0] if labs[c] else None) for c in CATEGORIES})
            self.ml = MLScorer(self.params).fit(days, labels)
        return self

    def features(self, days: Sequence[dt.date]) -> list[DayFeatures]:
        if self.enc is None:
            raise RuntimeError("call fit() first")
        for d in days:
            if self.history_end is not None and d <= self.history_end:
                raise ValueError(f"target {d} is not after the history ({self.history_end})")
        need = [d for d in days if d not in self._cache]
        if need:
            if self._state is None:   # one pass over the whole history, final state kept
                self._state = {}
                walk(self.enc, [], self.params, with_ml=False, keep_state=self._state)
            st = self._state
            for d in need:
                self._cache[d] = _target_features(self.enc, st["states"], st["pairs"], d, self.enc.N,
                                                  st["params"], self.name in ("ml", "ensemble"))
        return [self._cache[d] for d in days]

    def predict_arrays(self, day: dt.date) -> tuple[DayFeatures, dict]:
        df = self.features([day])[0]
        return df, probs_from_features(self.name, df, self.params, self.ml)

    def predict(self, day: dt.date) -> dict[str, dict[str, float]]:
        df, arrs = self.predict_arrays(day)
        return as_dict(df, arrs)

    def predict_week(self, days: Sequence[dt.date]) -> list[dict]:
        """Forecasts for several days (same history) with the same-week correction."""
        probs = [self.predict(d) for d in days]
        return week_correction(probs, self.week_factors(days[0]) if days else {})

    def week_factors(self, day: dt.date) -> dict:
        df = self.features([day])[0]
        return {c: (df.chans[c].week_factor if df.chans.get(c) else 1.0) for c in CATEGORIES}

    def p_new(self, day: dt.date) -> dict:
        df = self.features([day])[0]
        return {c: (df.chans[c].p_new if df.chans.get(c) else 1.0) for c in CATEGORIES}

    def p_beilage_given_haupt(self, day: dt.date, top_h: int | None = None) -> dict:
        df, arrs = self.predict_arrays(day)
        ph = as_dict(df, arrs)["hauptspeise"]
        if top_h is None:
            return pair_dict(df, None, top_b=10**6)
        return pair_dict(df, ph, top_h=top_h)


def predict(day: dt.date, history_menus: Sequence, norm, name: str = "heuristic", params: dict | None = None,
            calendar: WorkCalendar | None = None) -> dict[str, dict[str, float]]:
    """Convenience: train on the menus strictly before ``day`` and predict it."""
    hist = [m for m in history_menus if m.date < day]
    return Predictor(name, params, norm, calendar).fit(hist).predict(day)


def p_beilage_given_haupt(day: dt.date, history_menus: Sequence, norm, params: dict | None = None,
                          calendar: WorkCalendar | None = None) -> dict:
    hist = [m for m in history_menus if m.date < day]
    return Predictor("heuristic", params, norm, calendar).fit(hist).p_beilage_given_haupt(day)


STRATEGY_NAMES = ("week_planner", "greedy")


def load_strategy() -> str:
    """Decision strategy chosen on the validation split (data/model_params.json "strategy")."""
    from .config import MODEL_PARAMS_JSON, load_json

    obj = load_json(MODEL_PARAMS_JSON, None) or {}
    s = obj.get("strategy", "week_planner")
    return s if s in STRATEGY_NAMES else "week_planner"


def load_params() -> tuple[str, dict]:
    """(best model name, params) from data/model_params.json (defaults if missing)."""
    from .config import MODEL_PARAMS_JSON, load_json

    obj = load_json(MODEL_PARAMS_JSON, None) or {}
    name = obj.get("best_model", "heuristic")
    if name not in MODEL_NAMES:
        name = "heuristic"
    return name, merge_params(obj.get("params", {}))
