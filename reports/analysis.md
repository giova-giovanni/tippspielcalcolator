# Analyse Tippspiel Essen Wies

_Automatisch erzeugt von `engine/analyze.py` am 2026-10-29 11:31 UTC (Stichtag 2026-10-29). Datenstand: 444 servierte Menüs (2024: 34, 2025: 221, 2026: 189), letztes Menü 2026-10-27._

## Riassunto (IT)

- **Dati**: 444 menù serviti (2024: 34, 2025: 221, 2026: 189); piatti distinti: primo 60, secondo 48, contorno 19.
- **Primo più frequenti**: Arrabbiata (30), Nudel mit Käsesoße (30), Hirten (28); i primi 5 coprono 32 % dei giorni.
- **Secondo più frequenti**: Hühnerbrust (32), Champignonschnitzel (29), Truthahngeschnetzeltes (26); i primi 5 coprono 31 % dei giorni.
- **Contorno più frequenti**: Reis (100), Pommes (58), Spatzlen (45); i primi 5 coprono 64 % dei giorni.
- **Ripetizioni**: la cucina evita le ripetizioni. Primo e secondo: mai due volte nella stessa settimana (0 e 0 coppie contro 38 e 38 attese per caso, p < 0,001); quasi nessuna ripetizione entro 5 (primo) / 3 (secondo) giorni lavorativi; intervallo mediano 17 / 19 giorni lavorativi. Il contorno si ripete molto di più (17 coppie nella stessa settimana, 99 attese per caso). → Non tippare primo/secondo serviti negli ultimi giorni o già serviti questa settimana.
- **Giorno della settimana**: Reis (contorno) il lunedì 42/100 (atteso 19 %, p < 0,001); Schweinskotelett (secondo) il mercoledì 13/17 (atteso 21 %, p < 0,001); Arrabbiata (primo) il lunedì 17/30 (atteso 19 %, p < 0,001); Champignonschnitzel (secondo) il lunedì 16/29 (atteso 19 %, p < 0,001). 4 effetti restano significativi anche con correzione di Bonferroni: il giorno della settimana conta.
- **Ipotesi confermate**: pesce (tutti) il venerdì 11/13; pesce fuori Quaresima il venerdì 3/3; Plent (polenta) il venerdì 10/20. Non confermate: Scombri, Leberkas.
- **Contorno ↔ secondo**: conoscendo il secondo, il contorno più tipico è giusto nel 49 % dei casi (leave-one-out) contro 23 % tippando sempre Reis (es. Champignonschnitzel → Reis 76 %, Wienerschnitzel → Kartoffelsalat 83 %, Leberkas → Röstkartoffeln 60 %, Chilli con carne → Reis 100 %). Primo e secondo invece sono quasi indipendenti (MI 1,69 bit vs 1,65 per caso, p = 0,116).
- **Quaresima / pesce**: pesce in Quaresima nel 16 % dei giorni contro 1 % fuori (10 vs 3 giorni). Nessuna differenza significativa estate/inverno.
- **Trend 2026**: nuovi primi 10, nuovi secondi 13; spariti primi 26, secondi 7 (quasi tutti piatti rari, ≤ 3 volte). Pesatura per recenza (emivita migliore in giorni, log-loss): primo 365, secondo 180, contorno 180.
- **Giocatori 2026**: miglior media Johannes con 0,28 punti/giorno. Tipp (tutti i giocatori e anni) su piatti serviti negli ultimi 5 giorni lavorativi: primo centrato nel 2,9 % (n=68) contro 8,8 % per gli altri tipp; il momento migliore per tippare un primo è 21–40 giorni lavorativi dopo l'ultima volta (10,9 %).

## Kernaussagen

- **Keine Wiederholung in derselben Woche**: Vorspeise nie zweimal in derselben Kalenderwoche (0 Paare, Zufall 38,1, p < 0,001), Hauptspeise nie zweimal in derselben Kalenderwoche (0 Paare, Zufall 37,8, p < 0,001). Beilage dagegen 17 Paare (Zufall 99,5), v. a. Reis.
- **Mindestabstand**: Vorspeise frühestens wieder nach 3 Arbeitstagen, Hauptspeise nach 2; innerhalb von 5 bzw. 3 AT praktisch nie (< 25 % der Zufallsrate). Median-Abstand 17,0 (V), 19,0 (H), 8,0 (B) Arbeitstage.
- **Wochenrhythmus**: Bei Abständen von 10, 15, … 30 AT (gleicher Wochentag) ist dieselbe Speise nur bei H signifikant häufiger als bei anderen Abständen – V 4,9 % vs 4,1 % (p = 0,059), H 5,4 % vs 3,9 % (p < 0,001). Spitze Vorspeise L=30: 6,9 % vs 4,5 % (p = 0,025). Spitze Hauptspeise L=20: 7,9 % vs 4,3 % (p = 0,001).
- **Wochentag**: Reis (Beilage) am Montag 42/100 (42 %, erwartet 19 %, Lift 2,2, p < 0,001, Bonferroni-signifikant).
- **Wochentag**: Schweinskotelett (Hauptspeise) am Mittwoch 13/17 (76 %, erwartet 21 %, Lift 3,7, p < 0,001, Bonferroni-signifikant).
- **Wochentag**: Arrabbiata (Vorspeise) am Montag 17/30 (57 %, erwartet 19 %, Lift 2,9, p < 0,001, Bonferroni-signifikant).
- **Wochentag**: Champignonschnitzel (Hauptspeise) am Montag 16/29 (55 %, erwartet 19 %, Lift 2,8, p < 0,001, Bonferroni-signifikant).
- **Hypothese Fisch (alle Fischgerichte)**: häufigster Tag Freitag 11/13 (Mo–Fr: 0/0/2/0/11, p < 0,001) → bestätigt.
- **Hypothese Fisch außerhalb Fastenzeit**: häufigster Tag Freitag 3/3 (Mo–Fr: 0/0/0/0/3, p = 0,007) → bestätigt.
- **Hypothese Scombri**: häufigster Tag Freitag 2/3 (Mo–Fr: 0/0/1/0/2, p = 0,096) → nicht bestätigt.
- **Hypothese Plent**: häufigster Tag Freitag 10/20 (Mo–Fr: 0/0/5/5/10, p = 0,002) → bestätigt.
- **Hypothese Leberkas**: häufigster Tag Mittwoch 6/20 (Mo–Fr: 3/2/6/5/4, p = 0,214) → nicht bestätigt.
- **Hypothese Hauswurst**: häufigster Tag Freitag 7/15 (Mo–Fr: 0/0/4/4/7, p = 0,014) → Tendenz.
- **Beilage hängt an der Hauptspeise**: mit bekannter Hauptspeise trifft die typische Beilage in 49 % der Fälle (Leave-one-out), ohne nur 23 % (Reis); Entropie 3,51 → 1,44 bit. Feste Paare: Champignonschnitzel → Reis 76 % (22), Wienerschnitzel → Kartoffelsalat 83 % (19), Leberkas → Röstkartoffeln 60 % (12), Chilli con carne → Reis 100 % (17), Hühnerhaxlen → Pommes 71 % (12), Hauswurst → Plent 100 % (14), Cordon Bleu → Kartoffelsalat 100 % (12), Currywurst → Pommes 100 % (7), Sparerips → Pommes 71 % (5), Gekochtes Rindfleisch → Salzkartoffeln 100 % (6), Hackbraten → Püree 60 % (3), Pizzaiolaschnitzel → Ofenkartoffeln 60 % (3).
- **Vorspeise ↔ Hauptspeise**: kaum Zusammenhang (MI 1,693 vs Zufall 1,651 bit, p = 0,116); einzelne Paare mit hohem Lift entstehen v. a. über den gemeinsamen Wochentag.
- **Fisch & Fastenzeit**: Fisch an 16 % der Fastentage (10) vs 1 % sonst (3; p < 0,001). Sommer/Winter: keine signifikanten Unterschiede.
- Aktualitätsgewichtung: beste Halbwertszeit (Log-Loss, Tage) – Vorspeise 365, Hauptspeise 180, Beilage 180.
- **Tipp-Timing (alle Spieler)**: Tipps auf Gerichte, die vor 1–5 AT serviert wurden, treffen bei V nur 2,9 % (sonst 8,8 %), bei H 4,0 % (sonst 8,3 %). Beste Abstandsklasse: Vorspeise 21–40 AT (10,9 %, n=285), Hauptspeise 11–20 AT (9,5 %, n=514), Beilage 3–5 AT (27,5 %, n=437).
- **Spieler 2026**: beste Quote Johannes mit 0,276 Punkten/Tag; alle Spieler liegen eng beieinander: Johannes 0,276 (165 T.), Andreas 0,260 (171 T.), Johannes Paul III 0,250 (166 T.), Noah 0,238 (174 T.).

## 1. Häufigkeiten

Gezählt wird die erste angesagte Option (bei „A / B“ zählt A). „zuletzt“ berücksichtigt alle Optionen.

| Kategorie | verschiedene Gerichte | 2024 | 2025 | 2026 | Top-5-Anteil | Entropie (bit) |
|---|---|---|---|---|---|---|
| Vorspeise | 60 | 24 | 44 | 36 | 32 % | 4,95 |
| Hauptspeise | 48 | 20 | 35 | 41 | 31 % | 4,91 |
| Beilage | 19 | 13 | 14 | 17 | 64 % | 3,51 |

### Vorspeise – Top 20

| # | Gericht | gesamt | Anteil | 2024 | 2025 | 2026 | zuletzt |
|---|---|---|---|---|---|---|---|
| 1 | Arrabbiata | 30 | 6,8 % | 2 | 16 | 12 | 2026-10-05 |
| 2 | Nudel mit Käsesoße | 30 | 6,8 % | 1 | 15 | 14 | 2026-10-22 |
| 3 | Hirten | 28 | 6,3 % | 2 | 13 | 13 | 2026-09-30 |
| 4 | Aglio olio | 27 | 6,1 % | 1 | 15 | 11 | 2026-10-26 |
| 5 | Nudel mit Ragu | 26 | 5,9 % | 3 | 14 | 9 | 2026-10-15 |
| 6 | Nudel mit Thunfischsoße | 25 | 5,7 % | 2 | 14 | 9 | 2026-10-01 |
| 7 | Schlutzer | 24 | 5,4 % | 1 | 12 | 11 | 2026-10-20 |
| 8 | Nudel Mammarosa | 22 | 5,0 % | 2 | 11 | 9 | 2026-10-19 |
| 9 | Lasagne | 21 | 4,8 % | 2 | 9 | 10 | 2026-10-21 |
| 10 | Amatriciana | 19 | 4,3 % | 1 | 10 | 8 | 2026-10-12 |
| 11 | Tortellini mit Schinken-Rahm | 19 | 4,3 % | 0 | 8 | 11 | 2026-10-23 |
| 12 | Nudel mit Pesto | 16 | 3,6 % | 1 | 7 | 8 | 2026-09-10 |
| 13 | Spinatspatzlen | 16 | 3,6 % | 1 | 10 | 5 | 2026-09-29 |
| 14 | Gnocchi mit Tomatensoße | 15 | 3,4 % | 0 | 6 | 9 | 2026-10-27 |
| 15 | Käseknödel | 11 | 2,5 % | 2 | 4 | 5 | 2026-09-24 |
| 16 | Pizzastrudel | 11 | 2,5 % | 1 | 5 | 5 | 2026-10-07 |
| 17 | Carbonara | 10 | 2,3 % | 1 | 4 | 5 | 2026-09-18 |
| 18 | Spinatcannelloni | 10 | 2,3 % | 1 | 4 | 5 | 2026-09-16 |
| 19 | Nudel mit Lachs | 9 | 2,0 % | 0 | 5 | 4 | 2026-10-16 |
| 20 | Nudel mit Salsiccia-Ragu | 5 | 1,1 % | 0 | 2 | 3 | 2026-09-03 |

**Selten (n ≤ 2, 32 Gerichte):** Gnocchi mit Gorgonzolasoße, Gnocchi mit Käsesoße, Omelett mit Schinken und Käse, Plentauflauf, Ravioli, Spinatknödel mit Käsesoße, Spinatravioli, Gemüselasagne, Gerstsuppe, Gnocchi, Gnocchi mit Kräutersauce, Gnocchi mit Lachs, Gnocchi mit Ragu, Gulaschsuppe, Käse-Sofficini mit Tomantensoße, Kürbisrisotto, Nudel mit Lachs und Tomantensoße, Nudel mit Schinken-Rahm, Nudel mit Tomatensoße, Nudel mit Tomatensoße und Schinken, Pilzrisotto, Putanesca, Ravioli mit Käsesoße, Ravioli mit Tomantensoße, Schlutzer Schinken-Rahm, Schupfnudel mit Lachs, Schüttelbrot-Risotto mit Speckstreifen, Spargelrisotto, Speck-Zwiebel-Kuchen, Spinatknödel, Spinatknödel mit Gorgonzolasoße, Tomatenrisotto

**Nur als Alternative angesagt:** Fleischsuppe, Nudelsalat, Reissalat

### Hauptspeise – Top 20

| # | Gericht | gesamt | Anteil | 2024 | 2025 | 2026 | zuletzt |
|---|---|---|---|---|---|---|---|
| 1 | Hühnerbrust | 32 | 7,2 % | 2 | 16 | 14 | 2026-10-12 |
| 2 | Champignonschnitzel | 29 | 6,6 % | 2 | 16 | 11 | 2026-10-26 |
| 3 | Truthahngeschnetzeltes | 26 | 5,9 % | 2 | 13 | 11 | 2026-10-07 |
| 4 | Truthahnschnitzel | 26 | 5,9 % | 2 | 16 | 8 | 2026-09-14 |
| 5 | Schweinsschopf | 24 | 5,4 % | 3 | 11 | 10 | 2026-10-14 |
| 6 | Truthahnbraten | 24 | 5,4 % | 4 | 11 | 9 | 2026-10-19 |
| 7 | Wienerschnitzel | 23 | 5,2 % | 1 | 12 | 10 | 2026-10-21 |
| 8 | Schweinsfilet | 21 | 4,7 % | 2 | 12 | 7 | 2026-10-20 |
| 9 | Schweinsschnitzel | 21 | 4,7 % | 1 | 13 | 7 | 2026-08-24 |
| 10 | Leberkas | 20 | 4,5 % | 2 | 10 | 8 | 2026-10-27 |
| 11 | Chilli con carne | 17 | 3,8 % | 0 | 10 | 7 | 2026-09-29 |
| 12 | Hühnerhaxlen | 17 | 3,8 % | 2 | 7 | 8 | 2026-10-02 |
| 13 | Schweinskotelett | 17 | 3,8 % | 2 | 12 | 3 | 2026-06-10 |
| 14 | Hauswurst | 14 | 3,2 % | 1 | 7 | 6 | 2026-10-16 |
| 15 | Cordon Bleu | 12 | 2,7 % | 0 | 5 | 7 | 2026-10-06 |
| 16 | Zwiebelrostbraten | 12 | 2,7 % | 1 | 5 | 6 | 2026-09-22 |
| 17 | Schweinsgulasch | 11 | 2,5 % | 0 | 5 | 6 | 2026-10-09 |
| 18 | Zigeunerschnitzel | 10 | 2,3 % | 0 | 5 | 5 | 2026-08-03 |
| 19 | Currywurst | 7 | 1,6 % | 0 | 3 | 4 | 2026-08-26 |
| 20 | Ossobuchi | 7 | 1,6 % | 1 | 2 | 4 | 2026-10-15 |

**Selten (n ≤ 2, 16 Gerichte):** Forelle, Frittiertes Pangasiusfilet, Hamburger, Kalbsgulasch, Rotbarschfilet, Schweinsfilet mit Pfeffersoße, 1/2 Brathuhn, Frittiertes Schollenfilet, Hirschgulasch, Lammbraten, Pangasiusfilet, Pangasiusfilet mit Kräuterrahmsoße, Panierter Pangasius, Paprika-Schweinegulasch, Saures Rindfleisch, Spiegelei

**Nur als Alternative angesagt:** Fleischkrapfln

### Beilage – Top 20

| # | Gericht | gesamt | Anteil | 2024 | 2025 | 2026 | zuletzt |
|---|---|---|---|---|---|---|---|
| 1 | Reis | 100 | 22,6 % | 7 | 54 | 39 | 2026-10-26 |
| 2 | Pommes | 58 | 13,1 % | 3 | 28 | 27 | 2026-10-27 |
| 3 | Spatzlen | 45 | 10,2 % | 6 | 18 | 21 | 2026-10-15 |
| 4 | Püree | 44 | 9,9 % | 2 | 22 | 20 | 2026-10-20 |
| 5 | Ofenkartoffeln | 38 | 8,6 % | 4 | 23 | 11 | 2026-10-02 |
| 6 | Kartoffelsalat | 35 | 7,9 % | 1 | 15 | 19 | 2026-10-21 |
| 7 | Kroketten | 25 | 5,6 % | 2 | 14 | 9 | 2026-10-09 |
| 8 | Kartoffelgratin | 23 | 5,2 % | 1 | 16 | 6 | 2026-06-10 |
| 9 | Plent | 20 | 4,5 % | 1 | 12 | 7 | 2026-10-16 |
| 10 | Röstkartoffeln | 14 | 3,2 % | 2 | 7 | 5 | 2026-06-25 |
| 11 | Salzkartoffeln | 11 | 2,5 % | 1 | 5 | 5 | 2026-09-04 |
| 12 | Kartoffelstampf | 9 | 2,0 % | 2 | 3 | 4 | 2026-09-30 |
| 13 | Wedges | 7 | 1,6 % | 0 | 0 | 7 | 2026-10-14 |
| 14 | Bratkartoffeln | 6 | 1,4 % | 0 | 1 | 5 | 2026-08-06 |
| 15 | Gulasch | 3 | 0,7 % | 0 | 3 | 0 | 2025-12-16 |
| 16 | Röstinchen | 2 | 0,4 % | 0 | 0 | 2 | 2026-09-25 |
| 17 | Kartoffel-Käse-Kroketten | 1 | 0,2 % | 0 | 0 | 1 | 2026-02-11 |
| 18 | Knödel | 1 | 0,2 % | 0 | 0 | 1 | 2026-10-22 |
| 19 | Safranreis | 1 | 0,2 % | 1 | 0 | 0 | 2024-11-22 |

**Selten (n ≤ 2, 4 Gerichte):** Röstinchen, Kartoffel-Käse-Kroketten, Knödel, Safranreis

**Nur als Alternative angesagt:** Kraut, Peperonata, Zucchini

## 2. Wiederholungen und Refraktärzeit

Abstände in **Arbeitstagen** (Position im Spielkalender; freie Tage und Saisonpausen zählen nicht). Abstände über eine Saisongrenze hinweg werden ignoriert. „Zufall“ = Erwartung, wenn die Küche jeden Tag unabhängig nach den Jahreshäufigkeiten wählen würde.

| Kategorie | kleinster Abstand | Median | ≤ 2 AT | ≤ 5 AT | ≤ 10 AT | ≤ 20 AT | gleiche Woche (Paare) | Zufall | p (weniger als Zufall) | keine Wdh. innerhalb |
|---|---|---|---|---|---|---|---|---|---|---|
| Vorspeise | 3 | 17,0 | 0 % | 2 % | 16 % | 60 % | 0 | 38,1 | < 0,001 | 5 AT |
| Hauptspeise | 2 | 19,0 | 1 % | 4 % | 19 % | 58 % | 0 | 37,8 | < 0,001 | 3 AT |
| Beilage | 1 | 8,0 | 6 % | 31 % | 64 % | 87 % | 17 | 99,5 | < 0,001 | 1 AT |

- **Vorspeise**: Die Küche **vermeidet** Wiederholungen innerhalb von 5 Arbeitstagen (6 gleiche Paare, Zufall 95,7); innerhalb von 10 Arbeitstagen 55 vs 188,2. Erste Wiederholung frühestens nach 3 AT.
- **Hauptspeise**: Die Küche **vermeidet** Wiederholungen innerhalb von 5 Arbeitstagen (15 gleiche Paare, Zufall 94,7); innerhalb von 10 Arbeitstagen 70 vs 185,8. Erste Wiederholung frühestens nach 2 AT.
- **Beilage**: Die Küche wiederholt **seltener** als Zufall innerhalb von 5 Arbeitstagen (136 gleiche Paare, Zufall 249,8); innerhalb von 10 Arbeitstagen 366 vs 490,9. Erste Wiederholung frühestens nach 1 AT.

### Refraktärkurve P(gleiches Gericht im Abstand L)

Basis = Σ p² (globale Anteile, wie in `stats.json`); Saison-Basis = Erwartung für zwei Tage derselben Saison.

| L (AT) | Vorspeise | Hauptspeise | Beilage |
|---|---|---|---|
| 1 | 0,0 % (0/433) | 0,0 % (0/436) | 2,1 % (9/436) |
| 2 | 0,0 % (0/430) | 0,5 % (2/433) | 3,7 % (16/433) |
| 3 | 0,2 % (1/427) | 0,7 % (3/430) | 7,2 % (31/430) |
| 4 | 0,5 % (2/424) | 1,2 % (5/427) | 8,7 % (37/427) |
| 5 | 0,7 % (3/422) | 1,2 % (5/424) | 10,1 % (43/424) |
| 6 | 1,4 % (6/419) | 1,7 % (7/421) | 9,3 % (39/421) |
| 7 | 2,4 % (10/416) | 1,2 % (5/418) | 12,4 % (52/418) |
| 8 | 1,9 % (8/413) | 2,4 % (10/415) | 10,1 % (42/415) |
| 9 | 3,4 % (14/410) | 2,7 % (11/412) | 11,2 % (46/412) |
| 10 | 2,7 % (11/407) | 5,4 % (22/409) | 12,5 % (51/409) |
| 11 | 2,7 % (11/406) | 2,7 % (11/408) | 10,8 % (44/408) |
| 12 | 6,2 % (25/402) | 4,2 % (17/404) | 9,4 % (38/404) |
| 13 | 6,0 % (24/399) | 3,7 % (15/401) | 8,5 % (34/401) |
| 14 | 5,1 % (20/396) | 4,5 % (18/398) | 12,3 % (49/398) |
| 15 | 4,1 % (16/393) | 5,8 % (23/395) | 13,2 % (52/395) |
| 16 | 3,8 % (15/390) | 2,6 % (10/392) | 11,5 % (45/392) |
| 17 | 3,6 % (14/387) | 2,8 % (11/389) | 13,4 % (52/389) |
| 18 | 4,7 % (18/384) | 4,9 % (19/386) | 8,8 % (34/386) |
| 19 | 2,6 % (10/381) | 4,4 % (17/383) | 10,4 % (40/383) |
| 20 | 5,6 % (21/378) | 7,9 % (30/380) | 12,1 % (46/380) |
| 21 | 2,4 % (9/375) | 3,4 % (13/377) | 14,3 % (54/377) |
| 22 | 3,5 % (13/372) | 4,8 % (18/374) | 12,3 % (46/374) |
| 23 | 3,3 % (12/369) | 3,5 % (13/371) | 12,1 % (45/371) |
| 24 | 2,5 % (9/366) | 4,9 % (18/368) | 11,1 % (41/368) |
| 25 | 5,5 % (20/363) | 4,1 % (15/365) | 13,2 % (48/365) |
| 26 | 4,4 % (16/360) | 3,3 % (12/362) | 9,9 % (36/362) |
| 27 | 3,6 % (13/357) | 2,8 % (10/359) | 12,0 % (43/359) |
| 28 | 6,2 % (22/354) | 4,5 % (16/356) | 10,1 % (36/356) |
| 29 | 5,1 % (18/351) | 5,9 % (21/353) | 12,5 % (44/353) |
| 30 | 6,9 % (24/349) | 3,7 % (13/350) | 14,3 % (50/350) |
| Basis Σp² | 4,2 % | 4,1 % | 11,2 % |
| Saison-Basis | 4,5 % | 4,3 % | 11,6 % |

**Auffällige Spitzen (Rate > 1,3 × Saison-Basis, p < 0,05; L=5 ≈ 1 Woche, L=20 ≈ 4 Wochen):**

- Vorspeise: L=30 → 6,9 % vs 4,5 % (24/349, p = 0,025)
- Hauptspeise: L=20 → 7,9 % vs 4,3 % (30/380, p = 0,001)

**Wochenrhythmus** – gleiche Speise bei Abständen L = 10, 15, 20, 25, 30 AT (meist gleicher Wochentag) vs. allen anderen Abständen 10–30 AT:

| Kategorie | L = 5·k | andere L | p |
|---|---|---|---|
| Vorspeise | 4,9 % (92/1890) | 4,1 % (249/6049) | 0,059 |
| Hauptspeise | 5,4 % (103/1899) | 3,9 % (239/6081) | < 0,001 |
| Beilage | 13,0 % (247/1899) | 11,2 % (681/6081) | 0,008 |

→ Der Wochentag-Effekt (Abschnitt 3) erzeugt einen schwachen Wochenrhythmus; die Refraktärzeit dominiert aber die ersten 1–2 Wochen.

### Abstände je Gericht – Vorspeise (n ≥ 8)

| Gericht | n | Mittel | Median | min | max | Wdh. gleiche Woche |
|---|---|---|---|---|---|---|
| Arrabbiata | 30 | 14,6 | 13,0 | 7 | 25 | 0 |
| Nudel mit Käsesoße | 30 | 14,8 | 14,0 | 5 | 30 | 0 |
| Hirten | 28 | 14,6 | 13,0 | 4 | 45 | 0 |
| Aglio olio | 27 | 16,8 | 14,0 | 6 | 41 | 0 |
| Nudel mit Ragu | 26 | 17,4 | 18,0 | 5 | 48 | 0 |
| Nudel mit Thunfischsoße | 25 | 16,7 | 13,5 | 6 | 41 | 0 |
| Schlutzer | 24 | 17,8 | 14,0 | 3 | 41 | 0 |
| Nudel Mammarosa | 22 | 20,2 | 19,0 | 4 | 45 | 0 |
| Lasagne | 21 | 20,1 | 17,5 | 9 | 48 | 0 |
| Amatriciana | 19 | 21,7 | 20,0 | 12 | 51 | 0 |
| Tortellini mit Schinken-Rahm | 19 | 18,8 | 16,0 | 7 | 30 | 0 |
| Nudel mit Pesto | 16 | 22,8 | 20,0 | 6 | 49 | 0 |
| Spinatspatzlen | 16 | 27,7 | 25,0 | 8 | 71 | 0 |
| Gnocchi mit Tomatensoße | 15 | 25,5 | 19,0 | 7 | 78 | 0 |
| Käseknödel | 11 | 44,8 | 22,0 | 11 | 146 | 0 |
| Pizzastrudel | 11 | 41,1 | 41,5 | 30 | 61 | 0 |
| Carbonara | 10 | 33,9 | 33,0 | 18 | 63 | 0 |
| Spinatcannelloni | 10 | 44,3 | 48,0 | 23 | 67 | 0 |
| Nudel mit Lachs | 9 | 42,3 | 58,0 | 9 | 63 | 0 |

### Abstände je Gericht – Hauptspeise (n ≥ 8)

| Gericht | n | Mittel | Median | min | max | Wdh. gleiche Woche |
|---|---|---|---|---|---|---|
| Hühnerbrust | 32 | 13,4 | 12,0 | 4 | 31 | 0 |
| Champignonschnitzel | 29 | 14,7 | 13,5 | 3 | 34 | 0 |
| Truthahngeschnetzeltes | 26 | 17,0 | 16,0 | 8 | 34 | 0 |
| Truthahnschnitzel | 26 | 17,0 | 13,0 | 2 | 85 | 0 |
| Schweinsschopf | 24 | 19,1 | 15,0 | 4 | 73 | 0 |
| Truthahnbraten | 24 | 17,1 | 12,0 | 4 | 66 | 0 |
| Wienerschnitzel | 23 | 18,2 | 16,0 | 7 | 41 | 0 |
| Schweinsfilet | 21 | 19,0 | 16,0 | 4 | 44 | 0 |
| Schweinsschnitzel | 21 | 17,9 | 14,0 | 2 | 59 | 0 |
| Leberkas | 20 | 24,0 | 22,0 | 13 | 61 | 0 |
| Chilli con carne | 17 | 24,0 | 21,0 | 12 | 44 | 0 |
| Hühnerhaxlen | 17 | 28,0 | 24,5 | 7 | 76 | 0 |
| Schweinskotelett | 17 | 18,7 | 17,5 | 9 | 60 | 0 |
| Hauswurst | 14 | 34,6 | 27,0 | 17 | 87 | 0 |
| Cordon Bleu | 12 | 30,3 | 23,5 | 15 | 62 | 0 |
| Zwiebelrostbraten | 12 | 34,8 | 35,0 | 6 | 61 | 0 |
| Schweinsgulasch | 11 | 40,1 | 31,0 | 17 | 78 | 0 |
| Zigeunerschnitzel | 10 | 41,0 | 32,0 | 14 | 92 | 0 |

### Abstände je Gericht – Beilage

| Gericht | n | Mittel | Median | min | max | Wdh. gleiche Woche |
|---|---|---|---|---|---|---|
| Reis | 100 | 4,5 | 4,0 | 1 | 11 | 13 |
| Pommes | 58 | 7,7 | 6,0 | 1 | 25 | 3 |
| Spatzlen | 45 | 9,9 | 8,0 | 3 | 26 | 0 |
| Püree | 44 | 9,7 | 9,0 | 3 | 20 | 0 |
| Ofenkartoffeln | 38 | 10,9 | 9,0 | 2 | 45 | 1 |
| Kartoffelsalat | 35 | 11,8 | 10,0 | 4 | 32 | 0 |
| Kroketten | 25 | 16,5 | 13,0 | 7 | 31 | 0 |
| Kartoffelgratin | 23 | 13,2 | 11,5 | 3 | 40 | 0 |
| Plent | 20 | 22,4 | 21,0 | 4 | 60 | 0 |
| Röstkartoffeln | 14 | 25,3 | 23,0 | 2 | 47 | 0 |
| Salzkartoffeln | 11 | 42,6 | 22,0 | 5 | 151 | 0 |
| Kartoffelstampf | 9 | 61,5 | 47,0 | 10 | 134 | 0 |
| Wedges | 7 | 28,5 | 25,5 | 7 | 65 | 0 |
| Bratkartoffeln | 6 | 27,0 | 21,5 | 5 | 60 | 0 |

## 3. Wochentage

Servierte Tage je Wochentag (Hauptspeise): Mo 86, Di 90, Mi 91, Do 91, Fr 85. Getestet wurden 305 Kombinationen (Gericht mit n ≥ 5 × Wochentag) mit einem einseitigen Binomialtest; bei so vielen Tests sind einzelne p < 0,05 auch zufällig zu erwarten (Bonferroni-Schwelle ≈ 0,0002).

### Gezielte Hypothesen

| Merkmal | n Tage | Mo | Di | Mi | Do | Fr | häufigster Tag | Anteil (erwartet) | p |
|---|---|---|---|---|---|---|---|---|---|
| Fisch (alle Fischgerichte) | 13 | 0 | 0 | 2 | 0 | 11 | Fr | 85 % (19 %) | < 0,001 |
| Fisch außerhalb Fastenzeit | 3 | 0 | 0 | 0 | 0 | 3 | Fr | 100 % (19 %) | 0,007 |
| Scombri | 3 | 0 | 0 | 1 | 0 | 2 | Fr | 67 % (19 %) | 0,096 |
| Plent | 20 | 0 | 0 | 5 | 5 | 10 | Fr | 50 % (19 %) | 0,002 |
| Leberkas | 20 | 3 | 2 | 6 | 5 | 4 | Mi | 30 % (21 %) | 0,214 |
| Hauswurst | 15 | 0 | 0 | 4 | 4 | 7 | Fr | 47 % (19 %) | 0,014 |

### Auffällige Wochentag-Vorlieben (Lift ≥ 1,5, mind. 3×, p < 0,05)

| Kategorie | Gericht | Tag | an diesem Tag | Anteil | erwartet | Lift | p | Bonferroni |
|---|---|---|---|---|---|---|---|---|
| Beilage | Reis | Mo | 42/100 | 42 % | 19 % | 2,16 | < 0,001 | ✔ |
| Hauptspeise | Schweinskotelett | Mi | 13/17 | 76 % | 21 % | 3,72 | < 0,001 | ✔ |
| Vorspeise | Arrabbiata | Mo | 17/30 | 57 % | 19 % | 2,91 | < 0,001 | ✔ |
| Hauptspeise | Champignonschnitzel | Mo | 16/29 | 55 % | 19 % | 2,84 | < 0,001 | ✔ |
| Vorspeise | Amatriciana | Mo | 11/19 | 58 % | 19 % | 2,98 | < 0,001 |  |
| Vorspeise | Spinatspatzlen | Di | 10/16 | 62 % | 20 % | 3,07 | < 0,001 |  |
| Hauptspeise | Schweinsschnitzel | Mo | 11/21 | 52 % | 19 % | 2,70 | < 0,001 |  |
| Hauptspeise | Truthahnbraten | Di | 12/24 | 50 % | 20 % | 2,46 | 0,001 |  |
| Beilage | Salzkartoffeln | Fr | 7/11 | 64 % | 19 % | 3,32 | 0,002 |  |
| Beilage | Plent | Fr | 10/20 | 50 % | 19 % | 2,61 | 0,002 |  |
| Vorspeise | Nudel mit Lachs | Fr | 6/9 | 67 % | 19 % | 3,43 | 0,003 |  |
| Vorspeise | Lasagne | Di | 10/21 | 48 % | 20 % | 2,34 | 0,005 |  |
| Vorspeise | Nudel Mammarosa | Mo | 10/22 | 45 % | 19 % | 2,34 | 0,005 |  |
| Hauptspeise | Ossobuchi | Do | 5/7 | 71 % | 21 % | 3,48 | 0,005 |  |
| Beilage | Wedges | Mi | 5/7 | 71 % | 21 % | 3,48 | 0,005 |  |
| Beilage | Spatzlen | Do | 17/45 | 38 % | 21 % | 1,84 | 0,006 |  |
| Hauptspeise | Schweinsschnitzel mit Kräuterrahmsoße | Mo | 4/5 | 80 % | 19 % | 4,12 | 0,006 |  |
| Hauptspeise | Hühnerbrust | Di | 13/32 | 41 % | 20 % | 2,00 | 0,007 |  |
| Vorspeise | Tortellini mit Schinken-Rahm | Di | 9/19 | 47 % | 20 % | 2,33 | 0,008 |  |
| Hauptspeise | Truthahngeschnetzeltes | Di | 11/26 | 42 % | 20 % | 2,08 | 0,009 |  |
| Beilage | Püree | Di | 16/44 | 36 % | 20 % | 1,79 | 0,010 |  |
| Hauptspeise | Cordon Bleu | Mi | 6/12 | 50 % | 21 % | 2,43 | 0,022 |  |
| Beilage | Ofenkartoffeln | Mo | 13/38 | 34 % | 19 % | 1,76 | 0,023 |  |
| Vorspeise | Nudel mit Ragu | Do | 10/26 | 38 % | 20 % | 1,91 | 0,024 |  |
| Hauptspeise | Sparerips | Fr | 4/7 | 57 % | 19 % | 2,98 | 0,029 |  |

### Gerichte, die an einem Wochentag (fast) nie kommen (n ≥ 10, p < 0,05)

| Kategorie | Gericht | Tag | an diesem Tag | erwartet | p |
|---|---|---|---|---|---|
| Beilage | Plent | Di | 0/20 | 4,1 | 0,011 |
| Hauptspeise | Champignonschnitzel | Mi | 1/29 | 6,0 | 0,011 |
| Vorspeise | Amatriciana | Mi | 0/19 | 3,9 | 0,013 |
| Beilage | Plent | Mo | 0/20 | 3,9 | 0,013 |
| Hauptspeise | Champignonschnitzel | Fr | 1/29 | 5,6 | 0,016 |
| Vorspeise | Tortellini mit Schinken-Rahm | Mo | 0/19 | 3,7 | 0,016 |
| Hauptspeise | Schweinskotelett | Di | 0/17 | 3,5 | 0,021 |
| Hauptspeise | Schweinskotelett | Mo | 0/17 | 3,3 | 0,025 |
| Hauptspeise | Schweinskotelett | Fr | 0/17 | 3,3 | 0,027 |
| Vorspeise | Spinatspatzlen | Mo | 0/16 | 3,1 | 0,031 |
| Vorspeise | Nudel mit Pesto | Mo | 0/16 | 3,1 | 0,031 |
| Beilage | Kroketten | Mo | 1/25 | 4,9 | 0,032 |
| Vorspeise | Arrabbiata | Mi | 2/30 | 6,2 | 0,038 |
| Hauptspeise | Truthahnbraten | Fr | 1/24 | 4,6 | 0,040 |
| Hauptspeise | Hauswurst | Di | 0/14 | 2,8 | 0,042 |

### Vorspeise: Anzahl je Wochentag (Top 12)

| Gericht | Mo | Di | Mi | Do | Fr | max. Lift |
|---|---|---|---|---|---|---|
| Arrabbiata | 17 | 4 | 2 | 5 | 2 | 2,91 |
| Nudel mit Käsesoße | 8 | 3 | 9 | 2 | 8 | 1,46 |
| Hirten | 6 | 7 | 9 | 4 | 2 | 1,56 |
| Aglio olio | 6 | 3 | 5 | 7 | 6 | 1,29 |
| Nudel mit Ragu | 5 | 4 | 4 | 10 | 3 | 1,91 |
| Nudel mit Thunfischsoße | 7 | 3 | 5 | 4 | 6 | 1,44 |
| Schlutzer | 3 | 7 | 6 | 5 | 3 | 1,43 |
| Nudel Mammarosa | 10 | 2 | 2 | 7 | 1 | 2,34 |
| Lasagne | 1 | 10 | 2 | 7 | 1 | 2,34 |
| Amatriciana | 11 | 1 | 0 | 6 | 1 | 2,98 |
| Tortellini mit Schinken-Rahm | 0 | 9 | 1 | 3 | 6 | 2,33 |
| Nudel mit Pesto | 0 | 3 | 6 | 3 | 4 | 1,82 |

### Hauptspeise: Anzahl je Wochentag (Top 12)

| Gericht | Mo | Di | Mi | Do | Fr | max. Lift |
|---|---|---|---|---|---|---|
| Hühnerbrust | 3 | 13 | 4 | 9 | 3 | 2,00 |
| Champignonschnitzel | 16 | 8 | 1 | 3 | 1 | 2,84 |
| Truthahngeschnetzeltes | 4 | 11 | 4 | 5 | 2 | 2,08 |
| Truthahnschnitzel | 8 | 3 | 2 | 6 | 7 | 1,58 |
| Schweinsschopf | 4 | 5 | 9 | 3 | 3 | 1,83 |
| Truthahnbraten | 5 | 12 | 3 | 3 | 1 | 2,46 |
| Wienerschnitzel | 5 | 2 | 7 | 7 | 2 | 1,48 |
| Schweinsfilet | 5 | 2 | 2 | 6 | 6 | 1,49 |
| Schweinsschnitzel | 11 | 4 | 2 | 1 | 3 | 2,70 |
| Leberkas | 3 | 2 | 6 | 5 | 4 | 1,46 |
| Chilli con carne | 2 | 3 | 5 | 4 | 3 | 1,43 |
| Hühnerhaxlen | 1 | 5 | 2 | 5 | 4 | 1,45 |

### Beilage: Anzahl je Wochentag (Top 12)

| Gericht | Mo | Di | Mi | Do | Fr | max. Lift |
|---|---|---|---|---|---|---|
| Reis | 42 | 21 | 14 | 10 | 13 | 2,16 |
| Pommes | 7 | 14 | 13 | 11 | 13 | 1,19 |
| Spatzlen | 7 | 7 | 8 | 17 | 6 | 1,84 |
| Püree | 4 | 16 | 12 | 8 | 4 | 1,79 |
| Ofenkartoffeln | 13 | 8 | 4 | 8 | 5 | 1,76 |
| Kartoffelsalat | 5 | 3 | 12 | 8 | 7 | 1,67 |
| Kroketten | 1 | 7 | 3 | 5 | 9 | 1,88 |
| Kartoffelgratin | 2 | 5 | 6 | 8 | 2 | 1,69 |
| Plent | 0 | 0 | 5 | 5 | 10 | 2,61 |
| Röstkartoffeln | 2 | 0 | 3 | 5 | 4 | 1,74 |
| Salzkartoffeln | 0 | 1 | 0 | 3 | 7 | 3,32 |
| Kartoffelstampf | 2 | 4 | 3 | 0 | 0 | 2,19 |

## 4. Kombinationen

### Beilage | Hauptspeise (Hauptspeisen mit n ≥ 3)

Wer die Hauptspeise kennt (bzw. richtig schätzt), sollte die dazu typische Beilage tippen: Treffer 49 % (Leave-one-out) statt 23 % mit der global häufigsten Beilage (Reis).

| Hauptspeise | n | Beilage 1 | Beilage 2 | Beilage 3 |
|---|---|---|---|---|
| Hühnerbrust | 32 | Kroketten 34 % (11) | Spatzlen 22 % (7) | Kartoffelgratin 12 % (4) |
| Champignonschnitzel | 29 | Reis 76 % (22) | Kartoffelgratin 17 % (5) | Püree 3 % (1) |
| Truthahngeschnetzeltes | 26 | Püree 42 % (11) | Reis 35 % (9) | Spatzlen 19 % (5) |
| Truthahnschnitzel | 26 | Ofenkartoffeln 42 % (11) | Pommes 38 % (10) | Kroketten 8 % (2) |
| Schweinsschopf | 24 | Pommes 25 % (6) | Reis 17 % (4) | Kartoffelgratin 12 % (3) |
| Truthahnbraten | 24 | Püree 29 % (7) | Reis 21 % (5) | Spatzlen 21 % (5) |
| Wienerschnitzel | 23 | Kartoffelsalat 83 % (19) | Pommes 17 % (4) |  |
| Schweinsfilet | 21 | Kroketten 29 % (6) | Spatzlen 29 % (6) | Reis 24 % (5) |
| Schweinsschnitzel | 21 | Ofenkartoffeln 38 % (8) | Reis 24 % (5) | Pommes 10 % (2) |
| Leberkas | 20 | Röstkartoffeln 60 % (12) | Pommes 40 % (8) |  |
| Chilli con carne | 17 | Reis 100 % (17) |  |  |
| Hühnerhaxlen | 17 | Pommes 71 % (12) | Ofenkartoffeln 24 % (4) | Wedges 6 % (1) |
| Schweinskotelett | 17 | Kartoffelgratin 35 % (6) | Spatzlen 24 % (4) | Ofenkartoffeln 18 % (3) |
| Hauswurst | 14 | Plent 100 % (14) |  |  |
| Cordon Bleu | 12 | Kartoffelsalat 100 % (12) |  |  |
| Zwiebelrostbraten | 12 | Reis 50 % (6) | Püree 42 % (5) | Kroketten 8 % (1) |
| Schweinsgulasch | 11 | Püree 36 % (4) | Reis 36 % (4) | Spatzlen 18 % (2) |
| Zigeunerschnitzel | 10 | Reis 50 % (5) | Spatzlen 30 % (3) | Kartoffelstampf 10 % (1) |
| Currywurst | 7 | Pommes 100 % (7) |  |  |
| Ossobuchi | 7 | Spatzlen 57 % (4) | Reis 29 % (2) | Safranreis 14 % (1) |
| Sparerips | 7 | Pommes 71 % (5) | Röstinchen 14 % (1) | Wedges 14 % (1) |
| Gekochtes Rindfleisch | 6 | Salzkartoffeln 100 % (6) |  |  |
| Gulasch | 5 | Plent 40 % (2) | Reis 40 % (2) | Knödel 20 % (1) |
| Hackbraten | 5 | Püree 60 % (3) | Reis 40 % (2) |  |
| Pizzaiolaschnitzel | 5 | Ofenkartoffeln 60 % (3) | Pommes 40 % (2) |  |
| Schweinsschnitzel mit Kräuterrahmsoße | 5 | Reis 40 % (2) | Spatzlen 40 % (2) | Kroketten 20 % (1) |
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
| V–H | 1,693 | 1,651 | 0,116 |
| H–B | 2,070 | 0,832 | 0,003 |
| V–B | 0,897 | 0,887 | 0,359 |

| Vorspeise | Hauptspeise | zusammen | n(V) | n(H) | Lift | p |
|---|---|---|---|---|---|---|
| Lasagne | Truthahngeschnetzeltes | 5 | 20 | 26 | 4,24 | 0,005 |
| Nudel mit Thunfischsoße | Sparerips | 3 | 25 | 7 | 7,56 | 0,007 |
| Gnocchi mit Tomatensoße | Zwiebelrostbraten | 3 | 15 | 12 | 7,35 | 0,007 |
| Carbonara | Schweinsfilet | 3 | 10 | 21 | 6,30 | 0,010 |
| Nudel mit Lachs | Truthahnschnitzel | 3 | 9 | 26 | 5,65 | 0,013 |
| Nudel mit Thunfischsoße | Chilli con carne | 4 | 25 | 17 | 4,15 | 0,015 |
| Tortellini mit Schinken-Rahm | Schweinsschopf | 4 | 19 | 24 | 3,87 | 0,018 |
| Spinatspatzlen | Chilli con carne | 3 | 16 | 17 | 4,86 | 0,022 |
| Spinatspatzlen | Hühnerhaxlen | 3 | 16 | 17 | 4,86 | 0,022 |
| Arrabbiata | Champignonschnitzel | 5 | 30 | 29 | 2,53 | 0,044 |
| Tortellini mit Schinken-Rahm | Hühnerbrust | 4 | 19 | 32 | 2,90 | 0,045 |
| Nudel mit Ragu | Truthahnbraten | 4 | 26 | 24 | 2,83 | 0,050 |
| Arrabbiata | Schweinsfilet | 4 | 30 | 21 | 2,80 | 0,053 |
| Nudel mit Käsesoße | Wienerschnitzel | 4 | 30 | 22 | 2,67 | 0,060 |
| Hirten | Schweinskotelett | 3 | 28 | 17 | 2,78 | 0,092 |
| Aglio olio | Champignonschnitzel | 4 | 27 | 29 | 2,25 | 0,098 |
| Lasagne | Truthahnschnitzel | 3 | 20 | 26 | 2,54 | 0,111 |
| Nudel mit Thunfischsoße | Schweinsschnitzel | 3 | 25 | 21 | 2,52 | 0,114 |
| Arrabbiata | Leberkas | 3 | 30 | 19 | 2,32 | 0,138 |
| Nudel mit Ragu | Wienerschnitzel | 3 | 26 | 22 | 2,31 | 0,138 |
| Hirten | Hühnerbrust | 4 | 28 | 32 | 1,97 | 0,142 |
| Nudel mit Käsesoße | Schweinsschnitzel | 3 | 30 | 21 | 2,10 | 0,170 |
| Hirten | Truthahnbraten | 3 | 28 | 24 | 1,97 | 0,194 |
| Hirten | Truthahnschnitzel | 3 | 28 | 26 | 1,82 | 0,227 |
| Hirten | Truthahngeschnetzeltes | 3 | 28 | 26 | 1,82 | 0,227 |

## 5. Saisonalität

### Fastenzeit (Aschermittwoch – Ostersonntag)

Fastenzeiten in den Daten: 2025: 05.03.–20.04., 2026: 18.02.–05.04.. Fisch = jede Hauptspeise, die als Fisch gilt (inkl. Scombri).

**Hauptspeise** (Fastentage n=64, sonst n=379; Gerichte mit ≥ 2 Fastentagen):

| Gericht | Fastenzeit | sonst | Lift | p |
|---|---|---|---|---|
| Scombri | 4,7 % (3) | 0,0 % (0) | nur Fastenzeit | 0,003 |
| Fisch | 15,6 % (10) | 0,8 % (3) | 19,74 | < 0,001 |
| Currywurst | 3,1 % (2) | 1,3 % (5) | 2,37 | 0,268 |
| Truthahnbraten | 9,4 % (6) | 4,7 % (18) | 1,97 | 0,122 |
| Zigeunerschnitzel | 3,1 % (2) | 2,1 % (8) | 1,48 | 0,435 |
| Schweinsfilet | 6,2 % (4) | 4,5 % (17) | 1,39 | 0,361 |
| Chilli con carne | 4,7 % (3) | 3,7 % (14) | 1,27 | 0,454 |
| Schweinskotelett | 4,7 % (3) | 3,7 % (14) | 1,27 | 0,454 |
| Zwiebelrostbraten | 3,1 % (2) | 2,6 % (10) | 1,18 | 0,535 |
| Champignonschnitzel | 6,2 % (4) | 6,6 % (25) | 0,95 | 0,620 |
| Wienerschnitzel | 4,7 % (3) | 5,3 % (20) | 0,89 | 0,666 |
| Truthahngeschnetzeltes | 4,7 % (3) | 6,1 % (23) | 0,77 | 0,746 |

**Vorspeise** (Fastentage n=64, sonst n=378; Gerichte mit ≥ 2 Fastentagen):

| Gericht | Fastenzeit | sonst | Lift | p |
|---|---|---|---|---|
| Nudel mit Lachs | 3,1 % (2) | 1,9 % (7) | 1,69 | 0,382 |
| Amatriciana | 6,2 % (4) | 4,0 % (15) | 1,58 | 0,292 |
| Spinatcannelloni | 3,1 % (2) | 2,1 % (8) | 1,48 | 0,436 |
| Nudel mit Ragu | 7,8 % (5) | 5,6 % (21) | 1,41 | 0,321 |
| Spinatspatzlen | 4,7 % (3) | 3,4 % (13) | 1,36 | 0,415 |
| Pizzastrudel | 3,1 % (2) | 2,4 % (9) | 1,31 | 0,488 |
| Nudel mit Käsesoße | 7,8 % (5) | 6,6 % (25) | 1,18 | 0,443 |
| Schlutzer | 6,2 % (4) | 5,3 % (20) | 1,18 | 0,466 |
| Aglio olio | 6,2 % (4) | 6,1 % (23) | 1,03 | 0,563 |
| Lasagne | 4,7 % (3) | 4,8 % (18) | 0,98 | 0,604 |
| Arrabbiata | 6,2 % (4) | 6,9 % (26) | 0,91 | 0,649 |
| Gnocchi mit Tomatensoße | 3,1 % (2) | 3,4 % (13) | 0,91 | 0,661 |

**Beilage** (Fastentage n=64, sonst n=379; Gerichte mit ≥ 2 Fastentagen):

| Gericht | Fastenzeit | sonst | Lift | p |
|---|---|---|---|---|
| Salzkartoffeln | 4,7 % (3) | 2,1 % (8) | 2,22 | 0,205 |
| Kartoffelgratin | 9,4 % (6) | 4,5 % (17) | 2,09 | 0,103 |
| Plent | 7,8 % (5) | 4,0 % (15) | 1,97 | 0,152 |
| Röstkartoffeln | 4,7 % (3) | 2,9 % (11) | 1,62 | 0,329 |
| Kartoffelsalat | 10,9 % (7) | 7,4 % (28) | 1,48 | 0,234 |
| Püree | 12,5 % (8) | 9,5 % (36) | 1,32 | 0,299 |
| Kroketten | 6,2 % (4) | 5,5 % (21) | 1,13 | 0,497 |
| Spatzlen | 9,4 % (6) | 10,3 % (39) | 0,91 | 0,648 |
| Reis | 20,3 % (13) | 23,0 % (87) | 0,88 | 0,702 |
| Pommes | 7,8 % (5) | 14,0 % (53) | 0,56 | 0,935 |
| Ofenkartoffeln | 3,1 % (2) | 9,5 % (36) | 0,33 | 0,980 |

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

**Vorspeise** (Tage je Monat: Jan 30, Feb 40, Mär 42, Apr 34, Mai 39, Jun 39, Jul 45, Aug 22, Sep 43, Okt 45, Nov 35, Dez 28)

| Gericht | Jan | Feb | Mär | Apr | Mai | Jun | Jul | Aug | Sep | Okt | Nov | Dez |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Arrabbiata | 10 | 8 | 5 | 6 | 5 | 8 | 7 | 9 | 7 | 4 | 6 | 11 |
| Nudel mit Käsesoße | 7 | 8 | 7 | 3 | 10 | 10 | 4 | 5 | 7 | 9 | 6 | 4 |
| Hirten | · | 8 | 7 | 3 | 8 | 8 | 7 | 14 | 9 | 4 | 3 | 7 |
| Aglio olio | 10 | · | 7 | 6 | 5 | 5 | 4 | 14 | 5 | 7 | 9 | 7 |
| Nudel mit Ragu | 7 | 8 | 5 | 9 | 5 | 3 | 9 | · | 7 | 7 | 6 | 4 |
| Nudel mit Thunfischsoße | 7 | 10 | 2 | 6 | 5 | 5 | 4 | 9 | 2 | 7 | 9 | 4 |
| Schlutzer | 7 | 2 | 7 | 3 | 8 | 3 | 9 | 5 | 5 | 7 | 3 | 7 |
| Nudel Mammarosa | 3 | 5 | 5 | 3 | 3 | 8 | 4 | 5 | 7 | 4 | 3 | 11 |
| Lasagne | 3 | · | 5 | 6 | 8 | 5 | 7 | · | 5 | 9 | 3 | 4 |
| Amatriciana | 3 | 2 | 7 | 6 | 5 | 5 | 2 | 5 | 2 | 4 | 6 | 4 |

**Hauptspeise** (Tage je Monat: Jan 30, Feb 40, Mär 42, Apr 34, Mai 39, Jun 39, Jul 45, Aug 22, Sep 44, Okt 45, Nov 35, Dez 28)

| Gericht | Jan | Feb | Mär | Apr | Mai | Jun | Jul | Aug | Sep | Okt | Nov | Dez |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Hühnerbrust | 10 | 5 | 10 | 3 | 10 | 8 | 7 | · | 9 | 7 | 9 | 7 |
| Champignonschnitzel | 3 | 8 | 5 | 9 | 8 | 5 | 4 | 9 | 7 | 9 | 3 | 11 |
| Truthahngeschnetzeltes | 7 | 8 | 5 | 3 | 10 | 5 | 4 | 5 | 5 | 4 | 6 | 11 |
| Truthahnschnitzel | 7 | 2 | 5 | 3 | 8 | 18 | 7 | 5 | 5 | 2 | 3 | 7 |
| Schweinsschopf | 7 | 8 | 2 | 6 | 3 | · | 9 | 9 | 5 | 7 | 6 | 7 |
| Truthahnbraten | · | 5 | 10 | 9 | · | · | 4 | 14 | 7 | 7 | 9 | 4 |
| Wienerschnitzel | · | 10 | 2 | 3 | 5 | 3 | 9 | 5 | 9 | 7 | 3 | 4 |
| Schweinsfilet | 3 | 5 | 5 | 9 | 8 | 3 | 4 | · | 5 | 2 | 9 | 4 |
| Schweinsschnitzel | 3 | 5 | 2 | 3 | 3 | 8 | 9 | 9 | 2 | 4 | 6 | 4 |
| Leberkas | 7 | · | 2 | 6 | 5 | 5 | 4 | 5 | 5 | 7 | 6 | 4 |

**Beilage** (Tage je Monat: Jan 30, Feb 40, Mär 42, Apr 34, Mai 39, Jun 39, Jul 45, Aug 22, Sep 44, Okt 45, Nov 35, Dez 28)

| Gericht | Jan | Feb | Mär | Apr | Mai | Jun | Jul | Aug | Sep | Okt | Nov | Dez |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Reis | 23 | 22 | 24 | 21 | 18 | 18 | 24 | 27 | 20 | 29 | 20 | 25 |
| Pommes | 13 | 12 | 10 | 12 | 13 | 15 | 18 | 18 | 11 | 16 | 6 | 14 |
| Spatzlen | 10 | 8 | 10 | 12 | 13 | 5 | 9 | 14 | 11 | 9 | 11 | 14 |
| Püree | 10 | 12 | 12 | 12 | 18 | 8 | 7 | 14 | 7 | 7 | 11 | 4 |
| Ofenkartoffeln | 3 | 8 | 2 | 6 | 5 | 13 | 13 | 9 | 14 | 9 | 11 | 7 |
| Kartoffelsalat | 3 | 10 | 5 | 9 | 8 | 13 | 9 | 5 | 9 | 9 | 6 | 7 |
| Kroketten | 7 | 8 | 7 | 6 | 3 | 8 | 2 | 5 | 7 | 7 | 9 | · |
| Kartoffelgratin | 3 | 8 | 10 | 6 | 8 | 5 | 4 | · | 2 | 4 | 6 | 4 |
| Plent | 7 | 2 | 7 | 6 | 3 | 3 | 4 | · | 5 | 4 | 6 | 7 |
| Röstkartoffeln | 3 | 2 | 2 | 6 | 3 | 8 | 2 | · | 2 | 2 | 3 | 4 |

### Weihnachtszeit (1.–23. Dezember)

- **Vorspeise** (Dezembertage n=28): Fleischcannelloni 2× (7 % vs 0 % sonst, p = 0,012); Nudel Mammarosa 3× (11 % vs 5 % sonst, p = 0,160); Arrabbiata 3× (11 % vs 7 % sonst, p = 0,295)
- **Hauptspeise** (Dezembertage n=28): Zwiebelrostbraten 2× (7 % vs 2 % sonst, p = 0,173); Hauswurst 2× (7 % vs 3 % sonst, p = 0,220); Hühnerhaxlen 2× (7 % vs 4 % sonst, p = 0,292); Truthahngeschnetzeltes 3× (11 % vs 6 % sonst, p = 0,225); Champignonschnitzel 3× (11 % vs 6 % sonst, p = 0,277)
- **Beilage** (Dezembertage n=28): Kartoffelstampf 2× (7 % vs 2 % sonst, p = 0,107); Plent 2× (7 % vs 4 % sonst, p = 0,363)
- Letztes Menü vor Weihnachten 2024 (19.12.): Lasagne / Truthahngeschnetzeltes / Spatzlen
- Letztes Menü vor Weihnachten 2025 (19.12.): Nudel Mammarosa / Cordon Bleu / Kartoffelsalat

## 6. Trends (2026 vs. 2024, 2025)

- **Vorspeise neu 2026** (10): Gnocchi mit Gorgonzolasoße (2×), Spinatknödel mit Käsesoße (2×), Gnocchi mit Kräutersauce (1×), Gnocchi mit Lachs (1×), Käse-Sofficini mit Tomantensoße (1×), Nudel mit Schinken-Rahm (1×), Pilzrisotto (1×), Spargelrisotto (1×), Speck-Zwiebel-Kuchen (1×), Tomatenrisotto (1×)
- **Vorspeise verschwunden 2026** (26): Fleischcannelloni (3×), Ravioli mit Parmesan-Butter (3×), Tomatenrisotto mit Mozzarella (3×), Gnocchi mit Käsesoße (2×), Gulaschsuppe (2×), Nudelsalat (2×), Omelett mit Schinken und Käse (2×), Plentauflauf (2×), Ravioli (2×), Fleischsuppe (1×), Gemüselasagne (1×), Gnocchi (1×), Gnocchi mit Ragu (1×), Kürbisrisotto (1×), Nudel mit Lachs und Tomantensoße (1×), Nudel mit Tomatensoße (1×), Nudel mit Tomatensoße und Schinken (1×), Putanesca (1×), Ravioli mit Käsesoße (1×), Ravioli mit Tomantensoße (1×), Reissalat (1×), Schlutzer Schinken-Rahm (1×), Schupfnudel mit Lachs (1×), Schüttelbrot-Risotto mit Speckstreifen (1×), Spinatknödel (1×), Spinatknödel mit Gorgonzolasoße (1×)
- **Hauptspeise neu 2026** (13): Vitello tonnato (3×), Forelle (2×), Frittiertes Pangasiusfilet (2×), Hamburger (2×), Kalbsgulasch (2×), Schweinsfilet mit Pfeffersoße (2×), 1/2 Brathuhn (1×), Fleischkrapfln (1×), Hirschgulasch (1×), Lammbraten (1×), Pangasiusfilet mit Kräuterrahmsoße (1×), Panierter Pangasius (1×), Spiegelei (1×)
- **Hauptspeise verschwunden 2026** (7): Pizzaiolaschnitzel (5×), Knödel (3×), Rotbarschfilet (2×), Frittiertes Schollenfilet (1×), Pangasiusfilet (1×), Paprika-Schweinegulasch (1×), Saures Rindfleisch (1×)
- **Beilage neu 2026** (4): Wedges (7×), Röstinchen (2×), Kartoffel-Käse-Kroketten (1×), Knödel (1×)
- **Beilage verschwunden 2026** (4): Gulasch (3×), Kraut (1×), Safranreis (1×), Zucchini (1×)

**Aufsteiger / Absteiger** (Anteil 2025 → 2026, Gerichte mit n ≥ 5):

| Kategorie | Gericht |  | 2025 | 2026 |
|---|---|---|---|---|
| Vorspeise | Tortellini mit Schinken-Rahm | ↑ | 3,6 % | 5,8 % |
| Vorspeise | Gnocchi mit Tomatensoße | ↑ | 2,7 % | 4,8 % |
| Vorspeise | Lasagne | ↑ | 4,1 % | 5,3 % |
| Vorspeise | Nudel mit Pesto | ↑ | 3,2 % | 4,2 % |
| Vorspeise | Hirten | ↑ | 5,9 % | 6,9 % |
| Vorspeise | Spinatspatzlen | ↓ | 4,5 % | 2,6 % |
| Vorspeise | Nudel mit Ragu | ↓ | 6,4 % | 4,8 % |
| Vorspeise | Nudel mit Thunfischsoße | ↓ | 6,4 % | 4,8 % |
| Vorspeise | Aglio olio | ↓ | 6,8 % | 5,8 % |
| Vorspeise | Arrabbiata | ↓ | 7,3 % | 6,3 % |
| Hauptspeise | Sparerips | ↑ | 0,5 % | 2,6 % |
| Hauptspeise | Cordon Bleu | ↑ | 2,3 % | 3,7 % |
| Hauptspeise | Ossobuchi | ↑ | 0,9 % | 2,1 % |
| Hauptspeise | Hühnerhaxlen | ↑ | 3,2 % | 4,2 % |
| Hauptspeise | Schweinsgulasch | ↑ | 2,3 % | 3,2 % |
| Hauptspeise | Schweinskotelett | ↓ | 5,4 % | 1,6 % |
| Hauptspeise | Truthahnschnitzel | ↓ | 7,2 % | 4,2 % |
| Hauptspeise | Schweinsschnitzel | ↓ | 5,9 % | 3,7 % |
| Hauptspeise | Pizzaiolaschnitzel | ↓ | 1,8 % | 0,0 % |
| Hauptspeise | Schweinsfilet | ↓ | 5,4 % | 3,7 % |
| Beilage | Wedges | ↑ | 0,0 % | 3,7 % |
| Beilage | Kartoffelsalat | ↑ | 6,8 % | 10,1 % |
| Beilage | Spatzlen | ↑ | 8,1 % | 11,1 % |
| Beilage | Bratkartoffeln | ↑ | 0,5 % | 2,6 % |
| Beilage | Pommes | ↑ | 12,7 % | 14,3 % |
| Beilage | Ofenkartoffeln | ↓ | 10,4 % | 5,8 % |
| Beilage | Kartoffelgratin | ↓ | 7,2 % | 3,2 % |
| Beilage | Reis | ↓ | 24,4 % | 20,6 % |
| Beilage | Plent | ↓ | 5,4 % | 3,7 % |
| Beilage | Kroketten | ↓ | 6,3 % | 4,8 % |

### Gewichtung nach Aktualität

Mittlerer Log-Loss einer reinen Häufigkeitsprognose für jeden Tag 2026 (nur Vergangenheit, Gewicht 0,5^(Alter/Halbwertszeit), Glättung 0,5; kleiner = besser). Zeigt, ob jüngere Menüs mehr zählen sollten (Refraktärzeit und Wochentag sind hier bewusst nicht enthalten).

| Kategorie | 30 T | 60 T | 90 T | 180 T | 365 T | ∞ (ungewichtet) |
|---|---|---|---|---|---|---|
| Vorspeise | 3,777 | 3,620 | 3,557 | 3,507 | 3,500 | 3,513 |
| Hauptspeise | 3,752 | 3,665 | 3,635 | 3,618 | 3,625 | 3,647 |
| Beilage | 2,629 | 2,568 | 2,552 | 2,548 | 2,555 | 2,571 |

Aktualitätsgewichtung: beste Halbwertszeit (Log-Loss, Tage) – Vorspeise 365, Hauptspeise 180, Beilage 180.

### Anteile je Jahr (Top-Gerichte)

**Vorspeise**

| Gericht | 2024 | 2025 | 2026 |
|---|---|---|---|
| Arrabbiata | 6,1 % | 7,3 % | 6,3 % |
| Nudel mit Käsesoße | 3,0 % | 6,8 % | 7,4 % |
| Hirten | 6,1 % | 5,9 % | 6,9 % |
| Aglio olio | 3,0 % | 6,8 % | 5,8 % |
| Nudel mit Ragu | 9,1 % | 6,4 % | 4,8 % |
| Nudel mit Thunfischsoße | 6,1 % | 6,4 % | 4,8 % |
| Schlutzer | 3,0 % | 5,5 % | 5,8 % |
| Nudel Mammarosa | 6,1 % | 5,0 % | 4,8 % |
| Lasagne | 6,1 % | 4,1 % | 5,3 % |
| Amatriciana | 3,0 % | 4,5 % | 4,2 % |
| Tortellini mit Schinken-Rahm | 0,0 % | 3,6 % | 5,8 % |
| Nudel mit Pesto | 3,0 % | 3,2 % | 4,2 % |
| Spinatspatzlen | 3,0 % | 4,5 % | 2,6 % |
| Gnocchi mit Tomatensoße | 0,0 % | 2,7 % | 4,8 % |
| Käseknödel | 6,1 % | 1,8 % | 2,6 % |

**Hauptspeise**

| Gericht | 2024 | 2025 | 2026 |
|---|---|---|---|
| Hühnerbrust | 6,1 % | 7,2 % | 7,4 % |
| Champignonschnitzel | 6,1 % | 7,2 % | 5,8 % |
| Truthahngeschnetzeltes | 6,1 % | 5,9 % | 5,8 % |
| Truthahnschnitzel | 6,1 % | 7,2 % | 4,2 % |
| Schweinsschopf | 9,1 % | 5,0 % | 5,3 % |
| Truthahnbraten | 12,1 % | 5,0 % | 4,8 % |
| Wienerschnitzel | 3,0 % | 5,4 % | 5,3 % |
| Schweinsfilet | 6,1 % | 5,4 % | 3,7 % |
| Schweinsschnitzel | 3,0 % | 5,9 % | 3,7 % |
| Leberkas | 6,1 % | 4,5 % | 4,2 % |
| Chilli con carne | 0,0 % | 4,5 % | 3,7 % |
| Hühnerhaxlen | 6,1 % | 3,2 % | 4,2 % |
| Schweinskotelett | 6,1 % | 5,4 % | 1,6 % |
| Hauswurst | 3,0 % | 3,2 % | 3,2 % |
| Cordon Bleu | 0,0 % | 2,3 % | 3,7 % |

**Beilage**

| Gericht | 2024 | 2025 | 2026 |
|---|---|---|---|
| Reis | 21,2 % | 24,4 % | 20,6 % |
| Pommes | 9,1 % | 12,7 % | 14,3 % |
| Spatzlen | 18,2 % | 8,1 % | 11,1 % |
| Püree | 6,1 % | 10,0 % | 10,6 % |
| Ofenkartoffeln | 12,1 % | 10,4 % | 5,8 % |
| Kartoffelsalat | 3,0 % | 6,8 % | 10,1 % |
| Kroketten | 6,1 % | 6,3 % | 4,8 % |
| Kartoffelgratin | 3,0 % | 7,2 % | 3,2 % |
| Plent | 3,0 % | 5,4 % | 3,7 % |
| Röstkartoffeln | 6,1 % | 3,2 % | 2,6 % |
| Salzkartoffeln | 3,0 % | 2,3 % | 2,6 % |
| Kartoffelstampf | 6,1 % | 1,4 % | 2,1 % |
| Wedges | 0,0 % | 0,0 % | 3,7 % |
| Bratkartoffeln | 0,0 % | 0,4 % | 2,6 % |
| Gulasch | 0,0 % | 1,4 % | 0,0 % |

## 7. Spieler

Punkte = Neuberechnung der Engine (`tips.points`; identisch mit dem Excel bis auf dokumentierte manuelle Korrekturen). Nur servierte Tage vor dem Stichtag. „Alles falsch“ = 0 Punkte, „Alles richtig“ = 3 Punkte.

| Jahr | Spieler | Tage | Punkte | P./Tag | Alles falsch | Alles richtig | V | H | B | R4-Verstöße | Abw. Excel |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026 | Johannes | 165 | 45,5 | 0,276 | 105 (64 %) | 1 | 8 % | 10 % | 28 % | 4 | 0 |
| 2026 | Andreas | 171 | 44,5 | 0,260 | 112 (66 %) | 0 | 9 % | 9 % | 25 % | 1 | 0 |
| 2026 | Johannes Paul III | 166 | 41,5 | 0,250 | 115 (69 %) | 2 | 9 % | 9 % | 21 % | 1 | 0 |
| 2026 | Noah | 174 | 41,5 | 0,238 | 122 (70 %) | 1 | 7 % | 9 % | 24 % | 1 | 0 |
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
| 2026 | Johannes Paul III | Hirten 15, Lasagne 15, Nudel mit Käsesoße 14 | Champignonschnitzel 17, Hühnerbrust 15, Truthahngeschnetzeltes 15 | Reis 44, Pommes 19, Kartoffelsalat 18 |
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
| Vorspeise | 11,6 % (n=337) | 7,5 % (n=1008) |
| Hauptspeise | 9,6 % (n=456) | 7,2 % (n=890) |
| Beilage | 27,9 % (n=813) | 10,2 % (n=532) |

| Kategorie | 1–2 AT | 3–5 AT | 6–10 AT | 11–20 AT | 21–40 AT | > 40 AT | nie serviert |
|---|---|---|---|---|---|---|---|
| Vorspeise | 0,0 % (12) | 3,6 % (56) | 7,0 % (285) | 10,7 % (504) | 10,9 % (285) | 4,6 % (152) | 2,0 % (51) |
| Hauptspeise | 0,0 % (9) | 4,4 % (90) | 5,2 % (291) | 9,5 % (514) | 9,2 % (272) | 8,0 % (100) | 10,0 % (70) |
| Beilage | 25,3 % (83) | 27,5 % (437) | 21,0 % (353) | 15,5 % (303) | 14,9 % (114) | 4,5 % (44) | 0,0 % (11) |

- Vorspeise: Top-5-Tipps treffen 11,6 % vs 7,5 % (besser, Faktor 1,53).
- Hauptspeise: Top-5-Tipps treffen 9,6 % vs 7,2 % (besser, Faktor 1,34).
- Beilage: Top-5-Tipps treffen 27,9 % vs 10,2 % (besser, Faktor 2,75).

→ Tipps auf Gerichte, die erst vor 1–5 Arbeitstagen serviert wurden, treffen bei der Vorspeise nur 2,9 % (n=68) gegenüber 8,8 % sonst; Hauptspeise 4,0 % vs 8,3 %; Beilage 27,1 % vs 17,0 %.

### Strategie-Kennzahlen je Spieler und Jahr

Top-5-Anteil = Anteil der Tipps auf die 5 bis dahin häufigsten Gerichte; Vielfalt = mittlere Entropie der eigenen Tipps (bit); kürzlich = Anteil der Tipps auf Gerichte der letzten 5 Arbeitstage.

| Jahr | Spieler | P./Tag | Rang | Top-5-Anteil | Vielfalt | kürzlich |
|---|---|---|---|---|---|---|
| 2026 | Johannes | 0,276 | 1 | 40 % | 3,85 | 16 % |
| 2026 | Andreas | 0,260 | 2 | 40 % | 3,68 | 16 % |
| 2026 | Johannes Paul III | 0,250 | 3 | 45 % | 3,92 | 20 % |
| 2026 | Noah | 0,238 | 4 | 52 % | 3,50 | 19 % |
| 2025 | Noah | 0,242 | 1 | 36 % | 3,80 | 16 % |
| 2025 | Andreas | 0,222 | 2 | 35 % | 3,91 | 15 % |
| 2025 | Johannes | 0,187 | 3 | 36 % | 3,89 | 19 % |
| 2024 | Johannes | 0,222 | 1 | 25 % | 3,19 | 11 % |
| 2024 | Andreas | 0,191 | 2 | 26 % | 3,46 | 7 % |
| 2024 | Noah | 0,103 | 3 | 30 % | 3,25 | 10 % |

Korrelation mit Punkten/Tag über 7 Spieler-Jahre mit ≥ 100 Tagen (sehr kleine Stichprobe, nur Hinweis): Top-5-Anteil r=0,32, Vielfalt r=-0,22, kürzlich r=-0,26, V-Trefferquote r=0,16. Die Vorspeise zählt doppelt so viel wie H oder B (1 vs 0,5 Punkte); über die Spieler-Jahre erklärt die V-Trefferquote die Rangfolge aber nur schwach.

### Notizen je Spieler

- **Johannes 2026**: 0,28 Punkte/Tag (Rang 1/4 in 2026). Top-5-Anteil der Tipps 40 %, Vielfalt 3,8 bit, 16 % Tipps auf Gerichte, die in den letzten 5 Arbeitstagen serviert wurden. Stärkste Kategorie: Beilage (28 % Treffer). Regel-4-Verstöße: 4.
- **Andreas 2026**: 0,26 Punkte/Tag (Rang 2/4 in 2026). Top-5-Anteil der Tipps 40 %, Vielfalt 3,7 bit, 16 % Tipps auf Gerichte, die in den letzten 5 Arbeitstagen serviert wurden. Stärkste Kategorie: Beilage (25 % Treffer). Regel-4-Verstöße: 1.
- **Johannes Paul III 2026**: 0,25 Punkte/Tag (Rang 3/4 in 2026). Top-5-Anteil der Tipps 45 %, Vielfalt 3,9 bit, 20 % Tipps auf Gerichte, die in den letzten 5 Arbeitstagen serviert wurden. Stärkste Kategorie: Beilage (21 % Treffer). Regel-4-Verstöße: 1.
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

