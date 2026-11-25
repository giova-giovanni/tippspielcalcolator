# Ingest-Bericht

Quelle: `Tippspiel Essen.xlsx`

## Blätter

- Blatt 2024: Spieler ['Andreas', 'Johannes', 'Noah'], Daten ab Zeile 3
- Blatt 2025: Spieler ['Andreas', 'Johannes', 'Noah'], Daten ab Zeile 9
- Blatt 2026: Spieler ['Andreas', 'Johannes', 'Noah', 'Giovanni', 'Lorenz'], Daten ab Zeile 9

## Zeilen pro Jahr

| Jahr | serviert | frei | unbekannt (Bo/NV/-) | offen/zukünftig |
|---|---|---|---|---|
| 2024 | 34 | 0 | 0 | 1 |
| 2025 | 221 | 0 | 0 | 0 |
| 2026 | 210 | 19 | 3 | 16 |

## Spieler

- Andreas: 454 Tipps
- Johannes: 435 Tipps
- Noah: 451 Tipps
- Johannes Paul III: 195 Tipps
- Lorenz: 17 Tipps

## Einzigartige Gerichte (kanonisch, nur servierte)

- vorspeise: 65
- hauptspeise: 50
- beilage: 22

## Abweichungen Excel-Punkte vs. Neuberechnung

Neuberechnung = Normalisierung + 'Fisch'-Regel + Alternativen. Excel vergleicht nur exakte Texte.

| Datum | Spieler | Tipp | Menü | Excel | Engine |
|---|---|---|---|---|---|
| 2025-10-09 | Andreas | Spinatknödel / Schweinsschopfbraten / Spatzlen | Tortellini mit Schinken-Rahm / Schweinsschopf / Ofenkartoffeln | 0 | 0.5 |
| 2025-10-09 | Johannes | Schlutzer / Gulasch / Spatzlen | Tortellini mit Schinken-Rahm / Schweinsschopf / Ofenkartoffeln | 3 | 0 |
| 2025-12-19 | Johannes | Carbonara / Cordon Bleu / Pommes | Nudel Mammarosa / Cordon Bleu / Kartoffelsalat | 1 | 0.5 |
| 2026-10-14 | Andreas | Ravioli mit Parmesan-Butter / Schweinsschopfbraten / Püree | Nudel mit Grillgemüseragu / Schweinsschopf / Wedges | 0 | 0.5 |
