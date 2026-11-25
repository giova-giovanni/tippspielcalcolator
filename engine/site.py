"""Small site files: meta.json, menus.json (Datenbank), tips.json, dishes.json (autocomplete) and
today_alt.json (the second tip next to today.json: today's or the next game day's)."""
from __future__ import annotations

import datetime as dt
import os
import zoneinfo
from collections import Counter

from . import CATEGORIES
from .data import Dataset
from .dates import WEEKDAYS_DE, is_lent, season_end
from .output import read_site_json, write_site_json
from .recommend import deadline_passed

ALT = "today_alt"


def _read_prev(name: str):
    try:
        return read_site_json(name)
    except Exception:  # wrong passphrase / corrupt file: no carry-over, the tip is recomputed
        return None


def previous_tips() -> dict:
    """today.json and today_alt.json of the previous run – read BEFORE recommend.run rewrites them."""
    return {"today": _read_prev("today"), "alt": _read_prev(ALT)}


def _game_day(ds: Dataset, day: dt.date) -> bool:
    end = season_end(day.year, ds.config.get("season_end_mmdd", "12-23"))
    return day.weekday() < 5 and day not in ds.free_days and day <= end


def _has_rec(obj) -> bool:
    return isinstance(obj, dict) and bool(obj.get("recommendation"))


def alt_tip(ds: Dataset, today: dt.date, now: dt.datetime | None, main: dict | None,
            prev: dict | None = None) -> dict:
    """The second tip of the site, next to today.json (``main``).

    * ``main`` is for today (before the deadline, today's menu unknown): the tip of the next game day,
      ``provisional`` – computed as after today's deadline (today's menu forecast; my tip of today,
      or the one the engine assumes) and recomputed once today's menu and tips are entered.
    * ``main`` has moved on (deadline over or today's menu entered) and today is a game day: today's
      tip as the site showed it last – the previous today.json if it was for today, else the
      previous today_alt.json for today ("carried") – or, if neither exists, recomputed as of this
      morning (menus and tips of today hidden, "recomputed").
    * otherwise (weekend, free day, season over, no ``now``): ``{"role": None}``.

    Never uses the other players' tips (rule 6): only build()/as_of() of engine.recommend.
    """
    from . import recommend

    none = {"role": None, "date": None}
    if now is None or not main or not main.get("date"):
        return none
    if now.tzinfo is None:
        now = now.replace(tzinfo=zoneinfo.ZoneInfo(ds.config.get("timezone", "Europe/Rome")))
    stamp = now.isoformat(timespec="seconds")
    main_date = dt.date.fromisoformat(main["date"])
    prev = prev or {}

    if main_date == today:
        hh, mm = (int(x) for x in ds.config.get("deadline", "12:00").split(":"))
        tz = zoneinfo.ZoneInfo(ds.config.get("timezone", "Europe/Rome"))
        obj, _ = recommend.build(ds, today, now=max(now, dt.datetime(today.year, today.month, today.day, hh, mm, tzinfo=tz)))
        if not _has_rec(obj) or not obj.get("date") or obj["date"] <= today.isoformat():
            return none
        obj["generated_at"] = stamp   # build() stamps the pretended time (today's deadline)
        obj["missing_menus"] = recommend.missing_menus(ds, dt.date.fromisoformat(obj["date"]))
        obj.update(role="next", provisional=True, source="computed")
        return obj

    if main_date < today or not _game_day(ds, today):
        return none
    iso = today.isoformat()
    for cand in (prev.get("today"), prev.get("alt")):
        if _has_rec(cand) and cand.get("date") == iso:
            obj = dict(cand)
            obj.update(role="today", provisional=False, source="carried")
            return obj
    obj, _ = recommend.build(recommend.as_of(ds, today), today, now=None)
    if not _has_rec(obj) or obj.get("date") != iso:
        return none
    obj["generated_at"] = stamp
    obj["missing_menus"] = recommend.missing_menus(ds, today)
    obj.update(role="today", provisional=False, source="recomputed")
    return obj


def write_alt(ds: Dataset, today: dt.date, now: dt.datetime | None, main: dict | None,
              prev: dict | None = None) -> dict:
    obj = alt_tip(ds, today, now, main, prev)
    write_site_json(ALT, obj)
    return obj


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
    # After today's deadline (12:00 Rome) nobody can tip for today any more, so today's tips of the
    # others - e.g. entered from the website after lunch - are shown right away. Without ``now``
    # no deadline check: hidden, as before.
    today_open = not deadline_passed(today, now, cfg)
    trows = []
    for t in ds.tips:
        if t.player != ds.me and (t.date > today or (t.date == today and today_open)):
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
