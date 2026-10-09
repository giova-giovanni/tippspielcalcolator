"""Tests for engine/dates.py: Easter/Lent, Excel serials, ISO weeks, working days."""
from __future__ import annotations

import datetime as dt

import pytest

from engine.dates import (ash_wednesday, easter, is_lent, lent_range, next_workday, to_date, week_key,
                          week_monday, week_workdays)

D = dt.date


@pytest.mark.parametrize("year,ash,east", [
    (2024, D(2024, 2, 14), D(2024, 3, 31)),
    (2025, D(2025, 3, 5), D(2025, 4, 20)),
    (2026, D(2026, 2, 18), D(2026, 4, 5)),
    (2027, D(2027, 2, 10), D(2027, 3, 28)),
])
def test_easter_and_ash_wednesday(year, ash, east):
    assert easter(year) == east
    assert ash_wednesday(year) == ash
    assert lent_range(year) == (ash, east)
    assert easter(year).weekday() == 6 and ash_wednesday(year).weekday() == 2


@pytest.mark.parametrize("day,lent", [
    (D(2026, 2, 17), False),   # Faschingsdienstag
    (D(2026, 2, 18), True),    # Aschermittwoch
    (D(2026, 3, 6), True),
    (D(2026, 4, 3), True),     # Karfreitag
    (D(2026, 4, 5), True),     # Ostersonntag (inklusive)
    (D(2026, 4, 6), False),    # Ostermontag
    (D(2025, 3, 4), False),
    (D(2025, 3, 5), True),
    (D(2025, 4, 20), True),
    (D(2025, 4, 21), False),
    (D(2025, 11, 7), False),
])
def test_is_lent_boundaries(day, lent):
    assert is_lent(day) is lent


@pytest.mark.parametrize("value,expected", [
    (46034, D(2026, 1, 12)),
    (46034.0, D(2026, 1, 12)),
    ("46034", D(2026, 1, 12)),
    ("2026-01-12", D(2026, 1, 12)),
    ("2026-01-12T00:00:00", D(2026, 1, 12)),
    ("12.01.2026", D(2026, 1, 12)),
    ("12/01/2026", D(2026, 1, 12)),
    (dt.datetime(2026, 1, 12, 0, 0), D(2026, 1, 12)),
    (D(2026, 1, 12), D(2026, 1, 12)),
    (None, None),
    ("", None),
    ("kein Datum", None),
])
def test_to_date(value, expected):
    assert to_date(value) == expected


@pytest.mark.parametrize("day,key", [
    (D(2026, 10, 5), (2026, 41)),
    (D(2026, 10, 9), (2026, 41)),
    (D(2026, 10, 12), (2026, 42)),
    (D(2024, 12, 30), (2025, 1)),    # ISO year != calendar year
    (D(2027, 1, 1), (2026, 53)),
])
def test_week_key(day, key):
    assert week_key(day) == key


def test_week_helpers():
    assert week_monday(D(2026, 10, 9)) == D(2026, 10, 5)
    assert week_workdays(D(2026, 10, 7)) == [D(2026, 10, 5 + i) for i in range(5)]
    assert next_workday(D(2026, 10, 9)) == D(2026, 10, 12)                       # Fri -> Mon
    assert next_workday(D(2026, 10, 9), {D(2026, 10, 12)}) == D(2026, 10, 13)   # Monday free
    assert next_workday(D(2026, 10, 6)) == D(2026, 10, 7)
