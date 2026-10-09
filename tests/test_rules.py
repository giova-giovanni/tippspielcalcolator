"""Tests for engine/rules.py: scoring (rule 9 + 9.6 fish/Lent), Excel parity, rule 4 (R4)."""
from __future__ import annotations

import datetime as dt
from collections import defaultdict

import pytest

from engine.rules import DEFAULT_SCORING, R4, expected_value, score_tip

D = dt.date
# Data snapshot the expected numbers refer to. Later rows (new uploads) are not asserted,
# so a regular data update can never make the on-data workflow fail.
SNAPSHOT_LAST_SERVED = D(2026, 10, 8)

ACTUAL = {"vorspeise": ["Arrabbiata"], "hauptspeise": ["Leberkas"], "beilage": ["Röstkartoffeln"]}
DAY = D(2025, 11, 7)  # Friday, outside Lent


def _tip(v="Lasagne", h="Cordon Bleu", b="Reis"):
    return {"vorspeise": [v] if v else [], "hauptspeise": [h] if h else [], "beilage": [b] if b else []}


# ------------------------------------------------------------------ scoring
@pytest.mark.parametrize("tip,points", [
    (_tip(), 0.0),
    (_tip(v="Arrabbiata"), 1.0),
    (_tip(h="Leberkas"), 0.5),
    (_tip(b="Röstkartoffeln"), 0.5),
    (_tip(v="Arrabbiata", h="Leberkas"), 1.5),
    (_tip(v="Arrabbiata", b="Röstkartoffeln"), 1.5),
    (_tip(h="Leberkas", b="Röstkartoffeln"), 1.0),
    (_tip(v="Arrabbiata", h="Leberkas", b="Röstkartoffeln"), 3.0),
    (_tip(v=None, h=None, b=None), 0.0),
])
def test_score_combinations(norm, tip, points):
    pts, hits = score_tip(tip, ACTUAL, DAY, norm)
    assert pts == points
    assert set(hits) == {"vorspeise", "hauptspeise", "beilage"}


def test_score_hits_flags(norm):
    _, hits = score_tip(_tip(v="Arrabbiata", b="Röstkartoffeln"), ACTUAL, DAY, norm)
    assert hits == {"vorspeise": True, "hauptspeise": False, "beilage": True}


def test_score_case_insensitive(norm):
    tip = _tip(v="arrabbiata", h="LEBERKAS", b="röstkartoffeln")
    assert score_tip(tip, ACTUAL, DAY, norm)[0] == 3.0


def test_alternative_options_count(norm):
    actual = dict(ACTUAL, beilage=norm.options("Pommes / Kartoffelsalat", "beilage"))
    assert actual["beilage"] == ["Pommes", "Kartoffelsalat"]
    assert score_tip(_tip(b="Pommes"), actual, DAY, norm)[0] == 0.5
    assert score_tip(_tip(b="Kartoffelsalat"), actual, DAY, norm)[0] == 0.5
    only_first = {"alt_options_count": False}
    assert score_tip(_tip(b="Pommes"), actual, DAY, norm, only_first)[0] == 0.5
    assert score_tip(_tip(b="Kartoffelsalat"), actual, DAY, norm, only_first)[0] == 0.0


def test_full_menu_with_alternative_option(norm):
    actual = dict(ACTUAL, beilage=["Pommes", "Kartoffelsalat"])
    tip = _tip(v="Arrabbiata", h="Leberkas", b="Kartoffelsalat")
    assert score_tip(tip, actual, DAY, norm)[0] == 3.0


@pytest.mark.parametrize("day,served,tipped,hit", [
    (D(2025, 11, 7), "Rotbarschfilet", "Fisch", True),        # outside Lent: generic Fisch hits
    (D(2025, 11, 7), "Forelle", "fisch", True),
    (D(2026, 3, 6), "Rotbarschfilet", "Fisch", False),        # Lent: exact dish needed
    (D(2026, 3, 6), "Rotbarschfilet", "Rotbarschfilet", True),
    (D(2025, 11, 7), "Rotbarschfilet", "Rotbarschfilet", True),
    (D(2025, 11, 7), "Scombri", "Fisch", False),              # Scombri: always exact
    (D(2026, 3, 6), "Scombri", "Fisch", False),
    (D(2026, 3, 6), "Scombri", "Scombri", True),
    (D(2025, 11, 7), "Vitello tonnato", "Fisch", False),      # not a fish dish
    (D(2025, 11, 7), "Leberkas", "Fisch", False),
])
def test_fish_rule(norm, day, served, tipped, hit):
    actual = dict(ACTUAL, hauptspeise=[served])
    pts, hits = score_tip(_tip(h=tipped), actual, day, norm)
    assert hits["hauptspeise"] is hit
    assert pts == (0.5 if hit else 0.0)


def test_fish_generic_only_for_hauptspeise(norm):
    actual = dict(ACTUAL, vorspeise=["Rotbarschfilet"])
    assert score_tip(_tip(v="Fisch"), actual, DAY, norm)[0] == 0.0


def test_fish_hits_one_of_several_options(norm):
    actual = dict(ACTUAL, hauptspeise=["Schweinsschnitzel", "Rotbarschfilet"])
    assert score_tip(_tip(h="Fisch"), actual, D(2025, 12, 5), norm)[0] == 0.5


def test_expected_value():
    assert expected_value(1, 1, 1, 1) == pytest.approx(3.0)
    assert expected_value(0.2, 0.1, 0.3, 0.01) == pytest.approx(0.2 + 0.05 + 0.15 + 0.01)
    assert expected_value(0, 0, 0, 0) == 0.0
    assert DEFAULT_SCORING["full_menu_total"] == 3.0


# --------------------------------------------------------- Excel parity
KNOWN_SHEET_DIFFS = {
    (D(2025, 10, 9), "Andreas"),
    (D(2025, 10, 9), "Johannes"),
    (D(2025, 12, 19), "Johannes"),
}


def test_excel_parity(dataset):
    compared, diffs = 0, set()
    for t in dataset.tips:
        if t.date > SNAPSHOT_LAST_SERVED or t.points is None or t.points_sheet is None:
            continue
        compared += 1
        if abs(t.points - t.points_sheet) > 1e-9:
            diffs.add((t.date, t.player))
    assert compared >= 1400
    assert diffs == KNOWN_SHEET_DIFFS


def test_2026_totals_match_excel(dataset):
    totals = defaultdict(float)
    for t in dataset.tips:
        if t.date.year == 2026 and t.date <= SNAPSHOT_LAST_SERVED and t.points is not None:
            totals[t.player] += t.points
    assert dict(totals) == pytest.approx({"Andreas": 44.5, "Johannes": 45.5, "Noah": 41.5,
                                          "Johannes Paul III": 41.0})


# ------------------------------------------------------------------- rule 4
MON, TUE, WED, THU, FRI = (D(2026, 10, 5) + dt.timedelta(days=i) for i in range(5))
NEXT_MON = D(2026, 10, 12)
PREV_MON, PREV_WED, PREV_FRI = D(2026, 9, 28), D(2026, 9, 30), D(2026, 10, 2)


def _kinds(r4, day, history, dish="Reis", cat="beilage"):
    return sorted(v.kind for v in r4.violations(cat, dish, day, history))


def test_r4_defaults():
    r4 = R4()
    assert r4.max_per_week == 2 and r4.mode == "workday_adjacent_same_week"


def test_r4_max_two_per_week():
    r4 = R4()
    assert r4.allowed("beilage", "Reis", WED, {MON: ["Reis"]})
    hist = {MON: ["Reis"], WED: ["Reis"]}
    assert _kinds(r4, FRI, hist) == ["max_per_week"]
    assert not r4.allowed("beilage", "Reis", FRI, hist)
    v = r4.violations("beilage", "Reis", FRI, hist)[0]
    assert v.days == [MON, WED]
    d = v.to_dict()
    assert d["kind"] == "max_per_week" and d["days"] == ["2026-10-05", "2026-10-07"]
    assert d["message_de"] and d["message_it"]


def test_r4_other_dish_or_category_unaffected():
    r4 = R4()
    hist = {MON: ["Reis"], WED: ["Reis"]}
    assert r4.allowed("beilage", "Pommes", FRI, hist)
    assert r4.allowed("beilage", "Pommes", TUE, {MON: ["Reis"]})


def test_r4_case_insensitive():
    assert _kinds(R4(), TUE, {MON: ["reis"]}) == ["consecutive"]


def test_r4_consecutive_blocked_both_directions():
    r4 = R4()
    assert _kinds(r4, TUE, {MON: ["Reis"]}) == ["consecutive"]
    assert _kinds(r4, MON, {TUE: ["Reis"]}) == ["consecutive"]
    assert _kinds(r4, THU, {MON: ["Reis"], WED: ["Reis"]}) == ["consecutive", "max_per_week"]


def test_r4_same_day_is_ignored():
    assert R4().allowed("beilage", "Reis", MON, {MON: ["Reis"]})


@pytest.mark.parametrize("mode,blocked", [
    ("workday_adjacent_same_week", False),
    ("workday_adjacent_any", True),
    ("calendar_adjacent", False),
])
def test_r4_friday_to_next_monday(mode, blocked):
    r4 = R4(consecutive_mode=mode)
    assert (not r4.allowed("beilage", "Reis", NEXT_MON, {FRI: ["Reis"]})) is blocked


@pytest.mark.parametrize("mode,adjacent", [
    ("workday_adjacent_same_week", True),
    ("workday_adjacent_any", True),
    ("calendar_adjacent", False),
])
def test_r4_free_day_in_between(mode, adjacent):
    r4 = R4(consecutive_mode=mode, free_days={TUE})
    assert r4.adjacent(MON, WED) is adjacent
    assert (not r4.allowed("beilage", "Reis", WED, {MON: ["Reis"]})) is adjacent
    # without the free day Mon/Wed are never adjacent
    assert not R4(consecutive_mode=mode).adjacent(MON, WED)


def test_r4_other_weeks_irrelevant():
    r4 = R4()
    hist = {PREV_MON: ["Reis"], PREV_WED: ["Reis"], PREV_FRI: ["Reis"]}
    assert r4.allowed("beilage", "Reis", WED, hist)
    assert r4.allowed("beilage", "Reis", MON, hist)        # Fri -> Mon, other ISO week
    assert r4.allowed("beilage", "Reis", FRI, {**hist, MON: ["Reis"], WED: ["Reis"]}) is False


def test_r4_from_config():
    r4 = R4.from_config({"r4": {"max_per_week": 1, "consecutive_mode": "calendar_adjacent"}}, [TUE])
    assert r4.max_per_week == 1 and r4.mode == "calendar_adjacent" and TUE in r4.free_days
    assert _kinds(r4, FRI, {MON: ["Reis"]}) == ["max_per_week"]


def test_r4_check_sequence_synthetic():
    r4 = R4()
    tips = {
        MON: {"vorspeise": ["Arrabbiata"], "hauptspeise": ["Leberkas"], "beilage": ["Reis"]},
        TUE: {"vorspeise": ["Hirten"], "hauptspeise": ["Leberkas"], "beilage": ["Pommes"]},
        WED: {"vorspeise": ["Arrabbiata"], "hauptspeise": ["Gulasch"], "beilage": ["Reis"]},
        FRI: {"vorspeise": ["Arrabbiata"], "hauptspeise": ["Gulasch"], "beilage": ["Spatzlen"]},
    }
    found = sorted((d, v.category, v.dish, v.kind) for d, v in r4.check_sequence(tips))
    assert found == [
        (TUE, "hauptspeise", "Leberkas", "consecutive"),
        (FRI, "vorspeise", "Arrabbiata", "max_per_week"),
    ]


def test_r4_real_history_of_me(dataset):
    me = dataset.me
    assert me == "Johannes Paul III"
    tips = {t.date: t.options for t in dataset.tips_of(me) if t.date <= SNAPSHOT_LAST_SERVED}
    assert len(tips) > 100
    found = [(d, v.category, v.dish, v.kind) for d, v in dataset.r4().check_sequence(tips)]
    assert found == [(D(2026, 7, 3), "beilage", "Reis", "max_per_week")]
