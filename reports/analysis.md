# Analyse Tippspiel Essen Wies

_Automatisch erzeugt von `engine/analyze.py` am 2026-11-20 14:00 UTC (Stichtag 2026-11-20). Datenstand: 462 servierte Menüs (2024: 34, 2025: 221, 2026: 207), letztes Menü 2026-11-19._

## Riassunto (IT)

- **Dati**: 462 menù serviti (2024: 34, 2025: 221, 2026: 207); piatti distinti: primo 61, secondo 49, contorno 20.
- **Primo più frequenti**: Arrabbiata (31), Nudel mit Käsesoße (31), Hirten (30); i primi 5 coprono 32 % dei giorni.
- **Secondo più frequenti**: Hühnerbrust (33), Champignonschnitzel (29), Truthahngeschnetzeltes (28); i primi 5 coprono 31 % dei giorni.
- **Contorno più frequenti**: Reis (103), Pommes (60), Spatzlen (48); i primi 5 coprono 64 % dei giorni.
- **Ripetizioni**: la cucina evita le ripetizioni. Primo e secondo: mai due volte nella stessa settimana (0 e 0 coppie contro 40 e 39 attese per caso, p < 0,001); quasi nessuna ripetizione entro 5 (primo) / 3 (secondo) giorni lavorativi; intervallo mediano 17 / 19 giorni lavorativi. Il contorno si ripete molto di più (18 coppie nella stessa settimana, 103 attese per caso). → Non tippare primo/secondo serviti negli ultimi giorni o già serviti questa settimana.
- **Giorno della settimana**: Reis (contorno) il lunedì 44/103 (atteso 19 %, p < 0,001); Schweinskotelett (secondo) il mercoledì 13/17 (atteso 21 %, p < 0,001); Arrabbiata (primo) il lunedì 17/31 (atteso 19 %, p < 0,001); Champignonschnitzel (secondo) il lunedì 16/29 (atteso 19 %, p < 0,001). 4 effetti restano significativi anche con correzione di Bonferroni: il giorno della settimana conta.
- **Ipotesi confermate**: pesce (tutti) il venerdì 11/13; pesce fuori Quaresima il venerdì 3/3; Plent (polenta) il venerdì 10/21. Non confermate: Scombri, Leberkas.
- **Contorno ↔ secondo**: conoscendo il secondo, il contorno più tipico è giusto nel 50 % dei casi (leave-one-out) contro 22 % tippando sempre Reis (es. Champignonschnitzel → Reis 76 %, Wienerschnitzel → Kartoffelsalat 83 %, Leberkas → Röstkartoffeln 60 %, Chilli con carne → Reis 100 %). Primo e secondo invece sono quasi indipendenti (MI 1,67 bit vs 1,63 per caso, p = 0,173).
- **Quaresima / pesce**: pesce in Quaresima nel 16 % dei giorni contro 1 % fuori (10 vs 3 giorni). Nessuna differenza significativa estate/inverno.
- **Trend 2026**: nuovi primi 11, nuovi secondi 14; spariti primi 25, secondi 7 (quasi tutti piatti rari, ≤ 3 volte). Pesatura per recenza (emivita migliore in giorni, log-loss): primo 365, secondo 180, contorno 180.
- **Giocatori 2026**: miglior media Johannes con 0,28 punti/giorno. Tipp (tutti i giocatori e anni) su piatti serviti negli ultimi 5 giorni lavorativi: primo centrato nel 2,8 % (n=71) contro 9,0 % per gli altri tipp; il momento migliore per tippare un primo è 11–20 giorni lavorativi dopo l'ultima volta (11,5 %).

## Kernaussagen

- **Keine Wiederholung in derselben Woche**: Vorspeise nie zweimal in derselben Kalenderwoche (0 Paare, Zufall 39,8, p < 0,001), Hauptspeise nie zweimal in derselben Kalenderwoche (0 Paare, Zufall 39,1, p < 0,001). Beilage dagegen 18 Paare (Zufall 103,2), v. a. Reis.
- **Mindestabstand**: Vorspeise frühestens wieder nach 3 Arbeitstagen, Hauptspeise nach 2; innerhalb von 5 bzw. 3 AT praktisch nie (< 25 % der Zufallsrate). Median-Abstand 17,0 (V), 19,0 (H), 8,0 (B) Arbeitstage.
- **Wochenrhythmus**: Bei Abständen von 10, 15, … 30 AT (gleicher Wochentag) ist dieselbe Speise häufiger als bei anderen Abständen – V 5,0 % vs 4,1 % (p = 0,022), H 5,3 % vs 3,9 % (p < 0,001). Spitze Vorspeise L=30: 6,5 % vs 4,5 % (p = 0,041). Spitze Hauptspeise L=20: 7,8 % vs 4,3 % (p = 0,001).
- **Wochentag**: Reis (Beilage) am Montag 44/103 (43 %, erwartet 19 %, Lift 2,2, p < 0,001, Bonferroni-signifikant).
- **Wochentag**: Schweinskotelett (Hauptspeise) am Mittwoch 13/17 (76 %, erwartet 21 %, Lift 3,7, p < 0,001, Bonferroni-signifikant).
- **Wochentag**: Arrabbiata (Vorspeise) am Montag 17/31 (55 %, erwartet 19 %, Lift 2,8, p < 0,001, Bonferroni-signifikant).
- **Wochentag**: Champignonschnitzel (Hauptspeise) am Montag 16/29 (55 %, erwartet 19 %, Lift 2,9, p < 0,001, Bonferroni-signifikant).
- **Hypothese Fisch (alle Fischgerichte)**: häufigster Tag Freitag 11/13 (Mo–Fr: 0/0/2/0/11, p < 0,001) → bestätigt.
- **Hypothese Fisch außerhalb Fastenzeit**: häufigster Tag Freitag 3/3 (Mo–Fr: 0/0/0/0/3, p = 0,007) → bestätigt.
- **Hypothese Scombri**: häufigster Tag Freitag 2/3 (Mo–Fr: 0/0/1/0/2, p = 0,095) → nicht bestätigt.
- **Hypothese Plent**: häufigster Tag Freitag 10/21 (Mo–Fr: 0/0/5/6/10, p = 0,003) → bestätigt.
- **Hypothese Leberkas**: häufigster Tag Mittwoch 6/20 (Mo–Fr: 3/2/6/5/4, p = 0,216) → nicht bestätigt.
- **Hypothese Hauswurst**: häufigster Tag Freitag 7/15 (Mo–Fr: 0/0/4/4/7, p = 0,014) → Tendenz.
- **Beilage hängt an der Hauptspeise**: mit bekannter Hauptspeise trifft die typische Beilage in 50 % der Fälle (Leave-one-out), ohne nur 22 % (Reis); Entropie 3,53 → 1,44 bit. Feste Paare: Champignonschnitzel → Reis 76 % (22), Wienerschnitzel → Kartoffelsalat 83 % (20), Leberkas → Röstkartoffeln 60 % (12), Chilli con carne → Reis 100 % (18), Hühnerhaxlen → Pommes 71 % (12), Hauswurst → Plent 100 % (14), Cordon Bleu → Kartoffelsalat 100 % (13), Currywurst → Pommes 100 % (9), Sparerips → Pommes 71 % (5), Gekochtes Rindfleisch → Salzkartoffeln 100 % (6), Pizzaiolaschnitzel → Ofenkartoffeln 60 % (3).
- **Vorspeise ↔ Hauptspeise**: kaum Zusammenhang (MI 1,668 vs Zufall 1,635 bit, p = 0,173); einzelne Paare mit hohem Lift entstehen v. a. über den gemeinsamen Wochentag.
- **Fisch & Fastenzeit**: Fisch an 16 % der Fastentage (10) vs 1 % sonst (3; p < 0,001). Sommer/Winter: keine signifikanten Unterschiede.
- Aktualitätsgewichtung: beste Halbwertszeit (Log-Loss, Tage) – Vorspeise 365, Hauptspeise 180, Beilage 180.
- **Tipp-Timing (alle Spieler)**: Tipps auf Gerichte, die vor 1–5 AT serviert wurden, treffen bei V nur 2,8 % (sonst 9,0 %), bei H 3,9 % (sonst 8,9 %). Beste Abstandsklasse: Vorspeise 11–20 AT (11,5 %, n=567), Hauptspeise 21–40 AT (10,8 %, n=295), Beilage 3–5 AT (28,4 %, n=483).
- **Spieler 2026**: beste Quote Johannes mit 0,279 Punkten/Tag; Spannweite 0,079 Punkte/Tag: Johannes 0,279 (190 T.), Andreas 0,277 (197 T.), Johannes Paul III 0,263 (192 T.), Noah 0,247 (200 T.), Lorenz 0,200 (10 T.).

## 1. Häufigkeiten

Gezählt wird die erste angesagte Option (bei „A / B“ zählt A). „zuletzt“ berücksichtigt alle Optionen.

| Kategorie | verschiedene Gerichte | 2024 | 2025 | 2026 | Top-5-Anteil | Entropie (bit) |
|---|---|---|---|---|---|---|
| Vorspeise | 61 | 24 | 44 | 39 | 32 % | 4,96 |
| Hauptspeise | 49 | 20 | 35 | 42 | 31 % | 4,92 |
| Beilage | 20 | 13 | 14 | 18 | 64 % | 3,53 |

### Vorspeise – Top 20

| # | Gericht | gesamt | Anteil | 2024 | 2025 | 2026 | zuletzt |
|---|---|---|---|---|---|---|---|
| 1 | Arrabbiata | 31 | 6,7 % | 2 | 16 | 13 | 2026-11-06 |
| 2 | Nudel mit Käsesoße | 31 | 6,7 % | 1 | 15 | 15 | 2026-11-11 |
| 3 | Hirten | 30 | 6,5 % | 2 | 13 | 15 | 2026-11-19 |
| 4 | Aglio olio | 29 | 6,3 % | 1 | 15 | 13 | 2026-11-16 |
| 5 | Nudel mit Ragu | 27 | 5,9 % | 3 | 14 | 10 | 2026-11-12 |
| 6 | Nudel mit Thunfischsoße | 26 | 5,7 % | 2 | 14 | 10 | 2026-10-30 |
| 7 | Nudel Mammarosa | 24 | 5,2 % | 2 | 11 | 11 | 2026-11-17 |
| 8 | Schlutzer | 24 | 5,2 % | 1 | 12 | 11 | 2026-10-20 |
| 9 | Lasagne | 22 | 4,8 % | 2 | 9 | 11 | 2026-11-02 |
| 10 | Tortellini mit Schinken-Rahm | 20 | 4,3 % | 0 | 8 | 12 | 2026-11-03 |
| 11 | Amatriciana | 19 | 4,1 % | 1 | 10 | 8 | 2026-11-09 |
| 12 | Nudel mit Pesto | 17 | 3,7 % | 1 | 7 | 9 | 2026-11-04 |
| 13 | Spinatspatzlen | 16 | 3,5 % | 1 | 10 | 5 | 2026-09-29 |
| 14 | Gnocchi mit Tomatensoße | 15 | 3,3 % | 0 | 6 | 9 | 2026-10-27 |
| 15 | Käseknödel | 11 | 2,4 % | 2 | 4 | 5 | 2026-09-24 |
| 16 | Pizzastrudel | 11 | 2,4 % | 1 | 5 | 5 | 2026-10-07 |
| 17 | Spinatcannelloni | 11 | 2,4 % | 1 | 4 | 6 | 2026-10-29 |
| 18 | Carbonara | 10 | 2,2 % | 1 | 4 | 5 | 2026-09-18 |
| 19 | Nudel mit Lachs | 9 | 2,0 % | 0 | 5 | 4 | 2026-10-16 |
| 20 | Nudel mit Salsiccia-Ragu | 5 | 1,1 % | 0 | 2 | 3 | 2026-09-03 |

**Selten (n ≤ 2, 33 Gerichte):** Gerstsuppe, Gnocchi mit Gorgonzolasoße, Gnocchi mit Käsesoße, Omelett mit Schinken und Käse, Plentauflauf, Ravioli, Spinatknödel, Spinatknödel mit Käsesoße, Spinatravioli, Gemüselasagne, Gnocchi, Gnocchi mit Kräutersauce, Gnocchi mit Lachs, Gnocchi mit Ragu, Gulaschsuppe, Käse-Sofficini mit Tomantensoße, Kürbisrisotto, Nudel mit Lachs und Tomantensoße, Nudel mit Schinken-Rahm, Nudel mit Tomatensoße, Nudel mit Tomatensoße und Schinken, Pilzrisotto, Putanesca, Ravioli mit Käsesoße, Ravioli mit Tomantensoße, Schlutzer Schinken-Rahm, Schupfnudel mit Lachs, Schüttelbrot-Risotto mit Speckstreifen, Spargelrisotto, Speck-Zwiebel-Kuchen, Spinatknödel mit Gorgonzolasoße, Tomatenrisotto, Truthahn-Gemüse-Risotto

**Nur als Alternative angesagt:** Fleischsuppe, Nudelsalat, Reissalat

### Hauptspeise – Top 20

| # | Gericht | gesamt | Anteil | 2024 | 2025 | 2026 | zuletzt |
|---|---|---|---|---|---|---|---|
| 1 | Hühnerbrust | 33 | 7,2 % | 2 | 16 | 15 | 2026-11-19 |
| 2 | Champignonschnitzel | 29 | 6,3 % | 2 | 16 | 11 | 2026-10-26 |
| 3 | Truthahngeschnetzeltes | 28 | 6,1 % | 2 | 13 | 13 | 2026-11-16 |
| 4 | Truthahnschnitzel | 26 | 5,6 % | 2 | 16 | 8 | 2026-09-14 |
| 5 | Schweinsschopf | 25 | 5,4 % | 3 | 11 | 11 | 2026-11-18 |
| 6 | Truthahnbraten | 25 | 5,4 % | 4 | 11 | 10 | 2026-11-11 |
| 7 | Wienerschnitzel | 24 | 5,2 % | 1 | 12 | 11 | 2026-11-17 |
| 8 | Schweinsfilet | 22 | 4,8 % | 2 | 12 | 8 | 2026-10-28 |
| 9 | Schweinsschnitzel | 22 | 4,8 % | 1 | 13 | 8 | 2026-11-09 |
| 10 | Leberkas | 20 | 4,3 % | 2 | 10 | 8 | 2026-10-27 |
| 11 | Chilli con carne | 18 | 3,9 % | 0 | 10 | 8 | 2026-11-02 |
| 12 | Hühnerhaxlen | 17 | 3,7 % | 2 | 7 | 8 | 2026-10-02 |
| 13 | Schweinskotelett | 17 | 3,7 % | 2 | 12 | 3 | 2026-06-10 |
| 14 | Hauswurst | 14 | 3,0 % | 1 | 7 | 6 | 2026-10-16 |
| 15 | Cordon Bleu | 13 | 2,8 % | 0 | 5 | 8 | 2026-11-05 |
| 16 | Zwiebelrostbraten | 13 | 2,8 % | 1 | 5 | 7 | 2026-11-13 |
| 17 | Schweinsgulasch | 11 | 2,4 % | 0 | 5 | 6 | 2026-10-09 |
| 18 | Zigeunerschnitzel | 11 | 2,4 % | 0 | 5 | 6 | 2026-11-03 |
| 19 | Currywurst | 9 | 1,9 % | 0 | 3 | 6 | 2026-11-10 |
| 20 | Ossobuchi | 7 | 1,5 % | 1 | 2 | 4 | 2026-10-15 |

**Selten (n ≤ 2, 17 Gerichte):** Forelle, Frittiertes Pangasiusfilet, Hamburger, Kalbsgulasch, Rotbarschfilet, Schweinsfilet mit Pfeffersoße, 1/2 Brathuhn, Frittiertes Schollenfilet, Hirschgulasch, Lammbraten, Pangasiusfilet, Pangasiusfilet mit Kräuterrahmsoße, Panierter Pangasius, Paprika-Schweinegulasch, Saures Rindfleisch, Spiegelei, Surfleisch

**Nur als Alternative angesagt:** Fleischkrapfln

### Beilage – Top 20

| # | Gericht | gesamt | Anteil | 2024 | 2025 | 2026 | zuletzt |
|---|---|---|---|---|---|---|---|
| 1 | Reis | 103 | 22,3 % | 7 | 54 | 42 | 2026-11-13 |
| 2 | Pommes | 60 | 13,0 % | 3 | 28 | 29 | 2026-11-10 |
| 3 | Spatzlen | 48 | 10,4 % | 6 | 18 | 24 | 2026-11-19 |
| 4 | Püree | 46 | 10,0 % | 2 | 22 | 22 | 2026-11-16 |
| 5 | Ofenkartoffeln | 38 | 8,2 % | 4 | 23 | 11 | 2026-10-02 |
| 6 | Kartoffelsalat | 37 | 8,0 % | 1 | 15 | 21 | 2026-11-17 |
| 7 | Kroketten | 26 | 5,6 % | 2 | 14 | 10 | 2026-11-11 |
| 8 | Kartoffelgratin | 24 | 5,2 % | 1 | 16 | 7 | 2026-11-04 |
| 9 | Plent | 21 | 4,6 % | 1 | 12 | 8 | 2026-11-12 |
| 10 | Röstkartoffeln | 14 | 3,0 % | 2 | 7 | 5 | 2026-06-25 |
| 11 | Salzkartoffeln | 11 | 2,4 % | 1 | 5 | 5 | 2026-09-04 |
| 12 | Kartoffelstampf | 9 | 1,9 % | 2 | 3 | 4 | 2026-09-30 |
| 13 | Wedges | 8 | 1,7 % | 0 | 0 | 8 | 2026-11-18 |
| 14 | Bratkartoffeln | 6 | 1,3 % | 0 | 1 | 5 | 2026-08-06 |
| 15 | Gulasch | 3 | 0,7 % | 0 | 3 | 0 | 2025-12-16 |
| 16 | Röstinchen | 3 | 0,7 % | 0 | 0 | 3 | 2026-10-29 |
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
| Vorspeise | 3 | 17,0 | 0 % | 2 % | 17 % | 61 % | 0 | 39,8 | < 0,001 | 5 AT |
| Hauptspeise | 2 | 19,0 | 1 % | 4 % | 19 % | 57 % | 0 | 39,1 | < 0,001 | 3 AT |
| Beilage | 1 | 8,0 | 6 % | 31 % | 63 % | 87 % | 18 | 103,2 | < 0,001 | 1 AT |

- **Vorspeise**: Die Küche **vermeidet** Wiederholungen innerhalb von 5 Arbeitstagen (6 gleiche Paare, Zufall 99,9); innerhalb von 10 Arbeitstagen 61 vs 196,6. Erste Wiederholung frühestens nach 3 AT.
- **Hauptspeise**: Die Küche **vermeidet** Wiederholungen innerhalb von 5 Arbeitstagen (15 gleiche Paare, Zufall 97,9); innerhalb von 10 Arbeitstagen 71 vs 192,2. Erste Wiederholung frühestens nach 2 AT.
- **Beilage**: Die Küche wiederholt **seltener** als Zufall innerhalb von 5 Arbeitstagen (140 gleiche Paare, Zufall 258,9); innerhalb von 10 Arbeitstagen 380 vs 509,1. Erste Wiederholung frühestens nach 1 AT.

### Refraktärkurve P(gleiches Gericht im Abstand L)

Basis = Σ p² (globale Anteile, wie in `stats.json`); Saison-Basis = Erwartung für zwei Tage derselben Saison.

| L (AT) | Vorspeise | Hauptspeise | Beilage |
|---|---|---|---|
| 1 | 0,0 % (0/452) | 0,0 % (0/455) | 2,0 % (9/455) |
| 2 | 0,0 % (0/449) | 0,4 % (2/452) | 3,5 % (16/452) |
| 3 | 0,2 % (1/446) | 0,7 % (3/449) | 6,9 % (31/449) |
| 4 | 0,5 % (2/443) | 1,1 % (5/446) | 8,7 % (39/446) |
| 5 | 0,7 % (3/441) | 1,1 % (5/443) | 10,2 % (45/443) |
| 6 | 1,4 % (6/438) | 1,8 % (8/440) | 8,9 % (39/440) |
| 7 | 3,0 % (13/435) | 1,1 % (5/437) | 11,9 % (52/437) |
| 8 | 2,3 % (10/432) | 2,3 % (10/434) | 10,6 % (46/434) |
| 9 | 3,3 % (14/429) | 2,6 % (11/431) | 11,1 % (48/431) |
| 10 | 2,8 % (12/426) | 5,1 % (22/428) | 12,9 % (55/428) |
| 11 | 2,6 % (11/424) | 2,8 % (12/426) | 11,0 % (47/426) |
| 12 | 6,0 % (25/420) | 4,0 % (17/422) | 9,5 % (40/422) |
| 13 | 6,0 % (25/417) | 3,6 % (15/419) | 8,4 % (35/419) |
| 14 | 4,8 % (20/414) | 4,3 % (18/416) | 12,3 % (51/416) |
| 15 | 4,4 % (18/411) | 5,6 % (23/413) | 13,1 % (54/413) |
| 16 | 3,9 % (16/408) | 2,4 % (10/410) | 11,2 % (46/410) |
| 17 | 3,7 % (15/405) | 3,2 % (13/407) | 13,3 % (54/407) |
| 18 | 4,5 % (18/402) | 4,7 % (19/404) | 8,4 % (34/404) |
| 19 | 2,5 % (10/399) | 4,5 % (18/401) | 11,0 % (44/401) |
| 20 | 6,1 % (24/396) | 7,8 % (31/398) | 12,3 % (49/398) |
| 21 | 2,8 % (11/393) | 3,3 % (13/395) | 13,7 % (54/395) |
| 22 | 3,8 % (15/390) | 4,8 % (19/392) | 12,2 % (48/392) |
| 23 | 3,1 % (12/387) | 3,3 % (13/389) | 11,8 % (46/389) |
| 24 | 2,6 % (10/384) | 4,9 % (19/386) | 11,7 % (45/386) |
| 25 | 5,5 % (21/381) | 4,2 % (16/383) | 13,3 % (51/383) |
| 26 | 4,2 % (16/378) | 3,2 % (12/380) | 10,0 % (38/380) |
| 27 | 3,5 % (13/375) | 2,7 % (10/377) | 11,4 % (43/377) |
| 28 | 5,9 % (22/372) | 5,1 % (19/374) | 11,0 % (41/374) |
| 29 | 4,9 % (18/369) | 5,7 % (21/371) | 12,7 % (47/371) |
| 30 | 6,5 % (24/367) | 3,8 % (14/368) | 14,1 % (52/368) |
| Basis Σp² | 4,2 % | 4,1 % | 11,1 % |
| Saison-Basis | 4,5 % | 4,3 % | 11,5 % |

**Auffällige Spitzen (Rate > 1,3 × Saison-Basis, p < 0,05; L=5 ≈ 1 Woche, L=20 ≈ 4 Wochen):**

- Vorspeise: L=30 → 6,5 % vs 4,5 % (24/367, p = 0,041)
- Hauptspeise: L=20 → 7,8 % vs 4,3 % (31/398, p = 0,001)

**Wochenrhythmus** – gleiche Speise bei Abständen L = 10, 15, 20, 25, 30 AT (meist gleicher Wochentag) vs. allen anderen Abständen 10–30 AT:

| Kategorie | L = 5·k | andere L | p |
|---|---|---|---|
| Vorspeise | 5,0 % (99/1981) | 4,1 % (257/6337) | 0,022 |
| Hauptspeise | 5,3 % (106/1990) | 3,9 % (248/6369) | < 0,001 |
| Beilage | 13,1 % (261/1990) | 11,2 % (713/6369) | 0,004 |

→ Der Wochentag-Effekt (Abschnitt 3) erzeugt einen schwachen Wochenrhythmus; die Refraktärzeit dominiert aber die ersten 1–2 Wochen.

### Abstände je Gericht – Vorspeise (n ≥ 8)

| Gericht | n | Mittel | Median | min | max | Wdh. gleiche Woche |
|---|---|---|---|---|---|---|
| Arrabbiata | 31 | 15,0 | 13,5 | 7 | 25 | 0 |
| Nudel mit Käsesoße | 31 | 14,3 | 14,0 | 5 | 30 | 0 |
| Hirten | 30 | 14,8 | 13,0 | 4 | 45 | 0 |
| Aglio olio | 29 | 16,0 | 14,0 | 6 | 41 | 0 |
| Nudel mit Ragu | 27 | 17,5 | 18,0 | 5 | 48 | 0 |
| Nudel mit Thunfischsoße | 26 | 16,9 | 14,0 | 6 | 41 | 0 |
| Nudel Mammarosa | 24 | 19,3 | 17,0 | 4 | 45 | 0 |
| Schlutzer | 24 | 17,8 | 14,0 | 3 | 41 | 0 |
| Lasagne | 22 | 19,4 | 17,0 | 8 | 48 | 0 |
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
| Champignonschnitzel | 29 | 14,7 | 13,5 | 3 | 34 | 0 |
| Truthahngeschnetzeltes | 28 | 16,8 | 16,0 | 8 | 34 | 0 |
| Truthahnschnitzel | 26 | 17,0 | 13,0 | 2 | 85 | 0 |
| Schweinsschopf | 25 | 19,3 | 16,0 | 4 | 73 | 0 |
| Truthahnbraten | 25 | 17,1 | 12,5 | 4 | 66 | 0 |
| Wienerschnitzel | 24 | 18,3 | 17,0 | 7 | 41 | 0 |
| Schweinsfilet | 22 | 18,3 | 15,0 | 4 | 44 | 0 |
| Schweinsschnitzel | 22 | 19,9 | 14,0 | 2 | 59 | 0 |
| Leberkas | 20 | 24,0 | 22,0 | 13 | 61 | 0 |
| Chilli con carne | 18 | 24,0 | 21,5 | 12 | 44 | 0 |
| Hühnerhaxlen | 17 | 28,0 | 24,5 | 7 | 76 | 0 |
| Schweinskotelett | 17 | 18,7 | 17,5 | 9 | 60 | 0 |
| Hauswurst | 14 | 34,6 | 27,0 | 17 | 87 | 0 |
| Cordon Bleu | 13 | 29,6 | 23,0 | 15 | 62 | 0 |
| Zwiebelrostbraten | 13 | 35,1 | 36,0 | 6 | 61 | 0 |
| Schweinsgulasch | 11 | 40,1 | 31,0 | 17 | 78 | 0 |
| Zigeunerschnitzel | 11 | 42,7 | 35,0 | 14 | 92 | 0 |
| Currywurst | 9 | 43,4 | 39,0 | 20 | 77 | 0 |

### Abstände je Gericht – Beilage

| Gericht | n | Mittel | Median | min | max | Wdh. gleiche Woche |
|---|---|---|---|---|---|---|
| Reis | 103 | 4,5 | 4,0 | 1 | 11 | 14 |
| Pommes | 60 | 7,6 | 6,0 | 1 | 25 | 3 |
| Spatzlen | 48 | 9,8 | 8,0 | 3 | 26 | 0 |
| Püree | 46 | 9,7 | 9,0 | 3 | 20 | 0 |
| Ofenkartoffeln | 38 | 10,9 | 9,0 | 2 | 45 | 1 |
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

Servierte Tage je Wochentag (Hauptspeise): Mo 89, Di 94, Mi 95, Do 95, Fr 88. Getestet wurden 305 Kombinationen (Gericht mit n ≥ 5 × Wochentag) mit einem einseitigen Binomialtest; bei so vielen Tests sind einzelne p < 0,05 auch zufällig zu erwarten (Bonferroni-Schwelle ≈ 0,0002).

### Gezielte Hypothesen

| Merkmal | n Tage | Mo | Di | Mi | Do | Fr | häufigster Tag | Anteil (erwartet) | p |
|---|---|---|---|---|---|---|---|---|---|
| Fisch (alle Fischgerichte) | 13 | 0 | 0 | 2 | 0 | 11 | Fr | 85 % (19 %) | < 0,001 |
| Fisch außerhalb Fastenzeit | 3 | 0 | 0 | 0 | 0 | 3 | Fr | 100 % (19 %) | 0,007 |
| Scombri | 3 | 0 | 0 | 1 | 0 | 2 | Fr | 67 % (19 %) | 0,095 |
| Plent | 21 | 0 | 0 | 5 | 6 | 10 | Fr | 48 % (19 %) | 0,003 |
| Leberkas | 20 | 3 | 2 | 6 | 5 | 4 | Mi | 30 % (21 %) | 0,216 |
| Hauswurst | 15 | 0 | 0 | 4 | 4 | 7 | Fr | 47 % (19 %) | 0,014 |

### Auffällige Wochentag-Vorlieben (Lift ≥ 1,5, mind. 3×, p < 0,05)

| Kategorie | Gericht | Tag | an diesem Tag | Anteil | erwartet | Lift | p | Bonferroni |
|---|---|---|---|---|---|---|---|---|
| Beilage | Reis | Mo | 44/103 | 43 % | 19 % | 2,21 | < 0,001 | ✔ |
| Hauptspeise | Schweinskotelett | Mi | 13/17 | 76 % | 21 % | 3,71 | < 0,001 | ✔ |
| Vorspeise | Arrabbiata | Mo | 17/31 | 55 % | 19 % | 2,83 | < 0,001 | ✔ |
| Hauptspeise | Champignonschnitzel | Mo | 16/29 | 55 % | 19 % | 2,86 | < 0,001 | ✔ |
| Vorspeise | Amatriciana | Mo | 11/19 | 58 % | 19 % | 2,99 | < 0,001 |  |
| Hauptspeise | Schweinsschnitzel | Mo | 12/22 | 55 % | 19 % | 2,83 | < 0,001 |  |
| Vorspeise | Spinatspatzlen | Di | 10/16 | 62 % | 20 % | 3,06 | < 0,001 |  |
| Beilage | Wedges | Mi | 6/8 | 75 % | 21 % | 3,64 | 0,001 |  |
| Beilage | Salzkartoffeln | Fr | 7/11 | 64 % | 19 % | 3,33 | 0,001 |  |
| Hauptspeise | Truthahnbraten | Di | 12/25 | 48 % | 20 % | 2,35 | 0,002 |  |
| Vorspeise | Nudel mit Lachs | Fr | 6/9 | 67 % | 19 % | 3,45 | 0,003 |  |
| Beilage | Plent | Fr | 10/21 | 48 % | 19 % | 2,49 | 0,003 |  |
| Vorspeise | Tortellini mit Schinken-Rahm | Di | 10/20 | 50 % | 20 % | 2,45 | 0,003 |  |
| Beilage | Spatzlen | Do | 18/48 | 38 % | 21 % | 1,82 | 0,005 |  |
| Hauptspeise | Ossobuchi | Do | 5/7 | 71 % | 21 % | 3,47 | 0,005 |  |
| Hauptspeise | Schweinsschnitzel mit Kräuterrahmsoße | Mo | 4/5 | 80 % | 19 % | 4,14 | 0,006 |  |
| Vorspeise | Lasagne | Di | 10/22 | 45 % | 20 % | 2,22 | 0,007 |  |
| Hauptspeise | Hühnerbrust | Di | 13/33 | 39 % | 20 % | 1,93 | 0,010 |  |
| Vorspeise | Nudel Mammarosa | Mo | 10/24 | 42 % | 19 % | 2,15 | 0,010 |  |
| Vorspeise | Nudel mit Ragu | Do | 11/27 | 41 % | 20 % | 2,02 | 0,012 |  |
| Beilage | Püree | Di | 16/46 | 35 % | 20 % | 1,71 | 0,017 |  |
| Hauptspeise | Truthahngeschnetzeltes | Di | 11/28 | 39 % | 20 % | 1,93 | 0,017 |  |
| Hauptspeise | Schweinsschopf | Mi | 10/25 | 40 % | 21 % | 1,94 | 0,021 |  |
| Hauptspeise | Currywurst | Di | 5/9 | 56 % | 20 % | 2,72 | 0,021 |  |
| Beilage | Ofenkartoffeln | Mo | 13/38 | 34 % | 19 % | 1,77 | 0,022 |  |

### Gerichte, die an einem Wochentag (fast) nie kommen (n ≥ 10, p < 0,05)

| Kategorie | Gericht | Tag | an diesem Tag | erwartet | p |
|---|---|---|---|---|---|
| Beilage | Plent | Di | 0/21 | 4,3 | 0,008 |
| Hauptspeise | Champignonschnitzel | Mi | 1/29 | 6,0 | 0,011 |
| Beilage | Plent | Mo | 0/21 | 4,1 | 0,011 |
| Vorspeise | Amatriciana | Mi | 0/19 | 3,9 | 0,012 |
| Vorspeise | Tortellini mit Schinken-Rahm | Mo | 0/20 | 3,9 | 0,014 |
| Hauptspeise | Champignonschnitzel | Fr | 1/29 | 5,5 | 0,017 |
| Hauptspeise | Schweinskotelett | Di | 0/17 | 3,5 | 0,021 |
| Vorspeise | Nudel mit Pesto | Mo | 0/17 | 3,3 | 0,026 |
| Hauptspeise | Schweinskotelett | Mo | 0/17 | 3,3 | 0,026 |
| Hauptspeise | Schweinskotelett | Fr | 0/17 | 3,2 | 0,027 |
| Beilage | Kroketten | Mo | 1/26 | 5,0 | 0,027 |
| Vorspeise | Arrabbiata | Mi | 2/31 | 6,4 | 0,031 |
| Vorspeise | Spinatspatzlen | Mo | 0/16 | 3,1 | 0,032 |
| Hauptspeise | Truthahnbraten | Fr | 1/25 | 4,8 | 0,035 |
| Vorspeise | Nudel mit Käsesoße | Do | 2/31 | 6,3 | 0,035 |

### Vorspeise: Anzahl je Wochentag (Top 12)

| Gericht | Mo | Di | Mi | Do | Fr | max. Lift |
|---|---|---|---|---|---|---|
| Arrabbiata | 17 | 4 | 2 | 5 | 3 | 2,83 |
| Nudel mit Käsesoße | 8 | 4 | 9 | 2 | 8 | 1,41 |
| Hirten | 6 | 7 | 10 | 5 | 2 | 1,61 |
| Aglio olio | 8 | 3 | 5 | 7 | 6 | 1,43 |
| Nudel mit Ragu | 5 | 4 | 4 | 11 | 3 | 2,02 |
| Nudel mit Thunfischsoße | 7 | 3 | 5 | 4 | 7 | 1,39 |
| Nudel Mammarosa | 10 | 3 | 2 | 8 | 1 | 2,15 |
| Schlutzer | 3 | 7 | 6 | 5 | 3 | 1,43 |
| Lasagne | 2 | 10 | 2 | 7 | 1 | 2,22 |
| Tortellini mit Schinken-Rahm | 0 | 10 | 1 | 3 | 6 | 2,45 |
| Amatriciana | 11 | 1 | 0 | 6 | 1 | 2,99 |
| Nudel mit Pesto | 0 | 3 | 7 | 3 | 4 | 1,99 |

### Hauptspeise: Anzahl je Wochentag (Top 12)

| Gericht | Mo | Di | Mi | Do | Fr | max. Lift |
|---|---|---|---|---|---|---|
| Hühnerbrust | 3 | 13 | 4 | 10 | 3 | 1,93 |
| Champignonschnitzel | 16 | 8 | 1 | 3 | 1 | 2,86 |
| Truthahngeschnetzeltes | 5 | 11 | 4 | 5 | 3 | 1,93 |
| Truthahnschnitzel | 8 | 3 | 2 | 6 | 7 | 1,59 |
| Schweinsschopf | 4 | 5 | 10 | 3 | 3 | 1,94 |
| Truthahnbraten | 5 | 12 | 4 | 3 | 1 | 2,35 |
| Wienerschnitzel | 5 | 3 | 7 | 7 | 2 | 1,42 |
| Schweinsfilet | 5 | 2 | 3 | 6 | 6 | 1,43 |
| Schweinsschnitzel | 12 | 4 | 2 | 1 | 3 | 2,83 |
| Leberkas | 3 | 2 | 6 | 5 | 4 | 1,46 |
| Chilli con carne | 3 | 3 | 5 | 4 | 3 | 1,35 |
| Hühnerhaxlen | 1 | 5 | 2 | 5 | 4 | 1,44 |

### Beilage: Anzahl je Wochentag (Top 12)

| Gericht | Mo | Di | Mi | Do | Fr | max. Lift |
|---|---|---|---|---|---|---|
| Reis | 44 | 21 | 14 | 10 | 14 | 2,21 |
| Pommes | 7 | 16 | 13 | 11 | 13 | 1,31 |
| Spatzlen | 7 | 8 | 9 | 18 | 6 | 1,82 |
| Püree | 5 | 16 | 12 | 8 | 5 | 1,71 |
| Ofenkartoffeln | 13 | 8 | 4 | 8 | 5 | 1,77 |
| Kartoffelsalat | 5 | 4 | 12 | 9 | 7 | 1,57 |
| Kroketten | 1 | 7 | 4 | 5 | 9 | 1,81 |
| Kartoffelgratin | 2 | 5 | 7 | 8 | 2 | 1,62 |
| Plent | 0 | 0 | 5 | 6 | 10 | 2,50 |
| Röstkartoffeln | 2 | 0 | 3 | 5 | 4 | 1,73 |
| Salzkartoffeln | 0 | 1 | 0 | 3 | 7 | 3,33 |
| Kartoffelstampf | 2 | 4 | 3 | 0 | 0 | 2,18 |

## 4. Kombinationen

### Beilage | Hauptspeise (Hauptspeisen mit n ≥ 3)

Wer die Hauptspeise kennt (bzw. richtig schätzt), sollte die dazu typische Beilage tippen: Treffer 50 % (Leave-one-out) statt 22 % mit der global häufigsten Beilage (Reis).

| Hauptspeise | n | Beilage 1 | Beilage 2 | Beilage 3 |
|---|---|---|---|---|
| Hühnerbrust | 33 | Kroketten 33 % (11) | Spatzlen 24 % (8) | Kartoffelgratin 12 % (4) |
| Champignonschnitzel | 29 | Reis 76 % (22) | Kartoffelgratin 17 % (5) | Püree 3 % (1) |
| Truthahngeschnetzeltes | 28 | Püree 46 % (13) | Reis 32 % (9) | Spatzlen 18 % (5) |
| Truthahnschnitzel | 26 | Ofenkartoffeln 42 % (11) | Pommes 38 % (10) | Kroketten 8 % (2) |
| Schweinsschopf | 25 | Pommes 24 % (6) | Reis 16 % (4) | Wedges 16 % (4) |
| Truthahnbraten | 25 | Püree 28 % (7) | Reis 20 % (5) | Spatzlen 20 % (5) |
| Wienerschnitzel | 24 | Kartoffelsalat 83 % (20) | Pommes 17 % (4) |  |
| Schweinsfilet | 22 | Spatzlen 32 % (7) | Kroketten 27 % (6) | Reis 23 % (5) |
| Schweinsschnitzel | 22 | Ofenkartoffeln 36 % (8) | Reis 27 % (6) | Pommes 9 % (2) |
| Leberkas | 20 | Röstkartoffeln 60 % (12) | Pommes 40 % (8) |  |
| Chilli con carne | 18 | Reis 100 % (18) |  |  |
| Hühnerhaxlen | 17 | Pommes 71 % (12) | Ofenkartoffeln 24 % (4) | Wedges 6 % (1) |
| Schweinskotelett | 17 | Kartoffelgratin 35 % (6) | Spatzlen 24 % (4) | Ofenkartoffeln 18 % (3) |
| Hauswurst | 14 | Plent 100 % (14) |  |  |
| Cordon Bleu | 13 | Kartoffelsalat 100 % (13) |  |  |
| Zwiebelrostbraten | 13 | Reis 54 % (7) | Püree 38 % (5) | Kroketten 8 % (1) |
| Schweinsgulasch | 11 | Püree 36 % (4) | Reis 36 % (4) | Spatzlen 18 % (2) |
| Zigeunerschnitzel | 11 | Reis 45 % (5) | Spatzlen 36 % (4) | Kartoffelstampf 9 % (1) |
| Currywurst | 9 | Pommes 100 % (9) |  |  |
| Ossobuchi | 7 | Spatzlen 57 % (4) | Reis 29 % (2) | Safranreis 14 % (1) |
| Sparerips | 7 | Pommes 71 % (5) | Röstinchen 14 % (1) | Wedges 14 % (1) |
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
| V–H | 1,668 | 1,635 | 0,173 |
| H–B | 2,092 | 0,830 | 0,003 |
| V–B | 0,902 | 0,887 | 0,316 |

| Vorspeise | Hauptspeise | zusammen | n(V) | n(H) | Lift | p |
|---|---|---|---|---|---|---|
| Nudel mit Thunfischsoße | Sparerips | 3 | 26 | 7 | 7,57 | 0,007 |
| Lasagne | Truthahngeschnetzeltes | 5 | 21 | 28 | 3,90 | 0,008 |
| Gnocchi mit Tomatensoße | Zwiebelrostbraten | 3 | 15 | 13 | 7,06 | 0,008 |
| Carbonara | Schweinsfilet | 3 | 10 | 22 | 6,26 | 0,010 |
| Nudel mit Lachs | Truthahnschnitzel | 3 | 9 | 26 | 5,88 | 0,012 |
| Nudel mit Thunfischsoße | Chilli con carne | 4 | 26 | 18 | 3,92 | 0,018 |
| Spinatspatzlen | Hühnerhaxlen | 3 | 16 | 17 | 5,06 | 0,020 |
| Tortellini mit Schinken-Rahm | Schweinsschopf | 4 | 20 | 25 | 3,67 | 0,021 |
| Spinatspatzlen | Chilli con carne | 3 | 16 | 18 | 4,78 | 0,023 |
| Arrabbiata | Champignonschnitzel | 5 | 31 | 29 | 2,55 | 0,043 |
| Tortellini mit Schinken-Rahm | Hühnerbrust | 4 | 20 | 33 | 2,78 | 0,051 |
| Nudel mit Ragu | Truthahnbraten | 4 | 27 | 25 | 2,72 | 0,057 |
| Arrabbiata | Schweinsfilet | 4 | 31 | 22 | 2,69 | 0,059 |
| Amatriciana | Schweinsschnitzel | 3 | 19 | 22 | 3,29 | 0,060 |
| Hirten | Hühnerbrust | 5 | 30 | 33 | 2,32 | 0,061 |
| Nudel mit Käsesoße | Wienerschnitzel | 4 | 31 | 23 | 2,58 | 0,068 |
| Hirten | Schweinskotelett | 3 | 30 | 17 | 2,70 | 0,098 |
| Aglio olio | Champignonschnitzel | 4 | 29 | 29 | 2,18 | 0,108 |
| Lasagne | Truthahnschnitzel | 3 | 21 | 26 | 2,52 | 0,113 |
| Nudel mit Thunfischsoße | Schweinsschnitzel | 3 | 26 | 22 | 2,41 | 0,126 |
| Arrabbiata | Leberkas | 3 | 31 | 19 | 2,34 | 0,136 |
| Nudel mit Ragu | Wienerschnitzel | 3 | 27 | 23 | 2,22 | 0,151 |
| Nudel mit Käsesoße | Schweinsschnitzel | 3 | 31 | 22 | 2,02 | 0,184 |
| Hirten | Truthahnbraten | 3 | 30 | 25 | 1,84 | 0,223 |
| Hirten | Truthahnschnitzel | 3 | 30 | 26 | 1,77 | 0,240 |

## 5. Saisonalität

### Fastenzeit (Aschermittwoch – Ostersonntag)

Fastenzeiten in den Daten: 2025: 05.03.–20.04., 2026: 18.02.–05.04.. Fisch = jede Hauptspeise, die als Fisch gilt (inkl. Scombri).

**Hauptspeise** (Fastentage n=64, sonst n=397; Gerichte mit ≥ 2 Fastentagen):

| Gericht | Fastenzeit | sonst | Lift | p |
|---|---|---|---|---|
| Scombri | 4,7 % (3) | 0,0 % (0) | nur Fastenzeit | 0,003 |
| Fisch | 15,6 % (10) | 0,8 % (3) | 20,68 | < 0,001 |
| Truthahnbraten | 9,4 % (6) | 4,8 % (19) | 1,96 | 0,123 |
| Currywurst | 3,1 % (2) | 1,8 % (7) | 1,77 | 0,362 |
| Schweinsfilet | 6,2 % (4) | 4,5 % (18) | 1,38 | 0,365 |
| Zigeunerschnitzel | 3,1 % (2) | 2,3 % (9) | 1,38 | 0,464 |
| Schweinskotelett | 4,7 % (3) | 3,5 % (14) | 1,33 | 0,427 |
| Chilli con carne | 4,7 % (3) | 3,8 % (15) | 1,24 | 0,465 |
| Zwiebelrostbraten | 3,1 % (2) | 2,8 % (11) | 1,13 | 0,556 |
| Champignonschnitzel | 6,2 % (4) | 6,3 % (25) | 0,99 | 0,587 |
| Wienerschnitzel | 4,7 % (3) | 5,3 % (21) | 0,89 | 0,667 |
| Truthahnschnitzel | 4,7 % (3) | 5,8 % (23) | 0,81 | 0,720 |

**Vorspeise** (Fastentage n=64, sonst n=396; Gerichte mit ≥ 2 Fastentagen):

| Gericht | Fastenzeit | sonst | Lift | p |
|---|---|---|---|---|
| Nudel mit Lachs | 3,1 % (2) | 1,8 % (7) | 1,77 | 0,363 |
| Amatriciana | 6,2 % (4) | 3,8 % (15) | 1,65 | 0,267 |
| Spinatspatzlen | 4,7 % (3) | 3,3 % (13) | 1,43 | 0,389 |
| Nudel mit Ragu | 7,8 % (5) | 5,6 % (22) | 1,41 | 0,320 |
| Pizzastrudel | 3,1 % (2) | 2,3 % (9) | 1,38 | 0,465 |
| Spinatcannelloni | 3,1 % (2) | 2,3 % (9) | 1,38 | 0,465 |
| Schlutzer | 6,2 % (4) | 5,1 % (20) | 1,24 | 0,434 |
| Nudel mit Käsesoße | 7,8 % (5) | 6,6 % (26) | 1,19 | 0,436 |
| Aglio olio | 6,2 % (4) | 6,3 % (25) | 0,99 | 0,588 |
| Lasagne | 4,7 % (3) | 4,8 % (19) | 0,98 | 0,608 |
| Gnocchi mit Tomatensoße | 3,1 % (2) | 3,3 % (13) | 0,95 | 0,638 |
| Arrabbiata | 6,2 % (4) | 6,8 % (27) | 0,92 | 0,643 |

**Beilage** (Fastentage n=64, sonst n=397; Gerichte mit ≥ 2 Fastentagen):

| Gericht | Fastenzeit | sonst | Lift | p |
|---|---|---|---|---|
| Salzkartoffeln | 4,7 % (3) | 2,0 % (8) | 2,33 | 0,188 |
| Kartoffelgratin | 9,4 % (6) | 4,5 % (18) | 2,07 | 0,105 |
| Plent | 7,8 % (5) | 4,0 % (16) | 1,94 | 0,157 |
| Röstkartoffeln | 4,7 % (3) | 2,8 % (11) | 1,69 | 0,306 |
| Kartoffelsalat | 10,9 % (7) | 7,6 % (30) | 1,45 | 0,248 |
| Püree | 12,5 % (8) | 9,6 % (38) | 1,31 | 0,303 |
| Kroketten | 6,2 % (4) | 5,5 % (22) | 1,13 | 0,496 |
| Reis | 20,3 % (13) | 22,7 % (90) | 0,90 | 0,687 |
| Spatzlen | 9,4 % (6) | 10,6 % (42) | 0,89 | 0,672 |
| Pommes | 7,8 % (5) | 13,9 % (55) | 0,56 | 0,933 |
| Ofenkartoffeln | 3,1 % (2) | 9,1 % (36) | 0,34 | 0,976 |

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

**Vorspeise** (Tage je Monat: Jan 30, Feb 40, Mär 42, Apr 34, Mai 39, Jun 39, Jul 45, Aug 22, Sep 43, Okt 49, Nov 49, Dez 28)

| Gericht | Jan | Feb | Mär | Apr | Mai | Jun | Jul | Aug | Sep | Okt | Nov | Dez |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Arrabbiata | 10 | 8 | 5 | 6 | 5 | 8 | 7 | 9 | 7 | 4 | 6 | 11 |
| Nudel mit Käsesoße | 7 | 8 | 7 | 3 | 10 | 10 | 4 | 5 | 7 | 10 | 4 | 4 |
| Hirten | · | 8 | 7 | 3 | 8 | 8 | 7 | 14 | 9 | 6 | 4 | 7 |
| Aglio olio | 10 | · | 7 | 6 | 5 | 5 | 4 | 14 | 5 | 8 | 8 | 7 |
| Nudel mit Ragu | 7 | 8 | 5 | 9 | 5 | 3 | 9 | · | 7 | 6 | 6 | 4 |
| Nudel mit Thunfischsoße | 7 | 10 | 2 | 6 | 5 | 5 | 4 | 9 | 2 | 8 | 6 | 4 |
| Nudel Mammarosa | 3 | 5 | 5 | 3 | 3 | 8 | 4 | 5 | 7 | 4 | 6 | 11 |
| Schlutzer | 7 | 2 | 7 | 3 | 8 | 3 | 9 | 5 | 5 | 6 | 2 | 7 |
| Lasagne | 3 | · | 5 | 6 | 8 | 5 | 7 | · | 5 | 8 | 4 | 4 |
| Tortellini mit Schinken-Rahm | 3 | 2 | 2 | 6 | 10 | 5 | 4 | 5 | 2 | 6 | 4 | · |

**Hauptspeise** (Tage je Monat: Jan 30, Feb 40, Mär 42, Apr 34, Mai 39, Jun 39, Jul 45, Aug 22, Sep 44, Okt 49, Nov 49, Dez 28)

| Gericht | Jan | Feb | Mär | Apr | Mai | Jun | Jul | Aug | Sep | Okt | Nov | Dez |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Hühnerbrust | 10 | 5 | 10 | 3 | 10 | 8 | 7 | · | 9 | 6 | 8 | 7 |
| Champignonschnitzel | 3 | 8 | 5 | 9 | 8 | 5 | 4 | 9 | 7 | 8 | 2 | 11 |
| Truthahngeschnetzeltes | 7 | 8 | 5 | 3 | 10 | 5 | 4 | 5 | 5 | 6 | 6 | 11 |
| Truthahnschnitzel | 7 | 2 | 5 | 3 | 8 | 18 | 7 | 5 | 5 | 2 | 2 | 7 |
| Schweinsschopf | 7 | 8 | 2 | 6 | 3 | · | 9 | 9 | 5 | 6 | 6 | 7 |
| Truthahnbraten | · | 5 | 10 | 9 | · | · | 4 | 14 | 7 | 6 | 8 | 4 |
| Wienerschnitzel | · | 10 | 2 | 3 | 5 | 3 | 9 | 5 | 9 | 6 | 4 | 4 |
| Schweinsfilet | 3 | 5 | 5 | 9 | 8 | 3 | 4 | · | 5 | 4 | 6 | 4 |
| Schweinsschnitzel | 3 | 5 | 2 | 3 | 3 | 8 | 9 | 9 | 2 | 4 | 6 | 4 |
| Leberkas | 7 | · | 2 | 6 | 5 | 5 | 4 | 5 | 5 | 6 | 4 | 4 |

**Beilage** (Tage je Monat: Jan 30, Feb 40, Mär 42, Apr 34, Mai 39, Jun 39, Jul 45, Aug 22, Sep 44, Okt 49, Nov 49, Dez 28)

| Gericht | Jan | Feb | Mär | Apr | Mai | Jun | Jul | Aug | Sep | Okt | Nov | Dez |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Reis | 23 | 22 | 24 | 21 | 18 | 18 | 24 | 27 | 20 | 27 | 20 | 25 |
| Pommes | 13 | 12 | 10 | 12 | 13 | 15 | 18 | 18 | 11 | 16 | 6 | 14 |
| Spatzlen | 10 | 8 | 10 | 12 | 13 | 5 | 9 | 14 | 11 | 10 | 12 | 14 |
| Püree | 10 | 12 | 12 | 12 | 18 | 8 | 7 | 14 | 7 | 8 | 10 | 4 |
| Ofenkartoffeln | 3 | 8 | 2 | 6 | 5 | 13 | 13 | 9 | 14 | 8 | 8 | 7 |
| Kartoffelsalat | 3 | 10 | 5 | 9 | 8 | 13 | 9 | 5 | 9 | 8 | 8 | 7 |
| Kroketten | 7 | 8 | 7 | 6 | 3 | 8 | 2 | 5 | 7 | 6 | 8 | · |
| Kartoffelgratin | 3 | 8 | 10 | 6 | 8 | 5 | 4 | · | 2 | 4 | 6 | 4 |
| Plent | 7 | 2 | 7 | 6 | 3 | 3 | 4 | · | 5 | 4 | 6 | 7 |
| Röstkartoffeln | 3 | 2 | 2 | 6 | 3 | 8 | 2 | · | 2 | 2 | 2 | 4 |

### Weihnachtszeit (1.–23. Dezember)

- **Vorspeise** (Dezembertage n=28): Fleischcannelloni 2× (7 % vs 0 % sonst, p = 0,011); Nudel Mammarosa 3× (11 % vs 5 % sonst, p = 0,177); Arrabbiata 3× (11 % vs 6 % sonst, p = 0,292)
- **Hauptspeise** (Dezembertage n=28): Zwiebelrostbraten 2× (7 % vs 3 % sonst, p = 0,185); Hauswurst 2× (7 % vs 3 % sonst, p = 0,208); Hühnerhaxlen 2× (7 % vs 3 % sonst, p = 0,276); Truthahngeschnetzeltes 3× (11 % vs 6 % sonst, p = 0,240); Champignonschnitzel 3× (11 % vs 6 % sonst, p = 0,257)
- **Beilage** (Dezembertage n=28): Kartoffelstampf 2× (7 % vs 2 % sonst, p = 0,100); Plent 2× (7 % vs 4 % sonst, p = 0,367)
- Letztes Menü vor Weihnachten 2024 (19.12.): Lasagne / Truthahngeschnetzeltes / Spatzlen
- Letztes Menü vor Weihnachten 2025 (19.12.): Nudel Mammarosa / Cordon Bleu / Kartoffelsalat

## 6. Trends (2026 vs. 2024, 2025)

- **Vorspeise neu 2026** (11): Gnocchi mit Gorgonzolasoße (2×), Spinatknödel mit Käsesoße (2×), Gnocchi mit Kräutersauce (1×), Gnocchi mit Lachs (1×), Käse-Sofficini mit Tomantensoße (1×), Nudel mit Schinken-Rahm (1×), Pilzrisotto (1×), Spargelrisotto (1×), Speck-Zwiebel-Kuchen (1×), Tomatenrisotto (1×), Truthahn-Gemüse-Risotto (1×)
- **Vorspeise verschwunden 2026** (25): Fleischcannelloni (3×), Ravioli mit Parmesan-Butter (3×), Tomatenrisotto mit Mozzarella (3×), Gnocchi mit Käsesoße (2×), Gulaschsuppe (2×), Nudelsalat (2×), Omelett mit Schinken und Käse (2×), Plentauflauf (2×), Ravioli (2×), Fleischsuppe (1×), Gemüselasagne (1×), Gnocchi (1×), Gnocchi mit Ragu (1×), Kürbisrisotto (1×), Nudel mit Lachs und Tomantensoße (1×), Nudel mit Tomatensoße (1×), Nudel mit Tomatensoße und Schinken (1×), Putanesca (1×), Ravioli mit Käsesoße (1×), Ravioli mit Tomantensoße (1×), Reissalat (1×), Schlutzer Schinken-Rahm (1×), Schupfnudel mit Lachs (1×), Schüttelbrot-Risotto mit Speckstreifen (1×), Spinatknödel mit Gorgonzolasoße (1×)
- **Hauptspeise neu 2026** (14): Vitello tonnato (3×), Forelle (2×), Frittiertes Pangasiusfilet (2×), Hamburger (2×), Kalbsgulasch (2×), Schweinsfilet mit Pfeffersoße (2×), 1/2 Brathuhn (1×), Fleischkrapfln (1×), Hirschgulasch (1×), Lammbraten (1×), Pangasiusfilet mit Kräuterrahmsoße (1×), Panierter Pangasius (1×), Spiegelei (1×), Surfleisch (1×)
- **Hauptspeise verschwunden 2026** (7): Pizzaiolaschnitzel (5×), Knödel (3×), Rotbarschfilet (2×), Frittiertes Schollenfilet (1×), Pangasiusfilet (1×), Paprika-Schweinegulasch (1×), Saures Rindfleisch (1×)
- **Beilage neu 2026** (4): Wedges (8×), Röstinchen (3×), Kartoffel-Käse-Kroketten (1×), Knödel (1×)
- **Beilage verschwunden 2026** (3): Gulasch (3×), Safranreis (1×), Zucchini (1×)

**Aufsteiger / Absteiger** (Anteil 2025 → 2026, Gerichte mit n ≥ 5):

| Kategorie | Gericht |  | 2025 | 2026 |
|---|---|---|---|---|
| Vorspeise | Tortellini mit Schinken-Rahm | ↑ | 3,6 % | 5,8 % |
| Vorspeise | Gnocchi mit Tomatensoße | ↑ | 2,7 % | 4,3 % |
| Vorspeise | Hirten | ↑ | 5,9 % | 7,2 % |
| Vorspeise | Lasagne | ↑ | 4,1 % | 5,3 % |
| Vorspeise | Nudel mit Pesto | ↑ | 3,2 % | 4,3 % |
| Vorspeise | Spinatspatzlen | ↓ | 4,5 % | 2,4 % |
| Vorspeise | Nudel mit Ragu | ↓ | 6,4 % | 4,8 % |
| Vorspeise | Nudel mit Thunfischsoße | ↓ | 6,4 % | 4,8 % |
| Vorspeise | Arrabbiata | ↓ | 7,3 % | 6,3 % |
| Vorspeise | Amatriciana | ↓ | 4,5 % | 3,9 % |
| Hauptspeise | Sparerips | ↑ | 0,5 % | 2,4 % |
| Hauptspeise | Cordon Bleu | ↑ | 2,3 % | 3,9 % |
| Hauptspeise | Currywurst | ↑ | 1,4 % | 2,9 % |
| Hauptspeise | Zwiebelrostbraten | ↑ | 2,3 % | 3,4 % |
| Hauptspeise | Ossobuchi | ↑ | 0,9 % | 1,9 % |
| Hauptspeise | Schweinskotelett | ↓ | 5,4 % | 1,4 % |
| Hauptspeise | Truthahnschnitzel | ↓ | 7,2 % | 3,9 % |
| Hauptspeise | Schweinsschnitzel | ↓ | 5,9 % | 3,9 % |
| Hauptspeise | Champignonschnitzel | ↓ | 7,2 % | 5,3 % |
| Hauptspeise | Pizzaiolaschnitzel | ↓ | 1,8 % | 0,0 % |
| Beilage | Wedges | ↑ | 0,0 % | 3,9 % |
| Beilage | Spatzlen | ↑ | 8,1 % | 11,6 % |
| Beilage | Kartoffelsalat | ↑ | 6,8 % | 10,1 % |
| Beilage | Bratkartoffeln | ↑ | 0,5 % | 2,4 % |
| Beilage | Pommes | ↑ | 12,7 % | 14,0 % |
| Beilage | Ofenkartoffeln | ↓ | 10,4 % | 5,3 % |
| Beilage | Reis | ↓ | 24,4 % | 20,3 % |
| Beilage | Kartoffelgratin | ↓ | 7,2 % | 3,4 % |
| Beilage | Plent | ↓ | 5,4 % | 3,9 % |
| Beilage | Kroketten | ↓ | 6,3 % | 4,8 % |

### Gewichtung nach Aktualität

Mittlerer Log-Loss einer reinen Häufigkeitsprognose für jeden Tag 2026 (nur Vergangenheit, Gewicht 0,5^(Alter/Halbwertszeit), Glättung 0,5; kleiner = besser). Zeigt, ob jüngere Menüs mehr zählen sollten (Refraktärzeit und Wochentag sind hier bewusst nicht enthalten).

| Kategorie | 30 T | 60 T | 90 T | 180 T | 365 T | ∞ (ungewichtet) |
|---|---|---|---|---|---|---|
| Vorspeise | 3,773 | 3,621 | 3,561 | 3,514 | 3,508 | 3,524 |
| Hauptspeise | 3,766 | 3,679 | 3,647 | 3,628 | 3,633 | 3,655 |
| Beilage | 2,641 | 2,580 | 2,564 | 2,561 | 2,571 | 2,592 |

Aktualitätsgewichtung: beste Halbwertszeit (Log-Loss, Tage) – Vorspeise 365, Hauptspeise 180, Beilage 180.

### Anteile je Jahr (Top-Gerichte)

**Vorspeise**

| Gericht | 2024 | 2025 | 2026 |
|---|---|---|---|
| Arrabbiata | 6,1 % | 7,3 % | 6,3 % |
| Nudel mit Käsesoße | 3,0 % | 6,8 % | 7,2 % |
| Hirten | 6,1 % | 5,9 % | 7,2 % |
| Aglio olio | 3,0 % | 6,8 % | 6,3 % |
| Nudel mit Ragu | 9,1 % | 6,4 % | 4,8 % |
| Nudel mit Thunfischsoße | 6,1 % | 6,4 % | 4,8 % |
| Nudel Mammarosa | 6,1 % | 5,0 % | 5,3 % |
| Schlutzer | 3,0 % | 5,5 % | 5,3 % |
| Lasagne | 6,1 % | 4,1 % | 5,3 % |
| Tortellini mit Schinken-Rahm | 0,0 % | 3,6 % | 5,8 % |
| Amatriciana | 3,0 % | 4,5 % | 3,9 % |
| Nudel mit Pesto | 3,0 % | 3,2 % | 4,3 % |
| Spinatspatzlen | 3,0 % | 4,5 % | 2,4 % |
| Gnocchi mit Tomatensoße | 0,0 % | 2,7 % | 4,3 % |
| Käseknödel | 6,1 % | 1,8 % | 2,4 % |

**Hauptspeise**

| Gericht | 2024 | 2025 | 2026 |
|---|---|---|---|
| Hühnerbrust | 6,1 % | 7,2 % | 7,2 % |
| Champignonschnitzel | 6,1 % | 7,2 % | 5,3 % |
| Truthahngeschnetzeltes | 6,1 % | 5,9 % | 6,3 % |
| Truthahnschnitzel | 6,1 % | 7,2 % | 3,9 % |
| Schweinsschopf | 9,1 % | 5,0 % | 5,3 % |
| Truthahnbraten | 12,1 % | 5,0 % | 4,8 % |
| Wienerschnitzel | 3,0 % | 5,4 % | 5,3 % |
| Schweinsfilet | 6,1 % | 5,4 % | 3,9 % |
| Schweinsschnitzel | 3,0 % | 5,9 % | 3,9 % |
| Leberkas | 6,1 % | 4,5 % | 3,9 % |
| Chilli con carne | 0,0 % | 4,5 % | 3,9 % |
| Hühnerhaxlen | 6,1 % | 3,2 % | 3,9 % |
| Schweinskotelett | 6,1 % | 5,4 % | 1,5 % |
| Hauswurst | 3,0 % | 3,2 % | 2,9 % |
| Cordon Bleu | 0,0 % | 2,3 % | 3,9 % |

**Beilage**

| Gericht | 2024 | 2025 | 2026 |
|---|---|---|---|
| Reis | 21,2 % | 24,4 % | 20,3 % |
| Pommes | 9,1 % | 12,7 % | 14,0 % |
| Spatzlen | 18,2 % | 8,1 % | 11,6 % |
| Püree | 6,1 % | 10,0 % | 10,6 % |
| Ofenkartoffeln | 12,1 % | 10,4 % | 5,3 % |
| Kartoffelsalat | 3,0 % | 6,8 % | 10,1 % |
| Kroketten | 6,1 % | 6,3 % | 4,8 % |
| Kartoffelgratin | 3,0 % | 7,2 % | 3,4 % |
| Plent | 3,0 % | 5,4 % | 3,9 % |
| Röstkartoffeln | 6,1 % | 3,2 % | 2,4 % |
| Salzkartoffeln | 3,0 % | 2,3 % | 2,4 % |
| Kartoffelstampf | 6,1 % | 1,4 % | 1,9 % |
| Wedges | 0,0 % | 0,0 % | 3,9 % |
| Bratkartoffeln | 0,0 % | 0,4 % | 2,4 % |
| Gulasch | 0,0 % | 1,4 % | 0,0 % |

## 7. Spieler

Punkte = Neuberechnung der Engine (`tips.points`; identisch mit dem Excel bis auf dokumentierte manuelle Korrekturen). Nur servierte Tage vor dem Stichtag. „Alles falsch“ = 0 Punkte, „Alles richtig“ = 3 Punkte.

| Jahr | Spieler | Tage | Punkte | P./Tag | Alles falsch | Alles richtig | V | H | B | R4-Verstöße | Abw. Excel |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026 | Johannes | 190 | 53,0 | 0,279 | 119 (63 %) | 1 | 8 % | 11 % | 28 % | 5 | 0 |
| 2026 | Andreas | 197 | 54,5 | 0,277 | 127 (64 %) | 0 | 11 % | 10 % | 24 % | 2 | 1 |
| 2026 | Johannes Paul III | 192 | 50,5 | 0,263 | 130 (68 %) | 2 | 9 % | 11 % | 23 % | 2 | 0 |
| 2026 | Noah | 200 | 49,5 | 0,247 | 138 (69 %) | 1 | 8 % | 9 % | 24 % | 3 | 0 |
| 2026 | Lorenz | 10 | 2,0 | 0,200 | 6 (60 %) | 0 | 0 % | 10 % | 30 % | 0 | 0 |
| 2025 | Noah | 213 | 51,5 | 0,242 | 151 (71 %) | 1 | 11 % | 8 % | 17 % | 0 | 0 |
| 2025 | Andreas | 214 | 47,5 | 0,222 | 153 (72 %) | 1 | 8 % | 8 % | 20 % | 3 | 1 |
| 2025 | Johannes | 209 | 39,0 | 0,187 | 158 (76 %) | 1 | 8 % | 4 % | 16 % | 0 | 2 |
| 2024 | Johannes | 27 | 6,0 | 0,222 | 20 (74 %) | 0 | 15 % | 8 % | 8 % | 0 | 0 |
| 2024 | Andreas | 34 | 6,5 | 0,191 | 29 (85 %) | 1 | 9 % | 6 % | 9 % | 0 | 0 |
| 2024 | Noah | 29 | 3,0 | 0,103 | 24 (83 %) | 0 | 0 % | 7 % | 14 % | 0 | 0 |

### Lieblingstipps

| Jahr | Spieler | Vorspeise | Hauptspeise | Beilage |
|---|---|---|---|---|
| 2026 | Johannes | Amatriciana 25, Carbonara 22, Hirten 20 | Wienerschnitzel 31, Champignonschnitzel 25, Hühnerhaxlen 20 | Pommes 49, Reis 44, Kartoffelsalat 20 |
| 2026 | Andreas | Nudel mit Käsesoße 22, Lasagne 18, Spinatspatzlen 18 | Wienerschnitzel 28, Champignonschnitzel 23, Currywurst 19 | Pommes 53, Reis 37, Kartoffelsalat 26 |
| 2026 | Johannes Paul III | Hirten 20, Amatriciana 17, Lasagne 16 | Wienerschnitzel 20, Champignonschnitzel 19, Hühnerbrust 18 | Reis 49, Pommes 25, Kartoffelsalat 24 |
| 2026 | Noah | Amatriciana 36, Carbonara 22, Aglio olio 21 | Truthahngeschnetzeltes 40, Champignonschnitzel 37, Hühnerbrust 17 | Reis 47, Püree 43, Kartoffelgratin 25 |
| 2026 | Lorenz | Amatriciana 2, Aglio olio 1, Arrabbiata 1 | Wienerschnitzel 4, Truthahngeschnetzeltes 3, Gulasch 2 | Püree 3, Knödel 2, Pommes 2 |
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
| Vorspeise | 12,8 % (n=376) | 7,3 % (n=1081) |
| Hauptspeise | 10,2 % (n=489) | 7,7 % (n=969) |
| Beilage | 28,6 % (n=875) | 10,8 % (n=582) |

| Kategorie | 1–2 AT | 3–5 AT | 6–10 AT | 11–20 AT | 21–40 AT | > 40 AT | nie serviert |
|---|---|---|---|---|---|---|---|
| Vorspeise | 0,0 % (12) | 3,4 % (59) | 6,8 % (308) | 11,5 % (567) | 10,2 % (305) | 4,5 % (155) | 2,0 % (51) |
| Hauptspeise | 0,0 % (9) | 4,3 % (94) | 4,9 % (309) | 10,0 % (578) | 10,8 % (295) | 8,7 % (103) | 10,0 % (70) |
| Beilage | 25,8 % (89) | 28,4 % (483) | 20,1 % (378) | 17,9 % (319) | 14,7 % (116) | 4,9 % (61) | 0,0 % (11) |

- Vorspeise: Top-5-Tipps treffen 12,8 % vs 7,3 % (besser, Faktor 1,75).
- Hauptspeise: Top-5-Tipps treffen 10,2 % vs 7,7 % (besser, Faktor 1,32).
- Beilage: Top-5-Tipps treffen 28,6 % vs 10,8 % (besser, Faktor 2,64).

→ Tipps auf Gerichte, die erst vor 1–5 Arbeitstagen serviert wurden, treffen bei der Vorspeise nur 2,8 % (n=71) gegenüber 9,0 % sonst; Hauptspeise 3,9 % vs 8,9 %; Beilage 28,0 % vs 17,3 %.

### Strategie-Kennzahlen je Spieler und Jahr

Top-5-Anteil = Anteil der Tipps auf die 5 bis dahin häufigsten Gerichte; Vielfalt = mittlere Entropie der eigenen Tipps (bit); kürzlich = Anteil der Tipps auf Gerichte der letzten 5 Arbeitstage.

| Jahr | Spieler | P./Tag | Rang | Top-5-Anteil | Vielfalt | kürzlich |
|---|---|---|---|---|---|---|
| 2026 | Johannes | 0,279 | 1 | 39 % | 3,83 | 16 % |
| 2026 | Andreas | 0,277 | 2 | 40 % | 3,72 | 16 % |
| 2026 | Johannes Paul III | 0,263 | 3 | 44 % | 3,92 | 20 % |
| 2026 | Noah | 0,247 | 4 | 51 % | 3,51 | 18 % |
| 2026 | Lorenz | 0,200 | 5 | 53 % | 2,47 | 27 % |
| 2025 | Noah | 0,242 | 1 | 36 % | 3,80 | 16 % |
| 2025 | Andreas | 0,222 | 2 | 35 % | 3,91 | 15 % |
| 2025 | Johannes | 0,187 | 3 | 36 % | 3,89 | 19 % |
| 2024 | Johannes | 0,222 | 1 | 25 % | 3,19 | 11 % |
| 2024 | Andreas | 0,191 | 2 | 26 % | 3,46 | 7 % |
| 2024 | Noah | 0,103 | 3 | 30 % | 3,25 | 10 % |

Korrelation mit Punkten/Tag über 7 Spieler-Jahre mit ≥ 100 Tagen (sehr kleine Stichprobe, nur Hinweis): Top-5-Anteil r=0,39, Vielfalt r=-0,27, kürzlich r=-0,20, V-Trefferquote r=0,29. Die Vorspeise zählt doppelt so viel wie H oder B (1 vs 0,5 Punkte); über die Spieler-Jahre erklärt die V-Trefferquote die Rangfolge aber nur schwach.

### Notizen je Spieler

- **Johannes 2026**: 0,28 Punkte/Tag (Rang 1/5 in 2026). Top-5-Anteil der Tipps 39 %, Vielfalt 3,8 bit, 16 % Tipps auf Gerichte, die in den letzten 5 Arbeitstagen serviert wurden. Stärkste Kategorie: Beilage (28 % Treffer). Regel-4-Verstöße: 5.
- **Andreas 2026**: 0,28 Punkte/Tag (Rang 2/5 in 2026). Top-5-Anteil der Tipps 40 %, Vielfalt 3,7 bit, 16 % Tipps auf Gerichte, die in den letzten 5 Arbeitstagen serviert wurden. Stärkste Kategorie: Beilage (24 % Treffer). Regel-4-Verstöße: 2.
- **Johannes Paul III 2026**: 0,26 Punkte/Tag (Rang 3/5 in 2026). Top-5-Anteil der Tipps 44 %, Vielfalt 3,9 bit, 20 % Tipps auf Gerichte, die in den letzten 5 Arbeitstagen serviert wurden. Stärkste Kategorie: Beilage (23 % Treffer). Regel-4-Verstöße: 2.
- **Noah 2026**: 0,25 Punkte/Tag (Rang 4/5 in 2026). Top-5-Anteil der Tipps 51 %, Vielfalt 3,5 bit, 18 % Tipps auf Gerichte, die in den letzten 5 Arbeitstagen serviert wurden. Stärkste Kategorie: Beilage (24 % Treffer). Regel-4-Verstöße: 3.
- **Lorenz 2026**: 0,20 Punkte/Tag (Rang 5/5 in 2026). Top-5-Anteil der Tipps 53 %, Vielfalt 2,5 bit, 27 % Tipps auf Gerichte, die in den letzten 5 Arbeitstagen serviert wurden. Stärkste Kategorie: Beilage (30 % Treffer).
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

