"""Small site files: meta.json, menus.json (Datenbank), tips.json, dishes.json (autocomplete)."""
from __future__ import annotations

import datetime as dt
import os
from collections import Counter

from . import CATEGORIES
from .data import Dataset
from .dates import WEEKDAYS_DE, is_lent
from .output import write_site_json


def _repo_info(cfg) -> dict:
    full = os.environ.get("GITHUB_REPOSITORY", "")
    owner, _, name = full.partition("/")
    return {"owner": owner, "name": name, "branch": cfg.get("github", {}).get("branch", "main")}


def run(ds: Dataset, today: dt.date, now: dt.datetime | None = None) -> None:
    cfg = ds.config
    last = max((m.date for m in ds.served), default=None)
    write_site_json("meta", {
        "generated_at": (now or dt.datetime.now(dt.timezone.utc)).isoformat(timespec="seconds"),
        "today": today.isoformat(),
        "me": ds.me,
        "players": ds.players,
        "last_menu_date": last.isoformat() if last else None,
        "n_menus": len(ds.served),
        "n_tips": len(ds.tips),
        "years": sorted({m.date.year for m in ds.served}),
        "timezone": cfg.get("timezone", "Europe/Rome"),
        "deadline": cfg.get("deadline", "12:00"),
        "r4": cfg.get("r4", {}),
        "scoring": cfg.get("scoring", {}),
        "repo": _repo_info(cfg),
        "encrypted": bool(os.environ.get("SITE_PASSPHRASE")),
        "version": 1,
    })

    rows = []
    for m in ds.menus:
        if m.status == "pending" and m.date > today:
            continue
        rows.append({
            "date": m.date.isoformat(), "year": m.date.year, "weekday": m.date.weekday(),
            "status": m.status, "lent": is_lent(m.date),
            "v": m.raw[0], "h": m.raw[1], "b": m.raw[2],
            "v_norm": " / ".join(m.options.get("vorspeise", [])),
            "h_norm": " / ".join(m.options.get("hauptspeise", [])),
            "b_norm": " / ".join(m.options.get("beilage", [])),
        })
    free_future = [m.date.isoformat() for m in ds.menus if m.status == "free" and m.date >= today]
    write_site_json("menus", {"rows": rows, "free_days_ahead": free_future})

    # Rule 6: other players' tips of today (or later) are never published before the deadline.
    trows = []
    for t in ds.tips:
        if t.date >= today and t.player != ds.me:
            continue
        trows.append({"date": t.date.isoformat(), "player": t.player,
                      "v": t.raw[0], "h": t.raw[1], "b": t.raw[2],
                      "v_norm": " / ".join(t.options.get("vorspeise", [])),
                      "h_norm": " / ".join(t.options.get("hauptspeise", [])),
                      "b_norm": " / ".join(t.options.get("beilage", [])),
                      "points": t.points, "points_sheet": t.points_sheet})
    write_site_json("tips", {"rows": trows})

    dishes = {}
    for cat in CATEGORIES:
        c = Counter()
        for m in ds.served:
            for o in m.options.get(cat, []):
                c[o] += 1
        for t in ds.tips:
            for o in t.options.get(cat, []):
                c[o] += 0  # known name, no weight
        if cat == "hauptspeise":
            c[ds.norm.fish_label] += 0
        dishes[cat] = [d for d, _ in sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))]
    write_site_json("dishes", dishes)
