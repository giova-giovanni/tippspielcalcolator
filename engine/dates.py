"""Date helpers: Easter / Lent, ISO weeks, working-day adjacency."""
from __future__ import annotations

import datetime as dt
from functools import lru_cache

WEEKDAYS_DE = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
WEEKDAYS_DE_LONG = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
WEEKDAYS_IT = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]

EXCEL_EPOCH = dt.date(1899, 12, 30)


def excel_serial_to_date(serial: float) -> dt.date:
    return EXCEL_EPOCH + dt.timedelta(days=int(serial))


def to_date(value) -> dt.date | None:
    """Accept datetime/date/ISO string/Excel serial and return a date."""
    if value is None or value == "":
        return None
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    if isinstance(value, (int, float)):
        return excel_serial_to_date(value)
    s = str(value).strip()
    try:
        return dt.date.fromisoformat(s[:10])
    except ValueError:
        pass
    for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%d.%m.%y"):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    try:
        return excel_serial_to_date(float(s))
    except ValueError:
        return None


@lru_cache(maxsize=None)
def easter(year: int) -> dt.date:
    """Gregorian Easter Sunday (anonymous Gregorian algorithm)."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return dt.date(year, month, day)


def ash_wednesday(year: int) -> dt.date:
    return easter(year) - dt.timedelta(days=46)


def lent_range(year: int) -> tuple[dt.date, dt.date]:
    """Fastenzeit: Aschermittwoch bis Ostersonntag (inklusive)."""
    return ash_wednesday(year), easter(year)


def is_lent(day: dt.date) -> bool:
    start, end = lent_range(day.year)
    return start <= day <= end


def week_key(day: dt.date) -> tuple[int, int]:
    iso = day.isocalendar()
    return iso[0], iso[1]


def week_monday(day: dt.date) -> dt.date:
    return day - dt.timedelta(days=day.weekday())


def week_workdays(day: dt.date) -> list[dt.date]:
    mon = week_monday(day)
    return [mon + dt.timedelta(days=i) for i in range(5)]


def season_end(year: int, mmdd: str = "12-23") -> dt.date:
    m, d = (int(x) for x in mmdd.split("-"))
    return dt.date(year, m, d)


def next_workday(day: dt.date, free_days: set[dt.date] | None = None) -> dt.date:
    free_days = free_days or set()
    d = day + dt.timedelta(days=1)
    while d.weekday() >= 5 or d in free_days:
        d += dt.timedelta(days=1)
    return d


def season_phase(day: dt.date) -> str:
    """Grobe Jahreszeit für die Saisonanalyse."""
    m = day.month
    if m in (12, 1, 2):
        return "Winter"
    if m in (3, 4, 5):
        return "Frühling"
    if m in (6, 7, 8):
        return "Sommer"
    return "Herbst"
