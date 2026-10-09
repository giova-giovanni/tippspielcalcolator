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
VARIANT_CONNECTORS = ("mit", "und", "in", "im", "auf", "an", "vom", "nach")
HINT_ORDER = {"Tippfehler?": 0, "Variante?": 1, "ähnlich?": 2}


def alias_candidates(names_by_category: dict[str, Counter], normalizer: Normalizer,
                     threshold: float = 88.0) -> dict[str, list[dict]]:
    """Fuzzy *proposals* (never applied automatically).

    A pair (A, B) of names of the same category is proposed when, on lower-cased names,
    ``max(ratio, token_sort_ratio) >= threshold`` (no partial matching: "Gnocchi mit Lachs" vs
    "Omelett mit Schinken und Käse" is not a candidate) **or** when B is A plus a component
    ("Tomatenrisotto" -> "Tomatenrisotto mit Mozzarella").  Pairs that the normalizer already
    maps to the same canonical name and pairs listed in ``keep_separate`` are skipped.
    ``hint``: "Tippfehler?" (Levenshtein distance <= 2), "Variante?" (one name contains the
    other) or "ähnlich?".
    """
    try:
        from rapidfuzz import fuzz
        from rapidfuzz.distance import Levenshtein
        ratio, token_sort, lev = fuzz.ratio, fuzz.token_sort_ratio, Levenshtein.distance
    except ImportError:  # pragma: no cover - rapidfuzz is in requirements.txt
        from difflib import SequenceMatcher

        def ratio(a, b):
            return 100 * SequenceMatcher(None, a, b).ratio()

        def token_sort(a, b):
            return ratio(" ".join(sorted(a.split())), " ".join(sorted(b.split())))

        def lev(a, b):
            prev = list(range(len(b) + 1))
            for i, ca in enumerate(a, 1):
                cur = [i]
                for j, cb in enumerate(b, 1):
                    cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
                prev = cur
            return prev[-1]

    def with_component(short: str, long: str) -> bool:
        """``long`` = ``short`` + " mit/und/… <something>" (word boundary)."""
        if not long.startswith(short + " "):
            return False
        rest = long[len(short) + 1:].split()
        return len(rest) >= 2 and rest[0] in VARIANT_CONNECTORS

    keep_sep = {frozenset((fold(x["a"]), fold(x["b"]))) for x in normalizer.aliases.get("keep_separate", [])}
    out: dict[str, list[dict]] = {}
    for cat, ctr in names_by_category.items():
        names = sorted(n for n, k in ctr.items() if k > 0 and clean(n))
        canon = {}
        for n in names:
            try:
                opts = normalizer.options(n, cat)
            except KeyError:  # unknown category: compare the names as they are
                opts = []
            canon[n] = fold(opts[0]) if len(opts) == 1 else fold(n)
        # compare lower-cased, not casefolded: casefold() turns "ß" into "ss" and would penalise
        # "Lachs" vs "Lachssoße" (ß/ss variants are merged automatically anyway, see fold())
        low = {n: clean(n).lower() for n in names}
        cands = []
        for i, a in enumerate(names):
            fa, la = fold(a), low[a]
            for b in names[i + 1:]:
                fb, lb = fold(b), low[b]
                if fa == fb or canon[a] == canon[b] or frozenset((fa, fb)) in keep_sep:
                    continue
                score = max(ratio(la, lb), token_sort(la, lb))
                short, long = (la, lb) if len(la) <= len(lb) else (lb, la)
                variant = with_component(short, long)
                if score < threshold and not variant:
                    continue
                dist = int(lev(la, lb))
                hint = "Tippfehler?" if dist <= 2 else ("Variante?" if variant or short in long else "ähnlich?")
                cands.append({"a": a, "b": b, "score": round(float(score), 1), "distance": dist, "hint": hint,
                              "count_a": ctr[a], "count_b": ctr[b]})
        cands.sort(key=lambda x: (HINT_ORDER[x["hint"]], -x["score"], x["a"], x["b"]))
        out[cat] = cands
    return out


def write_alias_report(path, raw_counts: dict[str, Counter], normalizer: Normalizer,
                       quirks: list[dict] | None = None) -> None:
    """reports/alias_candidates.md: open decisions, kept-separate pairs, data quirks, applied aliases
    and fuzzy proposals.

    ``quirks`` (optional, computed by :mod:`engine.analyze`): ``[{"was", "tage": [iso dates], "hinweis"}]``
    – data oddities that are not a naming problem (e.g. dishes entered in the wrong column).
    """
    canon_counts: dict[str, Counter] = {}
    for cat, ctr in raw_counts.items():
        c = Counter()
        for raw, n in ctr.items():
            for opt in normalizer.options(raw, cat):
                c[opt] += n
        canon_counts[cat] = c
    cands = alias_candidates(canon_counts, normalizer)
    folded_total: Counter = Counter()
    for ctr in canon_counts.values():
        for name, n in ctr.items():
            folded_total[fold(name)] += n
    lines = ["# Alias-Kandidaten / candidati alias", "",
             "Automatisch erzeugt von `engine/normalize.py`. **Nichts hier wird automatisch zusammengeführt.**",
             "Um zwei Namen zu vereinen, trage die Variante in `data/aliases.json` unter der Kategorie ein; "
             "um einen Vorschlag dauerhaft auszublenden, trage das Paar unter `keep_separate` ein.",
             "Zählung: servierte Menüs + Tipps (fremde Tipps nur vor dem Stichtag, Regel 6).", ""]
    review = normalizer.aliases.get("review", [])
    if review:
        lines += ["## Offene / getroffene Entscheidungen", "", "| Varianten | → kanonisch | Status | Begründung |", "|---|---|---|---|"]
        for r in review:
            lines.append(f"| {', '.join(r['merge'])} | {r['into']} | {r['status']} | {r['why']} |")
        lines.append("")
    ks = normalizer.aliases.get("keep_separate", [])
    if ks:
        lines += ["## Bewusst getrennt gehalten", "",
                  "Diese Paare erscheinen nicht unter den Fuzzy-Vorschlägen. „unklar“ = Entscheidung noch offen.", "",
                  "| A | B | n(A) | n(B) | Warum |", "|---|---|---|---|---|"]
        lines += [f"| {x['a']} | {x['b']} | {folded_total[fold(x['a'])]} | {folded_total[fold(x['b'])]} | {x['why']} |"
                  for x in ks]
        lines.append("")
    if quirks is not None:
        lines += ["## Auffälligkeiten", "",
                  "Keine Namensfrage, sondern Auffälligkeiten in den Daten (werden nicht automatisch korrigiert).", ""]
        if quirks:
            lines += ["| Auffälligkeit | Tage | Hinweis |", "|---|---|---|"]
            lines += [f"| {q['was']} | {', '.join(q.get('tage', []))} | {q.get('hinweis', '')} |" for q in quirks]
        else:
            lines.append("_keine_")
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
    lines += ["## Fuzzy-Vorschläge", "",
              "Kandidaten: max(rapidfuzz `ratio`, `token_sort_ratio`) ≥ 88 auf kleingeschriebenen Namen, oder "
              "„X“ ↔ „X mit/und/vom …“. Ohne bereits zusammengeführte und bewusst getrennte Paare. "
              "Hinweis: **Tippfehler?** = höchstens 2 Zeichen Unterschied (Levenshtein), **Variante?** = ein Name "
              "enthält den anderen, **ähnlich?** = sonst.", ""]
    for cat, items in cands.items():
        lines += [f"### {cat.capitalize()}", ""]
        if not items:
            lines += ["_keine_", ""]
            continue
        lines += ["| A | B | Score | Lev. | Hinweis | n(A) | n(B) |", "|---|---|---|---|---|---|---|"]
        lines += [f"| {c['a']} | {c['b']} | {c['score']} | {c['distance']} | {c['hint']} | {c['count_a']} | {c['count_b']} |"
                  for c in items[:60]]
        if len(items) > 60:
            lines.append(f"\n_… {len(items) - 60} weitere_")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
