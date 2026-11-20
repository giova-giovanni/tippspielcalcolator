# Backtest – Tippspiel Essen Wies

_Automatisch erzeugt von `engine/backtest.py` am 2026-11-20T08:40:05+00:00._

## Kurzfassung

* **Modell:** *ensemble* (auf der Validierung 2025 nach Log-Loss gewählt), **Strategie:** Wochenplaner (auf der Validierung nach *erwarteten* Punkten gewählt). Regel 4 gilt gegen die eigenen simulierten Tipps der Woche; gewertet wird mit `rules.score_tip`.
* **2026 ist echter Test (out-of-sample):** keine Hyperparameter, keine Modell- oder Strategiewahl hat 2026 gesehen; für jeden Tag wird nur mit den Menüs *davor* trainiert.
* **2026** (Test, out-of-sample, mit Regel 4): Modell **68.5 Punkte** an 207 Spieltagen (0.331/Tag; laut Modell erwartet 72.7) → vor **allen** Spielern. Spieler: Andreas 54.5, Johannes 53, Johannes Paul III 50.5, Noah 49.5, Lorenz 2.
  * Gegen den Besten (Andreas): +14 Punkte, 95 %-Bootstrap-Intervall [-2.5, +31], P(Modell vorne) 94% → **statistisch nicht gesichert** (Intervall enthält 0).
  * Nur an den 197 Tagen, an denen Andreas getippt hat: +11.5 [-5.5, +28.5] (nicht gesichert).
  * Gegen Johannes Paul III (ich): +18 [+2.5, +33], nur meine 192 Tipptage +13 [-2, +28.5].
  * Andere Modelle 2026 (gleiche Strategie, nur zur Information – nicht zur Auswahl benutzt): frequency 40, heuristic 71, ml 70.5.
* **2025** (teilweise in-sample: Tuning/Validierung, mit Regel 4): Modell **65.5 Punkte** an 221 Spieltagen (0.296/Tag; laut Modell erwartet 57.2) → vor **allen** Spielern. Spieler: Noah 51.5, Andreas 47.5, Johannes 39.
  * Gegen den Besten (Noah): +14 Punkte, 95 %-Bootstrap-Intervall [-3, +31], P(Modell vorne) 94% → **statistisch nicht gesichert** (Intervall enthält 0).
  * Nur an den 213 Tagen, an denen Noah getippt hat: +11.5 [-5.5, +29] (nicht gesichert).
* **Wochenplaner vs. Greedy:** Validierung erwartete Punkte 24.93 (week_planner@1) vs. 24.62 (Greedy) → gewählt: Wochenplaner. Der Unterschied ist klein (+0.30 erwartete Punkte auf der Validierung); 2026 realisiert: Planer 68.5 vs. Greedy 67 – innerhalb des Zufallsrauschens.
* Eine Saison hat ~180 Spieltage mit stark schwankenden Tagespunkten (0–3): Unterschiede von wenigen Punkten sind Zufall. Das Modell tippt jeden Tag; Spieler haben einzelne Tage ausgelassen (zählen 0) – deshalb auch der Vergleich nur über die getippten Tage.

## Riassunto (italiano)

* **Modello:** *ensemble* (scelto sulla validazione 2025 per log-loss), **strategia:** pianificatore settimanale (scelta sulla validazione per punti *attesi*). Regola 4 rispettata rispetto ai propri tip simulati della settimana; punteggio con `rules.score_tip`.
* **Il 2026 è un vero test (fuori campione):** nessun iperparametro, nessuna scelta di modello o strategia ha visto il 2026; ogni giorno il modello usa solo i menù *precedenti*.
* **2026** (test, fuori campione, con regola 4): modello **68.5 punti** in 207 giorni (0.331/giorno; attesi secondo il modello 72.7) → davanti a **tutti** i giocatori. Giocatori: Andreas 54.5, Johannes 53, Johannes Paul III 50.5, Noah 49.5, Lorenz 2.
  * Contro il migliore (Andreas): +14 punti, intervallo bootstrap 95 % [-2.5, +31], P(modello davanti) 94% → **non statisticamente significativo** (l'intervallo contiene 0).
  * Solo nei 197 giorni in cui Andreas ha tippato: +11.5 [-5.5, +28.5] (non significativo).
  * Contro Johannes Paul III (io): +18 [+2.5, +33], solo i miei 192 giorni tippati +13 [-2, +28.5].
  * Altri modelli 2026 (stessa strategia, solo informativo – non usati per la scelta): frequency 40, heuristic 71, ml 70.5.
* **2025** (in parte nel campione: tuning/validazione, con regola 4): modello **65.5 punti** in 221 giorni (0.296/giorno; attesi secondo il modello 57.2) → davanti a **tutti** i giocatori. Giocatori: Noah 51.5, Andreas 47.5, Johannes 39.
  * Contro il migliore (Noah): +14 punti, intervallo bootstrap 95 % [-3, +31], P(modello davanti) 94% → **non statisticamente significativo** (l'intervallo contiene 0).
  * Solo nei 213 giorni in cui Noah ha tippato: +11.5 [-5.5, +29] (non significativo).
* **Pianificatore vs. greedy:** punti attesi sulla validazione 24.93 (week_planner@1) vs. 24.62 (greedy) → scelto: pianificatore settimanale. Differenza piccola (+0.30 punti attesi sulla validazione); 2026 realizzato: pianificatore 68.5 vs. greedy 67 – dentro il rumore casuale.
* Una stagione ha ~180 giorni con punti giornalieri molto variabili (0–3): differenze di pochi punti sono casuali. Il modello tippa ogni giorno; i giocatori hanno saltato alcuni giorni (contano 0) – per questo anche il confronto solo sui giorni tippati.

## Methode

* **Walk-forward**: für jeden Arbeitstag ab 13.01.2025 wird nur mit den Menüs *vor* diesem Tag trainiert (2024 = Aufwärmphase). Keine Tipps anderer Spieler als Eingabe (Regel 6).
* **Entscheidung** exakt wie in der Tagesempfehlung (`engine/recommend.py::decide`): Erwartungswert EV = 1·P(V) + 0,5·P(H) + 0,5·P(B) + 1·P(V∧H∧B) mit P(V∧H∧B) = P(V)·P(H)·P(B|H), Regel 4 gegen die *eigenen simulierten* Tipps derselben ISO-Woche. Strategien: Wochenplaner (Receding Horizon über die restlichen Arbeitstage der Woche, spätere Tage mit Faktor discount^k gewichtet, „anderes Gericht“ als Ausweichoption) oder Greedy (bester gültiger Tipp nur für heute). Verwendet: **Wochenplaner**, gewählt nach erwarteten Punkten auf der Validierung (Regel vorab festgelegt, nicht nach 2026).
* **Wertung** mit `rules.score_tip`: jede angesagte Option zählt, „Fisch“-Regel außerhalb der Fastenzeit.
* **Splits**: Tuning 13.01.–31.08.2025 · Validierung 01.09.–19.12.2025 · **Test 2026 (nie getunt)**. 2025 ist damit *teilweise in-sample* (Hyperparameter), 2026 ist ehrlich out-of-sample.
* Bestes Modell (Auswahl nach Validierungs-Log-Loss, nicht nach 2026): **ensemble**.
* Modellentwicklung (Features, Suchgitter, Entscheidungslogik) nur mit 2024/2025; 2026 wurde erst mit eingefrorenem Modell ausgewertet. Einzige Ausnahme: ein früher Diagnoselauf mit *ungetunten* Standardparametern zeigte einmal den 2026-Log-Loss; daraus wurde nichts abgeleitet.

## Punkte pro Jahr (mit Regel 4, Wochenplaner)

| Wer | 2025 Punkte | 2025 Tage | 2025 Pkt/Tag | 2026 Punkte | 2026 Tage | 2026 Pkt/Tag |
|---|---|---|---|---|---|---|
| Modell **frequency** | 36.0 | 221 | 0.163 | 40.0 | 207 | 0.193 |
| Modell **heuristic** | 64.5 | 221 | 0.292 | 71.0 | 207 | 0.343 |
| Modell **ml** | 55.5 | 221 | 0.251 | 70.5 | 207 | 0.341 |
| Modell **ensemble** | 65.5 | 221 | 0.296 | 68.5 | 207 | 0.331 |
| Andreas | 47.5 | 214 | 0.222 | 54.5 | 197 | 0.277 |
| Johannes | 39.0 | 209 | 0.187 | 53.0 | 190 | 0.279 |
| Noah | 51.5 | 213 | 0.242 | 49.5 | 200 | 0.247 |
| Johannes Paul III | – | – | – | 50.5 | 192 | 0.263 |
| Lorenz | – | – | – | 2.0 | 10 | 0.200 |

Spieler: Tage = servierte Tage mit eigenem Tipp (nicht getippte Tage zählen 0 Punkte). Modell: tippt jeden Arbeitstag.

## Fazit

* **2025** (teilweise getunt): Modell *ensemble* 65.5 Punkte → schlägt den besten Spieler Noah (51.5), Differenz +14. Punkte pro getipptem Tag: Modell 0.296 vs. bester Spieler 0.242.
  Andere Modelle: frequency 36, heuristic 64.5, ml 55.5.
* **2026** (Testjahr, out-of-sample): Modell *ensemble* 68.5 Punkte → schlägt den besten Spieler Andreas (54.5), Differenz +14. Punkte pro getipptem Tag: Modell 0.331 vs. bester Spieler 0.279.
  Gegen Johannes Paul III (ich): +18 Punkte (ab meinem ersten Tipp +16); pro getipptem Tag 0.263 (ich) vs. 0.331 (Modell).
  Andere Modelle: frequency 40, heuristic 71, ml 70.5.

### Wie sicher ist der Vorsprung? (gepaarter Bootstrap über Tage, 4000 Ziehungen)

| Jahr | gegen | Modell | Spieler | Differenz | 95 %-Intervall | P(Modell vorne) | nur getippte Tage (n) | 95 %-Intervall |
|---|---|---|---|---|---|---|---|---|
| 2025 | Andreas | 65.5 | 47.5 | +18 | [-0.5, +36] | 97% | +16.5 (214) | [-1.5, +35] |
| 2025 | Johannes | 65.5 | 39 | +26.5 | [+9.5, +44.5] | 100% | +23 (209) | [+5.5, +39.5] |
| 2025 | Noah | 65.5 | 51.5 | +14 | [-3, +31] | 94% | +11.5 (213) | [-5.5, +29] |
| 2026 | Andreas | 68.5 | 54.5 | +14 | [-2.5, +31] | 94% | +11.5 (197) | [-5.5, +28.5] |
| 2026 | Johannes | 68.5 | 53 | +15.5 | [-1, +32.5] | 96% | +8.5 (190) | [-8, +25] |
| 2026 | Noah | 68.5 | 49.5 | +19 | [+2.5, +35.5] | 99% | +16 (200) | [+0.5, +32.5] |
| 2026 | Johannes Paul III | 68.5 | 50.5 | +18 | [+2.5, +33] | 99% | +13 (192) | [-2, +28.5] |
| 2026 | Lorenz | 68.5 | 2 | +66.5 | [+53, +81] | 100% | +2.5 (10) | [-0.5, +5.5] |

Eine Saison hat nur ~180 Spieltage; die Tagespunkte schwanken stark (0 / 0,5 / 1 / 1,5 / 2 / 3). Ein Vorsprung von wenigen Punkten ist daher statistisch nicht gesichert.

## Wochenplaner vs. Greedy vs. ohne Regel 4

| Modell | Jahr | Wochenplaner | Greedy | ohne R4 (Obergrenze nur im Erwartungswert) | erwartete Punkte Planer | erwartete Punkte Greedy |
|---|---|---|---|---|---|---|
| frequency | 2025 | 36.0 | 34.5 | 36.0 | 31.4 | 31.4 |
| frequency | 2026 | 40.0 | 38.0 | 34.5 | 35.0 | 34.9 |
| heuristic | 2025 | 64.5 | 68.5 | 72.5 | 61.3 | 60.5 |
| heuristic | 2026 | 71.0 | 68.0 | 76.0 | 80.4 | 79.0 |
| ml | 2025 | 55.5 | 52.5 | 67.0 | 59.7 | 58.5 |
| ml | 2026 | 70.5 | 71.5 | 79.0 | 73.9 | 72.3 |
| ensemble | 2025 | 65.5 | 57.5 | 71.0 | 57.2 | 56.3 |
| ensemble | 2026 | 68.5 | 67.0 | 74.0 | 72.7 | 71.2 |

Summe über alle Modelle und Jahre: Wochenplaner 471.5 vs. Greedy 457.5 Punkte. „Erwartete Punkte“ = Summe der EV der gewählten Tipps laut Modell. Der Planer verteilt die knappen Regel-4-Kontingente (v. a. Reis, Montags-Favoriten) auf die Tage mit der höchsten Wahrscheinlichkeit; sein erwarteter Vorteil laut Modell beträgt 0.9–1.6 Punkte pro Saison und ist im realisierten Ergebnis vom Zufall nicht zu unterscheiden. Erwartete Punkte auf der Validierung (Planer vs. Greedy): frequency 12.8 vs. 12.7; heuristic 27.6 vs. 27.2; ml 25.4 vs. 24.9; ensemble 24.9 vs. 24.6. Ohne Regel 4 hätten die Modelle (außer frequency) realisiert 5–11.5 Punkte pro Saison mehr erzielt (ohne R4 ist nur der *erwartete* Wert eine Obergrenze – realisiert kann es auch weniger sein).

Strategiewahl für *ensemble* (Validierung, erwartete Punkte = Summe der EV): 

| Kandidat | Val. erwartet | Val. realisiert | Tuning erwartet | Tuning realisiert |
|---|---|---|---|---|
| greedy | 24.62 | 23.5 | 31.66 | 34 |
| week_planner@0.5 | 24.88 | 26 | 32.06 | 33 |
| week_planner@0.7 | 24.88 | 26 | 32.23 | 35 |
| week_planner@0.85 | 24.78 | 25.5 | 32.28 | 35.5 |
| week_planner@1 ✔ | 24.93 | 28 | 32.23 | 37.5 |


## Punkte nach Split (Wochenplaner)

| Modell | Tuning | Validierung | Test 2026 |
|---|---|---|---|
| frequency | 20.5 | 15.5 | 40.0 |
| heuristic | 41.0 | 23.5 | 71.0 |
| ml | 29.0 | 26.5 | 70.5 |
| ensemble | 37.5 | 28.0 | 68.5 |

## Trefferquoten der gewählten Tipps (mit R4)

| Modell | Jahr | V | H | B | volle Menüs |
|---|---|---|---|---|---|
| frequency | 2025 | 5.9% | 3.2% | 17.6% | 0 |
| frequency | 2026 | 3.4% | 8.7% | 23.2% | 0 |
| heuristic | 2025 | 10.9% | 13.1% | 21.7% | 2 |
| heuristic | 2026 | 15.9% | 7.2% | 27.5% | 2 |
| ml | 2025 | 10.9% | 11.3% | 16.3% | 1 |
| ml | 2026 | 13.5% | 10.1% | 29.0% | 2 |
| ensemble | 2025 | 11.8% | 12.2% | 20.8% | 3 |
| ensemble | 2026 | 13.5% | 8.2% | 29.0% | 2 |
| Andreas | 2025 | 7.9% | 7.9% | 19.6% | 1 |
| Andreas | 2026 | 10.7% | 9.6% | 24.4% | 0 |
| Johannes | 2025 | 8.1% | 4.3% | 15.8% | 1 |
| Johannes | 2026 | 7.9% | 10.5% | 28.4% | 1 |
| Noah | 2025 | 10.8% | 8.5% | 17.4% | 1 |
| Noah | 2026 | 7.5% | 9.0% | 24.5% | 1 |
| Johannes Paul III | 2026 | 8.8% | 10.4% | 22.4% | 2 |
| Lorenz | 2026 | 0.0% | 10.0% | 30.0% | 0 |

## Aufholjagd 2026 (Stand 2026-11-19, noch 23 Spieltage)

Noch 23 Spieltage. Andreas führt mit 54 Punkten, 3,5 vor Johannes Paul III. Mit den Tipps des Modells (0,33 Punkte/Tag im Backtest) liegt die Siegchance bei 17 % (in zwei Wochen vorne: 5 %); mit der bisherigen eigenen Form bei 3 %. Zum Überholen von Andreas braucht es im Schnitt 0,45 Punkte/Tag.

Monte Carlo: 20000 Saisonenden, jeder Spieltag = ein ganzer echter Tag der Saison (207 Tage, Punkte aller Spieler + Modell-Backtest, Korrelation bleibt erhalten). Neue Spieler (Lorenz) = Punkte eines zufälligen Stammspielers desselben Tages.

| Spieler | Stand | Pkt/Tag | erwartet Ende | Siegchance (ich = Modell) | Siegchance (ich = eigene Form) |
|---|---|---|---|---|---|
| Andreas | 54.0 | 0.274 | 60.0 | 55.9% | 67.1% |
| Johannes | 53.0 | 0.279 | 58.9 | 23.3% | 28.0% |
| Johannes Paul III | 50.5 | 0.263 | 58.1 | 19.6% | 3.4% |
| Lorenz | 50.0 | 0.200 | 55.8 | 0.3% | 0.4% |
| Noah | 49.5 | 0.247 | 55.0 | 0.8% | 1.1% |

Ich (Johannes Paul III) mit dem Modell: Platz 1 am Saisonende 17.4%, in 10 Spieltagen vorne 4.7%; vor Andreas am Ende 22.8%. Benötigt: 0.448 Pkt/Tag (Modell im Backtest 0.331).

## Wahrscheinlichkeitsgüte (Log-Loss, Top-1/Top-3 ohne R4)

| Modell | Split | LL V | LL H | LL B | Top1 V | Top1 H | Top1 B | Top3 V | Top3 H | Top3 B |
|---|---|---|---|---|---|---|---|---|---|---|
| frequency | tune | 3.394 | 3.272 | 2.563 | 5.6% | 4.2% | 23.2% | 12.7% | 12.7% | 43.7% |
| frequency | validation | 3.516 | 3.463 | 2.423 | 7.7% | 2.5% | 26.6% | 15.4% | 12.7% | 48.1% |
| frequency | test | 3.400 | 3.451 | 2.569 | 4.3% | 6.8% | 21.3% | 15.0% | 16.4% | 44.9% |
| heuristic | tune | 3.208 | 3.024 | 2.335 | 9.9% | 12.7% | 24.6% | 19.7% | 33.1% | 58.5% |
| heuristic | validation | 3.225 | 3.139 | 2.241 | 11.5% | 15.2% | 31.6% | 34.6% | 30.4% | 53.2% |
| heuristic | test | 3.047 | 3.252 | 2.269 | 15.0% | 8.2% | 34.8% | 34.8% | 21.3% | 58.0% |
| ml | tune | 3.253 | 3.092 | 2.396 | 8.5% | 11.3% | 24.6% | 23.9% | 30.3% | 53.5% |
| ml | validation | 3.185 | 3.168 | 2.234 | 15.4% | 12.7% | 26.6% | 39.7% | 32.9% | 55.7% |
| ml | test | 3.026 | 3.225 | 2.255 | 12.1% | 11.1% | 36.7% | 34.8% | 25.6% | 58.9% |
| ensemble | tune | 3.210 | 3.055 | 2.364 | 8.5% | 12.0% | 27.5% | 24.6% | 33.1% | 57.0% |
| ensemble | validation | 3.174 | 3.148 | 2.230 | 15.4% | 12.7% | 31.6% | 38.5% | 32.9% | 57.0% |
| ensemble | test | 3.013 | 3.222 | 2.269 | 11.6% | 9.2% | 37.2% | 34.8% | 25.6% | 58.5% |

## Kalibrierung (ensemble, alle Backtest-Tage)

| Kategorie | p-Bereich | mittleres p | Trefferquote | n |
|---|---|---|---|---|
| vorspeise | 0.00–0.02 | 0.005 | 0.006 | 17236 |
| vorspeise | 0.02–0.05 | 0.032 | 0.047 | 2530 |
| vorspeise | 0.05–0.10 | 0.070 | 0.082 | 1238 |
| vorspeise | 0.10–0.15 | 0.121 | 0.129 | 459 |
| vorspeise | 0.15–0.20 | 0.171 | 0.140 | 114 |
| vorspeise | 0.20–0.30 | 0.236 | 0.200 | 30 |
| vorspeise | 0.30–0.50 | 0.335 | 0.400 | 5 |
| hauptspeise | 0.00–0.02 | 0.009 | 0.010 | 9481 |
| hauptspeise | 0.02–0.05 | 0.031 | 0.040 | 3494 |
| hauptspeise | 0.05–0.10 | 0.069 | 0.075 | 1552 |
| hauptspeise | 0.10–0.15 | 0.120 | 0.118 | 357 |
| hauptspeise | 0.15–0.20 | 0.168 | 0.116 | 86 |
| hauptspeise | 0.20–0.30 | 0.233 | 0.125 | 24 |
| hauptspeise | 0.30–0.50 | 0.320 | 1.000 | 1 |
| beilage | 0.00–0.02 | 0.007 | 0.008 | 3586 |
| beilage | 0.02–0.05 | 0.033 | 0.029 | 1610 |
| beilage | 0.05–0.10 | 0.073 | 0.080 | 1374 |
| beilage | 0.10–0.15 | 0.122 | 0.115 | 679 |
| beilage | 0.15–0.20 | 0.172 | 0.203 | 339 |
| beilage | 0.20–0.30 | 0.237 | 0.299 | 164 |
| beilage | 0.30–0.50 | 0.389 | 0.505 | 97 |
| beilage | 0.50–1.00 | 0.505 | 0.000 | 3 |

## Gewählte Parameter

```json
{
 "half_life": {
  "vorspeise": 1000.0,
  "hauptspeise": 1000.0,
  "beilage": 400.0
 },
 "alpha": {
  "vorspeise": 0.5,
  "hauptspeise": 0.5,
  "beilage": 0.5
 },
 "hazard_mode": {
  "vorspeise": "rel",
  "hauptspeise": "rel",
  "beilage": "rel"
 },
 "hazard_kappa": {
  "vorspeise": 0.3,
  "hauptspeise": 1.0,
  "beilage": 3.0
 },
 "hazard_smooth": {
  "vorspeise": 0.25,
  "hauptspeise": 0.25,
  "beilage": 0.25
 },
 "weekday_beta": {
  "vorspeise": 12.0,
  "hauptspeise": 12.0,
  "beilage": 80.0
 },
 "season_beta": {
  "vorspeise": 0.0,
  "hauptspeise": 40.0,
  "beilage": 40.0
 },
 "week_kappa": {
  "vorspeise": 0.5,
  "hauptspeise": 0.5,
  "beilage": 2.0
 },
 "temperature": {
  "vorspeise": 1.4,
  "hauptspeise": 1.0,
  "beilage": 1.4
 },
 "fish_kappa": 1.0,
 "family_kappa": 0.0,
 "new_half_life": 150.0,
 "freq_half_life": 0.0,
 "short_half_life": 15.0,
 "pair_half_life": 500.0,
 "pair_gamma": 0.3,
 "beilage_mix": 0.3,
 "ml_C": 0.03,
 "ml_kind": "clogit",
 "ml_refit_every": 5,
 "ml_min_day": 20,
 "ensemble_w": 0.7,
 "plan_discount": 1.0
}
```

Modellauswahl auf der Validierung:

| Modell | Val-Log-Loss (gewichtet) | Val-Punkte | Tuning-Punkte |
|---|---|---|---|
| frequency | 3.2295 | 15.5 | 20.5 |
| heuristic | 2.9575 | 23.5 | 41.0 |
| ml | 2.9429 | 26.5 | 29.0 |
| ensemble | 2.9311 | 28.0 | 37.5 |

