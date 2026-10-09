"""Daily recommendation (today.json, week.json) and the decision code shared with the backtest.

Decision rule (identical in the backtest):

* model probabilities for the target day and the remaining working days of the ISO week
  (same history; later days get the same-week correction of :func:`engine.model.week_correction`)
* EV = 1·P(V) + 0.5·P(H) + 0.5·P(B) + 1·P(V∧H∧B), P(V∧H∧B) ≈ P(V)·P(H)·P(B|H)
* rule 4 (max 2× per week, never on consecutive working days) w.r.t. MY tips of the week only –
  other players' tips are never used (rule 6)
* weekly planner: receding horizon – today's tip is the first step of the best R4-valid plan
  for the rest of the week (per category, branch & bound; later days weighted ``plan_discount^k``,
  an "other dish" fallback that uses no quota is always allowed); ``greedy`` = best valid tip for
  today only. Which one is used is chosen on the 2025 validation split by expected points
  (data/model_params.json "strategy") – the same choice drives the backtest.
* target day: first working day >= today whose menu is unknown; after today's deadline (config
  "deadline", Europe/Rome) the next working day – possibly in the next ISO week, whose R4 history
  and plan are then used.
"""
from __future__ import annotations

import datetime as dt
import zoneinfo
from dataclasses import dataclass, field
from typing import Mapping, Sequence

from . import CATEGORIES
from .dates import WEEKDAYS_DE_LONG, is_lent, season_end, week_key, week_monday
from .normalize import fold
from .rules import DEFAULT_SCORING, R4

K_TODAY = 10
K_FUTURE = 6
K_TRIPLE = 6


# ------------------------------------------------------------------ decision core
@dataclass
class DayProbs:
    date: dt.date
    probs: dict                       # cat -> {label: p}
    pair: dict | None = None          # {"P": array, "h": {label: i}, "b": {label: k}}  (P(B|H))


@dataclass
class Decision:
    tip: dict                         # cat -> label
    p: dict                           # cat -> p
    p_full: float
    ev: float
    valid: bool
    strategy: str
    plan: list = field(default_factory=list)   # [{date, vorspeise, hauptspeise, beilage, ev}]


def _weights(scoring: Mapping | None) -> tuple[dict, float]:
    sc = {**DEFAULT_SCORING, **(scoring or {})}
    w = {c: float(sc[c]) for c in CATEGORIES}
    bonus = float(sc["full_menu_total"]) - sum(w.values())
    return w, bonus


class _R4Fast:
    """Rule-4 checks on a small set of days with cached adjacency (same semantics as rules.R4)."""

    def __init__(self, r4: R4):
        self.r4 = r4
        self._adj: dict = {}

    def adjacent(self, a: dt.date, b: dt.date) -> bool:
        k = (a, b) if a <= b else (b, a)
        v = self._adj.get(k)
        if v is None:
            v = self.r4.adjacent(a, b)
            self._adj[k] = v
        return v

    def ok(self, used_days: Sequence[dt.date], day: dt.date) -> bool:
        wk = week_key(day)
        n = 0
        for d in used_days:
            if d == day:
                continue
            if week_key(d) == wk:
                n += 1
            if self.adjacent(d, day):
                return False
        return n < self.r4.max_per_week


def _top(probs: Mapping[str, float], k: int) -> list[tuple[str, float]]:
    return sorted(probs.items(), key=lambda kv: (-kv[1], kv[0]))[:k]


def _best_future(days: Sequence[dt.date], cands: Sequence[list], w: Sequence[float], used: dict,
                 chk: _R4Fast, fallback: Sequence[float] | None = None) -> tuple[float, list]:
    """Branch & bound over the remaining days of one category.

    ``cands[i]`` = [(label, p)] sorted by p (top-k of day i); ``w[i]`` = category weight × discount of
    day i; ``fallback[i]`` = p of the best label *outside* the top-k (an "other dish" tip that never
    touches a rule-4 quota). Returns (value, [label | None per day]); None = "other dish".
    """
    m = len(days)
    if m == 0:
        return 0.0, []
    fb = list(fallback) if fallback is not None else [0.0] * m
    maxp = [max(c[0][1] if c else 0.0, fb[i]) for i, c in enumerate(cands)]
    suffix = [0.0] * (m + 1)
    for i in range(m - 1, -1, -1):
        suffix[i] = suffix[i + 1] + w[i] * maxp[i]
    best = [-1.0, [None] * m]
    assign: list = [None] * m

    def rec(i: int, val: float):
        if i == m:
            if val > best[0] + 1e-15:
                best[0] = val
                best[1] = list(assign)
            return
        if val + suffix[i] <= best[0] + 1e-15:
            return
        for lab, p in cands[i]:
            if p < fb[i] - 1e-15 or val + w[i] * p + suffix[i + 1] <= best[0] + 1e-15:
                break   # sorted by p: later candidates cannot improve on the bound / the fallback
            key = fold(lab)
            ud = used.get(key, [])
            if not chk.ok(ud, days[i]):
                continue
            used[key] = ud + [days[i]]
            assign[i] = lab
            rec(i + 1, val + w[i] * p)
            assign[i] = None
            if ud:
                used[key] = ud
            else:
                del used[key]
        # "other dish" on day i (no quota used)
        rec(i + 1, val + w[i] * fb[i])

    rec(0, 0.0)
    return max(best[0], 0.0), best[1]


def _fallback_p(probs: Mapping[str, float], k: int) -> float:
    top = _top(probs, k + 1)
    return top[k][1] if len(top) > k else 0.0


def decide(days: Sequence[DayProbs], history: Mapping[str, Mapping[dt.date, Sequence[str]]], r4: R4 | None,
           scoring: Mapping | None = None, strategy: str = "week_planner",
           k_today: int = K_TODAY, k_future: int = K_FUTURE, discount: float = 1.0) -> Decision:
    """Choose today's tip (``days[0]``) – the decision rule used by recommend AND backtest.

    ``history``: cat -> {date: [canonical options]} of MY tips (other dates). ``strategy``:
    ``week_planner`` | ``greedy`` | ``no_r4`` (upper bound, ignores rule 4).

    Per category the value of a candidate for today is ``w·p_today + Σ_k discount^k · w·p_k(plan)``
    where the plan for the later days of the week is the best rule-4-valid assignment given that
    candidate (``week_planner``; ``discount`` = 0 gives ``greedy``). The triple (V, H, B) maximises
    the sum of the category values + bonus·P(V)·P(H)·P(B|H) of today; the returned ``ev`` is today's
    EV = 1·P(V) + 0.5·P(H) + 0.5·P(B) + 1·P(V∧H∧B).
    """
    w, bonus = _weights(scoring)
    today = days[0]
    future = list(days[1:]) if strategy == "week_planner" and discount > 0 else []
    chk = _R4Fast(r4) if r4 is not None and strategy != "no_r4" else None
    if chk is None:
        future = []
    values: dict = {}
    futures: dict = {}
    for cat in CATEGORIES:
        used: dict = {}
        for d, opts in (history.get(cat) or {}).items():
            if d == today.date:
                continue
            for o in opts:
                used.setdefault(fold(o), []).append(d)
        cands = _top(today.probs.get(cat, {}), k_today)
        fut_days = [x.date for x in future]
        fut_c = [_top(x.probs.get(cat, {}), k_future) for x in future]
        fut_fb = [_fallback_p(x.probs.get(cat, {}), k_future) for x in future]
        fut_w = [w[cat] * discount ** (i + 1) for i in range(len(future))]
        vals = []
        for lab, p in cands:
            key = fold(lab)
            ud = used.get(key, [])
            if chk is not None and not chk.ok(ud, today.date):
                continue
            fval, fplan = 0.0, []
            if future:
                used[key] = ud + [today.date]
                fval, fplan = _best_future(fut_days, fut_c, fut_w, used, chk, fut_fb)
                if ud:
                    used[key] = ud
                else:
                    del used[key]
            vals.append((lab, p, w[cat] * p + fval, fplan))
        if not vals:   # nothing valid among the top-k: widen to all labels
            for lab, p in _top(today.probs.get(cat, {}), 10**6):
                if chk is None or chk.ok(used.get(fold(lab), []), today.date):
                    vals.append((lab, p, w[cat] * p, [None] * len(future)))
                    break
        vals.sort(key=lambda v: (-v[2], -v[1], v[0]))
        values[cat] = vals[:K_TRIPLE]
        futures[cat] = {v[0]: v[3] for v in vals}

    best = None
    pv = {c: today.probs.get(c, {}) for c in CATEGORIES}
    for lv, p_v, val_v, _ in values["vorspeise"] or [("", 0.0, 0.0, [])]:
        for lh, p_h, val_h, _ in values["hauptspeise"] or [("", 0.0, 0.0, [])]:
            for lb, p_b, val_b, _ in values["beilage"] or [("", 0.0, 0.0, [])]:
                pbh = _p_b_given_h(today, lh, lb, p_b)
                pf = p_v * p_h * pbh
                s = val_v + val_h + val_b + bonus * pf
                if best is None or s > best[0] + 1e-15:
                    best = (s, lv, lh, lb, pf)
    _, lv, lh, lb, pf = best
    tip = {"vorspeise": lv, "hauptspeise": lh, "beilage": lb}
    p = {c: float(pv[c].get(tip[c], 0.0)) for c in CATEGORIES}
    ev = sum(w[c] * p[c] for c in CATEGORIES) + bonus * pf
    valid = True
    if r4 is not None:
        for cat in CATEGORIES:
            if tip[cat] and r4.violations(cat, tip[cat], today.date, history.get(cat) or {}):
                valid = False
    plan = [{"date": today.date, **tip, "ev": ev}]
    if future:
        planned = {c: {d: list(o) for d, o in (history.get(c) or {}).items() if d != today.date}
                   for c in CATEGORIES}
        for c in CATEGORIES:
            if tip[c]:
                planned[c][today.date] = [tip[c]]
        rows = []
        for i, fd in enumerate(future):
            row = {"date": fd.date}
            for cat in CATEGORIES:
                fp = futures[cat].get(tip[cat]) or []
                row[cat] = fp[i] if i < len(fp) else None
                if row[cat]:
                    planned[cat][fd.date] = [row[cat]]
            rows.append(row)
        for fd, row in zip(future, rows):
            for cat in CATEGORIES:
                if row[cat] is None and r4 is not None:   # "other dish": best label still allowed
                    row[cat] = next((x for x, _ in _top(fd.probs.get(cat, {}), 10**6)
                                     if not r4.violations(cat, x, fd.date, planned[cat])), None)
                    if row[cat]:
                        planned[cat][fd.date] = [row[cat]]
            row["ev"] = _plan_ev(fd, row, w, bonus)
            plan.append(row)
    return Decision(tip, p, pf, ev, valid, strategy, plan)


def _plan_ev(day: DayProbs, row: Mapping, w: Mapping, bonus: float) -> float:
    pr = {c: (day.probs.get(c, {}).get(row[c], 0.0) if row.get(c) else 0.0) for c in CATEGORIES}
    return sum(w[c] * pr[c] for c in CATEGORIES) + bonus * pr["vorspeise"] * pr["hauptspeise"] * pr["beilage"]


def rollout(days: Sequence[DayProbs], history: Mapping[str, Mapping[dt.date, Sequence[str]]], r4: R4 | None,
            scoring: Mapping | None = None, strategy: str = "greedy", discount: float = 1.0) -> list[dict]:
    """Plan for the whole list of days by applying ``decide`` day after day on the forecasts
    (receding horizon; for ``greedy`` this is what the strategy would do if the forecasts held)."""
    hist = {c: {d: list(o) for d, o in (history.get(c) or {}).items()} for c in CATEGORIES}
    rows = []
    w, bonus = _weights(scoring)
    for i in range(len(days)):
        dec = decide(days[i:], hist, r4, scoring, strategy, discount=discount)
        rows.append({"date": days[i].date, **dec.tip,
                     "ev": dec.ev if i == 0 else _plan_ev(days[i], dec.tip, w, bonus)})
        for c in CATEGORIES:
            if dec.tip[c]:
                hist[c][days[i].date] = [dec.tip[c]]
    return rows


def _p_b_given_h(day: DayProbs, h: str, b: str, p_b: float) -> float:
    pr = day.pair
    if not pr or not h or not b:
        return p_b
    i, k = pr["h"].get(h), pr["b"].get(b)
    if i is None or k is None:
        return p_b
    return float(pr["P"][i, k])


def week_rest(day: dt.date, workdays: Sequence[dt.date], free_days=(), end: dt.date | None = None) -> list[dt.date]:
    """``day`` plus the later working days of its ISO week.

    Uses the known calendar (rows of menus.csv that are not free); for a week without any known
    row Mon–Fri minus free days is assumed. Days after ``end`` (season end) are dropped.
    """
    wk = week_key(day)
    free = set(free_days)
    known = [d for d in workdays if week_key(d) == wk]
    if known:
        days = {d for d in known if d > day}
    else:
        mon = week_monday(day)
        days = {mon + dt.timedelta(days=i) for i in range(5)}
        days = {d for d in days if d > day and d not in free}
    if end is not None:
        days = {d for d in days if d <= end}
    return [day] + sorted(days)


def my_week_history(ds, day: dt.date) -> dict:
    """My (config "me") tips relevant for rule 4 on ``day``: same ISO week + the previous workday."""
    me = ds.me
    out = {}
    lo = week_monday(day) - dt.timedelta(days=7)
    for cat in CATEGORIES:
        h = ds.tip_history(me, cat)
        out[cat] = {d: o for d, o in h.items() if lo <= d < day + dt.timedelta(days=7) and d != day}
    return out


# ------------------------------------------------------------------ run
def _tz(cfg) -> zoneinfo.ZoneInfo:
    return zoneinfo.ZoneInfo(cfg.get("timezone", "Europe/Rome"))


def _deadline_dt(day: dt.date, cfg) -> dt.datetime:
    hh, mm = (int(x) for x in cfg.get("deadline", "12:00").split(":"))
    return dt.datetime(day.year, day.month, day.day, hh, mm, tzinfo=_tz(cfg))


def deadline_passed(day: dt.date, now: dt.datetime | None, cfg) -> bool:
    """Is ``now`` (aware, or naive = local time of the game) at/after the tip deadline of ``day``?"""
    if now is None:
        return False
    if now.tzinfo is None:
        now = now.replace(tzinfo=_tz(cfg))
    return now >= _deadline_dt(day, cfg)


def _target_day(ds, today: dt.date, now: dt.datetime | None = None) -> tuple[dt.date | None, bool]:
    """(target day, season_over).

    Target = first working day >= ``today`` (Mon–Fri, not a known free day, <= season end) whose
    menu is not known yet (no row or status "pending"). If that day is ``today`` and ``now``
    (Europe/Rome) is at/after today's deadline (config "deadline", 12:00), today can no longer be
    tipped → the next such working day. No such day left in the season → (None, True).
    """
    end = season_end(today.year, ds.config.get("season_end_mmdd", "12-23"))

    def first_from(d: dt.date) -> dt.date | None:
        while d <= end:
            if d.weekday() < 5 and d not in ds.free_days:
                m = ds.menus_by_date.get(d)
                if m is None or m.status == "pending":
                    return d
            d += dt.timedelta(days=1)
        return None

    if today > end:
        return None, True
    target = first_from(today)
    if target == today and deadline_passed(today, now, ds.config):
        target = first_from(today + dt.timedelta(days=1))
    return target, target is None


def _reasons(cf, i: int, day: dt.date) -> list[dict]:
    f = cf.factors
    out = []
    lag = int(cf.lag[i])
    if f["in_week"][i] > 0:
        out.append({"de": "diese Woche schon serviert – Wiederholung unwahrscheinlich",
                    "it": "già servito questa settimana – ripetizione improbabile"})
    lf = float(f["lagfac"][i])
    if lf < 0.6:
        out.append({"de": f"erst vor {lag} Arbeitstagen serviert (Sperrfrist-Effekt ×{lf:.2f})",
                    "it": f"servito solo {lag} giorni lavorativi fa (effetto pausa ×{lf:.2f})"})
    elif lf > 1.3:
        out.append({"de": f"seit {lag} Arbeitstagen nicht mehr serviert – typischer Abstand (×{lf:.2f})",
                    "it": f"non servito da {lag} giorni lavorativi – intervallo tipico (×{lf:.2f})"})
    wf = float(f["wdfac"][i])
    wdn_de = WEEKDAYS_DE_LONG[day.weekday()]
    wdn_it = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"][day.weekday()]
    if wf > 1.25:
        out.append({"de": f"oft am {wdn_de} (×{wf:.2f})", "it": f"spesso di {wdn_it} (×{wf:.2f})"})
    elif wf < 0.75:
        out.append({"de": f"selten am {wdn_de} (×{wf:.2f})", "it": f"raramente di {wdn_it} (×{wf:.2f})"})
    ff = float(f["fishfac"][i])
    if ff != 1.0 and cf.fish[i]:
        out.append({"de": f"Fisch-Faktor {'Fastenzeit' if ff > 1 else 'außerhalb Fastenzeit'} ×{ff:.2f}",
                    "it": f"fattore pesce {'Quaresima' if ff > 1 else 'fuori Quaresima'} ×{ff:.2f}"})
    b = float(f["base"][i])
    if b > 0.04:
        out.append({"de": f"häufiges Gericht ({int(cf.cnt[i])}× insgesamt)",
                    "it": f"piatto frequente ({int(cf.cnt[i])} volte in totale)"})
    return out


def _deadline(day: dt.date, cfg) -> str:
    return _deadline_dt(day, cfg).isoformat()


def _dec_json(dec: Decision) -> dict:
    rec = {}
    for cat in CATEGORIES:
        rec[cat] = {"dish": dec.tip[cat], "p": dec.p[cat]}
    rec["p_full"] = dec.p_full
    rec["ev"] = dec.ev
    rec["copy_text"] = " / ".join(dec.tip[c] or "-" for c in CATEGORIES)
    rec["valid"] = dec.valid
    rec["strategy"] = dec.strategy
    return rec


def build(ds, today: dt.date, now: dt.datetime | None = None, model_name: str | None = None,
          params: dict | None = None, strategy: str | None = None) -> tuple[dict, dict]:
    """Compute today.json and week.json objects (no file writes).

    ``now`` (aware, Europe/Rome) enables the deadline check: after today's deadline the target is
    the next working day (possibly next week – then R4 history, plan and week.json use that week).
    Without ``now`` (e.g. ``--today`` debugging) no deadline is applied.
    """
    from . import model as M

    cfg = ds.config
    best, prm = M.load_params()
    model_name = model_name or best
    params = M.merge_params(params if params is not None else prm)
    strategy = strategy or M.load_strategy()
    discount = float(params.get("plan_discount", 1.0))
    gen_now = now or dt.datetime.now(_tz(cfg))
    target, season_over = _target_day(ds, today, now)
    r4 = ds.r4()
    scoring = cfg.get("scoring", {})
    w, bonus = _weights(scoring)
    me = ds.me
    week_anchor = target or today
    mon = week_monday(week_anchor)

    my_tips = {t.date: t for t in ds.tips if t.player == me}
    week_days_all = [mon + dt.timedelta(days=i) for i in range(5)]

    today_obj: dict = {
        "date": target.isoformat() if target else None,
        "weekday": target.weekday() if target else None,
        "is_today": bool(target == today),
        "deadline": _deadline(target, cfg) if target else None,
        "today_deadline_passed": bool(deadline_passed(today, now, cfg)) if today.weekday() < 5 else None,
        "generated_at": gen_now.isoformat(timespec="seconds"),
        "is_lent": bool(is_lent(target)) if target else False,
        "model": model_name,
        "strategy": strategy,
        "season_over": season_over,
    }
    forecasts: dict = {}
    if target is not None:
        cal = M.WorkCalendar(ds.workdays(), ds.free_days)
        hist = [m for m in ds.served if m.date < target]
        last_known = hist[-1].date if hist else None
        pr = M.Predictor(model_name, params, ds.norm, cal).fit(hist)
        end = season_end(target.year, cfg.get("season_end_mmdd", "12-23"))

        def open_day(d: dt.date) -> bool:
            m = ds.menus_by_date.get(d)
            return d.weekday() < 5 and d not in ds.free_days and (m is None or m.status == "pending")

        days = [d for d in week_rest(target, ds.workdays(), ds.free_days, end) if open_day(d)]
        if target not in days:
            days = [target] + days
        # earlier days of the same week whose menu is still unknown (e.g. today after the deadline):
        # they are forecast too, so that the same-week correction of the later days accounts for them
        pre = [d for d in week_days_all if d < target and open_day(d)
               and (last_known is None or d > last_known)]
        raw = [pr.predict(d) for d in pre + days]
        rho = pr.week_factors(target)
        allp = M.week_correction(raw, rho)
        probs = allp[len(pre):]
        df0 = pr.features([target])[0]
        pairs = M.full_pair_lookup(df0)
        dps = [DayProbs(d, pb, pairs if i == 0 else None) for i, (d, pb) in enumerate(zip(days, probs))]
        history = my_week_history(ds, target)
        # Stale data: open days of this week before the target (menu not entered yet, e.g. the
        # sheet was not pushed since yesterday, or today after the deadline) without a recorded tip
        # of mine. On those mornings the site showed the engine's recommendation – computed from
        # the same data, so it is reproduced here – and I most likely tipped it. Without this,
        # the target's tip repeated yesterday's in ~50 % of stale mornings (rule 4: consecutive).
        # A tip I enter later (site/sheet) replaces the assumption on the next run.
        assumed = {}
        seq = pre + days
        for i, d in enumerate(pre):
            if any(d in (history.get(c) or {}) for c in CATEGORIES):
                continue
            allp_d = M.week_correction(raw, pr.week_factors(d))
            pairs_d = M.full_pair_lookup(pr.features([d])[0])
            dps_d = [DayProbs(x, pb, pairs_d if j == 0 else None)
                     for j, (x, pb) in enumerate(zip(seq[i:], allp_d[i:]))]
            dec_d = decide(dps_d, history, r4, scoring, strategy, discount=discount)
            for c in CATEGORIES:
                if dec_d.tip[c]:
                    history.setdefault(c, {})[d] = [dec_d.tip[c]]
            assumed[d] = dict(dec_d.tip)
        dec = decide(dps, history, r4, scoring, strategy, discount=discount)
        greedy = dec if strategy == "greedy" else decide(dps, history, r4, scoring, "greedy")
        week_plan = dec.plan if strategy == "week_planner" else rollout(dps, history, r4, scoring, strategy)
        forecasts = {d: pb for d, pb in zip(pre + days, allp)}

        # alternatives with reasons and R4 status
        alts = {}
        blocked = []
        for cat in CATEGORIES:
            cf = df0.chans.get(cat)
            lst = []
            for lab, p in _top(probs[0].get(cat, {}), 10):
                viol = r4.violations(cat, lab, target, history.get(cat) or {})
                i = cf.labels.index(lab) if cf is not None and lab in cf.labels else None
                reasons = _reasons(cf, i, target) if i is not None else []
                for v in viol:
                    reasons.insert(0, {"de": "Regel 4: " + v.message("de"), "it": "Regola 4: " + v.message("it")})
                    blocked.append(v.to_dict())
                lst.append({
                    "dish": lab, "p": p, "blocked": bool(viol), "reasons": reasons,
                    "last_served": cf.last_date[i].isoformat() if i is not None and cf.last_date[i] else None,
                    "days_since": int(cf.lag[i]) if i is not None else None,
                    "n_total": int(cf.cnt[i]) if i is not None else 0,
                })
            alts[cat] = lst
        ph = probs[0].get("hauptspeise", {})
        pair_json = M.pair_dict(df0, ph, top_h=8, top_b=5)
        lent = is_lent(target)
        hp = probs[0].get("hauptspeise", {})
        p_fish = sum(p for lab, p in hp.items() if ds.norm.is_fish(lab))
        if lent:
            note_de = ("Fastenzeit: Für Fisch muss das genaue Gericht getippt werden (Regel 9.6). "
                       "Freitags ist Fisch besonders wahrscheinlich.")
            note_it = ("Quaresima: per il pesce bisogna indovinare il piatto esatto (regola 9.6). "
                       "Il venerdì il pesce è particolarmente probabile.")
        else:
            note_de = ("Außerhalb der Fastenzeit zählt der Tipp „Fisch“ für jedes Fischgericht (Regel 9.6) – "
                       "außer Scombri, das immer genau getippt werden muss.")
            note_it = ("Fuori dalla Quaresima il tip «Fisch» vale per qualsiasi piatto di pesce (regola 9.6) – "
                       "tranne Scombri, che va sempre indicato esattamente.")
        my_week = []
        for d in week_days_all:
            if d >= target:
                break
            t = my_tips.get(d)
            if t is None:
                if d in assumed:   # not recorded yet: assumed = the engine's recommendation of that day
                    my_week.append({"date": d.isoformat(), "tip": assumed[d], "points": None, "assumed": True})
                continue
            my_week.append({"date": d.isoformat(),
                            "tip": {c: (t.options.get(c) or [""])[0] for c in CATEGORIES},
                            "points": t.points})
        today_obj.update({
            "recommendation": _dec_json(dec),
            "greedy": _dec_json(greedy),
            "alternatives": alts,
            "pair_beilage_given_haupt": pair_json,
            "my_week": my_week,
            "blocked": blocked,
            "week_plan": [{"date": r["date"].isoformat(), **{c: r[c] for c in CATEGORIES}, "ev": r["ev"]}
                          for r in week_plan],
            "fish": {"lent": lent, "note_de": note_de, "note_it": note_it, "p_fish": p_fish},
            "p_new": pr.p_new(target),
        })
    else:
        today_obj.update({"recommendation": None, "greedy": None, "alternatives": {c: [] for c in CATEGORIES},
                          "pair_beilage_given_haupt": {}, "my_week": [], "blocked": [], "week_plan": [],
                          "fish": {"lent": False, "note_de": "", "note_it": "", "p_fish": 0.0}})

    # ---------------- week.json
    hist_all = {c: ds.tip_history(me, c) for c in CATEGORIES}
    wdays = []
    for d in week_days_all:
        m = ds.menus_by_date.get(d)
        status = m.status if m else ("free" if d in ds.free_days
                                     or d > season_end(d.year, cfg.get("season_end_mmdd", "12-23")) else "pending")
        t = my_tips.get(d)
        fc = forecasts.get(d)
        wdays.append({
            "date": d.isoformat(), "weekday": d.weekday(), "status": status,
            "menu": ({c: list(m.options.get(c, [])) for c in CATEGORIES} if m and m.status in ("served", "unknown") else None),
            "my_tip": ({c: (t.options.get(c) or [""])[0] for c in CATEGORIES} if t else None),
            "my_points": t.points if t else None,
            "forecast": ({c: [{"dish": lab, "p": p} for lab, p in _top(fc.get(c, {}), 3)] for c in CATEGORIES}
                         if fc else None),
        })
    tippable = {}
    s_end = season_end(mon.year, cfg.get("season_end_mmdd", "12-23"))
    rest = [d for d in week_days_all if (target is None or d >= target) and d.weekday() < 5
            and d not in ds.free_days and d <= s_end]
    for cat in CATEGORIES:
        names = []
        for d in week_days_all:
            for o in (hist_all[cat].get(d) or []):
                if o not in names:
                    names.append(o)
        if target is not None:
            for a in today_obj["alternatives"].get(cat, []):
                if a["dish"] not in names:
                    names.append(a["dish"])
        rows = []
        hist_week = {d: o for d, o in hist_all[cat].items() if week_monday(d) == mon or (mon - dt.timedelta(days=7)) <= d < mon}
        for name in names:
            used = sorted(d for d, o in hist_all[cat].items() if week_key(d) == week_key(mon)
                          and any(fold(x) == fold(name) for x in o))
            blocked_days = [d.isoformat() for d in rest if r4.violations(cat, name, d, hist_week)]
            rows.append({"dish": name, "used_days": [d.isoformat() for d in used],
                         "remaining": max(0, r4.max_per_week - len(used)), "blocked_days": blocked_days})
        tippable[cat] = rows
    week_obj = {"week_start": mon.isoformat(), "today": today.isoformat(), "days": wdays, "tippable": tippable,
                "r4": {"max_per_week": r4.max_per_week, "consecutive_mode": r4.mode}}
    return today_obj, week_obj


def as_of(ds, day: dt.date):
    """The dataset as it looked on the morning of ``day`` (debugging a past day with ``--today``).

    Menus from ``day`` on are not known yet (served/unknown -> pending; free days stay free) and
    no tips from ``day`` on are entered. Without this a past ``--today`` silently recommended for
    the first day whose menu is still unknown (i.e. months later). Returns ``ds`` itself when
    no menu from ``day`` on is known (the normal, live case).
    """
    from .data import Dataset, Menu

    if not any(m.date >= day and m.status in ("served", "unknown") for m in ds.menus):
        return ds
    menus = [Menu(m.date, "pending", ["", "", ""], {c: [] for c in CATEGORIES}, m.source)
             if m.date >= day and m.status in ("served", "unknown") else m for m in ds.menus]
    tips = [t for t in ds.tips if t.date < day]
    return Dataset(menus, tips, ds.norm, ds.config)


def run(ds, today: dt.date, now: dt.datetime | None = None) -> dict:
    from .output import write_site_json

    today_obj, week_obj = build(ds, today, now)
    write_site_json("today", today_obj)
    write_site_json("week", week_obj)
    return today_obj


def main(argv=None) -> int:
    import argparse
    import sys

    from .data import load_dataset

    ap = argparse.ArgumentParser(description="Tagesempfehlung / raccomandazione del giorno")
    ap.add_argument("--today", type=dt.date.fromisoformat)
    ap.add_argument("--now", type=dt.datetime.fromisoformat,
                    help="pretend local time (e.g. 2026-10-09T12:30) – enables the deadline check")
    ap.add_argument("--dry-run", action="store_true",
                    help="nur anzeigen, docs/data/today.json + week.json NICHT schreiben / solo stampa")
    ap.add_argument("--json", action="store_true", help="today.json auf stdout ausgeben")
    a = ap.parse_args(argv)
    ds = load_dataset()
    tz = _tz(ds.config)
    if a.now is not None:
        now = a.now if a.now.tzinfo else a.now.replace(tzinfo=tz)
        today = a.today or now.astimezone(tz).date()
    else:
        now = dt.datetime.now(tz)
        today = a.today or now.date()
        if a.today:
            now = None   # debugging another day: no deadline check
    if a.today is not None or a.now is not None:
        dsx = as_of(ds, today)     # a past day: pretend its morning (later menus/tips unknown)
        if dsx is not ds:
            print(f"Stand/stato: Morgen des {today.isoformat()} (spätere Menüs und Tipps ausgeblendet)",
                  file=sys.stderr)
            ds = dsx
    if a.dry_run:
        obj, _ = build(ds, today, now)
    else:
        obj = run(ds, today, now)
    if a.json:   # machine-readable: only the today.json object on stdout
        import json
        print(json.dumps(obj, ensure_ascii=False, indent=1, default=str))
        return 0
    if obj.get("season_over") or not obj.get("recommendation"):
        print("Saison vorbei / stagione finita")
        return 0
    rec = obj["recommendation"]
    print(f"Ziel/target: {obj['date']} ({'heute' if obj['is_today'] else 'nächster Tag'}), Modell {obj['model']}")
    print(f"Empfehlung: {rec['copy_text']}  EV={rec['ev']:.3f}  "
          + "  ".join(f"{c[0].upper()}={rec[c]['p']:.3f}" for c in CATEGORIES) + f"  valid={rec['valid']}")
    g = obj["greedy"]
    print(f"Greedy:     {g['copy_text']}  EV={g['ev']:.3f}")
    for r in obj["week_plan"]:
        print(f"  Plan {r['date']}: {r['vorspeise']} / {r['hauptspeise']} / {r['beilage']}  EV={r['ev']:.3f}")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
