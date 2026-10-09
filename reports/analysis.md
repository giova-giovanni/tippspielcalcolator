# Analyse Tippspiel Essen Wies

_Automatisch erzeugt von `engine/analyze.py` am 2026-10-09 17:01 UTC (Stichtag 2026-10-09). Datenstand: 432 servierte Menüs (2024: 34, 2025: 221, 2026: 177), letztes Menü 2026-10-08._

## Riassunto (IT)

- **Dati**: 432 menù serviti (2024: 34, 2025: 221, 2026: 177); piatti distinti: primo 60, secondo 48, contorno 18.
- **Primo più frequenti**: Arrabbiata (30), Nudel mit Käsesoße (29), Hirten (28); i primi 5 coprono 32 % dei giorni.
- **Secondo più frequenti**: Hühnerbrust (31), Champignonschnitzel (28), Truthahngeschnetzeltes (26); i primi 5 coprono 31 % dei giorni.
- **Contorno più frequenti**: Reis (97), Pommes (56), Spatzlen (44); i primi 5 coprono 65 % dei giorni.
- **Ripetizioni**: la cucina evita le ripetizioni. Primo e secondo: mai due volte nella stessa settimana (0 e 0 coppie contro 37 e 37 attese per caso, p < 0,001); quasi nessuna ripetizione entro 5 (primo) / 3 (secondo) giorni lavorativi; intervallo mediano 18 / 19 giorni lavorativi. Il contorno si ripete molto di più (17 coppie nella stessa settimana, 97 attese per caso). → Non tippare primo/secondo serviti negli ultimi giorni o già serviti questa settimana.
- **Giorno della settimana**: Schweinskotelett (secondo) il mercoledì 13/17 (atteso 21 %, p < 0,001); Reis (contorno) il lunedì 39/97 (atteso 19 %, p < 0,001); Arrabbiata (primo) il lunedì 17/30 (atteso 19 %, p < 0,001); Champignonschnitzel (secondo) il lunedì 15/28 (atteso 19 %, p < 0,001). 4 effetti restano significativi anche con correzione di Bonferroni: il giorno della settimana conta.
- **Ipotesi confermate**: pesce (tutti) il venerdì 11/13; pesce fuori Quaresima il venerdì 3/3; Plent (polenta) il venerdì 9/19. Non confermate: Scombri, Leberkas.
- **Contorno ↔ secondo**: conoscendo il secondo, il contorno più tipico è giusto nel 48 % dei casi (leave-one-out) contro 23 % tippando sempre Reis (es. Champignonschnitzel → Reis 75 %, Wienerschnitzel → Kartoffelsalat 82 %, Leberkas → Röstkartoffeln 63 %, Chilli con carne → Reis 100 %). Primo e secondo invece sono quasi indipendenti (MI 1,73 bit vs 1,68 per caso, p = 0,070).
- **Quaresima / pesce**: pesce in Quaresima nel 16 % dei giorni contro 1 % fuori (10 vs 3 giorni). Nessuna differenza significativa estate/inverno.
- **Trend 2026**: nuovi primi 10, nuovi secondi 13; spariti primi 27, secondi 7 (quasi tutti piatti rari, ≤ 3 volte). Pesatura per recenza (emivita migliore in giorni, log-loss): primo 365, secondo 180, contorno 180.
- **Giocatori 2026**: miglior media Johannes con 0,28 punti/giorno. Tipp (tutti i giocatori e anni) su piatti serviti negli ultimi 5 giorni lavorativi: primo centrato nel 2,9 % (n=68) contro 8,9 % per gli altri tipp; il momento migliore per tippare un primo è 21–40 giorni lavorativi dopo l'ultima volta (10,9 %).

## Kernaussagen

- **Keine Wiederholung in derselben Woche**: Vorspeise nie zweimal in derselben Kalenderwoche (0 Paare, Zufall 37,1, p < 0,001), Hauptspeise nie zweimal in derselben Kalenderwoche (0 Paare, Zufall 36,9, p < 0,001). Beilage dagegen 17 Paare (Zufall 97,1), v. a. Reis.
- **Mindestabstand**: Vorspeise frühestens wieder nach 3 Arbeitstagen, Hauptspeise nach 2; innerhalb von 5 bzw. 3 AT praktisch nie (< 25 % der Zufallsrate). Median-Abstand 17,5 (V), 19,0 (H), 8,0 (B) Arbeitstage.
- **Wochenrhythmus**: Bei Abständen von 10, 15, … 30 AT (gleicher Wochentag) ist dieselbe Speise häufiger als bei anderen Abständen – V 5,0 % vs 4,1 % (p = 0,037), H 5,5 % vs 3,9 % (p < 0,001). Spitze Vorspeise L=30: 7,1 % vs 4,5 % (p = 0,017). Spitze Hauptspeise L=20: 8,2 % vs 4,4 % (p < 0,001).
- **Wochentag**: Schweinskotelett (Hauptspeise) am Mittwoch 13/17 (76 %, erwartet 21 %, Lift 3,7, p < 0,001, Bonferroni-signifikant).
- **Wochentag**: Reis (Beilage) am Montag 39/97 (40 %, erwartet 19 %, Lift 2,1, p < 0,001, Bonferroni-signifikant).
- **Wochentag**: Arrabbiata (Vorspeise) am Montag 17/30 (57 %, erwartet 19 %, Lift 2,9, p < 0,001, Bonferroni-signifikant).
- **Wochentag**: Champignonschnitzel (Hauptspeise) am Montag 15/28 (54 %, erwartet 19 %, Lift 2,8, p < 0,001, Bonferroni-signifikant).
- **Hypothese Fisch (alle Fischgerichte)**: häufigster Tag Freitag 11/13 (Mo–Fr: 0/0/2/0/11, p < 0,001) → bestätigt.
- **Hypothese Fisch außerhalb Fastenzeit**: häufigster Tag Freitag 3/3 (Mo–Fr: 0/0/0/0/3, p = 0,007) → bestätigt.
- **Hypothese Scombri**: häufigster Tag Freitag 2/3 (Mo–Fr: 0/0/1/0/2, p = 0,095) → nicht bestätigt.
- **Hypothese Plent**: häufigster Tag Freitag 9/19 (Mo–Fr: 0/0/5/5/9, p = 0,005) → bestätigt.
- **Hypothese Leberkas**: häufigster Tag Mittwoch 6/19 (Mo–Fr: 3/1/6/5/4, p = 0,182) → nicht bestätigt.
- **Hypothese Hauswurst**: häufigster Tag Freitag 6/14 (Mo–Fr: 0/0/4/4/6, p = 0,035) → Tendenz.
- **Beilage hängt an der Hauptspeise**: mit bekannter Hauptspeise trifft die typische Beilage in 48 % der Fälle (Leave-one-out), ohne nur 23 % (Reis); Entropie 3,50 → 1,42 bit. Feste Paare: Champignonschnitzel → Reis 75 % (21), Wienerschnitzel → Kartoffelsalat 82 % (18), Leberkas → Röstkartoffeln 63 % (12), Chilli con carne → Reis 100 % (17), Hühnerhaxlen → Pommes 71 % (12), Hauswurst → Plent 100 % (13), Cordon Bleu → Kartoffelsalat 100 % (12), Currywurst → Pommes 100 % (7), Gekochtes Rindfleisch → Salzkartoffeln 100 % (6), Sparerips → Pommes 67 % (4), Hackbraten → Püree 60 % (3), Pizzaiolaschnitzel → Ofenkartoffeln 60 % (3).
- **Vorspeise ↔ Hauptspeise**: kaum Zusammenhang (MI 1,730 vs Zufall 1,681 bit, p = 0,070); einzelne Paare mit hohem Lift entstehen v. a. über den gemeinsamen Wochentag.
- **Fisch & Fastenzeit**: Fisch an 16 % der Fastentage (10) vs 1 % sonst (3; p < 0,001). Sommer/Winter: keine signifikanten Unterschiede.
- Aktualitätsgewichtung: beste Halbwertszeit (Log-Loss, Tage) – Vorspeise 365, Hauptspeise 180, Beilage 180.
- **Tipp-Timing (alle Spieler)**: Tipps auf Gerichte, die vor 1–5 AT serviert wurden, treffen bei V nur 2,9 % (sonst 8,9 %), bei H 4,0 % (sonst 8,4 %). Beste Abstandsklasse: Vorspeise 21–40 AT (10,9 %, n=284), Hauptspeise 11–20 AT (9,6 %, n=510), Beilage 3–5 AT (27,5 %, n=437).
- **Spieler 2026**: beste Quote Johannes mit 0,276 Punkten/Tag; alle Spieler liegen eng beieinander: Johannes 0,276 (165 T.), Andreas 0,260 (171 T.), Johannes Paul III 0,252 (163 T.), Noah 0,240 (173 T.).

## 1. Häufigkeiten

Gezählt wird die erste angesagte Option (bei „A / B“ zählt A). „zuletzt“ berücksichtigt alle Optionen.

| Kategorie | verschiedene Gerichte | 2024 | 2025 | 2026 | Top-5-Anteil | Entropie (bit) |
|---|---|---|---|---|---|---|
| Vorspeise | 60 | 24 | 44 | 36 | 32 % | 4,96 |
| Hauptspeise | 48 | 20 | 35 | 41 | 31 % | 4,91 |
| Beilage | 18 | 13 | 14 | 16 | 65 % | 3,50 |

### Vorspeise – Top 20

| # | Gericht | gesamt | Anteil | 2024 | 2025 | 2026 | zuletzt |
|---|---|---|---|---|---|---|---|
| 1 | Arrabbiata | 30 | 7,0 % | 2 | 16 | 12 | 2026-10-05 |
| 2 | Nudel mit Käsesoße | 29 | 6,7 % | 1 | 15 | 13 | 2026-10-02 |
| 3 | Hirten | 28 | 6,5 % | 2 | 13 | 13 | 2026-09-30 |
| 4 | Aglio olio | 26 | 6,0 % | 1 | 15 | 10 | 2026-09-21 |
| 5 | Nudel mit Ragu | 25 | 5,8 % | 3 | 14 | 8 | 2026-07-27 |
| 6 | Nudel mit Thunfischsoße | 25 | 5,8 % | 2 | 14 | 9 | 2026-10-01 |
| 7 | Schlutzer | 23 | 5,3 % | 1 | 12 | 10 | 2026-09-25 |
| 8 | Nudel Mammarosa | 21 | 4,9 % | 2 | 11 | 8 | 2026-09-22 |
| 9 | Lasagne | 20 | 4,7 % | 2 | 9 | 9 | 2026-10-08 |
| 10 | Amatriciana | 18 | 4,2 % | 1 | 10 | 7 | 2026-07-17 |
| 11 | Tortellini mit Schinken-Rahm | 18 | 4,2 % | 0 | 8 | 10 | 2026-10-06 |
| 12 | Nudel mit Pesto | 16 | 3,7 % | 1 | 7 | 8 | 2026-09-10 |
| 13 | Spinatspatzlen | 16 | 3,7 % | 1 | 10 | 5 | 2026-09-29 |
| 14 | Gnocchi mit Tomatensoße | 13 | 3,0 % | 0 | 6 | 7 | 2026-09-28 |
| 15 | Käseknödel | 11 | 2,6 % | 2 | 4 | 5 | 2026-09-24 |
| 16 | Pizzastrudel | 11 | 2,6 % | 1 | 5 | 5 | 2026-10-07 |
| 17 | Carbonara | 10 | 2,3 % | 1 | 4 | 5 | 2026-09-18 |
| 18 | Spinatcannelloni | 10 | 2,3 % | 1 | 4 | 5 | 2026-09-16 |
| 19 | Nudel mit Lachs | 8 | 1,9 % | 0 | 5 | 3 | 2026-09-23 |
| 20 | Nudel mit Salsiccia-Ragu | 5 | 1,2 % | 0 | 2 | 3 | 2026-09-03 |

**Selten (n ≤ 2, 33 Gerichte):** Gnocchi mit Gorgonzolasoße, Gnocchi mit Käsesoße, Nudel mit Grillgemüseragu, Omelett mit Schinken und Käse, Plentauflauf, Ravioli, Spinatknödel mit Käsesoße, Spinatravioli, Gemüselasagne, Gerstsuppe, Gnocchi, Gnocchi mit Kräutersauce, Gnocchi mit Lachs, Gnocchi mit Ragu, Gulaschsuppe, Käse-Sofficini mit Tomantensoße, Kürbisrisotto, Nudel mit Lachs und Tomantensoße, Nudel mit Schinken-Rahm, Nudel mit Tomatensoße, Nudel mit Tomatensoße und Schinken, Pilzrisotto, Putanesca, Ravioli mit Käsesoße, Ravioli mit Tomantensoße, Schlutzer Schinken-Rahm, Schupfnudel mit Lachs, Schüttelbrot-Risotto mit Speckstreifen, Spargelrisotto, Speck-Zwiebel-Kuchen, Spinatknödel, Spinatknödel mit Gorgonzolasoße, Tomatenrisotto

**Nur als Alternative angesagt:** Fleischsuppe, Nudelsalat, Reissalat

### Hauptspeise – Top 20

| # | Gericht | gesamt | Anteil | 2024 | 2025 | 2026 | zuletzt |
|---|---|---|---|---|---|---|---|
| 1 | Hühnerbrust | 31 | 7,2 % | 2 | 16 | 13 | 2026-09-25 |
| 2 | Champignonschnitzel | 28 | 6,5 % | 2 | 16 | 10 | 2026-10-05 |
| 3 | Truthahngeschnetzeltes | 26 | 6,0 % | 2 | 13 | 11 | 2026-10-07 |
| 4 | Truthahnschnitzel | 26 | 6,0 % | 2 | 16 | 8 | 2026-09-14 |
| 5 | Schweinsschopf | 23 | 5,3 % | 3 | 11 | 9 | 2026-09-03 |
| 6 | Truthahnbraten | 23 | 5,3 % | 4 | 11 | 8 | 2026-09-30 |
| 7 | Wienerschnitzel | 22 | 5,1 % | 1 | 12 | 9 | 2026-09-28 |
| 8 | Schweinsschnitzel | 21 | 4,9 % | 1 | 13 | 7 | 2026-08-24 |
| 9 | Schweinsfilet | 20 | 4,6 % | 2 | 12 | 6 | 2026-09-18 |
| 10 | Leberkas | 19 | 4,4 % | 2 | 10 | 7 | 2026-09-23 |
| 11 | Chilli con carne | 17 | 3,9 % | 0 | 10 | 7 | 2026-09-29 |
| 12 | Hühnerhaxlen | 17 | 3,9 % | 2 | 7 | 8 | 2026-10-02 |
| 13 | Schweinskotelett | 17 | 3,9 % | 2 | 12 | 3 | 2026-06-10 |
| 14 | Hauswurst | 13 | 3,0 % | 1 | 7 | 5 | 2026-09-09 |
| 15 | Cordon Bleu | 12 | 2,8 % | 0 | 5 | 7 | 2026-10-06 |
| 16 | Zwiebelrostbraten | 12 | 2,8 % | 1 | 5 | 6 | 2026-09-22 |
| 17 | Schweinsgulasch | 10 | 2,3 % | 0 | 5 | 5 | 2026-09-15 |
| 18 | Zigeunerschnitzel | 10 | 2,3 % | 0 | 5 | 5 | 2026-08-03 |
| 19 | Currywurst | 7 | 1,6 % | 0 | 3 | 4 | 2026-08-26 |
| 20 | Gekochtes Rindfleisch | 6 | 1,4 % | 1 | 2 | 3 | 2026-09-04 |

**Selten (n ≤ 2, 16 Gerichte):** Forelle, Frittiertes Pangasiusfilet, Hamburger, Kalbsgulasch, Rotbarschfilet, Schweinsfilet mit Pfeffersoße, 1/2 Brathuhn, Frittiertes Schollenfilet, Hirschgulasch, Lammbraten, Pangasiusfilet, Pangasiusfilet mit Kräuterrahmsoße, Panierter Pangasius, Paprika-Schweinegulasch, Saures Rindfleisch, Spiegelei

**Nur als Alternative angesagt:** Fleischkrapfln

### Beilage – Top 20

| # | Gericht | gesamt | Anteil | 2024 | 2025 | 2026 | zuletzt |
|---|---|---|---|---|---|---|---|
| 1 | Reis | 97 | 22,5 % | 7 | 54 | 36 | 2026-10-08 |
| 2 | Pommes | 56 | 13,0 % | 3 | 28 | 25 | 2026-10-01 |
| 3 | Spatzlen | 44 | 10,2 % | 6 | 18 | 20 | 2026-09-24 |
| 4 | Püree | 43 | 10,0 % | 2 | 22 | 19 | 2026-10-07 |
| 5 | Ofenkartoffeln | 38 | 8,8 % | 4 | 23 | 11 | 2026-10-02 |
| 6 | Kartoffelsalat | 34 | 7,9 % | 1 | 15 | 18 | 2026-10-06 |
| 7 | Kroketten | 24 | 5,6 % | 2 | 14 | 8 | 2026-09-18 |
| 8 | Kartoffelgratin | 23 | 5,3 % | 1 | 16 | 6 | 2026-06-10 |
| 9 | Plent | 19 | 4,4 % | 1 | 12 | 6 | 2026-09-09 |
| 10 | Röstkartoffeln | 14 | 3,2 % | 2 | 7 | 5 | 2026-06-25 |
| 11 | Salzkartoffeln | 11 | 2,5 % | 1 | 5 | 5 | 2026-09-04 |
| 12 | Kartoffelstampf | 9 | 2,1 % | 2 | 3 | 4 | 2026-09-30 |
| 13 | Bratkartoffeln | 6 | 1,4 % | 0 | 1 | 5 | 2026-08-06 |
| 14 | Wedges | 6 | 1,4 % | 0 | 0 | 6 | 2026-07-01 |
| 15 | Gulasch | 3 | 0,7 % | 0 | 3 | 0 | 2025-12-16 |
| 16 | Röstinchen | 2 | 0,5 % | 0 | 0 | 2 | 2026-09-25 |
| 17 | Kartoffel-Käse-Kroketten | 1 | 0,2 % | 0 | 0 | 1 | 2026-02-11 |
| 18 | Safranreis | 1 | 0,2 % | 1 | 0 | 0 | 2024-11-22 |

**Selten (n ≤ 2, 3 Gerichte):** Röstinchen, Kartoffel-Käse-Kroketten, Safranreis

**Nur als Alternative angesagt:** Kraut, Peperonata, Zucchini

## 2. Wiederholungen und Refraktärzeit

Abstände in **Arbeitstagen** (Position im Spielkalender; freie Tage und Saisonpausen zählen nicht). Abstände über eine Saisongrenze hinweg werden ignoriert. „Zufall“ = Erwartung, wenn die Küche jeden Tag unabhängig nach den Jahreshäufigkeiten wählen würde.

| Kategorie | kleinster Abstand | Median | ≤ 2 AT | ≤ 5 AT | ≤ 10 AT | ≤ 20 AT | gleiche Woche (Paare) | Zufall | p (weniger als Zufall) | keine Wdh. innerhalb |
|---|---|---|---|---|---|---|---|---|---|---|
| Vorspeise | 3 | 17,5 | 0 % | 2 % | 16 % | 60 % | 0 | 37,1 | < 0,001 | 5 AT |
| Hauptspeise | 2 | 19,0 | 1 % | 4 % | 20 % | 58 % | 0 | 36,9 | < 0,001 | 3 AT |
| Beilage | 1 | 8,0 | 6 % | 31 % | 64 % | 87 % | 17 | 97,1 | < 0,001 | 1 AT |

- **Vorspeise**: Die Küche **vermeidet** Wiederholungen innerhalb von 5 Arbeitstagen (6 gleiche Paare, Zufall 93,1); innerhalb von 10 Arbeitstagen 53 vs 183,0. Erste Wiederholung frühestens nach 3 AT.
- **Hauptspeise**: Die Küche **vermeidet** Wiederholungen innerhalb von 5 Arbeitstagen (15 gleiche Paare, Zufall 92,5); innerhalb von 10 Arbeitstagen 70 vs 181,4. Erste Wiederholung frühestens nach 2 AT.
- **Beilage**: Die Küche wiederholt **seltener** als Zufall innerhalb von 5 Arbeitstagen (131 gleiche Paare, Zufall 243,5); innerhalb von 10 Arbeitstagen 356 vs 478,3. Erste Wiederholung frühestens nach 1 AT.

### Refraktärkurve P(gleiches Gericht im Abstand L)

Basis = Σ p² (globale Anteile, wie in `stats.json`); Saison-Basis = Erwartung für zwei Tage derselben Saison.

| L (AT) | Vorspeise | Hauptspeise | Beilage |
|---|---|---|---|
| 1 | 0,0 % (0/422) | 0,0 % (0/425) | 2,1 % (9/425) |
| 2 | 0,0 % (0/419) | 0,5 % (2/422) | 3,3 % (14/422) |
| 3 | 0,2 % (1/416) | 0,7 % (3/419) | 7,4 % (31/419) |
| 4 | 0,5 % (2/413) | 1,2 % (5/416) | 8,9 % (37/416) |
| 5 | 0,7 % (3/411) | 1,2 % (5/413) | 9,7 % (40/413) |
| 6 | 1,5 % (6/408) | 1,7 % (7/410) | 9,5 % (39/410) |
| 7 | 2,5 % (10/405) | 1,2 % (5/407) | 12,5 % (51/407) |
| 8 | 2,0 % (8/402) | 2,5 % (10/404) | 10,4 % (42/404) |
| 9 | 3,0 % (12/399) | 2,7 % (11/401) | 11,0 % (44/401) |
| 10 | 2,8 % (11/396) | 5,5 % (22/398) | 12,3 % (49/398) |
| 11 | 2,8 % (11/394) | 2,5 % (10/396) | 10,9 % (43/396) |
| 12 | 6,2 % (24/390) | 4,3 % (17/392) | 9,4 % (37/392) |
| 13 | 5,9 % (23/387) | 3,6 % (14/389) | 8,7 % (34/389) |
| 14 | 4,9 % (19/384) | 4,7 % (18/386) | 12,4 % (48/386) |
| 15 | 4,2 % (16/381) | 5,7 % (22/383) | 12,5 % (48/383) |
| 16 | 4,0 % (15/378) | 2,4 % (9/380) | 11,6 % (44/380) |
| 17 | 3,2 % (12/375) | 2,4 % (9/377) | 13,8 % (52/377) |
| 18 | 4,8 % (18/372) | 4,8 % (18/374) | 8,8 % (33/374) |
| 19 | 2,4 % (9/369) | 4,6 % (17/371) | 10,0 % (37/371) |
| 20 | 5,7 % (21/366) | 8,2 % (30/368) | 11,7 % (43/368) |
| 21 | 2,2 % (8/363) | 3,6 % (13/365) | 14,5 % (53/365) |
| 22 | 3,6 % (13/360) | 4,7 % (17/362) | 12,4 % (45/362) |
| 23 | 3,4 % (12/357) | 3,6 % (13/359) | 12,5 % (45/359) |
| 24 | 2,5 % (9/354) | 4,8 % (17/356) | 11,0 % (39/356) |
| 25 | 5,4 % (19/351) | 4,0 % (14/353) | 13,3 % (47/353) |
| 26 | 4,6 % (16/348) | 3,4 % (12/350) | 10,3 % (36/350) |
| 27 | 3,8 % (13/345) | 2,6 % (9/347) | 11,8 % (41/347) |
| 28 | 6,1 % (21/342) | 4,4 % (15/344) | 10,2 % (35/344) |
| 29 | 5,0 % (17/339) | 5,6 % (19/341) | 12,6 % (43/341) |
| 30 | 7,1 % (24/337) | 3,8 % (13/338) | 14,5 % (49/338) |
| Basis Σp² | 4,2 % | 4,1 % | 11,2 % |
| Saison-Basis | 4,5 % | 4,3 % | 11,6 % |

**Auffällige Spitzen (Rate > 1,3 × Saison-Basis, p < 0,05; L=5 ≈ 1 Woche, L=20 ≈ 4 Wochen):**

- Vorspeise: L=30 → 7,1 % vs 4,5 % (24/337, p = 0,017)
- Hauptspeise: L=20 → 8,2 % vs 4,4 % (30/368, p < 0,001)

**Wochenrhythmus** – gleiche Speise bei Abständen L = 10, 15, 20, 25, 30 AT (meist gleicher Wochentag) vs. allen anderen Abständen 10–30 AT:

| Kategorie | L = 5·k | andere L | p |
|---|---|---|---|
| Vorspeise | 5,0 % (91/1831) | 4,1 % (240/5857) | 0,037 |
| Hauptspeise | 5,5 % (101/1840) | 3,9 % (227/5889) | < 0,001 |
| Beilage | 12,8 % (236/1840) | 11,3 % (665/5889) | 0,022 |

→ Der Wochentag-Effekt (Abschnitt 3) erzeugt einen schwachen Wochenrhythmus; die Refraktärzeit dominiert aber die ersten 1–2 Wochen.

### Abstände je Gericht – Vorspeise (n ≥ 8)

| Gericht | n | Mittel | Median | min | max | Wdh. gleiche Woche |
|---|---|---|---|---|---|---|
| Arrabbiata | 30 | 14,6 | 13,0 | 7 | 25 | 0 |
| Nudel mit Käsesoße | 29 | 14,9 | 14,0 | 5 | 30 | 0 |
| Hirten | 28 | 14,6 | 13,0 | 4 | 45 | 0 |
| Aglio olio | 26 | 16,4 | 14,0 | 6 | 41 | 0 |
| Nudel mit Ragu | 25 | 16,0 | 18,0 | 5 | 33 | 0 |
| Nudel mit Thunfischsoße | 25 | 16,7 | 13,5 | 6 | 41 | 0 |
| Schlutzer | 23 | 17,9 | 14,0 | 3 | 41 | 0 |
| Nudel Mammarosa | 21 | 20,3 | 18,5 | 4 | 45 | 0 |
| Lasagne | 20 | 20,7 | 18,0 | 12 | 48 | 0 |
| Amatriciana | 18 | 19,7 | 20,0 | 12 | 30 | 0 |
| Tortellini mit Schinken-Rahm | 18 | 19,2 | 19,0 | 7 | 30 | 0 |
| Nudel mit Pesto | 16 | 22,8 | 20,0 | 6 | 49 | 0 |
| Spinatspatzlen | 16 | 27,7 | 25,0 | 8 | 71 | 0 |
| Gnocchi mit Tomatensoße | 13 | 28,3 | 28,0 | 7 | 78 | 0 |
| Käseknödel | 11 | 44,8 | 22,0 | 11 | 146 | 0 |
| Pizzastrudel | 11 | 41,1 | 41,5 | 30 | 61 | 0 |
| Carbonara | 10 | 33,9 | 33,0 | 18 | 63 | 0 |
| Spinatcannelloni | 10 | 44,3 | 48,0 | 23 | 67 | 0 |
| Nudel mit Lachs | 8 | 46,5 | 58,5 | 9 | 63 | 0 |

### Abstände je Gericht – Hauptspeise (n ≥ 8)

| Gericht | n | Mittel | Median | min | max | Wdh. gleiche Woche |
|---|---|---|---|---|---|---|
| Hühnerbrust | 31 | 13,5 | 12,5 | 4 | 31 | 0 |
| Champignonschnitzel | 28 | 14,7 | 12,0 | 3 | 34 | 0 |
| Truthahngeschnetzeltes | 26 | 17,0 | 16,0 | 8 | 34 | 0 |
| Truthahnschnitzel | 26 | 17,0 | 13,0 | 2 | 85 | 0 |
| Schweinsschopf | 23 | 18,6 | 14,5 | 4 | 73 | 0 |
| Truthahnbraten | 23 | 17,2 | 11,0 | 4 | 66 | 0 |
| Wienerschnitzel | 22 | 18,3 | 15,0 | 7 | 41 | 0 |
| Schweinsschnitzel | 21 | 17,9 | 14,0 | 2 | 59 | 0 |
| Schweinsfilet | 20 | 18,8 | 15,0 | 4 | 44 | 0 |
| Leberkas | 19 | 24,0 | 21,0 | 13 | 61 | 0 |
| Chilli con carne | 17 | 24,0 | 21,0 | 12 | 44 | 0 |
| Hühnerhaxlen | 17 | 28,0 | 24,5 | 7 | 76 | 0 |
| Schweinskotelett | 17 | 18,7 | 17,5 | 9 | 60 | 0 |
| Hauswurst | 13 | 35,4 | 27,0 | 17 | 87 | 0 |
| Cordon Bleu | 12 | 30,3 | 23,5 | 15 | 62 | 0 |
| Zwiebelrostbraten | 12 | 34,8 | 35,0 | 6 | 61 | 0 |
| Schweinsgulasch | 10 | 42,9 | 33,0 | 17 | 78 | 0 |
| Zigeunerschnitzel | 10 | 41,0 | 32,0 | 14 | 92 | 0 |

### Abstände je Gericht – Beilage

| Gericht | n | Mittel | Median | min | max | Wdh. gleiche Woche |
|---|---|---|---|---|---|---|
| Reis | 97 | 4,5 | 4,0 | 1 | 11 | 13 |
| Pommes | 56 | 7,6 | 6,0 | 1 | 25 | 3 |
| Spatzlen | 44 | 9,7 | 8,0 | 3 | 26 | 0 |
| Püree | 43 | 9,7 | 9,0 | 3 | 20 | 0 |
| Ofenkartoffeln | 38 | 10,9 | 9,0 | 2 | 45 | 1 |
| Kartoffelsalat | 34 | 11,9 | 10,0 | 4 | 32 | 0 |
| Kroketten | 24 | 16,6 | 12,0 | 7 | 31 | 0 |
| Kartoffelgratin | 23 | 13,2 | 11,5 | 3 | 40 | 0 |
| Plent | 19 | 22,1 | 20,5 | 4 | 60 | 0 |
| Röstkartoffeln | 14 | 25,3 | 23,0 | 2 | 47 | 0 |
| Salzkartoffeln | 11 | 42,6 | 22,0 | 5 | 151 | 0 |
| Kartoffelstampf | 9 | 61,5 | 47,0 | 10 | 134 | 0 |
| Bratkartoffeln | 6 | 27,0 | 21,5 | 5 | 60 | 0 |
| Wedges | 6 | 21,2 | 21,0 | 7 | 35 | 0 |

## 3. Wochentage

Servierte Tage je Wochentag (Hauptspeise): Mo 83, Di 88, Mi 89, Do 89, Fr 82. Getestet wurden 300 Kombinationen (Gericht mit n ≥ 5 × Wochentag) mit einem einseitigen Binomialtest; bei so vielen Tests sind einzelne p < 0,05 auch zufällig zu erwarten (Bonferroni-Schwelle ≈ 0,0002).

### Gezielte Hypothesen

| Merkmal | n Tage | Mo | Di | Mi | Do | Fr | häufigster Tag | Anteil (erwartet) | p |
|---|---|---|---|---|---|---|---|---|---|
| Fisch (alle Fischgerichte) | 13 | 0 | 0 | 2 | 0 | 11 | Fr | 85 % (19 %) | < 0,001 |
| Fisch außerhalb Fastenzeit | 3 | 0 | 0 | 0 | 0 | 3 | Fr | 100 % (19 %) | 0,007 |
| Scombri | 3 | 0 | 0 | 1 | 0 | 2 | Fr | 67 % (19 %) | 0,095 |
| Plent | 19 | 0 | 0 | 5 | 5 | 9 | Fr | 47 % (19 %) | 0,005 |
| Leberkas | 19 | 3 | 1 | 6 | 5 | 4 | Mi | 32 % (21 %) | 0,182 |
| Hauswurst | 14 | 0 | 0 | 4 | 4 | 6 | Fr | 43 % (19 %) | 0,035 |

### Auffällige Wochentag-Vorlieben (Lift ≥ 1,5, mind. 3×, p < 0,05)

| Kategorie | Gericht | Tag | an diesem Tag | Anteil | erwartet | Lift | p | Bonferroni |
|---|---|---|---|---|---|---|---|---|
| Hauptspeise | Schweinskotelett | Mi | 13/17 | 76 % | 21 % | 3,70 | < 0,001 | ✔ |
| Beilage | Reis | Mo | 39/97 | 40 % | 19 % | 2,09 | < 0,001 | ✔ |
| Vorspeise | Arrabbiata | Mo | 17/30 | 57 % | 19 % | 2,94 | < 0,001 | ✔ |
| Hauptspeise | Champignonschnitzel | Mo | 15/28 | 54 % | 19 % | 2,78 | < 0,001 | ✔ |
| Vorspeise | Spinatspatzlen | Di | 10/16 | 62 % | 20 % | 3,05 | < 0,001 |  |
| Vorspeise | Amatriciana | Mo | 10/18 | 56 % | 19 % | 2,88 | < 0,001 |  |
| Hauptspeise | Schweinsschnitzel | Mo | 11/21 | 52 % | 19 % | 2,72 | < 0,001 |  |
| Hauptspeise | Truthahnbraten | Di | 12/23 | 52 % | 20 % | 2,56 | < 0,001 |  |
| Beilage | Salzkartoffeln | Fr | 7/11 | 64 % | 19 % | 3,34 | 0,001 |  |
| Vorspeise | Lasagne | Di | 10/20 | 50 % | 20 % | 2,44 | 0,003 |  |
| Beilage | Plent | Fr | 9/19 | 47 % | 19 % | 2,49 | 0,005 |  |
| Vorspeise | Tortellini mit Schinken-Rahm | Di | 9/18 | 50 % | 20 % | 2,44 | 0,005 |  |
| Hauptspeise | Hühnerbrust | Di | 13/31 | 42 % | 20 % | 2,05 | 0,005 |  |
| Hauptspeise | Schweinsschnitzel mit Kräuterrahmsoße | Mo | 4/5 | 80 % | 19 % | 4,15 | 0,006 |  |
| Vorspeise | Nudel mit Lachs | Fr | 5/8 | 62 % | 19 % | 3,24 | 0,009 |  |
| Hauptspeise | Truthahngeschnetzeltes | Di | 11/26 | 42 % | 20 % | 2,07 | 0,009 |  |
| Vorspeise | Nudel Mammarosa | Mo | 9/21 | 43 % | 19 % | 2,22 | 0,011 |  |
| Beilage | Spatzlen | Do | 16/44 | 36 % | 21 % | 1,76 | 0,012 |  |
| Hauptspeise | Ossobuchi | Do | 4/6 | 67 % | 21 % | 3,23 | 0,019 |  |
| Beilage | Wedges | Mi | 4/6 | 67 % | 21 % | 3,23 | 0,019 |  |
| Beilage | Püree | Di | 15/43 | 35 % | 20 % | 1,71 | 0,020 |  |
| Beilage | Ofenkartoffeln | Mo | 13/38 | 34 % | 19 % | 1,78 | 0,022 |  |
| Hauptspeise | Cordon Bleu | Mi | 6/12 | 50 % | 21 % | 2,42 | 0,023 |  |
| Vorspeise | Spinatcannelloni | Fr | 5/10 | 50 % | 19 % | 2,59 | 0,028 |  |
| Vorspeise | Carbonara | Fr | 5/10 | 50 % | 19 % | 2,59 | 0,028 |  |

### Gerichte, die an einem Wochentag (fast) nie kommen (n ≥ 10, p < 0,05)

| Kategorie | Gericht | Tag | an diesem Tag | erwartet | p |
|---|---|---|---|---|---|
| Vorspeise | Nudel mit Käsesoße | Do | 1/29 | 5,9 | 0,012 |
| Hauptspeise | Champignonschnitzel | Mi | 1/28 | 5,8 | 0,013 |
| Beilage | Plent | Di | 0/19 | 3,9 | 0,013 |
| Vorspeise | Amatriciana | Mi | 0/18 | 3,7 | 0,015 |
| Beilage | Plent | Mo | 0/19 | 3,7 | 0,017 |
| Hauptspeise | Champignonschnitzel | Fr | 1/28 | 5,3 | 0,021 |
| Hauptspeise | Schweinskotelett | Di | 0/17 | 3,5 | 0,021 |
| Vorspeise | Tortellini mit Schinken-Rahm | Mo | 0/18 | 3,5 | 0,021 |
| Hauptspeise | Schweinskotelett | Mo | 0/17 | 3,3 | 0,026 |
| Hauptspeise | Schweinskotelett | Fr | 0/17 | 3,2 | 0,028 |
| Vorspeise | Spinatspatzlen | Mo | 0/16 | 3,1 | 0,032 |
| Vorspeise | Nudel mit Pesto | Mo | 0/16 | 3,1 | 0,032 |
| Vorspeise | Arrabbiata | Mi | 2/30 | 6,2 | 0,037 |
| Beilage | Kroketten | Mo | 1/24 | 4,6 | 0,040 |
| Beilage | Röstkartoffeln | Di | 0/14 | 2,9 | 0,041 |

### Vorspeise: Anzahl je Wochentag (Top 12)

| Gericht | Mo | Di | Mi | Do | Fr | max. Lift |
|---|---|---|---|---|---|---|
| Arrabbiata | 17 | 4 | 2 | 5 | 2 | 2,94 |
| Nudel mit Käsesoße | 8 | 3 | 9 | 1 | 8 | 1,50 |
| Hirten | 6 | 7 | 9 | 4 | 2 | 1,55 |
| Aglio olio | 5 | 3 | 5 | 7 | 6 | 1,33 |
| Nudel mit Ragu | 5 | 4 | 4 | 9 | 3 | 1,78 |
| Nudel mit Thunfischsoße | 7 | 3 | 5 | 4 | 6 | 1,45 |
| Schlutzer | 3 | 6 | 6 | 5 | 3 | 1,27 |
| Nudel Mammarosa | 9 | 2 | 2 | 7 | 1 | 2,22 |
| Lasagne | 1 | 10 | 1 | 7 | 1 | 2,44 |
| Amatriciana | 10 | 1 | 0 | 6 | 1 | 2,88 |
| Tortellini mit Schinken-Rahm | 0 | 9 | 1 | 3 | 5 | 2,44 |
| Nudel mit Pesto | 0 | 3 | 6 | 3 | 4 | 1,81 |

### Hauptspeise: Anzahl je Wochentag (Top 12)

| Gericht | Mo | Di | Mi | Do | Fr | max. Lift |
|---|---|---|---|---|---|---|
| Hühnerbrust | 2 | 13 | 4 | 9 | 3 | 2,05 |
| Champignonschnitzel | 15 | 8 | 1 | 3 | 1 | 2,78 |
| Truthahngeschnetzeltes | 4 | 11 | 4 | 5 | 2 | 2,07 |
| Truthahnschnitzel | 8 | 3 | 2 | 6 | 7 | 1,60 |
| Schweinsschopf | 4 | 5 | 8 | 3 | 3 | 1,68 |
| Truthahnbraten | 4 | 12 | 3 | 3 | 1 | 2,56 |
| Wienerschnitzel | 5 | 2 | 6 | 7 | 2 | 1,54 |
| Schweinsschnitzel | 11 | 4 | 2 | 1 | 3 | 2,72 |
| Schweinsfilet | 5 | 1 | 2 | 6 | 6 | 1,58 |
| Leberkas | 3 | 1 | 6 | 5 | 4 | 1,53 |
| Chilli con carne | 2 | 3 | 5 | 4 | 3 | 1,42 |
| Hühnerhaxlen | 1 | 5 | 2 | 5 | 4 | 1,44 |

### Beilage: Anzahl je Wochentag (Top 12)

| Gericht | Mo | Di | Mi | Do | Fr | max. Lift |
|---|---|---|---|---|---|---|
| Reis | 39 | 21 | 14 | 10 | 13 | 2,09 |
| Pommes | 7 | 13 | 13 | 11 | 12 | 1,14 |
| Spatzlen | 7 | 7 | 8 | 16 | 6 | 1,76 |
| Püree | 4 | 15 | 12 | 8 | 4 | 1,71 |
| Ofenkartoffeln | 13 | 8 | 4 | 8 | 5 | 1,78 |
| Kartoffelsalat | 5 | 3 | 11 | 8 | 7 | 1,57 |
| Kroketten | 1 | 7 | 3 | 5 | 8 | 1,75 |
| Kartoffelgratin | 2 | 5 | 6 | 8 | 2 | 1,68 |
| Plent | 0 | 0 | 5 | 5 | 9 | 2,49 |
| Röstkartoffeln | 2 | 0 | 3 | 5 | 4 | 1,73 |
| Salzkartoffeln | 0 | 1 | 0 | 3 | 7 | 3,35 |
| Kartoffelstampf | 2 | 4 | 3 | 0 | 0 | 2,18 |

## 4. Kombinationen

### Beilage | Hauptspeise (Hauptspeisen mit n ≥ 3)

Wer die Hauptspeise kennt (bzw. richtig schätzt), sollte die dazu typische Beilage tippen: Treffer 48 % (Leave-one-out) statt 23 % mit der global häufigsten Beilage (Reis).

| Hauptspeise | n | Beilage 1 | Beilage 2 | Beilage 3 |
|---|---|---|---|---|
| Hühnerbrust | 31 | Kroketten 35 % (11) | Spatzlen 23 % (7) | Kartoffelgratin 13 % (4) |
| Champignonschnitzel | 28 | Reis 75 % (21) | Kartoffelgratin 18 % (5) | Püree 4 % (1) |
| Truthahngeschnetzeltes | 26 | Püree 42 % (11) | Reis 35 % (9) | Spatzlen 19 % (5) |
| Truthahnschnitzel | 26 | Ofenkartoffeln 42 % (11) | Pommes 38 % (10) | Kroketten 8 % (2) |
| Schweinsschopf | 23 | Pommes 26 % (6) | Reis 17 % (4) | Kartoffelgratin 13 % (3) |
| Truthahnbraten | 23 | Püree 30 % (7) | Spatzlen 22 % (5) | Reis 17 % (4) |
| Wienerschnitzel | 22 | Kartoffelsalat 82 % (18) | Pommes 18 % (4) |  |
| Schweinsschnitzel | 21 | Ofenkartoffeln 38 % (8) | Reis 24 % (5) | Pommes 10 % (2) |
| Schweinsfilet | 20 | Kroketten 30 % (6) | Spatzlen 30 % (6) | Reis 25 % (5) |
| Leberkas | 19 | Röstkartoffeln 63 % (12) | Pommes 37 % (7) |  |
| Chilli con carne | 17 | Reis 100 % (17) |  |  |
| Hühnerhaxlen | 17 | Pommes 71 % (12) | Ofenkartoffeln 24 % (4) | Wedges 6 % (1) |
| Schweinskotelett | 17 | Kartoffelgratin 35 % (6) | Spatzlen 24 % (4) | Ofenkartoffeln 18 % (3) |
| Hauswurst | 13 | Plent 100 % (13) |  |  |
| Cordon Bleu | 12 | Kartoffelsalat 100 % (12) |  |  |
| Zwiebelrostbraten | 12 | Reis 50 % (6) | Püree 42 % (5) | Kroketten 8 % (1) |
| Schweinsgulasch | 10 | Püree 40 % (4) | Reis 40 % (4) | Spatzlen 20 % (2) |
| Zigeunerschnitzel | 10 | Reis 50 % (5) | Spatzlen 30 % (3) | Kartoffelstampf 10 % (1) |
| Currywurst | 7 | Pommes 100 % (7) |  |  |
| Gekochtes Rindfleisch | 6 | Salzkartoffeln 100 % (6) |  |  |
| Ossobuchi | 6 | Spatzlen 50 % (3) | Reis 33 % (2) | Safranreis 17 % (1) |
| Sparerips | 6 | Pommes 67 % (4) | Röstinchen 17 % (1) | Wedges 17 % (1) |
| Hackbraten | 5 | Püree 60 % (3) | Reis 40 % (2) |  |
| Pizzaiolaschnitzel | 5 | Ofenkartoffeln 60 % (3) | Pommes 40 % (2) |  |
| Schweinsschnitzel mit Kräuterrahmsoße | 5 | Reis 40 % (2) | Spatzlen 40 % (2) | Kroketten 20 % (1) |
| Gulasch | 4 | Plent 50 % (2) | Reis 50 % (2) |  |
| Knödel | 3 | Gulasch 100 % (3) |  |  |
| Rindsbraten | 3 | Reis 67 % (2) | Püree 33 % (1) |  |
| Rindsschnitzel | 3 | Ofenkartoffeln 33 % (1) | Pommes 33 % (1) | Spatzlen 33 % (1) |
| Schweinshaxe | 3 | Ofenkartoffeln 33 % (1) | Plent 33 % (1) | Reis 33 % (1) |
| Scombri | 3 | Plent 100 % (3) |  |  |
| Vitello tonnato | 3 | Bratkartoffeln 100 % (3) |  |  |

### Vorspeise ↔ Hauptspeise (n ≥ 3)

Mutual Information zwischen den Kategorien vs. Erwartung bei zufälliger Zuordnung (300 Permutationen):

| Paar | MI (bit) | Zufall (bit) | p |
|---|---|---|---|
| V–H | 1,730 | 1,681 | 0,070 |
| H–B | 2,074 | 0,835 | 0,003 |
| V–B | 0,905 | 0,900 | 0,419 |

| Vorspeise | Hauptspeise | zusammen | n(V) | n(H) | Lift | p |
|---|---|---|---|---|---|---|
| Lasagne | Truthahngeschnetzeltes | 5 | 19 | 26 | 4,34 | 0,005 |
| Nudel mit Thunfischsoße | Sparerips | 3 | 25 | 6 | 8,58 | 0,005 |
| Gnocchi mit Tomatensoße | Zwiebelrostbraten | 3 | 13 | 12 | 8,25 | 0,005 |
| Carbonara | Schweinsfilet | 3 | 10 | 20 | 6,43 | 0,009 |
| Nudel mit Lachs | Truthahnschnitzel | 3 | 8 | 26 | 6,19 | 0,010 |
| Tortellini mit Schinken-Rahm | Schweinsschopf | 4 | 18 | 23 | 4,14 | 0,014 |
| Nudel mit Thunfischsoße | Chilli con carne | 4 | 25 | 17 | 4,04 | 0,016 |
| Spinatspatzlen | Chilli con carne | 3 | 16 | 17 | 4,73 | 0,024 |
| Spinatspatzlen | Hühnerhaxlen | 3 | 16 | 17 | 4,73 | 0,024 |
| Tortellini mit Schinken-Rahm | Hühnerbrust | 4 | 18 | 31 | 3,08 | 0,037 |
| Nudel mit Ragu | Truthahnbraten | 4 | 25 | 23 | 2,98 | 0,042 |
| Arrabbiata | Champignonschnitzel | 5 | 30 | 28 | 2,55 | 0,043 |
| Arrabbiata | Schweinsfilet | 4 | 30 | 20 | 2,86 | 0,049 |
| Nudel mit Käsesoße | Wienerschnitzel | 4 | 29 | 21 | 2,82 | 0,051 |
| Hirten | Schweinskotelett | 3 | 28 | 17 | 2,70 | 0,098 |
| Lasagne | Truthahnschnitzel | 3 | 19 | 26 | 2,61 | 0,104 |
| Nudel mit Thunfischsoße | Schweinsschnitzel | 3 | 25 | 21 | 2,45 | 0,121 |
| Nudel mit Ragu | Wienerschnitzel | 3 | 25 | 21 | 2,45 | 0,121 |
| Arrabbiata | Leberkas | 3 | 30 | 18 | 2,38 | 0,130 |
| Hirten | Hühnerbrust | 4 | 28 | 31 | 1,98 | 0,140 |
| Nudel mit Käsesoße | Schweinsschnitzel | 3 | 29 | 21 | 2,11 | 0,168 |
| Hirten | Truthahnbraten | 3 | 28 | 23 | 2,00 | 0,188 |
| Aglio olio | Champignonschnitzel | 3 | 26 | 28 | 1,77 | 0,239 |
| Hirten | Truthahnschnitzel | 3 | 28 | 26 | 1,77 | 0,239 |
| Hirten | Truthahngeschnetzeltes | 3 | 28 | 26 | 1,77 | 0,239 |

## 5. Saisonalität

### Fastenzeit (Aschermittwoch – Ostersonntag)

Fastenzeiten in den Daten: 2025: 05.03.–20.04., 2026: 18.02.–05.04.. Fisch = jede Hauptspeise, die als Fisch gilt (inkl. Scombri).

**Hauptspeise** (Fastentage n=64, sonst n=367; Gerichte mit ≥ 2 Fastentagen):

| Gericht | Fastenzeit | sonst | Lift | p |
|---|---|---|---|---|
| Scombri | 4,7 % (3) | 0,0 % (0) | nur Fastenzeit | 0,003 |
| Fisch | 15,6 % (10) | 0,8 % (3) | 19,11 | < 0,001 |
| Currywurst | 3,1 % (2) | 1,4 % (5) | 2,29 | 0,279 |
| Truthahnbraten | 9,4 % (6) | 4,6 % (17) | 2,02 | 0,115 |
| Schweinsfilet | 6,2 % (4) | 4,4 % (16) | 1,43 | 0,345 |
| Zigeunerschnitzel | 3,1 % (2) | 2,2 % (8) | 1,43 | 0,450 |
| Chilli con carne | 4,7 % (3) | 3,8 % (14) | 1,23 | 0,473 |
| Schweinskotelett | 4,7 % (3) | 3,8 % (14) | 1,23 | 0,473 |
| Zwiebelrostbraten | 3,1 % (2) | 2,7 % (10) | 1,15 | 0,551 |
| Champignonschnitzel | 6,2 % (4) | 6,5 % (24) | 0,96 | 0,614 |
| Wienerschnitzel | 4,7 % (3) | 5,2 % (19) | 0,91 | 0,655 |
| Truthahngeschnetzeltes | 4,7 % (3) | 6,3 % (23) | 0,75 | 0,764 |

**Vorspeise** (Fastentage n=64, sonst n=366; Gerichte mit ≥ 2 Fastentagen):

| Gericht | Fastenzeit | sonst | Lift | p |
|---|---|---|---|---|
| Nudel mit Lachs | 3,1 % (2) | 1,6 % (6) | 1,91 | 0,339 |
| Amatriciana | 6,2 % (4) | 3,8 % (14) | 1,63 | 0,275 |
| Nudel mit Ragu | 7,8 % (5) | 5,5 % (20) | 1,43 | 0,312 |
| Spinatcannelloni | 3,1 % (2) | 2,2 % (8) | 1,43 | 0,451 |
| Spinatspatzlen | 4,7 % (3) | 3,6 % (13) | 1,32 | 0,433 |
| Pizzastrudel | 3,1 % (2) | 2,5 % (9) | 1,27 | 0,503 |
| Schlutzer | 6,2 % (4) | 5,2 % (19) | 1,20 | 0,454 |
| Nudel mit Käsesoße | 7,8 % (5) | 6,6 % (24) | 1,19 | 0,437 |
| Aglio olio | 6,2 % (4) | 6,0 % (22) | 1,04 | 0,555 |
| Gnocchi mit Tomatensoße | 3,1 % (2) | 3,0 % (11) | 1,04 | 0,597 |
| Lasagne | 4,7 % (3) | 4,6 % (17) | 1,01 | 0,589 |
| Arrabbiata | 6,2 % (4) | 7,1 % (26) | 0,88 | 0,672 |

**Beilage** (Fastentage n=64, sonst n=367; Gerichte mit ≥ 2 Fastentagen):

| Gericht | Fastenzeit | sonst | Lift | p |
|---|---|---|---|---|
| Salzkartoffeln | 4,7 % (3) | 2,2 % (8) | 2,15 | 0,217 |
| Plent | 7,8 % (5) | 3,8 % (14) | 2,05 | 0,140 |
| Kartoffelgratin | 9,4 % (6) | 4,6 % (17) | 2,02 | 0,115 |
| Röstkartoffeln | 4,7 % (3) | 3,0 % (11) | 1,56 | 0,346 |
| Kartoffelsalat | 10,9 % (7) | 7,4 % (27) | 1,49 | 0,233 |
| Püree | 12,5 % (8) | 9,5 % (35) | 1,31 | 0,303 |
| Kroketten | 6,2 % (4) | 5,4 % (20) | 1,15 | 0,487 |
| Spatzlen | 9,4 % (6) | 10,4 % (38) | 0,91 | 0,654 |
| Reis | 20,3 % (13) | 22,9 % (84) | 0,89 | 0,698 |
| Pommes | 7,8 % (5) | 13,9 % (51) | 0,56 | 0,933 |
| Ofenkartoffeln | 3,1 % (2) | 9,8 % (36) | 0,32 | 0,983 |

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
| Röstkartoffeln | 3,8 % (4) | 3,1 % (3) | 1,000 |
| Wedges | 0,9 % (1) | 1,0 % (1) | 1,000 |
| Gulasch | 0,9 % (1) | 2,0 % (2) | 0,941 |
| Kartoffelgratin | 3,8 % (4) | 5,1 % (5) | 0,904 |
| Spatzlen | 8,5 % (9) | 10,2 % (10) | 0,862 |
| Plent | 2,8 % (3) | 5,1 % (5) | 0,643 |
| Salzkartoffeln | 0,0 % (0) | 3,1 % (3) | 0,222 |
| Kartoffelstampf | 0,9 % (1) | 4,1 % (4) | 0,328 |

Signifikant (p < 0,05): _keine_

### Monate (Anteil der servierten Tage, Top 10)

**Vorspeise** (Tage je Monat: Jan 30, Feb 40, Mär 42, Apr 34, Mai 39, Jun 39, Jul 45, Aug 22, Sep 43, Okt 33, Nov 35, Dez 28)

| Gericht | Jan | Feb | Mär | Apr | Mai | Jun | Jul | Aug | Sep | Okt | Nov | Dez |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Arrabbiata | 10 | 8 | 5 | 6 | 5 | 8 | 7 | 9 | 7 | 6 | 6 | 11 |
| Nudel mit Käsesoße | 7 | 8 | 7 | 3 | 10 | 10 | 4 | 5 | 7 | 9 | 6 | 4 |
| Hirten | · | 8 | 7 | 3 | 8 | 8 | 7 | 14 | 9 | 6 | 3 | 7 |
| Aglio olio | 10 | · | 7 | 6 | 5 | 5 | 4 | 14 | 5 | 6 | 9 | 7 |
| Nudel mit Ragu | 7 | 8 | 5 | 9 | 5 | 3 | 9 | · | 7 | 6 | 6 | 4 |
| Nudel mit Thunfischsoße | 7 | 10 | 2 | 6 | 5 | 5 | 4 | 9 | 2 | 9 | 9 | 4 |
| Schlutzer | 7 | 2 | 7 | 3 | 8 | 3 | 9 | 5 | 5 | 6 | 3 | 7 |
| Nudel Mammarosa | 3 | 5 | 5 | 3 | 3 | 8 | 4 | 5 | 7 | 3 | 3 | 11 |
| Lasagne | 3 | · | 5 | 6 | 8 | 5 | 7 | · | 5 | 9 | 3 | 4 |
| Amatriciana | 3 | 2 | 7 | 6 | 5 | 5 | 2 | 5 | 2 | 3 | 6 | 4 |

**Hauptspeise** (Tage je Monat: Jan 30, Feb 40, Mär 42, Apr 34, Mai 39, Jun 39, Jul 45, Aug 22, Sep 44, Okt 33, Nov 35, Dez 28)

| Gericht | Jan | Feb | Mär | Apr | Mai | Jun | Jul | Aug | Sep | Okt | Nov | Dez |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Hühnerbrust | 10 | 5 | 10 | 3 | 10 | 8 | 7 | · | 9 | 6 | 9 | 7 |
| Champignonschnitzel | 3 | 8 | 5 | 9 | 8 | 5 | 4 | 9 | 7 | 9 | 3 | 11 |
| Truthahngeschnetzeltes | 7 | 8 | 5 | 3 | 10 | 5 | 4 | 5 | 5 | 6 | 6 | 11 |
| Truthahnschnitzel | 7 | 2 | 5 | 3 | 8 | 18 | 7 | 5 | 5 | 3 | 3 | 7 |
| Schweinsschopf | 7 | 8 | 2 | 6 | 3 | · | 9 | 9 | 5 | 6 | 6 | 7 |
| Truthahnbraten | · | 5 | 10 | 9 | · | · | 4 | 14 | 7 | 6 | 9 | 4 |
| Wienerschnitzel | · | 10 | 2 | 3 | 5 | 3 | 9 | 5 | 9 | 6 | 3 | 4 |
| Schweinsschnitzel | 3 | 5 | 2 | 3 | 3 | 8 | 9 | 9 | 2 | 6 | 6 | 4 |
| Schweinsfilet | 3 | 5 | 5 | 9 | 8 | 3 | 4 | · | 5 | · | 9 | 4 |
| Leberkas | 7 | · | 2 | 6 | 5 | 5 | 4 | 5 | 5 | 6 | 6 | 4 |

**Beilage** (Tage je Monat: Jan 30, Feb 40, Mär 42, Apr 34, Mai 39, Jun 39, Jul 45, Aug 22, Sep 44, Okt 33, Nov 35, Dez 28)

| Gericht | Jan | Feb | Mär | Apr | Mai | Jun | Jul | Aug | Sep | Okt | Nov | Dez |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Reis | 23 | 22 | 24 | 21 | 18 | 18 | 24 | 27 | 20 | 30 | 20 | 25 |
| Pommes | 13 | 12 | 10 | 12 | 13 | 15 | 18 | 18 | 11 | 15 | 6 | 14 |
| Spatzlen | 10 | 8 | 10 | 12 | 13 | 5 | 9 | 14 | 11 | 9 | 11 | 14 |
| Püree | 10 | 12 | 12 | 12 | 18 | 8 | 7 | 14 | 7 | 6 | 11 | 4 |
| Ofenkartoffeln | 3 | 8 | 2 | 6 | 5 | 13 | 13 | 9 | 14 | 12 | 11 | 7 |
| Kartoffelsalat | 3 | 10 | 5 | 9 | 8 | 13 | 9 | 5 | 9 | 9 | 6 | 7 |
| Kroketten | 7 | 8 | 7 | 6 | 3 | 8 | 2 | 5 | 7 | 6 | 9 | · |
| Kartoffelgratin | 3 | 8 | 10 | 6 | 8 | 5 | 4 | · | 2 | 6 | 6 | 4 |
| Plent | 7 | 2 | 7 | 6 | 3 | 3 | 4 | · | 5 | 3 | 6 | 7 |
| Röstkartoffeln | 3 | 2 | 2 | 6 | 3 | 8 | 2 | · | 2 | 3 | 3 | 4 |

### Weihnachtszeit (1.–23. Dezember)

- **Vorspeise** (Dezembertage n=28): Fleischcannelloni 2× (7 % vs 0 % sonst, p = 0,012); Nudel Mammarosa 3× (11 % vs 4 % sonst, p = 0,153); Arrabbiata 3× (11 % vs 7 % sonst, p = 0,310)
- **Hauptspeise** (Dezembertage n=28): Zwiebelrostbraten 2× (7 % vs 2 % sonst, p = 0,181); Hauswurst 2× (7 % vs 3 % sonst, p = 0,205); Hühnerhaxlen 2× (7 % vs 4 % sonst, p = 0,304); Truthahngeschnetzeltes 3× (11 % vs 6 % sonst, p = 0,237); Champignonschnitzel 3× (11 % vs 6 % sonst, p = 0,273)
- **Beilage** (Dezembertage n=28): Kartoffelstampf 2× (7 % vs 2 % sonst, p = 0,112); Plent 2× (7 % vs 4 % sonst, p = 0,353)
- Letztes Menü vor Weihnachten 2024 (19.12.): Lasagne / Truthahngeschnetzeltes / Spatzlen
- Letztes Menü vor Weihnachten 2025 (19.12.): Nudel Mammarosa / Cordon Bleu / Kartoffelsalat

## 6. Trends (2026 vs. 2024, 2025)

- **Vorspeise neu 2026** (10): Gnocchi mit Gorgonzolasoße (2×), Spinatknödel mit Käsesoße (2×), Gnocchi mit Kräutersauce (1×), Gnocchi mit Lachs (1×), Käse-Sofficini mit Tomantensoße (1×), Nudel mit Schinken-Rahm (1×), Pilzrisotto (1×), Spargelrisotto (1×), Speck-Zwiebel-Kuchen (1×), Tomatenrisotto (1×)
- **Vorspeise verschwunden 2026** (27): Fleischcannelloni (3×), Ravioli mit Parmesan-Butter (3×), Tomatenrisotto mit Mozzarella (3×), Gerstsuppe (2×), Gnocchi mit Käsesoße (2×), Gulaschsuppe (2×), Nudelsalat (2×), Omelett mit Schinken und Käse (2×), Plentauflauf (2×), Ravioli (2×), Fleischsuppe (1×), Gemüselasagne (1×), Gnocchi (1×), Gnocchi mit Ragu (1×), Kürbisrisotto (1×), Nudel mit Lachs und Tomantensoße (1×), Nudel mit Tomatensoße (1×), Nudel mit Tomatensoße und Schinken (1×), Putanesca (1×), Ravioli mit Käsesoße (1×), Ravioli mit Tomantensoße (1×), Reissalat (1×), Schlutzer Schinken-Rahm (1×), Schupfnudel mit Lachs (1×), Schüttelbrot-Risotto mit Speckstreifen (1×), Spinatknödel (1×), Spinatknödel mit Gorgonzolasoße (1×)
- **Hauptspeise neu 2026** (13): Vitello tonnato (3×), Forelle (2×), Frittiertes Pangasiusfilet (2×), Hamburger (2×), Kalbsgulasch (2×), Schweinsfilet mit Pfeffersoße (2×), 1/2 Brathuhn (1×), Fleischkrapfln (1×), Hirschgulasch (1×), Lammbraten (1×), Pangasiusfilet mit Kräuterrahmsoße (1×), Panierter Pangasius (1×), Spiegelei (1×)
- **Hauptspeise verschwunden 2026** (7): Pizzaiolaschnitzel (5×), Knödel (3×), Rotbarschfilet (2×), Frittiertes Schollenfilet (1×), Pangasiusfilet (1×), Paprika-Schweinegulasch (1×), Saures Rindfleisch (1×)
- **Beilage neu 2026** (3): Wedges (6×), Röstinchen (2×), Kartoffel-Käse-Kroketten (1×)
- **Beilage verschwunden 2026** (4): Gulasch (3×), Kraut (1×), Safranreis (1×), Zucchini (1×)

**Aufsteiger / Absteiger** (Anteil 2025 → 2026, Gerichte mit n ≥ 5):

| Kategorie | Gericht |  | 2025 | 2026 |
|---|---|---|---|---|
| Vorspeise | Tortellini mit Schinken-Rahm | ↑ | 3,6 % | 5,6 % |
| Vorspeise | Hirten | ↑ | 5,9 % | 7,3 % |
| Vorspeise | Nudel mit Pesto | ↑ | 3,2 % | 4,5 % |
| Vorspeise | Gnocchi mit Tomatensoße | ↑ | 2,7 % | 4,0 % |
| Vorspeise | Carbonara | ↑ | 1,8 % | 2,8 % |
| Vorspeise | Nudel mit Ragu | ↓ | 6,4 % | 4,5 % |
| Vorspeise | Spinatspatzlen | ↓ | 4,5 % | 2,8 % |
| Vorspeise | Nudel mit Thunfischsoße | ↓ | 6,4 % | 5,1 % |
| Vorspeise | Aglio olio | ↓ | 6,8 % | 5,6 % |
| Vorspeise | Amatriciana | ↓ | 4,5 % | 4,0 % |
| Hauptspeise | Sparerips | ↑ | 0,5 % | 2,3 % |
| Hauptspeise | Cordon Bleu | ↑ | 2,3 % | 4,0 % |
| Hauptspeise | Hühnerhaxlen | ↑ | 3,2 % | 4,5 % |
| Hauptspeise | Zwiebelrostbraten | ↑ | 2,3 % | 3,4 % |
| Hauptspeise | Currywurst | ↑ | 1,4 % | 2,3 % |
| Hauptspeise | Schweinskotelett | ↓ | 5,4 % | 1,7 % |
| Hauptspeise | Truthahnschnitzel | ↓ | 7,2 % | 4,5 % |
| Hauptspeise | Schweinsfilet | ↓ | 5,4 % | 3,4 % |
| Hauptspeise | Schweinsschnitzel | ↓ | 5,9 % | 4,0 % |
| Hauptspeise | Pizzaiolaschnitzel | ↓ | 1,8 % | 0,0 % |
| Beilage | Wedges | ↑ | 0,0 % | 3,4 % |
| Beilage | Kartoffelsalat | ↑ | 6,8 % | 10,2 % |
| Beilage | Spatzlen | ↑ | 8,1 % | 11,3 % |
| Beilage | Bratkartoffeln | ↑ | 0,5 % | 2,8 % |
| Beilage | Pommes | ↑ | 12,7 % | 14,1 % |
| Beilage | Ofenkartoffeln | ↓ | 10,4 % | 6,2 % |
| Beilage | Reis | ↓ | 24,4 % | 20,3 % |
| Beilage | Kartoffelgratin | ↓ | 7,2 % | 3,4 % |
| Beilage | Plent | ↓ | 5,4 % | 3,4 % |
| Beilage | Kroketten | ↓ | 6,3 % | 4,5 % |

### Gewichtung nach Aktualität

Mittlerer Log-Loss einer reinen Häufigkeitsprognose für jeden Tag 2026 (nur Vergangenheit, Gewicht 0,5^(Alter/Halbwertszeit), Glättung 0,5; kleiner = besser). Zeigt, ob jüngere Menüs mehr zählen sollten (Refraktärzeit und Wochentag sind hier bewusst nicht enthalten).

| Kategorie | 30 T | 60 T | 90 T | 180 T | 365 T | ∞ (ungewichtet) |
|---|---|---|---|---|---|---|
| Vorspeise | 3,780 | 3,627 | 3,566 | 3,518 | 3,510 | 3,522 |
| Hauptspeise | 3,755 | 3,670 | 3,641 | 3,627 | 3,636 | 3,661 |
| Beilage | 2,624 | 2,562 | 2,546 | 2,541 | 2,546 | 2,560 |

Aktualitätsgewichtung: beste Halbwertszeit (Log-Loss, Tage) – Vorspeise 365, Hauptspeise 180, Beilage 180.

### Anteile je Jahr (Top-Gerichte)

**Vorspeise**

| Gericht | 2024 | 2025 | 2026 |
|---|---|---|---|
| Arrabbiata | 6,1 % | 7,3 % | 6,8 % |
| Nudel mit Käsesoße | 3,0 % | 6,8 % | 7,3 % |
| Hirten | 6,1 % | 5,9 % | 7,3 % |
| Aglio olio | 3,0 % | 6,8 % | 5,7 % |
| Nudel mit Ragu | 9,1 % | 6,4 % | 4,5 % |
| Nudel mit Thunfischsoße | 6,1 % | 6,4 % | 5,1 % |
| Schlutzer | 3,0 % | 5,5 % | 5,7 % |
| Nudel Mammarosa | 6,1 % | 5,0 % | 4,5 % |
| Lasagne | 6,1 % | 4,1 % | 5,1 % |
| Amatriciana | 3,0 % | 4,5 % | 4,0 % |
| Tortellini mit Schinken-Rahm | 0,0 % | 3,6 % | 5,7 % |
| Nudel mit Pesto | 3,0 % | 3,2 % | 4,5 % |
| Spinatspatzlen | 3,0 % | 4,5 % | 2,8 % |
| Gnocchi mit Tomatensoße | 0,0 % | 2,7 % | 4,0 % |
| Käseknödel | 6,1 % | 1,8 % | 2,8 % |

**Hauptspeise**

| Gericht | 2024 | 2025 | 2026 |
|---|---|---|---|
| Hühnerbrust | 6,1 % | 7,2 % | 7,3 % |
| Champignonschnitzel | 6,1 % | 7,2 % | 5,7 % |
| Truthahngeschnetzeltes | 6,1 % | 5,9 % | 6,2 % |
| Truthahnschnitzel | 6,1 % | 7,2 % | 4,5 % |
| Schweinsschopf | 9,1 % | 5,0 % | 5,1 % |
| Truthahnbraten | 12,1 % | 5,0 % | 4,5 % |
| Wienerschnitzel | 3,0 % | 5,4 % | 5,1 % |
| Schweinsschnitzel | 3,0 % | 5,9 % | 4,0 % |
| Schweinsfilet | 6,1 % | 5,4 % | 3,4 % |
| Leberkas | 6,1 % | 4,5 % | 4,0 % |
| Chilli con carne | 0,0 % | 4,5 % | 4,0 % |
| Hühnerhaxlen | 6,1 % | 3,2 % | 4,5 % |
| Schweinskotelett | 6,1 % | 5,4 % | 1,7 % |
| Hauswurst | 3,0 % | 3,2 % | 2,8 % |
| Cordon Bleu | 0,0 % | 2,3 % | 4,0 % |

**Beilage**

| Gericht | 2024 | 2025 | 2026 |
|---|---|---|---|
| Reis | 21,2 % | 24,4 % | 20,3 % |
| Pommes | 9,1 % | 12,7 % | 14,1 % |
| Spatzlen | 18,2 % | 8,1 % | 11,3 % |
| Püree | 6,1 % | 10,0 % | 10,7 % |
| Ofenkartoffeln | 12,1 % | 10,4 % | 6,2 % |
| Kartoffelsalat | 3,0 % | 6,8 % | 10,2 % |
| Kroketten | 6,1 % | 6,3 % | 4,5 % |
| Kartoffelgratin | 3,0 % | 7,2 % | 3,4 % |
| Plent | 3,0 % | 5,4 % | 3,4 % |
| Röstkartoffeln | 6,1 % | 3,2 % | 2,8 % |
| Salzkartoffeln | 3,0 % | 2,3 % | 2,8 % |
| Kartoffelstampf | 6,1 % | 1,4 % | 2,3 % |
| Bratkartoffeln | 0,0 % | 0,4 % | 2,8 % |
| Wedges | 0,0 % | 0,0 % | 3,4 % |
| Gulasch | 0,0 % | 1,4 % | 0,0 % |

## 7. Spieler

Punkte = Neuberechnung der Engine (`tips.points`; identisch mit dem Excel bis auf dokumentierte manuelle Korrekturen). Nur servierte Tage vor dem Stichtag. „Alles falsch“ = 0 Punkte, „Alles richtig“ = 3 Punkte.

| Jahr | Spieler | Tage | Punkte | P./Tag | Alles falsch | Alles richtig | V | H | B | R4-Verstöße | Abw. Excel |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026 | Johannes | 165 | 45,5 | 0,276 | 105 (64 %) | 1 | 8 % | 10 % | 28 % | 4 | 0 |
| 2026 | Andreas | 171 | 44,5 | 0,260 | 112 (66 %) | 0 | 9 % | 9 % | 25 % | 1 | 0 |
| 2026 | Johannes Paul III | 163 | 41,0 | 0,252 | 113 (69 %) | 2 | 9 % | 9 % | 21 % | 1 | 0 |
| 2026 | Noah | 173 | 41,5 | 0,240 | 121 (70 %) | 1 | 7 % | 9 % | 24 % | 1 | 0 |
| 2025 | Noah | 213 | 51,5 | 0,242 | 151 (71 %) | 1 | 11 % | 8 % | 17 % | 0 | 0 |
| 2025 | Andreas | 214 | 47,5 | 0,222 | 153 (72 %) | 1 | 8 % | 8 % | 20 % | 3 | 1 |
| 2025 | Johannes | 209 | 39,0 | 0,187 | 158 (76 %) | 1 | 8 % | 4 % | 16 % | 0 | 2 |
| 2024 | Johannes | 27 | 6,0 | 0,222 | 20 (74 %) | 0 | 15 % | 8 % | 8 % | 0 | 0 |
| 2024 | Andreas | 34 | 6,5 | 0,191 | 29 (85 %) | 1 | 9 % | 6 % | 9 % | 0 | 0 |
| 2024 | Noah | 29 | 3,0 | 0,103 | 24 (83 %) | 0 | 0 % | 7 % | 14 % | 0 | 0 |

### Lieblingstipps

| Jahr | Spieler | Vorspeise | Hauptspeise | Beilage |
|---|---|---|---|---|
| 2026 | Johannes | Amatriciana 22, Carbonara 15, Hirten 15 | Wienerschnitzel 25, Champignonschnitzel 22, Hühnerhaxlen 16 | Pommes 41, Reis 41, Ofenkartoffeln 17 |
| 2026 | Andreas | Nudel mit Käsesoße 22, Lasagne 18, Spinatspatzlen 15 | Champignonschnitzel 22, Wienerschnitzel 22, Currywurst 17 | Pommes 45, Reis 34, Kartoffelsalat 20 |
| 2026 | Johannes Paul III | Hirten 15, Lasagne 15, Nudel mit Käsesoße 14 | Champignonschnitzel 17, Truthahngeschnetzeltes 15, Wienerschnitzel 15 | Reis 44, Kartoffelsalat 18, Pommes 17 |
| 2026 | Noah | Amatriciana 32, Aglio olio 17, Carbonara 17 | Truthahngeschnetzeltes 36, Champignonschnitzel 32, Hühnerbrust 17 | Reis 42, Püree 39, Kartoffelgratin 22 |
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
| Vorspeise | 11,6 % (n=337) | 7,6 % (n=1004) |
| Hauptspeise | 9,7 % (n=453) | 7,2 % (n=889) |
| Beilage | 27,9 % (n=810) | 10,2 % (n=531) |

| Kategorie | 1–2 AT | 3–5 AT | 6–10 AT | 11–20 AT | 21–40 AT | > 40 AT | nie serviert |
|---|---|---|---|---|---|---|---|
| Vorspeise | 0,0 % (12) | 3,6 % (56) | 7,0 % (284) | 10,8 % (502) | 10,9 % (284) | 4,6 % (152) | 2,0 % (51) |
| Hauptspeise | 0,0 % (9) | 4,4 % (90) | 5,2 % (291) | 9,6 % (510) | 9,2 % (272) | 8,0 % (100) | 10,0 % (70) |
| Beilage | 24,4 % (82) | 27,5 % (437) | 21,1 % (351) | 15,5 % (303) | 15,0 % (113) | 4,5 % (44) | 0,0 % (11) |

- Vorspeise: Top-5-Tipps treffen 11,6 % vs 7,6 % (besser, Faktor 1,53).
- Hauptspeise: Top-5-Tipps treffen 9,7 % vs 7,2 % (besser, Faktor 1,35).
- Beilage: Top-5-Tipps treffen 27,9 % vs 10,2 % (besser, Faktor 2,74).

→ Tipps auf Gerichte, die erst vor 1–5 Arbeitstagen serviert wurden, treffen bei der Vorspeise nur 2,9 % (n=68) gegenüber 8,9 % sonst; Hauptspeise 4,0 % vs 8,4 %; Beilage 27,0 % vs 17,0 %.

### Strategie-Kennzahlen je Spieler und Jahr

Top-5-Anteil = Anteil der Tipps auf die 5 bis dahin häufigsten Gerichte; Vielfalt = mittlere Entropie der eigenen Tipps (bit); kürzlich = Anteil der Tipps auf Gerichte der letzten 5 Arbeitstage.

| Jahr | Spieler | P./Tag | Rang | Top-5-Anteil | Vielfalt | kürzlich |
|---|---|---|---|---|---|---|
| 2026 | Johannes | 0,276 | 1 | 40 % | 3,85 | 16 % |
| 2026 | Andreas | 0,260 | 2 | 40 % | 3,68 | 16 % |
| 2026 | Johannes Paul III | 0,252 | 3 | 45 % | 3,92 | 21 % |
| 2026 | Noah | 0,240 | 4 | 52 % | 3,49 | 19 % |
| 2025 | Noah | 0,242 | 1 | 36 % | 3,80 | 16 % |
| 2025 | Andreas | 0,222 | 2 | 35 % | 3,91 | 15 % |
| 2025 | Johannes | 0,187 | 3 | 36 % | 3,89 | 19 % |
| 2024 | Johannes | 0,222 | 1 | 25 % | 3,19 | 11 % |
| 2024 | Andreas | 0,191 | 2 | 26 % | 3,46 | 7 % |
| 2024 | Noah | 0,103 | 3 | 30 % | 3,25 | 10 % |

Korrelation mit Punkten/Tag über 7 Spieler-Jahre mit ≥ 100 Tagen (sehr kleine Stichprobe, nur Hinweis): Top-5-Anteil r=0,34, Vielfalt r=-0,23, kürzlich r=-0,23, V-Trefferquote r=0,16. Die Vorspeise zählt doppelt so viel wie H oder B (1 vs 0,5 Punkte); über die Spieler-Jahre erklärt die V-Trefferquote die Rangfolge aber nur schwach.

### Notizen je Spieler

- **Johannes 2026**: 0,28 Punkte/Tag (Rang 1/4 in 2026). Top-5-Anteil der Tipps 40 %, Vielfalt 3,8 bit, 16 % Tipps auf Gerichte, die in den letzten 5 Arbeitstagen serviert wurden. Stärkste Kategorie: Beilage (28 % Treffer). Regel-4-Verstöße: 4.
- **Andreas 2026**: 0,26 Punkte/Tag (Rang 2/4 in 2026). Top-5-Anteil der Tipps 40 %, Vielfalt 3,7 bit, 16 % Tipps auf Gerichte, die in den letzten 5 Arbeitstagen serviert wurden. Stärkste Kategorie: Beilage (25 % Treffer). Regel-4-Verstöße: 1.
- **Johannes Paul III 2026**: 0,25 Punkte/Tag (Rang 3/4 in 2026). Top-5-Anteil der Tipps 45 %, Vielfalt 3,9 bit, 21 % Tipps auf Gerichte, die in den letzten 5 Arbeitstagen serviert wurden. Stärkste Kategorie: Beilage (21 % Treffer). Regel-4-Verstöße: 1.
- **Noah 2026**: 0,24 Punkte/Tag (Rang 4/4 in 2026). Top-5-Anteil der Tipps 52 %, Vielfalt 3,5 bit, 19 % Tipps auf Gerichte, die in den letzten 5 Arbeitstagen serviert wurden. Stärkste Kategorie: Beilage (24 % Treffer). Regel-4-Verstöße: 1.
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

