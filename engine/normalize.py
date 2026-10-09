"""Normalisation of dish names.

Pipeline for one raw cell of a category:

1. collapse whitespace; missing tokens (``-``, ``Bo``, ``NV`` …) -> no options;
   ``Frei`` -> free day
2. whole-cell alias lookup (case-insensitive) – lets ``Ravioli mit Parmesan + Butter``
   survive although ``+`` is a separator
3. split into announced options (``A / B``, ``A oder B`` …), strip components
   such as ``(und Blaukraut)`` (rule 9.8)
4. per-option alias lookup, then automatic merge of pure case/whitespace variants
   (Excel compares case-insensitively, too)

Nothing else is merged automatically; :func:`alias_candidates` only *proposes*.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Iterable

from . import CATEGORIES
from .config import load_aliases

FREE = "__FREE__"


def clean(value) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return ""
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    s = str(value).replace(" ", " ")
    return re.sub(r"\s+", " ", s).strip()


def fold(s: str) -> str:
    return clean(s).casefold()


class Normalizer:
    def __init__(self, aliases: dict | None = None):
        self.aliases = aliases if aliases is not None else load_aliases()
        a = self.aliases
        self.missing = {fold(t) for t in a.get("missing_tokens", [])} | {""}
        self.free = {fold(t) for t in a.get("free_tokens", ["Frei"])}
        self.separators = {c: a.get("option_separators", {}).get(c, [" / "]) for c in CATEGORIES}
        self.strip_res = [re.compile(p, re.IGNORECASE) for p in a.get("strip_patterns", [])]
        self.alias_map: dict[str, dict[str, object]] = {}
        for cat in CATEGORIES:
            self.alias_map[cat] = {fold(k): v for k, v in a.get(cat, {}).items()}
        fish = a.get("fish", {})
        self.fish_label = fish.get("generic_label", "Fisch")
        self.fish_exact = {fold(x) for x in fish.get("always_exact", [])}
        self.fish_dishes = {fold(x) for x in fish.get("dishes", [])}
        self.fish_keywords = [k.casefold() for k in fish.get("keywords", [])]
        self.not_fish = {fold(x) for x in fish.get("not_fish", [])}
        # casefold -> preferred spelling, built by fit(); alias targets always win
        self.display: dict[str, dict[str, str]] = {c: {} for c in CATEGORIES}
        for cat in CATEGORIES:
            for v in a.get(cat, {}).values():
                for t in v if isinstance(v, list) else [v]:
                    self.display[cat][fold(t)] = clean(t)
        self.display["hauptspeise"].setdefault(fold(self.fish_label), self.fish_label)

    # ------------------------------------------------------------------ fit
    def fit(self, names_by_category: dict[str, Iterable[str]]) -> "Normalizer":
        """Choose the most frequent spelling for every case/whitespace variant group."""
        for cat, names in names_by_category.items():
            counts: dict[str, Counter] = defaultdict(Counter)
            for raw in names:
                for opt in self._options_raw(raw, cat):
                    counts[fold(opt)][opt] += 1
            for key, ctr in counts.items():
                if key not in self.display[cat]:
                    best = sorted(ctr.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
                    self.display[cat][key] = best
        return self

    # ------------------------------------------------------------ classify
    def is_missing(self, raw) -> bool:
        return fold(clean(raw)) in self.missing

    def is_free(self, raw) -> bool:
        return fold(clean(raw)) in self.free

    def _apply_alias(self, s: str, cat: str):
        return self.alias_map[cat].get(fold(s))

    def _strip(self, s: str) -> str:
        for rx in self.strip_res:
            s = rx.sub("", s)
        return clean(s)

    def _options_raw(self, raw, cat: str) -> list[str]:
        s = clean(raw)
        if fold(s) in self.missing or fold(s) in self.free:
            return []
        whole = self._apply_alias(s, cat)
        if whole is not None:
            return [clean(x) for x in (whole if isinstance(whole, list) else [whole])]
        parts = [s]
        for sep in self.separators[cat]:
            nxt = []
            for p in parts:
                nxt.extend(re.split(re.escape(sep), p, flags=re.IGNORECASE) if sep.strip() else [p])
            parts = nxt
        out = []
        for p in parts:
            p = self._strip(p)
            if not p or fold(p) in self.missing:
                continue
            al = self._apply_alias(p, cat)
            if al is not None:
                out.extend(clean(x) for x in (al if isinstance(al, list) else [al]))
            else:
                out.append(p)
        return out

    def options(self, raw, cat: str) -> list[str]:
        """Canonical announced options of a cell (first = primary)."""
        res: list[str] = []
        for opt in self._options_raw(raw, cat):
            name = self.display[cat].get(fold(opt), opt)
            if name not in res:
                res.append(name)
        return res

    def canonical(self, raw, cat: str) -> str:
        """Primary canonical name ('' if missing)."""
        opts = self.options(raw, cat)
        return opts[0] if opts else ""

    # ----------------------------------------------------------------- fish
    def is_fish(self, name: str) -> bool:
        k = fold(name)
        if not k or k in self.not_fish:
            return False
        if k == fold(self.fish_label) or k in self.fish_dishes or k in self.fish_exact:
            return True
        return any(kw in k for kw in self.fish_keywords)

    def is_generic_fish_ok(self, name: str) -> bool:
        """Fish dish that may be tipped as generic 'Fisch' outside Lent."""
        k = fold(name)
        return self.is_fish(name) and k not in self.fish_exact and k != fold(self.fish_label)

    def model_label(self, name: str, cat: str, lent: bool) -> str:
        """Label used by the models: fish grouped into 'Fisch' outside Lent (rule 9.6)."""
        if cat == "hauptspeise" and not lent and self.is_generic_fish_ok(name):
            return self.fish_label
        return name


# ---------------------------------------------------------------- reporting
def alias_candidates(names_by_category: dict[str, Counter], normalizer: Normalizer,
                     threshold: float = 85.0) -> dict[str, list[dict]]:
    """Fuzzy *proposals* (never applied automatically)."""
    try:
        from rapidfuzz import fuzz
    except ImportError:  # pragma: no cover
        from difflib import SequenceMatcher

        class fuzz:  # type: ignore
            @staticmethod
            def WRatio(a, b):
                return 100 * SequenceMatcher(None, a, b).ratio()

    keep_sep = {frozenset((fold(x["a"]), fold(x["b"]))) for x in normalizer.aliases.get("keep_separate", [])}
    out: dict[str, list[dict]] = {}
    for cat, ctr in names_by_category.items():
        names = sorted(ctr)
        cands = []
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                if frozenset((fold(a), fold(b))) in keep_sep:
                    continue
                score = fuzz.WRatio(a.casefold(), b.casefold())
                if score >= threshold:
                    cands.append({"a": a, "b": b, "score": round(float(score), 1),
                                  "count_a": ctr[a], "count_b": ctr[b]})
        cands.sort(key=lambda x: -x["score"])
        out[cat] = cands
    return out


def write_alias_report(path, raw_counts: dict[str, Counter], normalizer: Normalizer) -> None:
    """reports/alias_candidates.md: applied aliases, open decisions and fuzzy proposals."""
    canon_counts: dict[str, Counter] = {}
    for cat, ctr in raw_counts.items():
        c = Counter()
        for raw, n in ctr.items():
            for opt in normalizer.options(raw, cat):
                c[opt] += n
        canon_counts[cat] = c
    cands = alias_candidates(canon_counts, normalizer)
    lines = ["# Alias-Kandidaten / candidati alias", "",
             "Automatisch erzeugt von `engine/normalize.py`. **Nichts hier wird automatisch zusammengeführt.**",
             "Um zwei Namen zu vereinen, trage die Variante in `data/aliases.json` unter der Kategorie ein.", ""]
    review = normalizer.aliases.get("review", [])
    if review:
        lines += ["## Offene / getroffene Entscheidungen", "", "| Varianten | → kanonisch | Status | Begründung |", "|---|---|---|---|"]
        for r in review:
            lines.append(f"| {', '.join(r['merge'])} | {r['into']} | {r['status']} | {r['why']} |")
        lines.append("")
    ks = normalizer.aliases.get("keep_separate", [])
    if ks:
        lines += ["## Bewusst getrennt gehalten", "", "| A | B | Warum |", "|---|---|---|"]
        lines += [f"| {x['a']} | {x['b']} | {x['why']} |" for x in ks]
        lines.append("")
    lines += ["## Angewandte Aliase (Rohschreibweise → kanonisch)", ""]
    for cat, ctr in raw_counts.items():
        applied = []
        for raw, n in sorted(ctr.items()):
            opts = normalizer.options(raw, cat)
            if opts and " / ".join(opts) != clean(raw):
                applied.append(f"| `{clean(raw)}` | {' / '.join(opts)} | {n} |")
        if applied:
            lines += [f"### {cat.capitalize()}", "", "| Roh | Kanonisch | Anzahl |", "|---|---|---|", *applied, ""]
    lines += ["## Fuzzy-Vorschläge (rapidfuzz WRatio ≥ 85)", ""]
    for cat, items in cands.items():
        lines += [f"### {cat.capitalize()}", ""]
        if not items:
            lines += ["_keine_", ""]
            continue
        lines += ["| A | B | Score | n(A) | n(B) |", "|---|---|---|---|---|"]
        lines += [f"| {c['a']} | {c['b']} | {c['score']} | {c['count_a']} | {c['count_b']} |" for c in items[:60]]
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
