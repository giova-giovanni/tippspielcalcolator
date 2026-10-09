"""Tests for engine/ingest.py (read-only on the real workbook; writes only into tmp_path)."""
from __future__ import annotations

import csv
import datetime as dt
from collections import defaultdict

import pytest

from engine.ingest import fmt_points, merge, points_cell, read_workbook, tip_cell
from engine.normalize import Normalizer

D = dt.date
TODAY = D(2026, 10, 9)
KNOWN_FREE_2026 = {D(2026, 5, 1), D(2026, 5, 25), D(2026, 6, 1), D(2026, 6, 2), D(2026, 12, 8)} | {
    D(2026, 8, d) for d in (10, 11, 12, 13, 14, 17, 18, 19, 20, 21)}
BASE_PLAYERS = {"Andreas", "Johannes", "Noah"}


@pytest.fixture(scope="module")
def parsed(workbook_path):
    log: list[str] = []
    menus, tips = read_workbook(workbook_path, Normalizer(), TODAY, log)
    return menus, tips, log


# ------------------------------------------------------------ real workbook
def test_players_per_sheet(parsed):
    _, tips, log = parsed
    players = defaultdict(set)
    for t in tips:
        players[t["date"].year].add(t["player"])
    assert players[2024] == BASE_PLAYERS
    assert players[2025] == BASE_PLAYERS
    assert players[2026] >= BASE_PLAYERS | {"Johannes Paul III"}
    assert any(l.startswith("Blatt 2026") and "Johannes Paul III" in l for l in log)
    assert not any("Regelwerk" in l or "Grafische" in l for l in log)  # non-year sheets ignored


def test_free_days_2026(parsed):
    menus, _, _ = parsed
    free = {m["date"] for m in menus if m["status"] == "free" and m["date"].year == 2026}
    assert KNOWN_FREE_2026 <= free
    assert {d for d in free if d <= TODAY} == {d for d in KNOWN_FREE_2026 if d <= TODAY}
    assert len(KNOWN_FREE_2026) == 15
    assert all(d.weekday() < 5 for d in free)


def test_workbook_rows_sane(parsed):
    menus, tips, _ = parsed
    dates = [m["date"] for m in menus]
    assert len(dates) == len(set(dates)), "doppelte Datumszeilen"
    assert {m["status"] for m in menus} <= {"served", "free", "unknown", "pending"}
    assert all(m["date"].weekday() < 5 for m in menus)
    assert min(dates) == D(2024, 10, 25)
    served = [m for m in menus if m["status"] == "served"]
    assert len(served) >= 430
    assert all(any(m["raw"]) for m in served)
    assert all(not any(m["raw"]) for m in menus if m["status"] == "pending")
    # tips on free days carry no sheet points
    status = {m["date"]: m["status"] for m in menus}
    assert all(t["points_sheet"] is None for t in tips if status.get(t["date"]) == "free")
    assert len(tips) >= 1400


def test_cell_helpers():
    assert tip_cell("-") == "" and tip_cell(0) == "" and tip_cell(False) == "" and tip_cell(None) == ""
    assert tip_cell(" Reis ") == "Reis"
    assert points_cell(False) == 0.0 and points_cell(1) == 1.0 and points_cell("") is None
    assert points_cell("abc") is None
    assert fmt_points(3.0) == "3" and fmt_points(0.5) == "0.5" and fmt_points(None) == ""


# --------------------------------------------------------- synthetic workbook
def _make_workbook(path):
    import openpyxl

    wb = openpyxl.Workbook()
    wb.active.title = "Regelwerk"
    ws = wb.create_sheet("2027")
    ws.append(["Tag", "Vorspeise", "Hauptspeise", "Beilage", "Andreas", None, None, None, "Neu"])
    ws.append([None, None, None, None] + ["Vorspeise", "Hauptspeise", "Beilage", "Punkte"] * 2)
    ws.append([dt.datetime(2027, 1, 11), "Arrabbiata", "Leberkas", "Pommes / Kartoffelsalat",
               "Arrabbiata", "Gulasch", "Kartoffelsalat", 1.5, "-", "-", "-", False])
    ws.append([dt.datetime(2027, 1, 12), "Frei", "Frei", "Frei", "Hirten", "-", "-", None])
    ws.append([dt.datetime(2027, 1, 13), "Bo", "NV", "-", "Hirten", "Leberkas", "Reis", 0])
    ws.append([dt.datetime(2027, 1, 14), None, None, None])
    ws.append(["Summe", None, None, None])
    wb.save(path)


def test_synthetic_workbook_new_player(tmp_path):
    p = tmp_path / "Tippspiel Essen.xlsx"
    _make_workbook(p)
    log: list[str] = []
    menus, tips = read_workbook(p, Normalizer(), D(2027, 1, 12), log)
    assert [(m["date"], m["status"]) for m in menus] == [
        (D(2027, 1, 11), "served"), (D(2027, 1, 12), "free"),
        (D(2027, 1, 13), "unknown"), (D(2027, 1, 14), "pending")]
    assert menus[0]["raw"] == ["Arrabbiata", "Leberkas", "Pommes / Kartoffelsalat"]
    by_key = {(t["date"], t["player"]): t for t in tips}
    assert set(by_key) == {(D(2027, 1, 11), "Andreas"), (D(2027, 1, 12), "Andreas"), (D(2027, 1, 13), "Andreas")}
    assert by_key[(D(2027, 1, 11), "Andreas")]["points_sheet"] == 1.5
    assert by_key[(D(2027, 1, 12), "Andreas")]["points_sheet"] is None      # free day
    assert by_key[(D(2027, 1, 13), "Andreas")]["points_sheet"] == 0.0
    assert any("Neu" in l for l in log)                                     # block detected, no tips


# --------------------------------------------------------------------- merge
def _csv_menu(date, status, v="", h="", b="", source="form"):
    return {"date": date, "status": status, "vorspeise": v, "hauptspeise": h, "beilage": b, "source": source}


def _csv_tip(date, player, v, h, b, source="form"):
    return {"date": date, "player": player, "vorspeise": v, "hauptspeise": h, "beilage": b,
            "points_sheet": "", "source": source}


def test_merge_workbook_wins_and_csv_only_rows_survive():
    existing_menus = [
        _csv_menu("2026-10-08", "served", "Lasagne", "Rindsbraten", "Pommes", "form"),
        _csv_menu("2026-10-09", "served", "Arrabbiata", "Leberkas", "Röstkartoffeln", "form"),
        _csv_menu("2026-10-20", "served", "Hirten", "Gulasch", "Spatzlen", "form"),
    ]
    existing_tips = [
        _csv_tip("2026-10-08", "Andreas", "Hirten", "Gulasch", "Reis"),
        _csv_tip("2026-10-20", "Johannes Paul III", "Hirten", "Gulasch", "Spatzlen"),
    ]
    x_menus = [
        {"date": D(2026, 10, 8), "status": "served", "raw": ["Lasagne", "Rindsbraten", "Reis"]},
        {"date": D(2026, 10, 9), "status": "pending", "raw": ["", "", ""]},
        {"date": D(2026, 10, 12), "status": "pending", "raw": ["", "", ""]},
    ]
    x_tips = [{"date": D(2026, 10, 8), "player": "Andreas", "raw": ["Lasagne", "Rindsbraten", "Reis"],
               "points_sheet": 3.0}]
    menus, tips = merge(existing_menus, existing_tips, x_menus, x_tips)
    by_date = {m["date"]: m for m in menus}
    assert [m["date"] for m in menus] == ["2026-10-08", "2026-10-09", "2026-10-12", "2026-10-20"]
    # workbook has content -> workbook wins
    assert by_date["2026-10-08"]["beilage"] == "Reis" and by_date["2026-10-08"]["source"] == "xlsx"
    # pending workbook row does not erase the website-entered menu
    assert by_date["2026-10-09"]["hauptspeise"] == "Leberkas" and by_date["2026-10-09"]["source"] == "form"
    assert by_date["2026-10-09"]["status"] == "served"
    # new pending row from the workbook is added
    assert by_date["2026-10-12"]["status"] == "pending"
    # CSV-only (website) row for a future date is kept
    assert by_date["2026-10-20"]["source"] == "form" and by_date["2026-10-20"]["vorspeise"] == "Hirten"
    tip_by = {(t["date"], t["player"]): t for t in tips}
    assert tip_by[("2026-10-08", "Andreas")]["vorspeise"] == "Lasagne"
    assert tip_by[("2026-10-08", "Andreas")]["points_sheet"] == "3"
    assert tip_by[("2026-10-08", "Andreas")]["source"] == "xlsx"
    assert tip_by[("2026-10-20", "Johannes Paul III")]["source"] == "form"


def test_merge_pending_overrides_pending():
    existing = [_csv_menu("2026-10-09", "pending", source="xlsx")]
    menus, _ = merge(existing, [], [{"date": D(2026, 10, 9), "status": "served",
                                     "raw": ["Lasagne", "Leberkas", "Reis"]}], [])
    assert menus[0]["status"] == "served" and menus[0]["vorspeise"] == "Lasagne"


# --------------------------------------------------- hand-edited CSV (tmp copy)
def test_refresh_csvs_on_hand_edited_copy(data_copy):
    """Raw columns edited by hand (no status, no *_norm) are completed by refresh_csvs."""
    from engine.data import refresh_csvs

    menus_p, tips_p = data_copy / "menus.csv", data_copy / "tips.csv"
    with open(menus_p, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
        fields = list(rows[0].keys())
    rows.append({k: "" for k in fields} | {"date": "2030-01-07", "vorspeise": "Nudel Ragu",
                                            "hauptspeise": "Lachsforelle", "beilage": "Pommes / Kartoffelsalat"})
    with open(menus_p, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    with open(tips_p, "a", encoding="utf-8", newline="") as f:
        f.write("2030-01-07,Johannes Paul III,Nudel mit Ragu,Fisch,Kartoffelsalat,,,form\n")

    ds = refresh_csvs(menus_p, tips_p)
    m = ds.menus_by_date[D(2030, 1, 7)]
    assert m.status == "served"
    assert m.options == {"vorspeise": ["Nudel mit Ragu"], "hauptspeise": ["Forelle"],
                         "beilage": ["Pommes", "Kartoffelsalat"]}
    with open(menus_p, encoding="utf-8", newline="") as f:
        row = next(r for r in csv.DictReader(f) if r["date"] == "2030-01-07")
    assert row["status"] == "served" and row["weekday"] == "Mo" and row["year"] == "2030"
    assert row["hauptspeise_norm"] == "Forelle" and row["beilage_norm"] == "Pommes / Kartoffelsalat"
    with open(tips_p, encoding="utf-8", newline="") as f:
        trow = next(r for r in csv.DictReader(f) if r["date"] == "2030-01-07")
    assert trow["points"] == "3"   # V + Fisch (outside Lent) + one announced option = full menu
