"""Paths and configuration loading."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RAW = DATA / "raw"
REPORTS = ROOT / "reports"
DOCS = ROOT / "docs"
SITE_DATA = DOCS / "data"

MENUS_CSV = DATA / "menus.csv"
TIPS_CSV = DATA / "tips.csv"
ALIASES_JSON = DATA / "aliases.json"
CONFIG_JSON = DATA / "config.json"
MODEL_PARAMS_JSON = DATA / "model_params.json"
STATE_JSON = DATA / "state.json"


def load_json(path: Path, default=None):
    if not path.exists():
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def load_config(path: Path = CONFIG_JSON) -> dict:
    return load_json(path, {})


def load_aliases(path: Path = ALIASES_JSON) -> dict:
    return load_json(path, {})
