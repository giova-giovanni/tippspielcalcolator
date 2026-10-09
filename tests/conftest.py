"""Shared pytest fixtures.

Rules for every test in this folder:
* fast and offline (no network);
* never write into ``data/``, ``docs/data`` or ``reports/`` – copy files to ``tmp_path`` first
  (see the ``data_copy`` fixture).
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:  # `pytest` without `python -m` and without pytest.ini
    sys.path.insert(0, str(ROOT))

DATA = ROOT / "data"
WORKBOOK = DATA / "raw" / "Tippspiel Essen.xlsx"


@pytest.fixture(scope="session")
def root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def norm():
    """Normalizer with the real data/aliases.json (not fitted)."""
    from engine.normalize import Normalizer

    return Normalizer()


@pytest.fixture(scope="session")
def dataset():
    """The real dataset (data/menus.csv + data/tips.csv), loaded read-only."""
    from engine.data import load_dataset

    return load_dataset()


@pytest.fixture(scope="session")
def workbook_path() -> Path:
    if not WORKBOOK.exists():
        pytest.skip(f"{WORKBOOK} fehlt")
    return WORKBOOK


@pytest.fixture()
def data_copy(tmp_path) -> Path:
    """Copy of data/*.csv + json in a temp dir, for tests that need to write."""
    dst = tmp_path / "data"
    dst.mkdir()
    for p in DATA.iterdir():
        if p.is_file() and p.suffix in (".csv", ".json"):
            shutil.copy2(p, dst / p.name)
    return dst
