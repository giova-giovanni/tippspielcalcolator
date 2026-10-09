"""Excel -> data/menus.csv + data/tips.csv.

Usage::

    python -m engine.ingest                      # data/raw/*.xlsx (newest)
    python -m engine.ingest --xlsx path.xlsx     # explicit file
    python -m engine.ingest --if-changed         # only when the xlsx hash changed

The year sheets ("2024", "2025", …) are detected automatically; so are the player
blocks (4 columns each: Vorspeise, Hauptspeise, Beilage, Punkte) – new players
just appear. Rows already present in the CSVs but not (or only empty) in the
workbook – e.g. entered through the website – are kept.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import re
import sys
from collections import Counter
from pathlib import Path

from . import CATEGORIES
from .config import MENUS_CSV, RAW, REPORTS, STATE_JSON, TIPS_CSV, load_config, load_json, save_json
from .dates import WEEKDAYS_DE, to_date
from .normalize import Normalizer, clean, write_alias_report

MENU_FIELDS = ["date", "year", "weekday", "status",
               "vorspeise", "hauptspeise", "beilage",
               "vorspeise_norm", "hauptspeise_norm", "beilage_norm", "source"]
TIP_FIELDS = ["date", "player", "vorspeise", "hauptspeise", "beilage", "points", "points_sheet", "source"]

HEADER_WORDS = {"vorspeise", "hauptspeise", "beilage", "punkte", "tag"}
NON_PLAYER_LABELS = {"punkte", "punkteausbeute", "alles falsch", "alles richtig", "summe",
                     "durchschnittspunkte pro kalenderwoche", "ergebnisse", "regelwerk siehe entsprechendes tabellenblatt",
                     "tippspiel essen wies"}


# ------------------------------------------------------------------ helpers
def tip_cell(value) -> str:
    """Raw tip cell -> string ('' for '-', 0, FALSE, empty)."""
    if value is None or isinstance(value, bool):
        return ""
    if isinstance(value, (int, float)):
        return "" if value == 0 else clean(value)
    s = clean(value)
    return "" if s in ("-", "0") else s


def points_cell(value):
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def find_workbook() -> Path | None:
    files = sorted(RAW.glob("*.xlsx"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


# ------------------------------------------------------------- sheet parsing
def parse_year_sheet(ws, norm: Normalizer, today: dt.date, log: list[str]):
    rows = [list(r) for r in ws.iter_rows(values_only=True)]
    tag_row = next((i for i, r in enumerate(rows) if r and clean(r[0]).casefold() == "tag"), None)
    if tag_row is None:
        log.append(f"Blatt {ws.title}: keine 'Tag'-Zeile gefunden – übersprungen")
        return [], []
    # label row = the row holding 'Vorspeise' at column E (index 4): tag row or the next one
    label_row = tag_row
    for cand in (tag_row, tag_row + 1):
        if cand < len(rows) and len(rows[cand]) > 4 and clean(rows[cand][4]).casefold() == "vorspeise":
            label_row = cand
            break
    players: list[tuple[str, int]] = []
    col = 4
    while col + 3 < len(rows[label_row]):
        labels = [clean(rows[label_row][col + k]).casefold() for k in range(4)]
        if labels != ["vorspeise", "hauptspeise", "beilage", "punkte"]:
            break
        name = None
        for r in range(0, label_row + 1):
            v = clean(rows[r][col]) if col < len(rows[r]) else ""
            if v and v.casefold() not in HEADER_WORDS and v.casefold() not in NON_PLAYER_LABELS:
                name = v
                break
        if not name:
            log.append(f"Blatt {ws.title}: Spielerblock ab Spalte {col + 1} ohne Namen – übersprungen")
        else:
            players.append((name, col))
        col += 4
    log.append(f"Blatt {ws.title}: Spieler {[p for p, _ in players]}, Daten ab Zeile {label_row + 2}")

    menus, tips = [], []
    for r in rows[label_row + 1:]:
        if not r or not isinstance(r[0], (dt.datetime, dt.date, int, float)) or isinstance(r[0], bool):
            continue
        day = to_date(r[0])
        if day is None:
            continue
        raw = [clean(r[i]) if i < len(r) else "" for i in (1, 2, 3)]
        tip_rows = []
        for name, c in players:
            t = [tip_cell(r[c + k]) if c + k < len(r) else "" for k in range(3)]
            p = points_cell(r[c + 3]) if c + 3 < len(r) else None
            if any(t):
                tip_rows.append((name, t, p))
        if any(norm.is_free(x) for x in raw if x):
            status = "free"
        elif not any(raw):
            status = "pending"
        elif all(not x or norm.is_missing(x) for x in raw):
            status = "unknown"
        else:
            status = "served"
        menus.append({"date": day, "status": status, "raw": raw})
        for name, t, p in tip_rows:
            tips.append({"date": day, "player": name, "raw": t,
                         "points_sheet": p if status in ("served", "unknown") else None})
    return menus, tips


def read_workbook(path: Path, norm: Normalizer, today: dt.date, log: list[str]):
    import openpyxl

    wb = openpyxl.load_workbook(path, data_only=True, read_only=False)
    menus, tips = [], []
    for ws in wb.worksheets:
        if not re.fullmatch(r"\d{4}", ws.title.strip()):
            continue
        m, t = parse_year_sheet(ws, norm, today, log)
        menus += m
        tips += t
    return menus, tips


# ------------------------------------------------------------------ CSV I/O
def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8", newline="") as f:
        return [dict(r) for r in csv.DictReader(f)]


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in fields})


def fmt_points(p) -> str:
    if p is None or p == "":
        return ""
    p = float(p)
    return str(int(p)) if p.is_integer() else f"{p:g}"


# -------------------------------------------------------------------- main
def menu_row(day: dt.date, status: str, raw: list[str], source: str) -> dict:
    return {"date": day.isoformat(), "year": day.year, "weekday": WEEKDAYS_DE[day.weekday()],
            "status": status, "vorspeise": raw[0], "hauptspeise": raw[1], "beilage": raw[2],
            "source": source}


def merge(existing_menus: list[dict], existing_tips: list[dict], x_menus: list[dict], x_tips: list[dict]):
    """Workbook wins wherever it has content; CSV-only rows (website/manual) are kept."""
    menus = {r["date"]: r for r in existing_menus}
    for m in x_menus:
        key = m["date"].isoformat()
        new = menu_row(m["date"], m["status"], m["raw"], "xlsx")
        old = menus.get(key)
        if old and m["status"] == "pending" and old.get("status") not in ("", "pending", None):
            continue
        menus[key] = new
    tips = {(r["date"], r["player"]): r for r in existing_tips}
    for t in x_tips:
        key = (t["date"].isoformat(), t["player"])
        tips[key] = {"date": key[0], "player": t["player"], "vorspeise": t["raw"][0],
                     "hauptspeise": t["raw"][1], "beilage": t["raw"][2],
                     "points_sheet": fmt_points(t["points_sheet"]), "source": "xlsx"}
    return sorted(menus.values(), key=lambda r: r["date"]), sorted(tips.values(), key=lambda r: (r["date"], r["player"]))


def run(xlsx: Path | None = None, if_changed: bool = False, today: dt.date | None = None) -> bool:
    """Returns True when the CSVs were (re)written from the workbook."""
    xlsx = xlsx or find_workbook()
    if xlsx is None:
        print("ingest: keine .xlsx in data/raw – nichts zu tun")
        return False
    state = load_json(STATE_JSON, {}) or {}
    digest = sha256(xlsx)
    if if_changed and state.get("ingested_sha256") == digest and MENUS_CSV.exists():
        print(f"ingest: {xlsx.name} unverändert – übersprungen")
        return False
    cfg = load_config()
    import zoneinfo
    today = today or dt.datetime.now(zoneinfo.ZoneInfo(cfg.get("timezone", "Europe/Rome"))).date()
    norm = Normalizer()
    log: list[str] = []
    x_menus, x_tips = read_workbook(xlsx, norm, today, log)
    menus, tips = merge(read_csv(MENUS_CSV), read_csv(TIPS_CSV), x_menus, x_tips)
    write_csv(MENUS_CSV, MENU_FIELDS, menus)
    write_csv(TIPS_CSV, TIP_FIELDS, tips)
    state.update({"ingested_sha256": digest, "ingested_file": xlsx.name,
                  "ingested_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")})
    save_json(STATE_JSON, state)
    # derived columns + recomputed points + reports
    from .data import refresh_csvs
    refresh_csvs()
    write_ingest_report(xlsx, log)
    print("\n".join(log))
    print(f"ingest: {len(menus)} Menüzeilen, {len(tips)} Tippzeilen geschrieben")
    return True


def write_ingest_report(xlsx: Path, log: list[str]) -> None:
    from .data import load_dataset

    ds = load_dataset()
    lines = ["# Ingest-Bericht", "", f"Quelle: `{xlsx.name}`", "", "## Blätter", ""]
    lines += [f"- {l}" for l in log]
    lines += ["", "## Zeilen pro Jahr", "", "| Jahr | serviert | frei | unbekannt (Bo/NV/-) | offen/zukünftig |", "|---|---|---|---|---|"]
    for y in sorted({d.year for d in ds.menus_by_date}):
        c = Counter(m.status for m in ds.menus if m.date.year == y)
        lines.append(f"| {y} | {c['served']} | {c['free']} | {c['unknown']} | {c['pending']} |")
    lines += ["", "## Spieler", ""]
    for p in ds.players:
        n = sum(1 for t in ds.tips if t.player == p)
        lines.append(f"- {p}: {n} Tipps")
    lines += ["", "## Einzigartige Gerichte (kanonisch, nur servierte)", ""]
    for cat in CATEGORIES:
        names = {o for m in ds.served for o in m.options[cat]}
        lines.append(f"- {cat}: {len(names)}")
    diffs = [t for t in ds.tips if t.points is not None and t.points_sheet is not None and abs(t.points - t.points_sheet) > 1e-9]
    lines += ["", "## Abweichungen Excel-Punkte vs. Neuberechnung", "",
              "Neuberechnung = Normalisierung + 'Fisch'-Regel + Alternativen. Excel vergleicht nur exakte Texte.", ""]
    if diffs:
        lines += ["| Datum | Spieler | Tipp | Menü | Excel | Engine |", "|---|---|---|---|---|---|"]
        for t in diffs:
            m = ds.menus_by_date[t.date]
            lines.append(f"| {t.date} | {t.player} | {' / '.join(t.raw)} | {' / '.join(m.raw)} | {fmt_points(t.points_sheet)} | {fmt_points(t.points)} |")
    else:
        lines.append("_keine_")
    (REPORTS / "ingest_report.md").parent.mkdir(parents=True, exist_ok=True)
    (REPORTS / "ingest_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--xlsx", type=Path)
    ap.add_argument("--if-changed", action="store_true")
    a = ap.parse_args(argv)
    run(a.xlsx, a.if_changed)


if __name__ == "__main__":
    sys.exit(main())
