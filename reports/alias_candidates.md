# Alias-Kandidaten / candidati alias

Automatisch erzeugt von `engine/normalize.py`. **Nichts hier wird automatisch zusammengeführt.**
Um zwei Namen zu vereinen, trage die Variante in `data/aliases.json` unter der Kategorie ein; um einen Vorschlag dauerhaft auszublenden, trage das Paar unter `keep_separate` ein.
Zählung: servierte Menüs + Tipps (fremde Tipps nur vor dem Stichtag, Regel 6).

## Offene / getroffene Entscheidungen

| Varianten | → kanonisch | Status | Begründung |
|---|---|---|---|
| Truthahnschnitzel mit Champignonsauce, Schnitzel mit Champignonsauce, Schweinsschnitzel mit Champignonsauce | Champignonschnitzel | OFFEN – bitte bestätigen | 2024/Anfang 2025 so notiert, ab 27.02.2025 nur noch 'Champignonschnitzel'; immer mit Reis. Zum Trennen die 3 Zeilen oben in 'hauptspeise' löschen. |
| Penne mamma rosa | Nudel Mammarosa | angenommen | 2024 'Penne mamma rosa', ab 2025 'Nudel Mammarosa'. |
| Kräuterrahmschnitzel | Schweinsschnitzel mit Kräuterrahmsoße | angenommen | gleiches Gericht, andere Schreibweise. |
| Forellenfilet, Lachsforelle | Forelle | Regel 17 | Lachsforelle gilt als Forelle. |
| Puttanesca | Putanesca | angenommen | Schreibweise wie im Excel beibehalten. |

## Bewusst getrennt gehalten

Diese Paare erscheinen nicht unter den Fuzzy-Vorschlägen. „unklar“ = Entscheidung noch offen.

| A | B | n(A) | n(B) | Warum |
|---|---|---|---|---|
| Kartoffelstampf | Püree | 13 | 191 | Entscheidung Johannes Paul III: zwei verschiedene Gerichte (Stampf = grob, mit Stücken). |
| Safranreis | Reis | 1 | 394 | eigene Beilage (zu Ossobuchi). |
| Tomatenrisotto | Tomatenrisotto mit Mozzarella | 4 | 3 | unklar, bleibt getrennt. |
| Röstinchen | Röstkartoffeln | 3 | 118 | unklar, bleibt getrennt. |
| Paprika-Schweinegulasch | Schweinsgulasch | 1 | 14 | unklar, bleibt getrennt. |
| Schweinsfilet mit Pfeffersoße | Schweinsfilet | 2 | 101 | eigene Variante. |
| Spinatknödel mit Käsesoße | Spinatknödel | 5 | 17 | eigene Variante. |
| Schlutzer Schinken-Rahm | Schlutzer | 1 | 72 | eigene Variante. |

## Auffälligkeiten

Keine Namensfrage, sondern Auffälligkeiten in den Daten (werden nicht automatisch korrigiert).

| Auffälligkeit | Tage | Hinweis |
|---|---|---|
| Beilage „Gulasch“ (3×), sonst Hauptspeise (4×); Hauptspeise an diesen Tagen: „Knödel“ | 2025-01-24, 2025-07-30, 2025-12-16 | Spalten Hauptspeise/Beilage vertauscht? Gemeint ist wohl Hauptspeise „Gulasch“ mit Beilage „Knödel“ („Knödel“ kommt als Hauptspeise nur an diesen Tagen vor). Für Statistik/Modell zählt es so, wie es im Excel steht; Korrektur in der Excel-Datei (oder bewusst so lassen). Tipps an diesen Tagen mit einem der Namen: 0. |

## Angewandte Aliase (Rohschreibweise → kanonisch)

### Vorspeise

| Roh | Kanonisch | Anzahl |
|---|---|---|
| `Aglio Olio` | Aglio olio | 48 |
| `Algio Olio` | Aglio olio | 3 |
| `Amatriciana oder Gerstsuppe` | Amatriciana / Gerstsuppe | 1 |
| `Amatriciana oder Nudelsalat` | Amatriciana / Nudelsalat | 1 |
| `Gnocchi mit Tomantensoße` | Gnocchi mit Tomatensoße | 1 |
| `Gnocchi mit Tomantensoße + Mozzarelline` | Gnocchi mit Tomatensoße | 1 |
| `Griesscheiben mit Schinken/Käse und Tomatensoße` | Griesscheiben mit Schinken/Käse und Tomantensoße | 1 |
| `Gulaschsuppe + Nudel mit Käsesoße` | Gulaschsuppe / Nudel mit Käsesoße | 1 |
| `Hirten oder Nudel mit Grillgemüseragu` | Hirten / Nudel mit Grillgemüseragu | 1 |
| `Hirten oder Reissalat` | Hirten / Reissalat | 1 |
| `Nudel Ragu` | Nudel mit Ragu | 1 |
| `Nudel mit Käsesauce` | Nudel mit Käsesoße | 5 |
| `Nudel mit Meeresfrüchte` | Nudel mit Meeresfrüchten | 10 |
| `Nudel mit Ragu oder Aglio olio` | Nudel mit Ragu / Aglio olio | 1 |
| `Nudel mit Thunfisch` | Nudel mit Thunfischsoße | 3 |
| `Nudel mit Tomantensauce` | Nudel mit Tomatensoße | 1 |
| `Nudel mit Tomatensoße und Mozarella / Fleischsuppe` | Nudel mit Tomatensoße und Mozzarella / Fleischsuppe | 1 |
| `Nudel mit ragu` | Nudel mit Ragu | 1 |
| `Nudel mt Ragu` | Nudel mit Ragu | 1 |
| `Omlett mit Schinken und Käse` | Omelett mit Schinken und Käse | 1 |
| `Penne mamma rosa` | Nudel Mammarosa | 2 |
| `Ravioli mit Butter + Parmesan` | Ravioli mit Parmesan-Butter | 9 |
| `Ravioli mit Parmesan + Butter` | Ravioli mit Parmesan-Butter | 7 |
| `Ravioli mit Parmesan+Butter` | Ravioli mit Parmesan-Butter | 1 |
| `Speck-Zwiebelkuchen` | Speck-Zwiebel-Kuchen | 1 |
| `Spinatcanneloni` | Spinatcannelloni | 5 |
| `Spinatspatzlen + Nudelsalat` | Spinatspatzlen / Nudelsalat | 1 |
| `Tomantenrisotto` | Tomatenrisotto | 1 |
| `Tortellini Schinken-Rahm` | Tortellini mit Schinken-Rahm | 3 |

### Hauptspeise

| Roh | Kanonisch | Anzahl |
|---|---|---|
| `Champignonschintzel` | Champignonschnitzel | 2 |
| `Chili con carne` | Chilli con carne | 1 |
| `Chilli con Carne` | Chilli con carne | 7 |
| `Chmpignonschnitzel` | Champignonschnitzel | 2 |
| `Fleischkarpfln` | Fleischkrapfln | 1 |
| `Fleischkrapflen` | Fleischkrapfln | 1 |
| `Forellenfilet` | Forelle | 7 |
| `Frittiertes Pengasiusfilet` | Frittiertes Pangasiusfilet | 3 |
| `Hühnerhaxl` | Hühnerhaxlen | 2 |
| `Hühnnerhaxlen` | Hühnerhaxlen | 1 |
| `Kräuterrahmschnitzel` | Schweinsschnitzel mit Kräuterrahmsoße | 2 |
| `Lachsforelle` | Forelle | 1 |
| `Panierter Pengasius / Wienerschnitzel` | Panierter Pangasius / Wienerschnitzel | 2 |
| `Pizzaioloschnitzel` | Pizzaiolaschnitzel | 30 |
| `Pizzalioloschnitzel` | Pizzaiolaschnitzel | 2 |
| `Rotbarsch` | Rotbarschfilet | 1 |
| `Schnitzel mit Champignonsauce` | Champignonschnitzel | 1 |
| `Schweinschnitzel` | Schweinsschnitzel | 1 |
| `Schweinschopf` | Schweinsschopf | 7 |
| `Schweinshax` | Schweinshaxe | 2 |
| `Schweinsschnitzel mit Champignonsauce` | Champignonschnitzel | 1 |
| `Schweinsschopf-braten` | Schweinsschopf | 6 |
| `Schweinsschopfbraten` | Schweinsschopf | 30 |
| `Spareribs` | Sparerips | 1 |
| `Truthahn-geschnetzeltes` | Truthahngeschnetzeltes | 2 |
| `Truthahnschnitzel mit Champignonsauce` | Champignonschnitzel | 7 |
| `Vitello tonato` | Vitello tonnato | 2 |
| `Zigeunerschnitzel / Osso buchi` | Zigeunerschnitzel / Ossobuchi | 1 |

### Beilage

| Roh | Kanonisch | Anzahl |
|---|---|---|
| `Bratkaroffeln` | Bratkartoffeln | 1 |
| `Bratkartoffel` | Bratkartoffeln | 1 |
| `Kartoffegratin` | Kartoffelgratin | 1 |
| `Kartoffelwedges` | Wedges | 1 |
| `Kroketten und Zucchini` | Kroketten / Zucchini | 1 |
| `Ofenkaroffel` | Ofenkartoffeln | 1 |
| `Plent und Kraut` | Plent / Kraut | 1 |
| `Püree + Peperonata` | Püree / Peperonata | 1 |
| `Pürree` | Püree | 9 |
| `Röstinchen und Peperonata` | Röstinchen / Peperonata | 1 |
| `Salzkartoffel` | Salzkartoffeln | 2 |
| `Spatzlen (und Blaukraut)` | Spatzlen | 2 |

## Fuzzy-Vorschläge

Kandidaten: max(rapidfuzz `ratio`, `token_sort_ratio`) ≥ 88 auf kleingeschriebenen Namen, oder „X“ ↔ „X mit/und/vom …“. Ohne bereits zusammengeführte und bewusst getrennte Paare. Hinweis: **Tippfehler?** = höchstens 2 Zeichen Unterschied (Levenshtein), **Variante?** = ein Name enthält den anderen, **ähnlich?** = sonst.

### Vorspeise

| A | B | Score | Lev. | Hinweis | n(A) | n(B) |
|---|---|---|---|---|---|---|
| Nudel mit Lachs | Nudel mit Lachssoße | 88.2 | 4 | Variante? | 12 | 2 |
| Nudel mit Tomatensoße | Nudel mit Tomatensoße und Schinken | 76.4 | 13 | Variante? | 2 | 1 |
| Nudel mit Tomatensoße | Nudel mit Tomatensoße und Mozzarella | 73.7 | 15 | Variante? | 2 | 5 |
| Nudel mit Lachs | Nudel mit Lachs und Rahmsoße | 69.8 | 13 | Variante? | 12 | 1 |
| Nudel mit Lachs | Nudel mit Lachs und Tomantensoße | 63.8 | 17 | Variante? | 12 | 1 |
| Gnocchi | Gnocchi mit Ragu | 60.9 | 9 | Variante? | 6 | 1 |
| Gnocchi | Gnocchi mit Lachs | 58.3 | 10 | Variante? | 6 | 1 |
| Spinatknödel | Spinatknödel mit Gorgonzolasoße | 55.8 | 19 | Variante? | 17 | 1 |
| Gnocchi | Gnocchi mit Käsesoße | 51.9 | 13 | Variante? | 6 | 8 |
| Ravioli | Ravioli mit Käsesoße | 51.9 | 13 | Variante? | 2 | 1 |
| Gnocchi | Gnocchi mit Tomatensoße | 46.7 | 16 | Variante? | 6 | 22 |
| Gnocchi | Gnocchi mit Kräutersauce | 45.2 | 17 | Variante? | 6 | 1 |
| Ravioli | Ravioli mit Tomantensoße | 45.2 | 17 | Variante? | 2 | 1 |
| Gnocchi | Gnocchi mit Gorgonzolasoße | 42.4 | 19 | Variante? | 6 | 2 |
| Ravioli | Ravioli mit Parmesan-Butter | 41.2 | 20 | Variante? | 2 | 36 |

### Hauptspeise

| A | B | Score | Lev. | Hinweis | n(A) | n(B) |
|---|---|---|---|---|---|---|
| Truthahnschnitzel | Truthahnschnitzel vom Grill | 77.3 | 10 | Variante? | 121 | 3 |
| Schweinsschnitzel | Schweinsschnitzel mit Kräuterrahmsoße | 63.0 | 20 | Variante? | 45 | 19 |
| Pangasiusfilet | Pangasiusfilet mit Kräuterrahmsoße | 58.3 | 20 | Variante? | 1 | 1 |

### Beilage

_keine_

