# Analyse Tippspiel Essen Wies

_Automatisch erzeugt von `engine/analyze.py` am 2026-11-27 09:02 UTC (Stichtag 2026-11-27). Datenstand: 467 servierte Menüs (2024: 34, 2025: 221, 2026: 212), letztes Menü 2026-11-26._

## Riassunto (IT)

- **Dati**: 467 menù serviti (2024: 34, 2025: 221, 2026: 212); piatti distinti: primo 62, secondo 49, contorno 20.
- **Primo più frequenti**: Arrabbiata (32), Nudel mit Käsesoße (31), Hirten (30); i primi 5 coprono 32 % dei giorni.
- **Secondo più frequenti**: Hühnerbrust (33), Champignonschnitzel (30), Truthahngeschnetzeltes (28); i primi 5 coprono 31 % dei giorni.
- **Contorno più frequenti**: Reis (104), Pommes (61), Spatzlen (48); i primi 5 coprono 64 % dei giorni.
- **Ripetizioni**: la cucina evita le ripetizioni. Primo e secondo: mai due volte nella stessa settimana (0 e 0 coppie contro 40 e 40 attese per caso, p < 0,001); quasi nessuna ripetizione entro 5 (primo) / 3 (secondo) giorni lavorativi; intervallo mediano 17 / 19 giorni lavorativi. Il contorno si ripete molto di più (18 coppie nella stessa settimana, 104 attese per caso). → Non tippare primo/secondo serviti negli ultimi giorni o già serviti questa settimana.
- **Giorno della settimana**: Reis (contorno) il lunedì 45/104 (atteso 19 %, p < 0,001); Schweinskotelett (secondo) il mercoledì 13/17 (atteso 21 %, p < 0,001); Arrabbiata (primo) il lunedì 18/32 (atteso 19 %, p < 0,001); Champignonschnitzel (secondo) il lunedì 17/30 (atteso 19 %, p < 0,001). 4 effetti restano significativi anche con correzione di Bonferroni: il giorno della settimana conta.
- **Ipotesi confermate**: pesce (tutti) il venerdì 11/13; pesce fuori Quaresima il venerdì 3/3; Plent (polenta) il venerdì 10/21. Non confermate: Scombri, Leberkas.
- **Contorno ↔ secondo**: conoscendo il secondo, il contorno più tipico è giusto nel 50 % dei casi (leave-one-out) contro 22 % tippando sempre Reis (es. Champignonschnitzel → Reis 77 %, Wienerschnitzel → Kartoffelsalat 83 %, Chilli con carne → Reis 100 %, Hühnerhaxlen → Pommes 67 %). Primo e secondo invece sono quasi indipendenti (MI 1,67 bit vs 1,63 per caso, p = 0,150).
- **Quaresima / pesce**: pesce in Quaresima nel 16 % dei giorni contro 1 % fuori (10 vs 3 giorni). Nessuna differenza significativa estate/inverno.
- **Trend 2026**: nuovi primi 12, nuovi secondi 14; spariti primi 24, secondi 7 (quasi tutti piatti rari, ≤ 3 volte). Pesatura per recenza (emivita migliore in giorni, log-loss): primo 365, secondo 180, contorno 180.
- **Giocatori 2026**: miglior media Lorenz con 0,33 punti/giorno. Tipp (tutti i giocatori e anni) su piatti serviti negli ultimi 5 giorni lavorativi: primo centrato nel 2,8 % (n=71) contro 9,1 % per gli altri tipp; il momento migliore per tippare un primo è 11–20 giorni lavorativi dopo l'ultima volta (11,9 %).

## Kernaussagen

- **Keine Wiederholung in derselben Woche**: Vorspeise nie zweimal in derselben Kalenderwoche (0 Paare, Zufall 40,1, p < 0,001), Hauptspeise nie zweimal in derselben Kalenderwoche (0 Paare, Zufall 39,6, p < 0,001). Beilage dagegen 18 Paare (Zufall 104,3), v. a. Reis.
- **Mindestabstand**: Vorspeise frühestens wieder nach 3 Arbeitstagen, Hauptspeise nach 2; innerhalb von 5 bzw. 3 AT praktisch nie (< 25 % der Zufallsrate). Median-Abstand 17,0 (V), 19,0 (H), 8,0 (B) Arbeitstage.
- **Wochenrhythmus**: Bei Abständen von 10, 15, … 30 AT (gleicher Wochentag) ist dieselbe Speise häufiger als bei anderen Abständen – V 5,0 % vs 4,1 % (p = 0,017), H 5,5 % vs 3,9 % (p < 0,001). Spitze Vorspeise L=30: 6,5 % vs 4,4 % (p = 0,045). Spitze Hauptspeise L=20: 8,4 % vs 4,3 % (p < 0,001).
- **Wochentag**: Reis (Beilage) am Montag 45/104 (43 %, erwartet 19 %, Lift 2,2, p < 0,001, Bonferroni-signifikant).
- **Wochentag**: Schweinskotelett (Hauptspeise) am Mittwoch 13/17 (76 %, erwartet 21 %, Lift 3,7, p < 0,001, Bonferroni-signifikant).
- **Wochentag**: Arrabbiata (Vorspeise) am Montag 18/32 (56 %, erwartet 19 %, Lift 2,9, p < 0,001, Bonferroni-signifikant).
- **Wochentag**: Champignonschnitzel (Hauptspeise) am Montag 17/30 (57 %, erwartet 19 %, Lift 2,9, p < 0,001, Bonferroni-signifikant).
- **Hypothese Fisch (alle Fischgerichte)**: häufigster Tag Freitag 11/13 (Mo–Fr: 0/0/2/0/11, p < 0,001) → bestätigt.
- **Hypothese Fisch außerhalb Fastenzeit**: häufigster Tag Freitag 3/3 (Mo–Fr: 0/0/0/0/3, p = 0,007) → bestätigt.
- **Hypothese Scombri**: häufigster Tag Freitag 2/3 (Mo–Fr: 0/0/1/0/2, p = 0,095) → nicht bestätigt.
- **Hypothese Plent**: häufigster Tag Freitag 10/21 (Mo–Fr: 0/0/5/6/10, p = 0,003) → bestätigt.
- **Hypothese Leberkas**: häufigster Tag Mittwoch 6/21 (Mo–Fr: 3/3/6/5/4, p = 0,253) → nicht bestätigt.
- **Hypothese Hauswurst**: häufigster Tag Freitag 7/15 (Mo–Fr: 0/0/4/4/7, p = 0,014) → Tendenz.
- **Beilage hängt an der Hauptspeise**: mit bekannter Hauptspeise trifft die typische Beilage in 50 % der Fälle (Leave-one-out), ohne nur 22 % (Reis); Entropie 3,54 → 1,44 bit. Feste Paare: Champignonschnitzel → Reis 77 % (23), Wienerschnitzel → Kartoffelsalat 83 % (20), Chilli con carne → Reis 100 % (18), Hühnerhaxlen → Pommes 67 % (12), Hauswurst → Plent 100 % (14), Cordon Bleu → Kartoffelsalat 100 % (13), Currywurst → Pommes 100 % (9), Sparerips → Pommes 62 % (5), Gekochtes Rindfleisch → Salzkartoffeln 100 % (6), Pizzaiolaschnitzel → Ofenkartoffeln 60 % (3).
- **Vorspeise ↔ Hauptspeise**: kaum Zusammenhang (MI 1,668 vs Zufall 1,631 bit, p = 0,150); einzelne Paare mit hohem Lift entstehen v. a. über den gemeinsamen Wochentag.
- **Fisch & Fastenzeit**: Fisch an 16 % der Fastentage (10) vs 1 % sonst (3; p < 0,001). Sommer/Winter: keine signifikanten Unterschiede.
- Aktualitätsgewichtung: beste Halbwertszeit (Log-Loss, Tage) – Vorspeise 365, Hauptspeise 180, Beilage 180.
- **Tipp-Timing (alle Spieler)**: Tipps auf Gerichte, die vor 1–5 AT serviert wurden, treffen bei V nur 2,8 % (sonst 9,1 %), bei H 3,9 % (sonst 9,4 %). Beste Abstandsklasse: Vorspeise 11–20 AT (11,9 %, n=589), Hauptspeise 11–20 AT (11,1 %, n=603), Beilage 3–5 AT (27,8 %, n=492).
- **Spieler 2026**: beste Quote Lorenz mit 0,333 Punkten/Tag; Spannweite 0,083 Punkte/Tag: Lorenz 0,333 (18 T.), Andreas 0,285 (205 T.), Johannes 0,285 (198 T.), Johannes Paul III 0,279 (197 T.), Noah 0,250 (208 T.).

## 1. Häufigkeiten

Gezählt wird die erste angesagte Option (bei „A / B“ zählt A). „zuletzt“ berücksichtigt alle Optionen.

| Kategorie | verschiedene Gerichte | 2024 | 2025 | 2026 | Top-5-Anteil | Entropie (bit) |
|---|---|---|---|---|---|---|
| Vorspeise | 62 | 24 | 44 | 41 | 32 % | 4,97 |
| Hauptspeise | 49 | 20 | 35 | 42 | 31 % | 4,92 |
| Beilage | 20 | 13 | 14 | 18 | 64 % | 3,54 |

### Vorspeise – Top 20

| # | Gericht | gesamt | Anteil | 2024 | 2025 | 2026 | zuletzt |
|---|---|---|---|---|---|---|---|
| 1 | Arrabbiata | 32 | 6,9 % | 2 | 16 | 14 | 2026-11-23 |
| 2 | Nudel mit Käsesoße | 31 | 6,7 % | 1 | 15 | 15 | 2026-11-11 |
| 3 | Hirten | 30 | 6,5 % | 2 | 13 | 15 | 2026-11-19 |
| 4 | Aglio olio | 29 | 6,2 % | 1 | 15 | 13 | 2026-11-16 |
| 5 | Nudel mit Ragu | 27 | 5,8 % | 3 | 14 | 10 | 2026-11-16 |
| 6 | Nudel mit Thunfischsoße | 26 | 5,6 % | 2 | 14 | 10 | 2026-10-30 |
| 7 | Nudel Mammarosa | 25 | 5,4 % | 2 | 11 | 12 | 2026-11-26 |
| 8 | Schlutzer | 24 | 5,2 % | 1 | 12 | 11 | 2026-10-20 |
| 9 | Lasagne | 23 | 5,0 % | 2 | 9 | 12 | 2026-11-25 |
| 10 | Tortellini mit Schinken-Rahm | 20 | 4,3 % | 0 | 8 | 12 | 2026-11-03 |
| 11 | Amatriciana | 19 | 4,1 % | 1 | 10 | 8 | 2026-11-09 |
| 12 | Nudel mit Pesto | 17 | 3,7 % | 1 | 7 | 9 | 2026-11-04 |
| 13 | Spinatspatzlen | 16 | 3,4 % | 1 | 10 | 5 | 2026-09-29 |
| 14 | Gnocchi mit Tomatensoße | 15 | 3,2 % | 0 | 6 | 9 | 2026-10-27 |
| 15 | Käseknödel | 11 | 2,4 % | 2 | 4 | 5 | 2026-09-24 |
| 16 | Pizzastrudel | 11 | 2,4 % | 1 | 5 | 5 | 2026-10-07 |
| 17 | Spinatcannelloni | 11 | 2,4 % | 1 | 4 | 6 | 2026-10-29 |
| 18 | Carbonara | 10 | 2,1 % | 1 | 4 | 5 | 2026-09-18 |
| 19 | Nudel mit Lachs | 9 | 1,9 % | 0 | 5 | 4 | 2026-10-16 |
| 20 | Nudel mit Salsiccia-Ragu | 5 | 1,1 % | 0 | 2 | 3 | 2026-09-03 |

**Selten (n ≤ 2, 33 Gerichte):** Gerstsuppe, Gnocchi mit Gorgonzolasoße, Omelett mit Schinken und Käse, Plentauflauf, Ravioli, Spinatknödel, Spinatknödel mit Käsesoße, Spinatravioli, Gemüselasagne, Gnocchi, Gnocchi mit Kräutersauce, Gnocchi mit Lachs, Gnocchi mit Ragu, Gulaschsuppe, Käse-Sofficini mit Tomantensoße, Kürbisrisotto, Nudel mit Lachs und Tomantensoße, Nudel mit Schinken-Rahm, Nudel mit Tomatensoße, Nudel mit Tomatensoße und Schinken, Pilzrisotto, Putanesca, Ravioli mit Käsesoße, Ravioli mit Tomantensoße, Schlutzer Schinken-Rahm, Schupfnudel mit Lachs, Schüttelbrot-Risotto mit Speckstreifen, Spargelrisotto, Speck-Zwiebel-Kuchen, Spinatknödel mit Gorgonzolasoße, Spinatravioli mit Schinken-Rahm, Tomatenrisotto, Truthahn-Gemüse-Risotto

**Nur als Alternative angesagt:** Fleischsuppe, Nudelsalat, Reissalat

### Hauptspeise – Top 20

| # | Gericht | gesamt | Anteil | 2024 | 2025 | 2026 | zuletzt |
|---|---|---|---|---|---|---|---|
| 1 | Hühnerbrust | 33 | 7,1 % | 2 | 16 | 15 | 2026-11-19 |
| 2 | Champignonschnitzel | 30 | 6,4 % | 2 | 16 | 12 | 2026-11-23 |
| 3 | Truthahngeschnetzeltes | 28 | 6,0 % | 2 | 13 | 13 | 2026-11-16 |
| 4 | Truthahnbraten | 26 | 5,6 % | 4 | 11 | 11 | 2026-11-25 |
| 5 | Truthahnschnitzel | 26 | 5,6 % | 2 | 16 | 8 | 2026-09-14 |
| 6 | Schweinsschopf | 25 | 5,4 % | 3 | 11 | 11 | 2026-11-18 |
| 7 | Wienerschnitzel | 24 | 5,1 % | 1 | 12 | 11 | 2026-11-17 |
| 8 | Schweinsfilet | 22 | 4,7 % | 2 | 12 | 8 | 2026-10-28 |
| 9 | Schweinsschnitzel | 22 | 4,7 % | 1 | 13 | 8 | 2026-11-09 |
| 10 | Leberkas | 21 | 4,5 % | 2 | 10 | 9 | 2026-11-24 |
| 11 | Chilli con carne | 18 | 3,9 % | 0 | 10 | 8 | 2026-11-02 |
| 12 | Hühnerhaxlen | 18 | 3,9 % | 2 | 7 | 9 | 2026-11-26 |
| 13 | Schweinskotelett | 17 | 3,6 % | 2 | 12 | 3 | 2026-06-10 |
| 14 | Hauswurst | 14 | 3,0 % | 1 | 7 | 6 | 2026-10-16 |
| 15 | Cordon Bleu | 13 | 2,8 % | 0 | 5 | 8 | 2026-11-05 |
| 16 | Zwiebelrostbraten | 13 | 2,8 % | 1 | 5 | 7 | 2026-11-13 |
| 17 | Schweinsgulasch | 11 | 2,4 % | 0 | 5 | 6 | 2026-10-09 |
| 18 | Zigeunerschnitzel | 11 | 2,4 % | 0 | 5 | 6 | 2026-11-03 |
| 19 | Currywurst | 9 | 1,9 % | 0 | 3 | 6 | 2026-11-10 |
| 20 | Sparerips | 8 | 1,7 % | 1 | 1 | 6 | 2026-11-20 |

**Selten (n ≤ 2, 17 Gerichte):** Forelle, Frittiertes Pangasiusfilet, Hamburger, Kalbsgulasch, Rotbarschfilet, Schweinsfilet mit Pfeffersoße, 1/2 Brathuhn, Frittiertes Schollenfilet, Hirschgulasch, Lammbraten, Pangasiusfilet, Pangasiusfilet mit Kräuterrahmsoße, Panierter Pangasius, Paprika-Schweinegulasch, Saures Rindfleisch, Spiegelei, Surfleisch

**Nur als Alternative angesagt:** Fleischkrapfln

### Beilage – Top 20

| # | Gericht | gesamt | Anteil | 2024 | 2025 | 2026 | zuletzt |
|---|---|---|---|---|---|---|---|
| 1 | Reis | 104 | 22,3 % | 7 | 54 | 43 | 2026-11-23 |
| 2 | Pommes | 61 | 13,1 % | 3 | 28 | 30 | 2026-11-24 |
| 3 | Spatzlen | 48 | 10,3 % | 6 | 18 | 24 | 2026-11-19 |
| 4 | Püree | 47 | 10,1 % | 2 | 22 | 23 | 2026-11-25 |
| 5 | Ofenkartoffeln | 39 | 8,4 % | 4 | 23 | 12 | 2026-11-26 |
| 6 | Kartoffelsalat | 37 | 7,9 % | 1 | 15 | 21 | 2026-11-17 |
| 7 | Kroketten | 26 | 5,6 % | 2 | 14 | 10 | 2026-11-11 |
| 8 | Kartoffelgratin | 24 | 5,1 % | 1 | 16 | 7 | 2026-11-04 |
| 9 | Plent | 21 | 4,5 % | 1 | 12 | 8 | 2026-11-12 |
| 10 | Röstkartoffeln | 14 | 3,0 % | 2 | 7 | 5 | 2026-06-25 |
| 11 | Salzkartoffeln | 11 | 2,4 % | 1 | 5 | 5 | 2026-09-04 |
| 12 | Kartoffelstampf | 9 | 1,9 % | 2 | 3 | 4 | 2026-09-30 |
| 13 | Wedges | 8 | 1,7 % | 0 | 0 | 8 | 2026-11-18 |
| 14 | Bratkartoffeln | 6 | 1,3 % | 0 | 1 | 5 | 2026-08-06 |
| 15 | Röstinchen | 4 | 0,9 % | 0 | 0 | 4 | 2026-11-20 |
| 16 | Gulasch | 3 | 0,6 % | 0 | 3 | 0 | 2025-12-16 |
| 17 | Kartoffel-Käse-Kroketten | 1 | 0,2 % | 0 | 0 | 1 | 2026-02-11 |
| 18 | Knödel | 1 | 0,2 % | 0 | 0 | 1 | 2026-10-22 |
| 19 | Kraut | 1 | 0,2 % | 0 | 0 | 1 | 2026-11-06 |
| 20 | Safranreis | 1 | 0,2 % | 1 | 0 | 0 | 2024-11-22 |

**Selten (n ≤ 2, 4 Gerichte):** Kartoffel-Käse-Kroketten, Knödel, Kraut, Safranreis

**Nur als Alternative angesagt:** Peperonata, Zucchini

## 2. Wiederholungen und Refraktärzeit

Abstände in **Arbeitstagen** (Position im Spielkalender; freie Tage und Saisonpausen zählen nicht). Abstände über eine Saisongrenze hinweg werden ignoriert. „Zufall“ = Erwartung, wenn die Küche jeden Tag unabhängig nach den Jahreshäufigkeiten wählen würde.

| Kategorie | kleinster Abstand | Median | ≤ 2 AT | ≤ 5 AT | ≤ 10 AT | ≤ 20 AT | gleiche Woche (Paare) | Zufall | p (weniger als Zufall) | keine Wdh. innerhalb |
|---|---|---|---|---|---|---|---|---|---|---|
| Vorspeise | 3 | 17,0 | 0 % | 2 % | 17 % | 61 % | 0 | 40,1 | < 0,001 | 5 AT |
| Hauptspeise | 2 | 19,0 | 1 % | 4 % | 19 % | 57 % | 0 | 39,6 | < 0,001 | 3 AT |
| Beilage | 1 | 8,0 | 6 % | 30 % | 63 % | 86 % | 18 | 104,3 | < 0,001 | 1 AT |

- **Vorspeise**: Die Küche **vermeidet** Wiederholungen innerhalb von 5 Arbeitstagen (6 gleiche Paare, Zufall 100,6); innerhalb von 10 Arbeitstagen 62 vs 198,0. Erste Wiederholung frühestens nach 3 AT.
- **Hauptspeise**: Die Küche **vermeidet** Wiederholungen innerhalb von 5 Arbeitstagen (15 gleiche Paare, Zufall 99,1); innerhalb von 10 Arbeitstagen 72 vs 194,6. Erste Wiederholung frühestens nach 2 AT.
- **Beilage**: Die Küche wiederholt **seltener** als Zufall innerhalb von 5 Arbeitstagen (140 gleiche Paare, Zufall 261,5); innerhalb von 10 Arbeitstagen 384 vs 514,2. Erste Wiederholung frühestens nach 1 AT.

### Refraktärkurve P(gleiches Gericht im Abstand L)

Basis = Σ p² (globale Anteile, wie in `stats.json`); Saison-Basis = Erwartung für zwei Tage derselben Saison.

| L (AT) | Vorspeise | Hauptspeise | Beilage |
|---|---|---|---|
| 1 | 0,0 % (0/457) | 0,0 % (0/460) | 2,0 % (9/460) |
| 2 | 0,0 % (0/454) | 0,4 % (2/457) | 3,5 % (16/457) |
| 3 | 0,2 % (1/451) | 0,7 % (3/454) | 6,8 % (31/454) |
| 4 | 0,4 % (2/448) | 1,1 % (5/451) | 8,6 % (39/451) |
| 5 | 0,7 % (3/446) | 1,1 % (5/448) | 10,0 % (45/448) |
| 6 | 1,4 % (6/443) | 1,8 % (8/445) | 9,0 % (40/445) |
| 7 | 3,2 % (14/440) | 1,1 % (5/442) | 12,0 % (53/442) |
| 8 | 2,3 % (10/437) | 2,3 % (10/439) | 10,5 % (46/439) |
| 9 | 3,2 % (14/434) | 2,5 % (11/436) | 11,0 % (48/436) |
| 10 | 2,8 % (12/431) | 5,3 % (23/433) | 13,2 % (57/433) |
| 11 | 2,8 % (12/429) | 2,8 % (12/431) | 10,9 % (47/431) |
| 12 | 5,9 % (25/425) | 4,0 % (17/427) | 9,4 % (40/427) |
| 13 | 5,9 % (25/422) | 3,5 % (15/424) | 8,3 % (35/424) |
| 14 | 4,8 % (20/419) | 4,3 % (18/421) | 12,1 % (51/421) |
| 15 | 4,6 % (19/416) | 5,5 % (23/418) | 13,2 % (55/418) |
| 16 | 3,9 % (16/413) | 2,4 % (10/415) | 11,3 % (47/415) |
| 17 | 3,9 % (16/410) | 3,2 % (13/412) | 13,1 % (54/412) |
| 18 | 4,4 % (18/407) | 4,6 % (19/409) | 8,6 % (35/409) |
| 19 | 2,5 % (10/404) | 4,4 % (18/406) | 10,8 % (44/406) |
| 20 | 6,0 % (24/401) | 8,4 % (34/403) | 12,7 % (51/403) |
| 21 | 2,8 % (11/398) | 3,2 % (13/400) | 13,5 % (54/400) |
| 22 | 3,8 % (15/395) | 4,8 % (19/397) | 12,3 % (49/397) |
| 23 | 3,1 % (12/392) | 3,3 % (13/394) | 11,7 % (46/394) |
| 24 | 2,6 % (10/389) | 4,9 % (19/391) | 11,5 % (45/391) |
| 25 | 5,7 % (22/386) | 4,1 % (16/388) | 13,4 % (52/388) |
| 26 | 4,2 % (16/383) | 3,1 % (12/385) | 10,1 % (39/385) |
| 27 | 3,4 % (13/380) | 2,9 % (11/382) | 11,3 % (43/382) |
| 28 | 6,1 % (23/377) | 5,0 % (19/379) | 10,8 % (41/379) |
| 29 | 4,8 % (18/374) | 5,6 % (21/376) | 12,5 % (47/376) |
| 30 | 6,5 % (24/372) | 3,8 % (14/373) | 14,5 % (54/373) |
| Basis Σp² | 4,2 % | 4,1 % | 11,1 % |
| Saison-Basis | 4,4 % | 4,3 % | 11,5 % |

**Auffällige Spitzen (Rate > 1,3 × Saison-Basis, p < 0,05; L=5 ≈ 1 Woche, L=20 ≈ 4 Wochen):**

- Vorspeise: L=30 → 6,5 % vs 4,4 % (24/372, p = 0,045)
- Hauptspeise: L=20 → 8,4 % vs 4,3 % (34/403, p < 0,001)

**Wochenrhythmus** – gleiche Speise bei Abständen L = 10, 15, 20, 25, 30 AT (meist gleicher Wochentag) vs. allen anderen Abständen 10–30 AT:

| Kategorie | L = 5·k | andere L | p |
|---|---|---|---|
| Vorspeise | 5,0 % (101/2006) | 4,1 % (260/6417) | 0,017 |
| Hauptspeise | 5,5 % (110/2015) | 3,9 % (249/6449) | < 0,001 |
| Beilage | 13,3 % (269/2015) | 11,1 % (717/6449) | 0,001 |

→ Der Wochentag-Effekt (Abschnitt 3) erzeugt einen schwachen Wochenrhythmus; die Refraktärzeit dominiert aber die ersten 1–2 Wochen.

### Abstände je Gericht – Vorspeise (n ≥ 8)

| Gericht | n | Mittel | Median | min | max | Wdh. gleiche Woche |
|---|---|---|---|---|---|---|
| Arrabbiata | 32 | 14,8 | 13,0 | 7 | 25 | 0 |
| Nudel mit Käsesoße | 31 | 14,3 | 14,0 | 5 | 30 | 0 |
| Hirten | 30 | 14,8 | 13,0 | 4 | 45 | 0 |
| Aglio olio | 29 | 16,0 | 14,0 | 6 | 41 | 0 |
| Nudel mit Ragu | 27 | 17,5 | 18,0 | 5 | 48 | 0 |
| Nudel mit Thunfischsoße | 26 | 16,9 | 14,0 | 6 | 41 | 0 |
| Nudel Mammarosa | 25 | 18,7 | 17,0 | 4 | 45 | 0 |
| Schlutzer | 24 | 17,8 | 14,0 | 3 | 41 | 0 |
| Lasagne | 23 | 19,3 | 17,0 | 8 | 48 | 0 |
| Tortellini mit Schinken-Rahm | 20 | 18,2 | 16,0 | 7 | 30 | 0 |
| Amatriciana | 19 | 22,9 | 20,0 | 12 | 71 | 0 |
| Nudel mit Pesto | 17 | 23,9 | 21,5 | 6 | 49 | 0 |
| Spinatspatzlen | 16 | 27,7 | 25,0 | 8 | 71 | 0 |
| Gnocchi mit Tomatensoße | 15 | 25,5 | 19,0 | 7 | 78 | 0 |
| Käseknödel | 11 | 44,8 | 22,0 | 11 | 146 | 0 |
| Pizzastrudel | 11 | 41,1 | 41,5 | 30 | 61 | 0 |
| Spinatcannelloni | 11 | 42,6 | 39,5 | 23 | 67 | 0 |
| Carbonara | 10 | 33,9 | 33,0 | 18 | 63 | 0 |
| Nudel mit Lachs | 9 | 42,3 | 58,0 | 9 | 63 | 0 |

### Abstände je Gericht – Hauptspeise (n ≥ 8)

| Gericht | n | Mittel | Median | min | max | Wdh. gleiche Woche |
|---|---|---|---|---|---|---|
| Hühnerbrust | 33 | 13,9 | 12,5 | 4 | 31 | 0 |
| Champignonschnitzel | 30 | 14,9 | 15,0 | 3 | 34 | 0 |
| Truthahngeschnetzeltes | 28 | 16,8 | 16,0 | 8 | 34 | 0 |
| Truthahnbraten | 26 | 16,7 | 12,0 | 4 | 66 | 0 |
| Truthahnschnitzel | 26 | 17,0 | 13,0 | 2 | 85 | 0 |
| Schweinsschopf | 25 | 19,3 | 16,0 | 4 | 73 | 0 |
| Wienerschnitzel | 24 | 18,3 | 17,0 | 7 | 41 | 0 |
| Schweinsfilet | 22 | 18,3 | 15,0 | 4 | 44 | 0 |
| Schweinsschnitzel | 22 | 19,9 | 14,0 | 2 | 59 | 0 |
| Leberkas | 21 | 23,8 | 21,0 | 13 | 61 | 0 |
| Chilli con carne | 18 | 24,0 | 21,5 | 12 | 44 | 0 |
| Hühnerhaxlen | 18 | 28,7 | 26,0 | 7 | 76 | 0 |
| Schweinskotelett | 17 | 18,7 | 17,5 | 9 | 60 | 0 |
| Hauswurst | 14 | 34,6 | 27,0 | 17 | 87 | 0 |
| Cordon Bleu | 13 | 29,6 | 23,0 | 15 | 62 | 0 |
| Zwiebelrostbraten | 13 | 35,1 | 36,0 | 6 | 61 | 0 |
| Schweinsgulasch | 11 | 40,1 | 31,0 | 17 | 78 | 0 |
| Zigeunerschnitzel | 11 | 42,7 | 35,0 | 14 | 92 | 0 |
| Currywurst | 9 | 43,4 | 39,0 | 20 | 77 | 0 |
| Sparerips | 8 | 26,6 | 23,0 | 16 | 45 | 0 |

### Abstände je Gericht – Beilage

| Gericht | n | Mittel | Median | min | max | Wdh. gleiche Woche |
|---|---|---|---|---|---|---|
| Reis | 104 | 4,5 | 4,0 | 1 | 11 | 14 |
| Pommes | 61 | 7,6 | 6,0 | 1 | 25 | 3 |
| Spatzlen | 48 | 9,8 | 8,0 | 3 | 26 | 0 |
| Püree | 47 | 9,6 | 9,0 | 3 | 20 | 0 |
| Ofenkartoffeln | 39 | 11,6 | 9,0 | 2 | 45 | 1 |
| Kartoffelsalat | 37 | 11,7 | 10,0 | 4 | 32 | 0 |
| Kroketten | 26 | 16,8 | 14,0 | 7 | 31 | 0 |
| Kartoffelgratin | 24 | 17,1 | 12,0 | 3 | 95 | 0 |
| Plent | 21 | 22,2 | 20,5 | 4 | 60 | 0 |
| Röstkartoffeln | 14 | 25,3 | 23,0 | 2 | 47 | 0 |
| Salzkartoffeln | 11 | 42,6 | 22,0 | 5 | 151 | 0 |
| Kartoffelstampf | 9 | 61,5 | 47,0 | 10 | 134 | 0 |
| Wedges | 8 | 28,0 | 25,0 | 7 | 65 | 0 |
| Bratkartoffeln | 6 | 27,0 | 21,5 | 5 | 60 | 0 |

## 3. Wochentage

Servierte Tage je Wochentag (Hauptspeise): Mo 90, Di 95, Mi 96, Do 96, Fr 89. Getestet wurden 305 Kombinationen (Gericht mit n ≥ 5 × Wochentag) mit einem einseitigen Binomialtest; bei so vielen Tests sind einzelne p < 0,05 auch zufällig zu erwarten (Bonferroni-Schwelle ≈ 0,0002).

### Gezielte Hypothesen

| Merkmal | n Tage | Mo | Di | Mi | Do | Fr | häufigster Tag | Anteil (erwartet) | p |
|---|---|---|---|---|---|---|---|---|---|
| Fisch (alle Fischgerichte) | 13 | 0 | 0 | 2 | 0 | 11 | Fr | 85 % (19 %) | < 0,001 |
| Fisch außerhalb Fastenzeit | 3 | 0 | 0 | 0 | 0 | 3 | Fr | 100 % (19 %) | 0,007 |
| Scombri | 3 | 0 | 0 | 1 | 0 | 2 | Fr | 67 % (19 %) | 0,095 |
| Plent | 21 | 0 | 0 | 5 | 6 | 10 | Fr | 48 % (19 %) | 0,003 |
| Leberkas | 21 | 3 | 3 | 6 | 5 | 4 | Mi | 29 % (21 %) | 0,253 |
| Hauswurst | 15 | 0 | 0 | 4 | 4 | 7 | Fr | 47 % (19 %) | 0,014 |

### Auffällige Wochentag-Vorlieben (Lift ≥ 1,5, mind. 3×, p < 0,05)

| Kategorie | Gericht | Tag | an diesem Tag | Anteil | erwartet | Lift | p | Bonferroni |
|---|---|---|---|---|---|---|---|---|
| Beilage | Reis | Mo | 45/104 | 43 % | 19 % | 2,24 | < 0,001 | ✔ |
| Hauptspeise | Schweinskotelett | Mi | 13/17 | 76 % | 21 % | 3,71 | < 0,001 | ✔ |
| Vorspeise | Arrabbiata | Mo | 18/32 | 56 % | 19 % | 2,91 | < 0,001 | ✔ |
| Hauptspeise | Champignonschnitzel | Mo | 17/30 | 57 % | 19 % | 2,93 | < 0,001 | ✔ |
| Vorspeise | Amatriciana | Mo | 11/19 | 58 % | 19 % | 2,99 | < 0,001 |  |
| Hauptspeise | Schweinsschnitzel | Mo | 12/22 | 55 % | 19 % | 2,82 | < 0,001 |  |
| Vorspeise | Spinatspatzlen | Di | 10/16 | 62 % | 20 % | 3,06 | < 0,001 |  |
| Beilage | Wedges | Mi | 6/8 | 75 % | 21 % | 3,64 | 0,001 |  |
| Beilage | Salzkartoffeln | Fr | 7/11 | 64 % | 19 % | 3,33 | 0,001 |  |
| Vorspeise | Nudel mit Lachs | Fr | 6/9 | 67 % | 19 % | 3,44 | 0,003 |  |
| Hauptspeise | Truthahnbraten | Di | 12/26 | 46 % | 20 % | 2,26 | 0,003 |  |
| Beilage | Plent | Fr | 10/21 | 48 % | 19 % | 2,49 | 0,003 |  |
| Vorspeise | Tortellini mit Schinken-Rahm | Di | 10/20 | 50 % | 20 % | 2,45 | 0,003 |  |
| Beilage | Spatzlen | Do | 18/48 | 38 % | 21 % | 1,82 | 0,005 |  |
| Hauptspeise | Ossobuchi | Do | 5/7 | 71 % | 21 % | 3,47 | 0,005 |  |
| Hauptspeise | Schweinsschnitzel mit Kräuterrahmsoße | Mo | 4/5 | 80 % | 19 % | 4,14 | 0,006 |  |
| Hauptspeise | Sparerips | Fr | 5/8 | 62 % | 19 % | 3,27 | 0,008 |  |
| Hauptspeise | Hühnerbrust | Di | 13/33 | 39 % | 20 % | 1,93 | 0,010 |  |
| Vorspeise | Lasagne | Di | 10/23 | 43 % | 20 % | 2,13 | 0,010 |  |
| Vorspeise | Nudel mit Ragu | Do | 11/27 | 41 % | 20 % | 2,02 | 0,012 |  |
| Vorspeise | Nudel Mammarosa | Mo | 10/25 | 40 % | 19 % | 2,07 | 0,014 |  |
| Hauptspeise | Truthahngeschnetzeltes | Di | 11/28 | 39 % | 20 % | 1,93 | 0,017 |  |
| Beilage | Püree | Di | 16/47 | 34 % | 20 % | 1,67 | 0,020 |  |
| Hauptspeise | Schweinsschopf | Mi | 10/25 | 40 % | 21 % | 1,94 | 0,021 |  |
| Hauptspeise | Currywurst | Di | 5/9 | 56 % | 20 % | 2,73 | 0,021 |  |

### Gerichte, die an einem Wochentag (fast) nie kommen (n ≥ 10, p < 0,05)

| Kategorie | Gericht | Tag | an diesem Tag | erwartet | p |
|---|---|---|---|---|---|
| Beilage | Plent | Di | 0/21 | 4,3 | 0,008 |
| Hauptspeise | Champignonschnitzel | Mi | 1/30 | 6,2 | 0,009 |
| Beilage | Plent | Mo | 0/21 | 4,1 | 0,011 |
| Vorspeise | Amatriciana | Mi | 0/19 | 3,9 | 0,012 |
| Vorspeise | Tortellini mit Schinken-Rahm | Mo | 0/20 | 3,9 | 0,014 |
| Hauptspeise | Champignonschnitzel | Fr | 1/30 | 5,7 | 0,014 |
| Hauptspeise | Schweinskotelett | Di | 0/17 | 3,5 | 0,021 |
| Vorspeise | Nudel mit Pesto | Mo | 0/17 | 3,3 | 0,026 |
| Hauptspeise | Schweinskotelett | Mo | 0/17 | 3,3 | 0,026 |
| Vorspeise | Arrabbiata | Mi | 2/32 | 6,6 | 0,026 |
| Hauptspeise | Schweinskotelett | Fr | 0/17 | 3,2 | 0,027 |
| Beilage | Kroketten | Mo | 1/26 | 5,0 | 0,027 |
| Hauptspeise | Truthahnbraten | Fr | 1/26 | 5,0 | 0,029 |
| Vorspeise | Spinatspatzlen | Mo | 0/16 | 3,1 | 0,032 |
| Vorspeise | Nudel Mammarosa | Fr | 1/25 | 4,8 | 0,032 |

### Vorspeise: Anzahl je Wochentag (Top 12)

| Gericht | Mo | Di | Mi | Do | Fr | max. Lift |
|---|---|---|---|---|---|---|
| Arrabbiata | 18 | 4 | 2 | 5 | 3 | 2,91 |
| Nudel mit Käsesoße | 8 | 4 | 9 | 2 | 8 | 1,41 |
| Hirten | 6 | 7 | 10 | 5 | 2 | 1,61 |
| Aglio olio | 8 | 3 | 5 | 7 | 6 | 1,43 |
| Nudel mit Ragu | 5 | 4 | 4 | 11 | 3 | 2,02 |
| Nudel mit Thunfischsoße | 7 | 3 | 5 | 4 | 7 | 1,39 |
| Nudel Mammarosa | 10 | 3 | 2 | 9 | 1 | 2,07 |
| Schlutzer | 3 | 7 | 6 | 5 | 3 | 1,43 |
| Lasagne | 2 | 10 | 3 | 7 | 1 | 2,13 |
| Tortellini mit Schinken-Rahm | 0 | 10 | 1 | 3 | 6 | 2,45 |
| Amatriciana | 11 | 1 | 0 | 6 | 1 | 2,99 |
| Nudel mit Pesto | 0 | 3 | 7 | 3 | 4 | 1,99 |

### Hauptspeise: Anzahl je Wochentag (Top 12)

| Gericht | Mo | Di | Mi | Do | Fr | max. Lift |
|---|---|---|---|---|---|---|
| Hühnerbrust | 3 | 13 | 4 | 10 | 3 | 1,93 |
| Champignonschnitzel | 17 | 8 | 1 | 3 | 1 | 2,93 |
| Truthahngeschnetzeltes | 5 | 11 | 4 | 5 | 3 | 1,93 |
| Truthahnbraten | 5 | 12 | 5 | 3 | 1 | 2,26 |
| Truthahnschnitzel | 8 | 3 | 2 | 6 | 7 | 1,59 |
| Schweinsschopf | 4 | 5 | 10 | 3 | 3 | 1,94 |
| Wienerschnitzel | 5 | 3 | 7 | 7 | 2 | 1,42 |
| Schweinsfilet | 5 | 2 | 3 | 6 | 6 | 1,43 |
| Schweinsschnitzel | 12 | 4 | 2 | 1 | 3 | 2,82 |
| Leberkas | 3 | 3 | 6 | 5 | 4 | 1,39 |
| Chilli con carne | 3 | 3 | 5 | 4 | 3 | 1,35 |
| Hühnerhaxlen | 1 | 5 | 2 | 6 | 4 | 1,62 |

### Beilage: Anzahl je Wochentag (Top 12)

| Gericht | Mo | Di | Mi | Do | Fr | max. Lift |
|---|---|---|---|---|---|---|
| Reis | 45 | 21 | 14 | 10 | 14 | 2,24 |
| Pommes | 7 | 17 | 13 | 11 | 13 | 1,37 |
| Spatzlen | 7 | 8 | 9 | 18 | 6 | 1,82 |
| Püree | 5 | 16 | 13 | 8 | 5 | 1,67 |
| Ofenkartoffeln | 13 | 8 | 4 | 9 | 5 | 1,73 |
| Kartoffelsalat | 5 | 4 | 12 | 9 | 7 | 1,57 |
| Kroketten | 1 | 7 | 4 | 5 | 9 | 1,81 |
| Kartoffelgratin | 2 | 5 | 7 | 8 | 2 | 1,62 |
| Plent | 0 | 0 | 5 | 6 | 10 | 2,49 |
| Röstkartoffeln | 2 | 0 | 3 | 5 | 4 | 1,73 |
| Salzkartoffeln | 0 | 1 | 0 | 3 | 7 | 3,33 |
| Kartoffelstampf | 2 | 4 | 3 | 0 | 0 | 2,18 |

## 4. Kombinationen

### Beilage | Hauptspeise (Hauptspeisen mit n ≥ 3)

Wer die Hauptspeise kennt (bzw. richtig schätzt), sollte die dazu typische Beilage tippen: Treffer 50 % (Leave-one-out) statt 22 % mit der global häufigsten Beilage (Reis).

| Hauptspeise | n | Beilage 1 | Beilage 2 | Beilage 3 |
|---|---|---|---|---|
| Hühnerbrust | 33 | Kroketten 33 % (11) | Spatzlen 24 % (8) | Kartoffelgratin 12 % (4) |
| Champignonschnitzel | 30 | Reis 77 % (23) | Kartoffelgratin 17 % (5) | Püree 3 % (1) |
| Truthahngeschnetzeltes | 28 | Püree 46 % (13) | Reis 32 % (9) | Spatzlen 18 % (5) |
| Truthahnbraten | 26 | Püree 31 % (8) | Reis 19 % (5) | Spatzlen 19 % (5) |
| Truthahnschnitzel | 26 | Ofenkartoffeln 42 % (11) | Pommes 38 % (10) | Kroketten 8 % (2) |
| Schweinsschopf | 25 | Pommes 24 % (6) | Reis 16 % (4) | Wedges 16 % (4) |
| Wienerschnitzel | 24 | Kartoffelsalat 83 % (20) | Pommes 17 % (4) |  |
| Schweinsfilet | 22 | Spatzlen 32 % (7) | Kroketten 27 % (6) | Reis 23 % (5) |
| Schweinsschnitzel | 22 | Ofenkartoffeln 36 % (8) | Reis 27 % (6) | Pommes 9 % (2) |
| Leberkas | 21 | Röstkartoffeln 57 % (12) | Pommes 43 % (9) |  |
| Chilli con carne | 18 | Reis 100 % (18) |  |  |
| Hühnerhaxlen | 18 | Pommes 67 % (12) | Ofenkartoffeln 28 % (5) | Wedges 6 % (1) |
| Schweinskotelett | 17 | Kartoffelgratin 35 % (6) | Spatzlen 24 % (4) | Ofenkartoffeln 18 % (3) |
| Hauswurst | 14 | Plent 100 % (14) |  |  |
| Cordon Bleu | 13 | Kartoffelsalat 100 % (13) |  |  |
| Zwiebelrostbraten | 13 | Reis 54 % (7) | Püree 38 % (5) | Kroketten 8 % (1) |
| Schweinsgulasch | 11 | Püree 36 % (4) | Reis 36 % (4) | Spatzlen 18 % (2) |
| Zigeunerschnitzel | 11 | Reis 45 % (5) | Spatzlen 36 % (4) | Kartoffelstampf 9 % (1) |
| Currywurst | 9 | Pommes 100 % (9) |  |  |
| Sparerips | 8 | Pommes 62 % (5) | Röstinchen 25 % (2) | Wedges 12 % (1) |
| Ossobuchi | 7 | Spatzlen 57 % (4) | Reis 29 % (2) | Safranreis 14 % (1) |
| Gekochtes Rindfleisch | 6 | Salzkartoffeln 100 % (6) |  |  |
| Hackbraten | 6 | Püree 50 % (3) | Reis 33 % (2) | Kartoffelgratin 17 % (1) |
| Gulasch | 5 | Plent 40 % (2) | Reis 40 % (2) | Knödel 20 % (1) |
| Pizzaiolaschnitzel | 5 | Ofenkartoffeln 60 % (3) | Pommes 40 % (2) |  |
| Schweinsschnitzel mit Kräuterrahmsoße | 5 | Reis 40 % (2) | Spatzlen 40 % (2) | Kroketten 20 % (1) |
| Rindsschnitzel | 4 | Ofenkartoffeln 25 % (1) | Pommes 25 % (1) | Röstinchen 25 % (1) |
| Schweinshaxe | 4 | Plent 50 % (2) | Ofenkartoffeln 25 % (1) | Reis 25 % (1) |
| Knödel | 3 | Gulasch 100 % (3) |  |  |
| Rindsbraten | 3 | Reis 67 % (2) | Püree 33 % (1) |  |
| Scombri | 3 | Plent 100 % (3) |  |  |
| Vitello tonnato | 3 | Bratkartoffeln 100 % (3) |  |  |

### Vorspeise ↔ Hauptspeise (n ≥ 3)

Mutual Information zwischen den Kategorien vs. Erwartung bei zufälliger Zuordnung (300 Permutationen):

| Paar | MI (bit) | Zufall (bit) | p |
|---|---|---|---|
| V–H | 1,668 | 1,631 | 0,150 |
| H–B | 2,093 | 0,821 | 0,003 |
| V–B | 0,913 | 0,891 | 0,262 |

| Vorspeise | Hauptspeise | zusammen | n(V) | n(H) | Lift | p |
|---|---|---|---|---|---|---|
| Gnocchi mit Tomatensoße | Zwiebelrostbraten | 3 | 15 | 13 | 7,14 | 0,008 |
| Lasagne | Truthahngeschnetzeltes | 5 | 22 | 28 | 3,77 | 0,009 |
| Nudel mit Thunfischsoße | Sparerips | 3 | 26 | 8 | 6,69 | 0,010 |
| Carbonara | Schweinsfilet | 3 | 10 | 22 | 6,33 | 0,010 |
| Nudel mit Lachs | Truthahnschnitzel | 3 | 9 | 26 | 5,95 | 0,011 |
| Arrabbiata | Champignonschnitzel | 6 | 32 | 30 | 2,90 | 0,015 |
| Nudel mit Thunfischsoße | Chilli con carne | 4 | 26 | 18 | 3,97 | 0,017 |
| Tortellini mit Schinken-Rahm | Schweinsschopf | 4 | 20 | 25 | 3,71 | 0,020 |
| Spinatspatzlen | Chilli con carne | 3 | 16 | 18 | 4,83 | 0,022 |
| Spinatspatzlen | Hühnerhaxlen | 3 | 16 | 18 | 4,83 | 0,022 |
| Tortellini mit Schinken-Rahm | Hühnerbrust | 4 | 20 | 33 | 2,81 | 0,049 |
| Hirten | Hühnerbrust | 5 | 30 | 33 | 2,34 | 0,058 |
| Amatriciana | Schweinsschnitzel | 3 | 19 | 22 | 3,33 | 0,059 |
| Nudel mit Ragu | Truthahnbraten | 4 | 27 | 26 | 2,64 | 0,062 |
| Arrabbiata | Schweinsfilet | 4 | 32 | 22 | 2,64 | 0,063 |
| Nudel mit Käsesoße | Wienerschnitzel | 4 | 31 | 23 | 2,60 | 0,065 |
| Hirten | Schweinskotelett | 3 | 30 | 17 | 2,73 | 0,096 |
| Aglio olio | Champignonschnitzel | 4 | 29 | 30 | 2,13 | 0,115 |
| Lasagne | Truthahnschnitzel | 3 | 22 | 26 | 2,43 | 0,123 |
| Nudel mit Thunfischsoße | Schweinsschnitzel | 3 | 26 | 22 | 2,43 | 0,123 |
| Nudel mit Ragu | Wienerschnitzel | 3 | 27 | 23 | 2,24 | 0,148 |
| Arrabbiata | Leberkas | 3 | 32 | 20 | 2,17 | 0,158 |
| Nudel mit Käsesoße | Schweinsschnitzel | 3 | 31 | 22 | 2,04 | 0,180 |
| Hirten | Truthahnbraten | 3 | 30 | 26 | 1,78 | 0,235 |
| Hirten | Truthahnschnitzel | 3 | 30 | 26 | 1,78 | 0,235 |

## 5. Saisonalität

### Fastenzeit (Aschermittwoch – Ostersonntag)

Fastenzeiten in den Daten: 2025: 05.03.–20.04., 2026: 18.02.–05.04.. Fisch = jede Hauptspeise, die als Fisch gilt (inkl. Scombri).

**Hauptspeise** (Fastentage n=64, sonst n=402; Gerichte mit ≥ 2 Fastentagen):

| Gericht | Fastenzeit | sonst | Lift | p |
|---|---|---|---|---|
| Scombri | 4,7 % (3) | 0,0 % (0) | nur Fastenzeit | 0,003 |
| Fisch | 15,6 % (10) | 0,7 % (3) | 20,94 | < 0,001 |
| Truthahnbraten | 9,4 % (6) | 5,0 % (20) | 1,88 | 0,137 |
| Currywurst | 3,1 % (2) | 1,7 % (7) | 1,79 | 0,356 |
| Schweinsfilet | 6,2 % (4) | 4,5 % (18) | 1,40 | 0,358 |
| Zigeunerschnitzel | 3,1 % (2) | 2,2 % (9) | 1,40 | 0,458 |
| Schweinskotelett | 4,7 % (3) | 3,5 % (14) | 1,35 | 0,420 |
| Chilli con carne | 4,7 % (3) | 3,7 % (15) | 1,26 | 0,458 |
| Zwiebelrostbraten | 3,1 % (2) | 2,7 % (11) | 1,14 | 0,550 |
| Champignonschnitzel | 6,2 % (4) | 6,5 % (26) | 0,97 | 0,605 |
| Wienerschnitzel | 4,7 % (3) | 5,2 % (21) | 0,90 | 0,659 |
| Truthahnschnitzel | 4,7 % (3) | 5,7 % (23) | 0,82 | 0,713 |

**Vorspeise** (Fastentage n=64, sonst n=401; Gerichte mit ≥ 2 Fastentagen):

| Gericht | Fastenzeit | sonst | Lift | p |
|---|---|---|---|---|
| Nudel mit Lachs | 3,1 % (2) | 1,7 % (7) | 1,79 | 0,357 |
| Amatriciana | 6,2 % (4) | 3,7 % (15) | 1,67 | 0,260 |
| Spinatspatzlen | 4,7 % (3) | 3,2 % (13) | 1,45 | 0,382 |
| Nudel mit Ragu | 7,8 % (5) | 5,5 % (22) | 1,42 | 0,311 |
| Pizzastrudel | 3,1 % (2) | 2,2 % (9) | 1,39 | 0,459 |
| Spinatcannelloni | 3,1 % (2) | 2,2 % (9) | 1,39 | 0,459 |
| Schlutzer | 6,2 % (4) | 5,0 % (20) | 1,25 | 0,425 |
| Nudel mit Käsesoße | 7,8 % (5) | 6,5 % (26) | 1,20 | 0,427 |
| Aglio olio | 6,2 % (4) | 6,2 % (25) | 1,00 | 0,579 |
| Gnocchi mit Tomatensoße | 3,1 % (2) | 3,2 % (13) | 0,96 | 0,632 |
| Lasagne | 4,7 % (3) | 5,0 % (20) | 0,94 | 0,631 |
| Arrabbiata | 6,2 % (4) | 7,0 % (28) | 0,90 | 0,659 |

**Beilage** (Fastentage n=64, sonst n=402; Gerichte mit ≥ 2 Fastentagen):

| Gericht | Fastenzeit | sonst | Lift | p |
|---|---|---|---|---|
| Salzkartoffeln | 4,7 % (3) | 2,0 % (8) | 2,36 | 0,184 |
| Kartoffelgratin | 9,4 % (6) | 4,5 % (18) | 2,09 | 0,101 |
| Plent | 7,8 % (5) | 4,0 % (16) | 1,96 | 0,152 |
| Röstkartoffeln | 4,7 % (3) | 2,7 % (11) | 1,71 | 0,300 |
| Kartoffelsalat | 10,9 % (7) | 7,5 % (30) | 1,47 | 0,239 |
| Püree | 12,5 % (8) | 9,7 % (39) | 1,29 | 0,314 |
| Kroketten | 6,2 % (4) | 5,5 % (22) | 1,14 | 0,488 |
| Reis | 20,3 % (13) | 22,6 % (91) | 0,90 | 0,685 |
| Spatzlen | 9,4 % (6) | 10,4 % (42) | 0,90 | 0,661 |
| Pommes | 7,8 % (5) | 13,9 % (56) | 0,56 | 0,934 |
| Ofenkartoffeln | 3,1 % (2) | 9,2 % (37) | 0,34 | 0,977 |

### Sommer (Jun–Aug) vs Winter (Dez–Feb)

**Vorspeise** (Sommertage n=106, Wintertage n=98):

| Gericht | Sommer | Winter | p (zweiseitig) |
|---|---|---|---|
| Nudel mit Pesto | 5,7 % (6) | 2,0 % (2) | 0,344 |
| Hirten | 8,5 % (9) | 5,1 % (5) | 0,515 |
| Lasagne | 4,7 % (5) | 2,0 % (2) | 0,520 |
| Tortellini mit Schinken-Rahm | 4,7 % (5) | 2,0 % (2) | 0,520 |
| Gnocchi mit Tomatensoße | 3,8 % (4) | 2,0 % (2) | 0,762 |
| Aglio olio | 6,6 % (7) | 5,1 % (5) | 0,882 |
| Nudel mit Ragu | 4,7 % (5) | 6,1 % (6) | 0,894 |
| Nudel mit Thunfischsoße | 5,7 % (6) | 7,1 % (7) | 0,885 |
| Arrabbiata | 7,5 % (8) | 9,2 % (9) | 0,870 |
| Fleischcannelloni | 0,0 % (0) | 2,0 % (2) | 0,462 |
| Spinatspatzlen | 2,8 % (3) | 5,1 % (5) | 0,643 |
| Käseknödel | 0,9 % (1) | 4,1 % (4) | 0,328 |

Signifikant (p < 0,05): _keine_

**Hauptspeise** (Sommertage n=106, Wintertage n=98):

| Gericht | Sommer | Winter | p (zweiseitig) |
|---|---|---|---|
| Truthahnschnitzel | 10,4 % (11) | 5,1 % (5) | 0,273 |
| Schweinsschnitzel | 8,5 % (9) | 4,1 % (4) | 0,333 |
| Rindsschnitzel | 2,8 % (3) | 0,0 % (0) | 0,281 |
| Schweinsschnitzel mit Kräuterrahmsoße | 1,9 % (2) | 0,0 % (0) | 0,540 |
| Vitello tonnato | 1,9 % (2) | 0,0 % (0) | 0,540 |
| Cordon Bleu | 3,8 % (4) | 2,0 % (2) | 0,762 |
| Hühnerbrust | 5,7 % (6) | 7,1 % (7) | 0,885 |
| Schweinsschopf | 5,7 % (6) | 7,1 % (7) | 0,885 |
| Gekochtes Rindfleisch | 0,0 % (0) | 2,0 % (2) | 0,462 |
| Hackbraten | 0,0 % (0) | 2,0 % (2) | 0,462 |
| Zigeunerschnitzel | 1,9 % (2) | 4,1 % (4) | 0,615 |
| Truthahngeschnetzeltes | 4,7 % (5) | 8,2 % (8) | 0,487 |

Signifikant (p < 0,05): _keine_

**Beilage** (Sommertage n=106, Wintertage n=98):

| Gericht | Sommer | Winter | p (zweiseitig) |
|---|---|---|---|
| Ofenkartoffeln | 12,3 % (13) | 6,1 % (6) | 0,226 |
| Pommes | 17,0 % (18) | 13,3 % (13) | 0,619 |
| Kartoffelsalat | 9,4 % (10) | 7,1 % (7) | 0,750 |
| Bratkartoffeln | 2,8 % (3) | 1,0 % (1) | 0,685 |
| Röstinchen | 0,9 % (1) | 0,0 % (0) | 1,000 |
| Röstkartoffeln | 3,8 % (4) | 3,1 % (3) | 1,000 |
| Gulasch | 0,9 % (1) | 2,0 % (2) | 0,941 |
| Kartoffelgratin | 3,8 % (4) | 5,1 % (5) | 0,904 |
| Spatzlen | 8,5 % (9) | 10,2 % (10) | 0,862 |
| Plent | 2,8 % (3) | 5,1 % (5) | 0,643 |
| Salzkartoffeln | 0,0 % (0) | 3,1 % (3) | 0,222 |
| Kartoffelstampf | 0,9 % (1) | 4,1 % (4) | 0,328 |

Signifikant (p < 0,05): _keine_

### Monate (Anteil der servierten Tage, Top 10)

**Vorspeise** (Tage je Monat: Jan 30, Feb 40, Mär 42, Apr 34, Mai 39, Jun 39, Jul 45, Aug 22, Sep 43, Okt 49, Nov 54, Dez 28)

| Gericht | Jan | Feb | Mär | Apr | Mai | Jun | Jul | Aug | Sep | Okt | Nov | Dez |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Arrabbiata | 10 | 8 | 5 | 6 | 5 | 8 | 7 | 9 | 7 | 4 | 7 | 11 |
| Nudel mit Käsesoße | 7 | 8 | 7 | 3 | 10 | 10 | 4 | 5 | 7 | 10 | 4 | 4 |
| Hirten | · | 8 | 7 | 3 | 8 | 8 | 7 | 14 | 9 | 6 | 4 | 7 |
| Aglio olio | 10 | · | 7 | 6 | 5 | 5 | 4 | 14 | 5 | 8 | 7 | 7 |
| Nudel mit Ragu | 7 | 8 | 5 | 9 | 5 | 3 | 9 | · | 7 | 6 | 6 | 4 |
| Nudel mit Thunfischsoße | 7 | 10 | 2 | 6 | 5 | 5 | 4 | 9 | 2 | 8 | 6 | 4 |
| Nudel Mammarosa | 3 | 5 | 5 | 3 | 3 | 8 | 4 | 5 | 7 | 4 | 7 | 11 |
| Schlutzer | 7 | 2 | 7 | 3 | 8 | 3 | 9 | 5 | 5 | 6 | 2 | 7 |
| Lasagne | 3 | · | 5 | 6 | 8 | 5 | 7 | · | 5 | 8 | 6 | 4 |
| Tortellini mit Schinken-Rahm | 3 | 2 | 2 | 6 | 10 | 5 | 4 | 5 | 2 | 6 | 4 | · |

**Hauptspeise** (Tage je Monat: Jan 30, Feb 40, Mär 42, Apr 34, Mai 39, Jun 39, Jul 45, Aug 22, Sep 44, Okt 49, Nov 54, Dez 28)

| Gericht | Jan | Feb | Mär | Apr | Mai | Jun | Jul | Aug | Sep | Okt | Nov | Dez |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Hühnerbrust | 10 | 5 | 10 | 3 | 10 | 8 | 7 | · | 9 | 6 | 7 | 7 |
| Champignonschnitzel | 3 | 8 | 5 | 9 | 8 | 5 | 4 | 9 | 7 | 8 | 4 | 11 |
| Truthahngeschnetzeltes | 7 | 8 | 5 | 3 | 10 | 5 | 4 | 5 | 5 | 6 | 6 | 11 |
| Truthahnbraten | · | 5 | 10 | 9 | · | · | 4 | 14 | 7 | 6 | 9 | 4 |
| Truthahnschnitzel | 7 | 2 | 5 | 3 | 8 | 18 | 7 | 5 | 5 | 2 | 2 | 7 |
| Schweinsschopf | 7 | 8 | 2 | 6 | 3 | · | 9 | 9 | 5 | 6 | 6 | 7 |
| Wienerschnitzel | · | 10 | 2 | 3 | 5 | 3 | 9 | 5 | 9 | 6 | 4 | 4 |
| Schweinsfilet | 3 | 5 | 5 | 9 | 8 | 3 | 4 | · | 5 | 4 | 6 | 4 |
| Schweinsschnitzel | 3 | 5 | 2 | 3 | 3 | 8 | 9 | 9 | 2 | 4 | 6 | 4 |
| Leberkas | 7 | · | 2 | 6 | 5 | 5 | 4 | 5 | 5 | 6 | 6 | 4 |

**Beilage** (Tage je Monat: Jan 30, Feb 40, Mär 42, Apr 34, Mai 39, Jun 39, Jul 45, Aug 22, Sep 44, Okt 49, Nov 54, Dez 28)

| Gericht | Jan | Feb | Mär | Apr | Mai | Jun | Jul | Aug | Sep | Okt | Nov | Dez |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Reis | 23 | 22 | 24 | 21 | 18 | 18 | 24 | 27 | 20 | 27 | 20 | 25 |
| Pommes | 13 | 12 | 10 | 12 | 13 | 15 | 18 | 18 | 11 | 16 | 7 | 14 |
| Spatzlen | 10 | 8 | 10 | 12 | 13 | 5 | 9 | 14 | 11 | 10 | 11 | 14 |
| Püree | 10 | 12 | 12 | 12 | 18 | 8 | 7 | 14 | 7 | 8 | 11 | 4 |
| Ofenkartoffeln | 3 | 8 | 2 | 6 | 5 | 13 | 13 | 9 | 14 | 8 | 9 | 7 |
| Kartoffelsalat | 3 | 10 | 5 | 9 | 8 | 13 | 9 | 5 | 9 | 8 | 7 | 7 |
| Kroketten | 7 | 8 | 7 | 6 | 3 | 8 | 2 | 5 | 7 | 6 | 7 | · |
| Kartoffelgratin | 3 | 8 | 10 | 6 | 8 | 5 | 4 | · | 2 | 4 | 6 | 4 |
| Plent | 7 | 2 | 7 | 6 | 3 | 3 | 4 | · | 5 | 4 | 6 | 7 |
| Röstkartoffeln | 3 | 2 | 2 | 6 | 3 | 8 | 2 | · | 2 | 2 | 2 | 4 |

### Weihnachtszeit (1.–23. Dezember)

- **Vorspeise** (Dezembertage n=28): Fleischcannelloni 2× (7 % vs 0 % sonst, p = 0,010); Nudel Mammarosa 3× (11 % vs 5 % sonst, p = 0,188); Arrabbiata 3× (11 % vs 7 % sonst, p = 0,303)
- **Hauptspeise** (Dezembertage n=28): Zwiebelrostbraten 2× (7 % vs 3 % sonst, p = 0,182); Hauswurst 2× (7 % vs 3 % sonst, p = 0,204); Hühnerhaxlen 2× (7 % vs 4 % sonst, p = 0,295); Truthahngeschnetzeltes 3× (11 % vs 6 % sonst, p = 0,235); Champignonschnitzel 3× (11 % vs 6 % sonst, p = 0,268)
- **Beilage** (Dezembertage n=28): Kartoffelstampf 2× (7 % vs 2 % sonst, p = 0,098); Plent 2× (7 % vs 4 % sonst, p = 0,362)
- Letztes Menü vor Weihnachten 2024 (19.12.): Lasagne / Truthahngeschnetzeltes / Spatzlen
- Letztes Menü vor Weihnachten 2025 (19.12.): Nudel Mammarosa / Cordon Bleu / Kartoffelsalat

## 6. Trends (2026 vs. 2024, 2025)

- **Vorspeise neu 2026** (12): Gnocchi mit Gorgonzolasoße (2×), Spinatknödel mit Käsesoße (2×), Gnocchi mit Kräutersauce (1×), Gnocchi mit Lachs (1×), Käse-Sofficini mit Tomantensoße (1×), Nudel mit Schinken-Rahm (1×), Pilzrisotto (1×), Spargelrisotto (1×), Speck-Zwiebel-Kuchen (1×), Spinatravioli mit Schinken-Rahm (1×), Tomatenrisotto (1×), Truthahn-Gemüse-Risotto (1×)
- **Vorspeise verschwunden 2026** (24): Fleischcannelloni (3×), Ravioli mit Parmesan-Butter (3×), Tomatenrisotto mit Mozzarella (3×), Gulaschsuppe (2×), Nudelsalat (2×), Omelett mit Schinken und Käse (2×), Plentauflauf (2×), Ravioli (2×), Fleischsuppe (1×), Gemüselasagne (1×), Gnocchi (1×), Gnocchi mit Ragu (1×), Kürbisrisotto (1×), Nudel mit Lachs und Tomantensoße (1×), Nudel mit Tomatensoße (1×), Nudel mit Tomatensoße und Schinken (1×), Putanesca (1×), Ravioli mit Käsesoße (1×), Ravioli mit Tomantensoße (1×), Reissalat (1×), Schlutzer Schinken-Rahm (1×), Schupfnudel mit Lachs (1×), Schüttelbrot-Risotto mit Speckstreifen (1×), Spinatknödel mit Gorgonzolasoße (1×)
- **Hauptspeise neu 2026** (14): Vitello tonnato (3×), Forelle (2×), Frittiertes Pangasiusfilet (2×), Hamburger (2×), Kalbsgulasch (2×), Schweinsfilet mit Pfeffersoße (2×), 1/2 Brathuhn (1×), Fleischkrapfln (1×), Hirschgulasch (1×), Lammbraten (1×), Pangasiusfilet mit Kräuterrahmsoße (1×), Panierter Pangasius (1×), Spiegelei (1×), Surfleisch (1×)
- **Hauptspeise verschwunden 2026** (7): Pizzaiolaschnitzel (5×), Knödel (3×), Rotbarschfilet (2×), Frittiertes Schollenfilet (1×), Pangasiusfilet (1×), Paprika-Schweinegulasch (1×), Saures Rindfleisch (1×)
- **Beilage neu 2026** (4): Wedges (8×), Röstinchen (4×), Kartoffel-Käse-Kroketten (1×), Knödel (1×)
- **Beilage verschwunden 2026** (3): Gulasch (3×), Safranreis (1×), Zucchini (1×)

**Aufsteiger / Absteiger** (Anteil 2025 → 2026, Gerichte mit n ≥ 5):

| Kategorie | Gericht |  | 2025 | 2026 |
|---|---|---|---|---|
| Vorspeise | Tortellini mit Schinken-Rahm | ↑ | 3,6 % | 5,7 % |
| Vorspeise | Lasagne | ↑ | 4,1 % | 5,7 % |
| Vorspeise | Gnocchi mit Tomatensoße | ↑ | 2,7 % | 4,2 % |
| Vorspeise | Hirten | ↑ | 5,9 % | 7,1 % |
| Vorspeise | Nudel mit Pesto | ↑ | 3,2 % | 4,2 % |
| Vorspeise | Spinatspatzlen | ↓ | 4,5 % | 2,4 % |
| Vorspeise | Nudel mit Ragu | ↓ | 6,4 % | 4,7 % |
| Vorspeise | Nudel mit Thunfischsoße | ↓ | 6,4 % | 4,7 % |
| Vorspeise | Amatriciana | ↓ | 4,5 % | 3,8 % |
| Vorspeise | Aglio olio | ↓ | 6,8 % | 6,1 % |
| Hauptspeise | Sparerips | ↑ | 0,5 % | 2,8 % |
| Hauptspeise | Cordon Bleu | ↑ | 2,3 % | 3,8 % |
| Hauptspeise | Currywurst | ↑ | 1,4 % | 2,8 % |
| Hauptspeise | Hühnerhaxlen | ↑ | 3,2 % | 4,2 % |
| Hauptspeise | Zwiebelrostbraten | ↑ | 2,3 % | 3,3 % |
| Hauptspeise | Schweinskotelett | ↓ | 5,4 % | 1,4 % |
| Hauptspeise | Truthahnschnitzel | ↓ | 7,2 % | 3,8 % |
| Hauptspeise | Schweinsschnitzel | ↓ | 5,9 % | 3,8 % |
| Hauptspeise | Pizzaiolaschnitzel | ↓ | 1,8 % | 0,0 % |
| Hauptspeise | Schweinsfilet | ↓ | 5,4 % | 3,8 % |
| Beilage | Wedges | ↑ | 0,0 % | 3,8 % |
| Beilage | Spatzlen | ↑ | 8,1 % | 11,3 % |
| Beilage | Kartoffelsalat | ↑ | 6,8 % | 9,9 % |
| Beilage | Bratkartoffeln | ↑ | 0,5 % | 2,4 % |
| Beilage | Pommes | ↑ | 12,7 % | 14,2 % |
| Beilage | Ofenkartoffeln | ↓ | 10,4 % | 5,7 % |
| Beilage | Reis | ↓ | 24,4 % | 20,3 % |
| Beilage | Kartoffelgratin | ↓ | 7,2 % | 3,3 % |
| Beilage | Plent | ↓ | 5,4 % | 3,8 % |
| Beilage | Kroketten | ↓ | 6,3 % | 4,7 % |

### Gewichtung nach Aktualität

Mittlerer Log-Loss einer reinen Häufigkeitsprognose für jeden Tag 2026 (nur Vergangenheit, Gewicht 0,5^(Alter/Halbwertszeit), Glättung 0,5; kleiner = besser). Zeigt, ob jüngere Menüs mehr zählen sollten (Refraktärzeit und Wochentag sind hier bewusst nicht enthalten).

| Kategorie | 30 T | 60 T | 90 T | 180 T | 365 T | ∞ (ungewichtet) |
|---|---|---|---|---|---|---|
| Vorspeise | 3,775 | 3,628 | 3,570 | 3,527 | 3,522 | 3,540 |
| Hauptspeise | 3,762 | 3,672 | 3,640 | 3,620 | 3,625 | 3,646 |
| Beilage | 2,641 | 2,580 | 2,564 | 2,561 | 2,572 | 2,593 |

Aktualitätsgewichtung: beste Halbwertszeit (Log-Loss, Tage) – Vorspeise 365, Hauptspeise 180, Beilage 180.

### Anteile je Jahr (Top-Gerichte)

**Vorspeise**

| Gericht | 2024 | 2025 | 2026 |
|---|---|---|---|
| Arrabbiata | 6,1 % | 7,3 % | 6,6 % |
| Nudel mit Käsesoße | 3,0 % | 6,8 % | 7,1 % |
| Hirten | 6,1 % | 5,9 % | 7,1 % |
| Aglio olio | 3,0 % | 6,8 % | 6,1 % |
| Nudel mit Ragu | 9,1 % | 6,4 % | 4,7 % |
| Nudel mit Thunfischsoße | 6,1 % | 6,4 % | 4,7 % |
| Nudel Mammarosa | 6,1 % | 5,0 % | 5,7 % |
| Schlutzer | 3,0 % | 5,5 % | 5,2 % |
| Lasagne | 6,1 % | 4,1 % | 5,7 % |
| Tortellini mit Schinken-Rahm | 0,0 % | 3,6 % | 5,7 % |
| Amatriciana | 3,0 % | 4,5 % | 3,8 % |
| Nudel mit Pesto | 3,0 % | 3,2 % | 4,2 % |
| Spinatspatzlen | 3,0 % | 4,5 % | 2,4 % |
| Gnocchi mit Tomatensoße | 0,0 % | 2,7 % | 4,2 % |
| Käseknödel | 6,1 % | 1,8 % | 2,4 % |

**Hauptspeise**

| Gericht | 2024 | 2025 | 2026 |
|---|---|---|---|
| Hühnerbrust | 6,1 % | 7,2 % | 7,1 % |
| Champignonschnitzel | 6,1 % | 7,2 % | 5,7 % |
| Truthahngeschnetzeltes | 6,1 % | 5,9 % | 6,1 % |
| Truthahnbraten | 12,1 % | 5,0 % | 5,2 % |
| Truthahnschnitzel | 6,1 % | 7,2 % | 3,8 % |
| Schweinsschopf | 9,1 % | 5,0 % | 5,2 % |
| Wienerschnitzel | 3,0 % | 5,4 % | 5,2 % |
| Schweinsfilet | 6,1 % | 5,4 % | 3,8 % |
| Schweinsschnitzel | 3,0 % | 5,9 % | 3,8 % |
| Leberkas | 6,1 % | 4,5 % | 4,2 % |
| Chilli con carne | 0,0 % | 4,5 % | 3,8 % |
| Hühnerhaxlen | 6,1 % | 3,2 % | 4,2 % |
| Schweinskotelett | 6,1 % | 5,4 % | 1,4 % |
| Hauswurst | 3,0 % | 3,2 % | 2,8 % |
| Cordon Bleu | 0,0 % | 2,3 % | 3,8 % |

**Beilage**

| Gericht | 2024 | 2025 | 2026 |
|---|---|---|---|
| Reis | 21,2 % | 24,4 % | 20,3 % |
| Pommes | 9,1 % | 12,7 % | 14,1 % |
| Spatzlen | 18,2 % | 8,1 % | 11,3 % |
| Püree | 6,1 % | 10,0 % | 10,8 % |
| Ofenkartoffeln | 12,1 % | 10,4 % | 5,7 % |
| Kartoffelsalat | 3,0 % | 6,8 % | 9,9 % |
| Kroketten | 6,1 % | 6,3 % | 4,7 % |
| Kartoffelgratin | 3,0 % | 7,2 % | 3,3 % |
| Plent | 3,0 % | 5,4 % | 3,8 % |
| Röstkartoffeln | 6,1 % | 3,2 % | 2,4 % |
| Salzkartoffeln | 3,0 % | 2,3 % | 2,4 % |
| Kartoffelstampf | 6,1 % | 1,4 % | 1,9 % |
| Wedges | 0,0 % | 0,0 % | 3,8 % |
| Bratkartoffeln | 0,0 % | 0,4 % | 2,4 % |
| Röstinchen | 0,0 % | 0,0 % | 1,9 % |

## 7. Spieler

Punkte = Neuberechnung der Engine (`tips.points`; identisch mit dem Excel bis auf dokumentierte manuelle Korrekturen). Nur servierte Tage vor dem Stichtag. „Alles falsch“ = 0 Punkte, „Alles richtig“ = 3 Punkte.

| Jahr | Spieler | Tage | Punkte | P./Tag | Alles falsch | Alles richtig | V | H | B | R4-Verstöße | Abw. Excel |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026 | Lorenz | 18 | 6,0 | 0,333 | 9 (50 %) | 0 | 6 % | 11 % | 44 % | 0 | 0 |
| 2026 | Andreas | 205 | 58,5 | 0,285 | 130 (63 %) | 0 | 11 % | 11 % | 25 % | 2 | 1 |
| 2026 | Johannes | 198 | 56,5 | 0,285 | 123 (62 %) | 1 | 8 % | 12 % | 28 % | 5 | 0 |
| 2026 | Johannes Paul III | 197 | 55,0 | 0,279 | 132 (67 %) | 3 | 9 % | 11 % | 24 % | 2 | 0 |
| 2026 | Noah | 208 | 52,0 | 0,250 | 143 (69 %) | 1 | 8 % | 9 % | 25 % | 3 | 0 |
| 2025 | Noah | 213 | 51,5 | 0,242 | 151 (71 %) | 1 | 11 % | 8 % | 17 % | 0 | 0 |
| 2025 | Andreas | 214 | 47,5 | 0,222 | 153 (72 %) | 1 | 8 % | 8 % | 20 % | 3 | 1 |
| 2025 | Johannes | 209 | 39,0 | 0,187 | 158 (76 %) | 1 | 8 % | 4 % | 16 % | 0 | 2 |
| 2024 | Johannes | 27 | 6,0 | 0,222 | 20 (74 %) | 0 | 15 % | 8 % | 8 % | 0 | 0 |
| 2024 | Andreas | 34 | 6,5 | 0,191 | 29 (85 %) | 1 | 9 % | 6 % | 9 % | 0 | 0 |
| 2024 | Noah | 29 | 3,0 | 0,103 | 24 (83 %) | 0 | 0 % | 7 % | 14 % | 0 | 0 |

### Lieblingstipps

| Jahr | Spieler | Vorspeise | Hauptspeise | Beilage |
|---|---|---|---|---|
| 2026 | Lorenz | Nudel mit Thunfischsoße 3, Amatriciana 2, Hirten 2 | Truthahngeschnetzeltes 4, Wienerschnitzel 4, Gulasch 3 | Reis 5, Püree 4, Kartoffelsalat 3 |
| 2026 | Andreas | Nudel mit Käsesoße 22, Spinatspatzlen 19, Lasagne 18 | Wienerschnitzel 29, Champignonschnitzel 24, Currywurst 20 | Pommes 56, Reis 39, Kartoffelsalat 27 |
| 2026 | Johannes | Amatriciana 25, Carbonara 24, Hirten 21 | Wienerschnitzel 32, Champignonschnitzel 26, Hühnerhaxlen 20 | Pommes 51, Reis 46, Kartoffelsalat 21 |
| 2026 | Johannes Paul III | Hirten 20, Amatriciana 17, Lasagne 17 | Champignonschnitzel 20, Wienerschnitzel 20, Hühnerbrust 18 | Reis 50, Pommes 27, Kartoffelsalat 24 |
| 2026 | Noah | Amatriciana 37, Carbonara 24, Aglio olio 22 | Truthahngeschnetzeltes 41, Champignonschnitzel 39, Hühnerbrust 17 | Reis 49, Püree 44, Kartoffelgratin 26 |
| 2025 | Noah | Hirten 39, Lasagne 34, Aglio olio 23 | Truthahnschnitzel 24, Champignonschnitzel 22, Schweinsfilet 22 | Reis 51, Püree 27, Kartoffelgratin 23 |
| 2025 | Andreas | Tortellini mit Schinken-Rahm 24, Hirten 21, Nudel mit Käsesoße 21 | Leberkas 23, Wienerschnitzel 21, Champignonschnitzel 18 | Pommes 47, Reis 32, Püree 25 |
| 2025 | Johannes | Hirten 36, Carbonara 32, Lasagne 17 | Wienerschnitzel 23, Hühnerhaxlen 21, Truthahnschnitzel 19 | Pommes 53, Reis 35, Ofenkartoffeln 32 |
| 2024 | Johannes | Carbonara 5, Hirten 5, Käseknödel 3 | Wienerschnitzel 6, Knödel 4, Schweinsbraten 3 | Kartoffelsalat 5, Gulasch 4, Ofenkartoffeln 4 |
| 2024 | Andreas | Lasagne 6, Spinatspatzlen 5, Nudel mit Käsesoße 4 | Leberkas 6, Hauswurst 3, Pizzaiolaschnitzel 3 | Ofenkartoffeln 6, Reis 6, Röstkartoffeln 6 |
| 2024 | Noah | Lasagne 7, Carbonara 6, Tortellini mit Ragu 4 | Champignonschnitzel 6, Hauswurst 5, Leberkas 3 | Reis 6, Kartoffelsalat 5, Ofenkartoffeln 4 |

### Was funktioniert? (alle Spieler, Ebene Einzeltipp)

Trefferquote je Kategorie, je nachdem ob der getippte Name zu den 5 bis dahin häufigsten gehörte, und je nach Arbeitstagen seit dem letzten Servieren des getippten Gerichts (Fisch außerhalb der Fastenzeit als Gruppe „Fisch“). Die ersten 20 servierten Tage sind ausgenommen (noch keine Historie).

| Kategorie | Tipp in Top-5 | Tipp außerhalb Top-5 |
|---|---|---|
| Vorspeise | 13,6 % (n=382) | 7,2 % (n=1112) |
| Hauptspeise | 11,2 % (n=499) | 7,9 % (n=996) |
| Beilage | 29,2 % (n=901) | 11,0 % (n=593) |

| Kategorie | 1–2 AT | 3–5 AT | 6–10 AT | 11–20 AT | 21–40 AT | > 40 AT | nie serviert |
|---|---|---|---|---|---|---|---|
| Vorspeise | 0,0 % (12) | 3,4 % (59) | 6,7 % (312) | 11,9 % (589) | 10,0 % (309) | 4,3 % (162) | 2,0 % (51) |
| Hauptspeise | 0,0 % (9) | 4,3 % (94) | 4,7 % (316) | 11,1 % (603) | 11,0 % (300) | 8,7 % (103) | 10,0 % (70) |
| Beilage | 25,8 % (89) | 27,8 % (492) | 22,4 % (402) | 18,0 % (322) | 14,7 % (116) | 4,8 % (62) | 0,0 % (11) |

- Vorspeise: Top-5-Tipps treffen 13,6 % vs 7,2 % (besser, Faktor 1,89).
- Hauptspeise: Top-5-Tipps treffen 11,2 % vs 7,9 % (besser, Faktor 1,41).
- Beilage: Top-5-Tipps treffen 29,2 % vs 11,0 % (besser, Faktor 2,66).

→ Tipps auf Gerichte, die erst vor 1–5 Arbeitstagen serviert wurden, treffen bei der Vorspeise nur 2,8 % (n=71) gegenüber 9,1 % sonst; Hauptspeise 3,9 % vs 9,4 %; Beilage 27,5 % vs 18,4 %.

### Strategie-Kennzahlen je Spieler und Jahr

Top-5-Anteil = Anteil der Tipps auf die 5 bis dahin häufigsten Gerichte; Vielfalt = mittlere Entropie der eigenen Tipps (bit); kürzlich = Anteil der Tipps auf Gerichte der letzten 5 Arbeitstage.

| Jahr | Spieler | P./Tag | Rang | Top-5-Anteil | Vielfalt | kürzlich |
|---|---|---|---|---|---|---|
| 2026 | Lorenz | 0,333 | 1 | 46 % | 2,99 | 19 % |
| 2026 | Andreas | 0,285 | 2 | 40 % | 3,72 | 16 % |
| 2026 | Johannes | 0,285 | 3 | 39 % | 3,83 | 15 % |
| 2026 | Johannes Paul III | 0,279 | 4 | 44 % | 3,92 | 20 % |
| 2026 | Noah | 0,250 | 5 | 51 % | 3,51 | 18 % |
| 2025 | Noah | 0,242 | 1 | 36 % | 3,80 | 16 % |
| 2025 | Andreas | 0,222 | 2 | 35 % | 3,91 | 15 % |
| 2025 | Johannes | 0,187 | 3 | 36 % | 3,89 | 19 % |
| 2024 | Johannes | 0,222 | 1 | 25 % | 3,19 | 11 % |
| 2024 | Andreas | 0,191 | 2 | 26 % | 3,46 | 7 % |
| 2024 | Noah | 0,103 | 3 | 30 % | 3,25 | 10 % |

Korrelation mit Punkten/Tag über 7 Spieler-Jahre mit ≥ 100 Tagen (sehr kleine Stichprobe, nur Hinweis): Top-5-Anteil r=0,41, Vielfalt r=-0,22, kürzlich r=-0,19, V-Trefferquote r=0,34. Die Vorspeise zählt doppelt so viel wie H oder B (1 vs 0,5 Punkte); über die Spieler-Jahre erklärt die V-Trefferquote die Rangfolge aber nur schwach.

### Notizen je Spieler

- **Lorenz 2026**: 0,33 Punkte/Tag (Rang 1/5 in 2026). Top-5-Anteil der Tipps 46 %, Vielfalt 3,0 bit, 19 % Tipps auf Gerichte, die in den letzten 5 Arbeitstagen serviert wurden. Stärkste Kategorie: Beilage (44 % Treffer).
- **Andreas 2026**: 0,29 Punkte/Tag (Rang 2/5 in 2026). Top-5-Anteil der Tipps 40 %, Vielfalt 3,7 bit, 16 % Tipps auf Gerichte, die in den letzten 5 Arbeitstagen serviert wurden. Stärkste Kategorie: Beilage (25 % Treffer). Regel-4-Verstöße: 2.
- **Johannes 2026**: 0,29 Punkte/Tag (Rang 3/5 in 2026). Top-5-Anteil der Tipps 39 %, Vielfalt 3,8 bit, 15 % Tipps auf Gerichte, die in den letzten 5 Arbeitstagen serviert wurden. Stärkste Kategorie: Beilage (28 % Treffer). Regel-4-Verstöße: 5.
- **Johannes Paul III 2026**: 0,28 Punkte/Tag (Rang 4/5 in 2026). Top-5-Anteil der Tipps 44 %, Vielfalt 3,9 bit, 20 % Tipps auf Gerichte, die in den letzten 5 Arbeitstagen serviert wurden. Stärkste Kategorie: Beilage (24 % Treffer). Regel-4-Verstöße: 2.
- **Noah 2026**: 0,25 Punkte/Tag (Rang 5/5 in 2026). Top-5-Anteil der Tipps 51 %, Vielfalt 3,5 bit, 18 % Tipps auf Gerichte, die in den letzten 5 Arbeitstagen serviert wurden. Stärkste Kategorie: Beilage (25 % Treffer). Regel-4-Verstöße: 3.
- **Noah 2025**: 0,24 Punkte/Tag (Rang 1/3 in 2025). Top-5-Anteil der Tipps 36 %, Vielfalt 3,8 bit, 16 % Tipps auf Gerichte, die in den letzten 5 Arbeitstagen serviert wurden. Stärkste Kategorie: Beilage (17 % Treffer).
- **Andreas 2025**: 0,22 Punkte/Tag (Rang 2/3 in 2025). Top-5-Anteil der Tipps 35 %, Vielfalt 3,9 bit, 15 % Tipps auf Gerichte, die in den letzten 5 Arbeitstagen serviert wurden. Stärkste Kategorie: Beilage (20 % Treffer). Regel-4-Verstöße: 3.
- **Johannes 2025**: 0,19 Punkte/Tag (Rang 3/3 in 2025). Top-5-Anteil der Tipps 36 %, Vielfalt 3,9 bit, 19 % Tipps auf Gerichte, die in den letzten 5 Arbeitstagen serviert wurden. Stärkste Kategorie: Beilage (16 % Treffer).
- **Johannes 2024**: 0,22 Punkte/Tag (Rang 1/3 in 2024). Top-5-Anteil der Tipps 25 %, Vielfalt 3,2 bit, 11 % Tipps auf Gerichte, die in den letzten 5 Arbeitstagen serviert wurden. Stärkste Kategorie: Vorspeise (15 % Treffer).
- **Andreas 2024**: 0,19 Punkte/Tag (Rang 2/3 in 2024). Top-5-Anteil der Tipps 26 %, Vielfalt 3,5 bit, 7 % Tipps auf Gerichte, die in den letzten 5 Arbeitstagen serviert wurden. Stärkste Kategorie: Vorspeise (9 % Treffer).
- **Noah 2024**: 0,10 Punkte/Tag (Rang 3/3 in 2024). Top-5-Anteil der Tipps 30 %, Vielfalt 3,2 bit, 10 % Tipps auf Gerichte, die in den letzten 5 Arbeitstagen serviert wurden. Stärkste Kategorie: Beilage (14 % Treffer).

## Methodik

- Datenbasis: `data/menus.csv` (Status `served`), `data/tips.csv`; Namen kanonisch nach `data/aliases.json` (siehe `reports/alias_candidates.md`).
- Häufigkeiten, Abstände, Wochentage, Paare, Saison: erste angesagte Option. Neu/verschwunden: alle Optionen.
- Arbeitstage = alle Spieltage (serviert/unbekannt/offen) ohne freie Tage; Saisonpausen zählen nicht.
- p-Werte: exakter Binomialtest (einseitig, außer Sommer/Winter), ohne Korrektur für Mehrfachtests – kleine p-Werte bei vielen Tests sind Hinweise, keine Beweise.
- Spieler: nur Tipps vor dem Stichtag (Regel 6), Punkte aus der Engine-Neuberechnung.

