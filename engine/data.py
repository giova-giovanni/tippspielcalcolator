"""Shared data access for every engine module.

>>> ds = load_dataset()
>>> ds.served            # served menus, chronological (Menu objects)
>>> ds.tips_of("Johannes Paul III")
>>> ds.norm.options("Pommes / Kartoffelsalat", "beilage")
"""
from __future__ import annotations

import datetime as dt
from collections import defaultdict
from dataclasses import dataclass, field

from . import CATEGORIES
from .config import MENUS_CSV, TIPS_CSV, load_config
from .dates import is_lent, to_date
from .normalize import Normalizer, clean
from .rules import R4, score_tip


@dataclass
class Menu:
    date: dt.date
    status: str                                   # served | free | unknown | pending
    raw: list[str]                                # [V, H, B] as written
    options: dict[str, list[str]] = field(default_factory=dict)   # cat -> canonical options (first = primary)
    source: str = ""

    @property
    def primary(self) -> dict[str, str]:
        return {c: (self.options[c][0] if self.options.get(c) else "") for c in CATEGORIES}

    @property
    def lent(self) -> bool:
        return is_lent(self.date)

    @property
    def weekday(self) -> int:
        return self.date.weekday()


@dataclass
class Tip:
    date: dt.date
    player: str
    raw: list[str]
    options: dict[str, list[str]] = field(default_factory=dict)
    points_sheet: float | None = None
    points: float | None = None                    # recomputed by the engine
    hits: dict[str, bool] = field(default_factory=dict)
    source: str = ""


@dataclass
class Dataset:
    menus: list[Menu]
    tips: list[Tip]
    norm: Normalizer
    config: dict

    def __post_init__(self):
        self.menus.sort(key=lambda m: m.date)
        self.tips.sort(key=lambda t: (t.date, t.player))
        self.menus_by_date = {m.date: m for m in self.menus}
        self.served = [m for m in self.menus if m.status == "served"]
        self.free_days = {m.date for m in self.menus if m.status == "free"}
        seen = []
        for t in self.tips:
            if t.player not in seen:
                seen.append(t.player)
        self.players = seen
        self.me = self.config.get("me", "")

    def tips_of(self, player: str) -> list[Tip]:
        return [t for t in self.tips if t.player == player]

    def tip_history(self, player: str, cat: str) -> dict[dt.date, list[str]]:
        """date -> canonical options of ``player``'s tips in ``cat`` (for rule 4)."""
        return {t.date: t.options.get(cat, []) for t in self.tips if t.player == player and t.options.get(cat)}

    def r4(self) -> R4:
        return R4.from_config(self.config, self.free_days)

    def workdays(self) -> list[dt.date]:
        """Every known game day (served/unknown/pending), chronological."""
        return [m.date for m in self.menus if m.status != "free"]


def _read(path):
    import csv

    if not path.exists():
        return []
    with open(path, encoding="utf-8", newline="") as f:
        return [dict(r) for r in csv.DictReader(f)]


def _float(v):
    try:
        return None if v in (None, "") else float(v)
    except ValueError:
        return None


def load_dataset(menus_path=MENUS_CSV, tips_path=TIPS_CSV, config: dict | None = None,
                 aliases: dict | None = None) -> Dataset:
    cfg = config if config is not None else load_config()
    norm = Normalizer(aliases)
    mrows, trows = _read(menus_path), _read(tips_path)
    norm.fit({c: [r.get(c, "") for r in mrows] + [r.get(c, "") for r in trows] for c in CATEGORIES})
    aliases_p = cfg.get("player_aliases", {})
    menus = []
    for r in mrows:
        d = to_date(r.get("date"))
        if d is None:
            continue
        raw = [clean(r.get(c, "")) for c in CATEGORIES]
        status = (r.get("status") or "").strip()
        if not status:  # hand-edited row without status
            if any(norm.is_free(x) for x in raw if x):
                status = "free"
            elif not any(raw):
                status = "pending"
            elif all(not x or norm.is_missing(x) for x in raw):
                status = "unknown"
            else:
                status = "served"
        opts = {c: norm.options(x, c) for c, x in zip(CATEGORIES, raw)} if status in ("served", "unknown") else {c: [] for c in CATEGORIES}
        menus.append(Menu(d, status, raw, opts, r.get("source", "")))
    by_date = {m.date: m for m in menus}
    scoring = cfg.get("scoring", {})
    tips = []
    for r in trows:
        d = to_date(r.get("date"))
        player = clean(r.get("player"))
        if d is None or not player:
            continue
        player = aliases_p.get(player, player)
        raw = [clean(r.get(c, "")) for c in CATEGORIES]
        opts = {c: norm.options(x, c) for c, x in zip(CATEGORIES, raw)}
        t = Tip(d, player, raw, opts, _float(r.get("points_sheet")), None, {}, r.get("source", ""))
        m = by_date.get(d)
        if m and m.status in ("served", "unknown") and any(opts.values()):
            t.points, t.hits = score_tip(opts, m.options, d, norm, scoring)
        elif m and m.status in ("served", "unknown"):
            t.points, t.hits = 0.0, {c: False for c in CATEGORIES}
        tips.append(t)
    return Dataset(menus, tips, norm, cfg)


def refresh_csvs(menus_path=MENUS_CSV, tips_path=TIPS_CSV) -> Dataset:
    """Rewrite derived columns (``*_norm``, ``points``) so hand edits stay consistent."""
    from .ingest import MENU_FIELDS, TIP_FIELDS, fmt_points, write_csv
    from .dates import WEEKDAYS_DE

    ds = load_dataset(menus_path, tips_path)
    mrows = []
    for m in ds.menus:
        row = {"date": m.date.isoformat(), "year": m.date.year, "weekday": WEEKDAYS_DE[m.date.weekday()],
               "status": m.status, "source": m.source}
        for c, x in zip(CATEGORIES, m.raw):
            row[c] = x
            row[f"{c}_norm"] = " / ".join(m.options.get(c, []))
        mrows.append(row)
    write_csv(menus_path, MENU_FIELDS, mrows)
    trows = []
    for t in ds.tips:
        row = {"date": t.date.isoformat(), "player": t.player, "points": fmt_points(t.points),
               "points_sheet": fmt_points(t.points_sheet), "source": t.source}
        for c, x in zip(CATEGORIES, t.raw):
            row[c] = x
        trows.append(row)
    write_csv(tips_path, TIP_FIELDS, trows)
    return ds


if __name__ == "__main__":
    ds = refresh_csvs()
    print(f"{len(ds.menus)} Menüs ({len(ds.served)} serviert), {len(ds.tips)} Tipps, Spieler: {ds.players}")
