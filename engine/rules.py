"""Game rules (Regelwerk): scoring (rule 9), fish/Lent (9.6) and the weekly tip limit (rule 4)."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import Iterable, Mapping, Sequence

from . import CATEGORIES
from .dates import WEEKDAYS_DE, is_lent, week_key
from .normalize import Normalizer, fold

DEFAULT_SCORING = {
    "vorspeise": 1.0,
    "hauptspeise": 0.5,
    "beilage": 0.5,
    "full_menu_total": 3.0,
    "alt_options_count": True,
}


# ------------------------------------------------------------------ scoring
def category_match(cat: str, tip_options: Sequence[str], actual_options: Sequence[str],
                   day: dt.date, norm: Normalizer, alt_options_count: bool = True) -> bool:
    """Does a tip (canonical options) hit the served dish of one category?

    * any announced option counts when ``alt_options_count`` (rules 9.1/9.5, Excel practice)
    * Hauptspeise: generic "Fisch" hits any fish dish outside Lent, except Scombri (rule 9.6)
    """
    if not tip_options or not actual_options:
        return False
    served = list(actual_options) if alt_options_count else list(actual_options[:1])
    served_f = {fold(x) for x in served}
    lent = is_lent(day)
    for t in tip_options:
        tf = fold(t)
        if tf in served_f:
            return True
        if cat == "hauptspeise" and tf == fold(norm.fish_label) and not lent:
            if any(norm.is_generic_fish_ok(s) for s in served):
                return True
    return False


def score_tip(tip: Mapping[str, Sequence[str]], actual: Mapping[str, Sequence[str]], day: dt.date,
              norm: Normalizer, scoring: Mapping | None = None) -> tuple[float, dict[str, bool]]:
    """Points of one tip. ``tip``/``actual`` map category -> canonical option list.

    V = 1, H = 0.5, B = 0.5, whole menu = 3 (bonus +1), exactly like the Excel formula.
    """
    sc = {**DEFAULT_SCORING, **(scoring or {})}
    hits = {c: category_match(c, tip.get(c, []), actual.get(c, []), day, norm, sc["alt_options_count"])
            for c in CATEGORIES}
    if all(hits.values()):
        return float(sc["full_menu_total"]), hits
    pts = sum(float(sc[c]) for c in CATEGORIES if hits[c])
    return pts, hits


def expected_value(p_v: float, p_h: float, p_b: float, p_full: float, scoring: Mapping | None = None) -> float:
    """EV = 1·P(V) + 0.5·P(H) + 0.5·P(B) + bonus·P(V∧H∧B)."""
    sc = {**DEFAULT_SCORING, **(scoring or {})}
    bonus = sc["full_menu_total"] - (sc["vorspeise"] + sc["hauptspeise"] + sc["beilage"])
    return sc["vorspeise"] * p_v + sc["hauptspeise"] * p_h + sc["beilage"] * p_b + bonus * p_full


# ------------------------------------------------------------------- rule 4
@dataclass
class Violation:
    category: str
    dish: str
    kind: str  # "max_per_week" | "consecutive"
    days: list[dt.date] = field(default_factory=list)

    def message(self, lang: str = "de") -> str:
        names = ", ".join(WEEKDAYS_DE[d.weekday()] for d in self.days)
        if lang == "it":
            from .dates import WEEKDAYS_IT
            names = ", ".join(WEEKDAYS_IT[d.weekday()] for d in self.days)
            if self.kind == "max_per_week":
                return f"{self.dish}: già tippato 2 volte questa settimana ({names})"
            return f"{self.dish}: tippato in un giorno adiacente ({names})"
        if self.kind == "max_per_week":
            return f"{self.dish}: diese Woche schon 2× getippt ({names})"
        return f"{self.dish}: am Nachbartag getippt ({names})"

    def to_dict(self) -> dict:
        return {"category": self.category, "dish": self.dish, "kind": self.kind,
                "days": [d.isoformat() for d in self.days],
                "message_de": self.message("de"), "message_it": self.message("it")}


class R4:
    """Rule 4: same dish max ``max_per_week`` times per working week, never on consecutive days.

    ``consecutive_mode``:
      * ``workday_adjacent_same_week`` (default): neighbouring *working* days inside the same
        ISO week (Mon/Wed count as consecutive if Tuesday is a free day)
      * ``calendar_adjacent``: dates exactly one calendar day apart
      * ``workday_adjacent_any``: neighbouring working days, also Friday -> Monday
    """

    def __init__(self, max_per_week: int = 2, consecutive_mode: str = "workday_adjacent_same_week",
                 free_days: Iterable[dt.date] = ()):
        self.max_per_week = max_per_week
        self.mode = consecutive_mode
        self.free_days = set(free_days)

    @classmethod
    def from_config(cls, cfg: Mapping, free_days: Iterable[dt.date] = ()) -> "R4":
        r = cfg.get("r4", {})
        return cls(r.get("max_per_week", 2), r.get("consecutive_mode", "workday_adjacent_same_week"), free_days)

    def is_workday(self, d: dt.date) -> bool:
        return d.weekday() < 5 and d not in self.free_days

    def _prev_workday(self, d: dt.date) -> dt.date:
        x = d - dt.timedelta(days=1)
        while not self.is_workday(x):
            x -= dt.timedelta(days=1)
        return x

    def _next_workday(self, d: dt.date) -> dt.date:
        x = d + dt.timedelta(days=1)
        while not self.is_workday(x):
            x += dt.timedelta(days=1)
        return x

    def adjacent(self, a: dt.date, b: dt.date) -> bool:
        if a == b:
            return False
        a, b = min(a, b), max(a, b)
        if self.mode == "calendar_adjacent":
            return (b - a).days == 1
        if self.mode == "workday_adjacent_any":
            return self._next_workday(a) == b
        # workday_adjacent_same_week
        return week_key(a) == week_key(b) and self._next_workday(a) == b

    def violations(self, cat: str, dish: str, day: dt.date,
                   history: Mapping[dt.date, Sequence[str]]) -> list[Violation]:
        """Would tipping ``dish`` in ``cat`` on ``day`` break rule 4?

        ``history`` maps date -> canonical tip options of *my* tips in that category
        (other dates; ``day`` itself is ignored).
        """
        if not dish:
            return []
        k = fold(dish)
        same = sorted(d for d, opts in history.items()
                      if d != day and any(fold(o) == k for o in opts))
        out = []
        in_week = [d for d in same if week_key(d) == week_key(day)]
        if len(in_week) >= self.max_per_week:
            out.append(Violation(cat, dish, "max_per_week", in_week))
        adj = [d for d in same if self.adjacent(d, day)]
        if adj:
            out.append(Violation(cat, dish, "consecutive", adj))
        return out

    def allowed(self, cat: str, dish: str, day: dt.date, history: Mapping[dt.date, Sequence[str]]) -> bool:
        return not self.violations(cat, dish, day, history)

    def check_sequence(self, tips: Mapping[dt.date, Mapping[str, Sequence[str]]]) -> list[tuple[dt.date, Violation]]:
        """Validate a whole tip history (date -> {cat: options}); returns all violations."""
        res = []
        for cat in CATEGORIES:
            hist = {d: t.get(cat, []) for d, t in tips.items()}
            for d in sorted(tips):
                earlier = {x: o for x, o in hist.items() if x < d}
                for opt in hist[d]:
                    for v in self.violations(cat, opt, d, earlier):
                        res.append((d, v))
        return res
