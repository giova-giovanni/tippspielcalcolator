"""Tests for engine/normalize.py with the real data/aliases.json."""
from __future__ import annotations

import pytest

from engine.normalize import Normalizer, clean, fold

V, H, B = "vorspeise", "hauptspeise", "beilage"


@pytest.mark.parametrize("cat,raw,expected", [
    (V, "Nudel mit Käsesauce", ["Nudel mit Käsesoße"]),
    (V, "Nudel Ragu", ["Nudel mit Ragu"]),
    (V, "Ravioli mit Parmesan + Butter", ["Ravioli mit Parmesan-Butter"]),   # whole-cell alias, not split
    (V, "Gulaschsuppe + Nudel mit Käsesoße", ["Gulaschsuppe", "Nudel mit Käsesoße"]),
    (H, "Truthahn-geschnetzeltes", ["Truthahngeschnetzeltes"]),
    (H, "Lachsforelle", ["Forelle"]),
    (B, "Pürree", ["Püree"]),
    (B, "Kartoffelstampf", ["Kartoffelstampf"]),                            # user decision: != Püree
    (B, "Spatzlen (und Blaukraut)", ["Spatzlen"]),
    (B, "Pommes / Kartoffelsalat", ["Pommes", "Kartoffelsalat"]),
    (B, "  Reis  ", ["Reis"]),
])
def test_options(norm, cat, raw, expected):
    assert norm.options(raw, cat) == expected
    assert norm.canonical(raw, cat) == expected[0]


def test_aglio_olio_case_variants(norm):
    assert norm.options("Aglio olio", V) == norm.options("Aglio Olio", V) == norm.options("aglio OLIO", V)


def test_kartoffelstampf_is_not_pueree(norm):
    assert norm.options("Kartoffelstampf", B) != norm.options("Püree", B)


@pytest.mark.parametrize("variants", [
    ["Schweinsschopf-braten", "Schweinsschopfbraten", "Schweinsschopf"],
    ["Pizzaioloschnitzel", "Pizzalioloschnitzel"],
])
def test_hauptspeise_variants_merge(norm, variants):
    canon = {tuple(norm.options(v, H)) for v in variants}
    assert len(canon) == 1 and len(next(iter(canon))) == 1


@pytest.mark.parametrize("raw", ["-", "Bo", "NV", "", None, "  "])
def test_missing_tokens(norm, raw):
    for cat in (V, H, B):
        assert norm.options(raw, cat) == []
        assert norm.canonical(raw, cat) == ""
    assert norm.is_missing(raw)
    assert not norm.is_free(raw)


def test_free_token(norm):
    assert norm.is_free("Frei") and norm.is_free("frei")
    assert norm.options("Frei", V) == []
    assert not norm.is_missing("Frei")


def test_plus_is_not_a_separator_for_hauptspeise(norm):
    assert norm.options("Rindsbraten / Scombri", H) == ["Rindsbraten", "Scombri"]
    assert len(norm.options("Rindsbraten + Scombri", H)) == 1


def test_fish_classification(norm):
    assert norm.is_fish("Rotbarschfilet")
    assert norm.is_fish("Forelle") and norm.is_fish("Panierter Pangasius")
    assert norm.is_fish("Scombri")
    assert not norm.is_fish("Vitello tonnato")
    assert not norm.is_fish("Leberkas")
    assert norm.is_generic_fish_ok("Rotbarschfilet")
    assert not norm.is_generic_fish_ok("Scombri")


def test_model_label(norm):
    assert norm.model_label("Rotbarschfilet", H, lent=False) == "Fisch"
    assert norm.model_label("Rotbarschfilet", H, lent=True) == "Rotbarschfilet"
    assert norm.model_label("Scombri", H, lent=False) == "Scombri"
    assert norm.model_label("Scombri", H, lent=True) == "Scombri"
    assert norm.model_label("Leberkas", H, lent=False) == "Leberkas"
    assert norm.model_label("Vitello tonnato", H, lent=False) == "Vitello tonnato"
    assert norm.model_label("Nudel mit Thunfischsoße", V, lent=False) == "Nudel mit Thunfischsoße"


def test_fit_picks_most_frequent_spelling():
    n = Normalizer().fit({V: ["Hirten", "hirten", "Hirten", "HIRTEN"]})
    assert n.options("hIrTeN", V) == ["Hirten"]
    # alias targets always win over the observed spelling
    n2 = Normalizer().fit({V: ["Aglio Olio"] * 5})
    assert n2.options("Aglio Olio", V) == ["Aglio olio"]


def test_clean_and_fold():
    assert clean("  Nudel   mit   Ragu ") == "Nudel mit Ragu"
    assert clean(None) == "" and clean(True) == "" and clean(3.0) == "3"
    assert fold("ÄÖÜ") == "äöü"
    assert fold("Käsesoße") == fold("KÄSESOSSE")  # casefold: ß == ss


def test_dataset_normalizer_consistent(dataset):
    """The fitted normalizer of the real data keeps the alias decisions."""
    n = dataset.norm
    assert n.options("Pommes / Kartoffelsalat", B) == ["Pommes", "Kartoffelsalat"]
    assert n.options("Kartoffelstampf", B) == ["Kartoffelstampf"]
    assert n.options("Aglio Olio", V) == ["Aglio olio"]
