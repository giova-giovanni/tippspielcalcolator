"""docs/piano/dish_nutrition.json (Piano): struttura, valori plausibili, copertura dei menù.

Regole concordate:
* il test fallisce SOLO se il file è malformato o un valore non è plausibile
  (es. 0 kcal o più di 1500 kcal per piatto);
* un piatto di data/menus.csv che non è in tabella non fa mai fallire il test: lo coprono le
  regole di riserva (regex) oppure prende la media della sua categoria. Esce solo come avviso.

La ricerca qui sotto replica quella del sito (docs/piano-core.js → dishInfo).
"""
from __future__ import annotations

import csv
import json
import re
import warnings
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "docs" / "piano" / "dish_nutrition.json"
MENUS_CSV = ROOT / "data" / "menus.csv"
CATS = ("vorspeise", "hauptspeise", "beilage")
KCAL_MIN, KCAL_MAX = 1, 1500
PROT_MIN, PROT_MAX = 0, 150


def fold(s) -> str:
    """Come fold() del sito: NBSP → spazio, spazi compattati, minuscolo, ß → ss."""
    s = re.sub(r"\s+", " ", str(s or "").replace(" ", " ")).strip()
    return s.lower().replace("ß", "ss")


@pytest.fixture(scope="module")
def table() -> dict:
    with open(TABLE, encoding="utf-8") as f:
        return json.load(f)


def _plausible(where: str, entry: dict, tags: set, need_values: bool = True) -> None:
    assert isinstance(entry, dict), f"{where}: deve essere un oggetto"
    for key, lo, hi in (("kcal", KCAL_MIN, KCAL_MAX), ("prot", PROT_MIN, PROT_MAX)):
        if key not in entry:
            assert not need_values, f"{where}: manca {key}"
            continue
        v = entry[key]
        assert isinstance(v, (int, float)) and not isinstance(v, bool), f"{where}: {key} non numerico ({v!r})"
        assert lo <= v <= hi, f"{where}: {key} = {v} fuori dall'intervallo plausibile [{lo}, {hi}]"
    t = entry.get("tags", [])
    assert isinstance(t, list), f"{where}: tags deve essere una lista"
    unknown = [x for x in t if x not in tags]
    assert not unknown, f"{where}: tag sconosciuti {unknown}"


def category_means(table: dict) -> dict:
    out = {}
    for c in CATS:
        vals = list(table["dishes"][c].values())
        out[c] = {
            "kcal": round(sum(v["kcal"] for v in vals) / len(vals) / 10) * 10,
            "prot": round(sum(v["prot"] for v in vals) / len(vals)),
        }
    return out


def resolve(table: dict, cat: str, name: str) -> tuple[str, int, int]:
    """(fonte, kcal, prot) con fonte = 'table' | 'rule' | 'default'."""
    k = fold(name)
    for n, e in table["dishes"][cat].items():
        if fold(n) == k:
            return "table", e["kcal"], e["prot"]
    means = category_means(table)[cat]
    for r in table["rules"]:
        if r.get("cat") not in (None, cat):
            continue
        if re.search(r["match"], k, re.IGNORECASE):
            return "rule", r.get("kcal", means["kcal"]), r.get("prot", means["prot"])
    return "default", means["kcal"], means["prot"]


def test_structure_and_values(table):
    assert table.get("version") == 1
    tags = table.get("tags")
    assert isinstance(tags, list) and tags and all(isinstance(x, str) for x in tags)
    tagset = set(tags)
    for key in ("fritto", "impanato", "cremoso", "carne_grassa"):  # usati dalle regole del livello
        assert key in tagset
    dishes = table.get("dishes")
    assert isinstance(dishes, dict) and set(dishes) == set(CATS)
    for c in CATS:
        assert isinstance(dishes[c], dict) and dishes[c], f"categoria vuota: {c}"
        seen = {}
        for name, entry in dishes[c].items():
            assert isinstance(name, str) and name.strip(), f"{c}: nome vuoto"
            _plausible(f"{c} / {name}", entry, tagset)
            k = fold(name)
            assert k not in seen, f"{c}: '{name}' e '{seen[k]}' sono lo stesso piatto"
            seen[k] = name
    about = table.get("about", {})
    assert about.get("de") and about.get("it")


def test_rules_are_valid(table):
    tagset = set(table["tags"])
    rules = table.get("rules")
    assert isinstance(rules, list) and rules
    for i, r in enumerate(rules):
        where = f"regola {i} ({r.get('match')!r})"
        assert r.get("cat") in (None, *CATS), f"{where}: categoria non valida"
        assert isinstance(r.get("match"), str) and r["match"], f"{where}: match vuoto"
        re.compile(r["match"])  # deve compilare anche in Python (il sito usa RegExp con lo stesso testo)
        assert r["match"] == r["match"].lower(), f"{where}: scrivere il pattern in minuscolo (i nomi sono confrontati dopo fold)"
        _plausible(where, r, tagset, need_values=False)


def test_category_means_plausible(table):
    for c, m in category_means(table).items():
        assert KCAL_MIN <= m["kcal"] <= KCAL_MAX and PROT_MIN <= m["prot"] <= PROT_MAX, c


@pytest.mark.parametrize("cat,name,source", [
    ("vorspeise", "nudel mit käsesosse", "table"),          # maiuscole e ß indifferenti
    ("hauptspeise", "Puten-Cordon-Bleu", "rule"),
    ("hauptspeise", "Hendlschnitzel", "rule"),
    ("vorspeise", "Tomatencremesuppe", "rule"),
    ("beilage", "Süßkartoffel-Pommes", "rule"),
    ("vorspeise", "Xyz", "default"),
])
def test_resolve_examples(table, cat, name, source):
    assert resolve(table, cat, name)[0] == source


def test_menu_dishes_covered(table):
    """Ogni piatto servito ha una stima plausibile; quelli fuori tabella escono come avviso."""
    if not MENUS_CSV.exists():
        pytest.skip("data/menus.csv non trovato")
    names = {c: set() for c in CATS}
    with open(MENUS_CSV, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if (row.get("status") or "").strip() != "served":
                continue
            for c in CATS:
                for opt in (row.get(f"{c}_norm") or "").split(" / "):
                    if opt.strip():
                        names[c].add(opt.strip())
    via_rule, via_default = [], []
    for c in CATS:
        for n in sorted(names[c]):
            source, kcal, prot = resolve(table, c, n)
            assert KCAL_MIN <= kcal <= KCAL_MAX and PROT_MIN <= prot <= PROT_MAX, (c, n)
            if source == "rule":
                via_rule.append(f"{c}: {n}")
            elif source == "default":
                via_default.append(f"{c}: {n}")
    if via_rule or via_default:
        warnings.warn(
            "Piatti non in docs/piano/dish_nutrition.json – "
            f"coperti da una regola: {via_rule or '-'}; con la media della categoria: {via_default or '-'}",
            UserWarning,
        )
