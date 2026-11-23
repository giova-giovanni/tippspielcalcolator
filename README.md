# Tippspiel Essen Wies – Tipp-Rechner

> **Kurz auf Deutsch.** Diese Seite rechnet jeden Arbeitstag den besten Tipp (Vorspeise / Hauptspeise /
> Beilage) für das Mittagsmenü-Tippspiel im Hotel Schönwies aus – für *Johannes Paul III*. Die Daten
> kommen aus der Excel-Tabelle, aus `data/*.csv` oder aus dem Formular „Eingabe“ der Website. Eine
> GitHub Action (Python) rechnet Statistik, Backtest und Empfehlung neu und schreibt `docs/data/*.json`;
> GitHub Pages zeigt die Website (`docs/`) an – optimiert fürs Handy, Sprache Deutsch (umschaltbar auf
> Italienisch). Die Empfehlung hält Regel 4 ein (gleiches Gericht max. 2× pro Woche, nie an
> aufeinanderfolgenden Tagen) und benutzt **nie** die Tipps der anderen Mitspieler (Regel 6).
> Einrichtung: Branch in `main` mergen → Settings → Pages → *Deploy from a branch* → `main` / `/docs` →
> Settings → Actions → *Read and write permissions* → Actions → **on-data** → *Run workflow*.
> Der Rest dieser Anleitung ist auf Italienisch.

---

## Che cos'è

Un piccolo sistema che, ogni giorno lavorativo, consiglia la giocata migliore per il *Tippspiel*
(pronostico del menù del pranzo dei lavoratori all'Hotel Schönwies di Trodena): **antipasto (Vorspeise),
piatto principale (Hauptspeise) e contorno (Beilage)**, da inviare entro le **12:00**.

- Il motore Python analizza lo storico dei menù (dal 25.10.2024 in poi), stima la probabilità di ogni
  piatto per il giorno target e sceglie la combinazione con il **massimo valore atteso di punti**,
  rispettando la regola 4 sulle mie giocate (`config.json → me = "Johannes Paul III"`).
- Il sito (GitHub Pages, cartella `docs/`) mostra il consiglio del giorno, la pianificazione della
  settimana, statistiche, classifica, backtest, il database dei menù e un modulo per inserire nuovi dati.
- Interfaccia in tedesco con pulsante per l'italiano; i nomi dei piatti restano sempre in tedesco.

## Architettura

```
 ┌──────────────────────────┐  ┌──────────────────────────┐  ┌─────────────────────────────┐
 │ Excel                    │  │ CSV modificati a mano     │  │ Sito → scheda "Eingabe"     │
 │ data/raw/                │  │ data/menus.csv            │  │ (commit via GitHub API con  │
 │  "Tippspiel Essen.xlsx"  │  │ data/tips.csv             │  │  token personale)           │
 └────────────┬─────────────┘  └────────────┬─────────────┘  └──────────────┬──────────────┘
              └──────────── push su main ───┴───────────────────────────────┘
                                            │            + cron lun–ven 05:17 UTC (daily.yml)
                                            ▼
              ┌──────────────────────────────────────────────────────────────┐
              │ GitHub Actions (on-data.yml / daily.yml), Python 3.11        │
              │  engine.pipeline:                                            │
              │   ingest (solo se l'hash dell'xlsx è cambiato)               │
              │   → refresh CSV (colonne *_norm, points)                     │
              │   → analyze → backtest → recommend → site                    │
              │  → commit di docs/data, data/*.csv, reports come             │
              │    github-actions[bot]                                       │
              └──────────────────────────────┬───────────────────────────────┘
                                             ▼
                          docs/data/*.json  (+ reports/*.md)
                                             ▼
              ┌──────────────────────────────────────────────────────────────┐
              │ GitHub Pages: docs/index.html + app.js legge docs/data/*.json│
              │ (opzionale: JSON cifrati AES-GCM, il browser chiede la frase)│
              └──────────────────────────────────────────────────────────────┘
```

Workflow in `.github/workflows/`:

| File | Quando | Cosa fa |
|---|---|---|
| `daily.yml` | lun–ven 05:17 UTC (06:17 CET / 07:17 CEST) + run di riserva 07:47 UTC + manuale | `python -m engine.pipeline --daily` (salta il backtest se esiste già), commit + push; il run di riserva non fa niente se `today.json` è già stato aggiornato oggi |
| `on-data.yml` | push su `main` che tocca `data/**`, `engine/**`, `requirements.txt` o il workflow stesso + manuale (opzioni *tune*, *force_ingest*) | pipeline completa, commit + push; `pytest` in un job separato, in parallelo |
| `tests.yml` | pull request e push su branch diversi da `main` | `pytest` e, in parallelo, i test JS del Piano (`node --test`) |

I due workflow della pipeline condividono il gruppo di concorrenza `pipeline` (mai due esecuzioni
in parallelo). In `on-data` i test girano in un job a parte: se un test fallisce il run diventa rosso
(e GitHub manda un'e-mail), ma i nuovi menù/tipp arrivano comunque sul sito. Prima `pytest` girava
prima del commit, e un test legato ai dati del 09.10.2026 bloccava ogni inserimento dal sito; ora i
test che usano i dati reali lavorano su uno snapshot fisso (`SNAPSHOT_DAY` / `SNAPSHOT_LAST_SERVED`).
I push fatti dal bot con il `GITHUB_TOKEN` **non** riattivano nessun workflow, quindi non ci sono cicli; i push fatti dal sito con il token personale invece sì (ed è voluto).

## Prima configurazione

1. **Merge del branch in `main`** (pull request → *Merge*), così workflow e sito finiscono su `main`.
2. **GitHub Pages**: *Settings → Pages → Build and deployment → Source: Deploy from a branch →
   Branch `main`, cartella `/docs` → Save*. Dopo 1–2 minuti il sito è su
   `https://<utente>.github.io/<repo>/` (qui: `https://giova-giovanni.github.io/tippspielcalcolator/`).
   - Alternativa: *Source: GitHub Actions* **e** variabile di repository `PAGES_MODE=actions`
     (*Settings → Secrets and variables → Actions → Variables → New repository variable*).
     Allora il job `deploy` di `daily.yml`/`on-data.yml` pubblica `docs/` dopo ogni esecuzione.
     Senza la variabile il job `deploy` viene saltato.
3. **Permessi delle Actions**: *Settings → Actions → General → Workflow permissions → Read and write
   permissions → Save* (serve per il commit del bot).
4. **Prima esecuzione**: scheda *Actions* → se richiesto *I understand my workflows, go ahead and enable
   them* → workflow **on-data** → *Run workflow* (branch `main`). Dura ~1–2 minuti; poi il sito ha dati
   freschi. Da lì in avanti `daily` gira da solo ogni mattina feriale.
5. (Opzionale) **Cifratura**: *Settings → Secrets and variables → Actions → New repository secret*
   `SITE_PASSPHRASE` = una frase lunga. Al prossimo run i `docs/data/*.json` vengono cifrati e il sito
   chiede la frase una volta (salvata solo nel browser). Vedi [Privacy](#privacy-e-limiti-di-github-free).
6. **Vecchio `index.html` nella radice**: è il vecchio blog di viaggi, non c'entra niente. Quando Pages
   pubblica da `/docs` non viene servito; si può cancellare tranquillamente.

## Come aggiornare i dati

Tre modi, combinabili. Ogni push su `main` in `data/**` avvia `on-data`, che ricalcola tutto.

1. **Caricare un nuovo Excel**: su github.com → cartella `data/raw/` → *Add file → Upload files* →
   file chiamato esattamente **`Tippspiel Essen.xlsx`** (sostituisce quello vecchio; tenerne uno solo)
   → *Commit changes*.
   - L'ingest parte solo se l'hash del file è cambiato (`data/state.json`); per forzarlo:
     *Actions → on-data → Run workflow → force_ingest*.
   - Fogli `2024`, `2025`, `2026`, … e blocchi giocatore (4 colonne) vengono riconosciuti da soli;
     un nuovo anno o un nuovo giocatore non richiede modifiche al codice.
   - **L'Excel vince dove ha contenuto**; le righe inserite dal sito (o a mano) per date che nell'Excel
     sono vuote/future vengono mantenute. Una riga "pending" (vuota) dell'Excel non cancella un menù
     inserito dal sito.
2. **Modificare i CSV su github.com**: aprire `data/menus.csv` o `data/tips.csv` → icona matita →
   modificare → *Commit changes*. Basta toccare le colonne "grezze": `date`, `vorspeise`, `hauptspeise`,
   `beilage` (e `status` per i menù, `player` per i tips). Le colonne derivate (`*_norm`, `points`,
   `year`, `weekday`, e `status` se vuoto) vengono rigenerate dalla pipeline. Nota: se poi carichi un
   Excel che ha contenuto per la stessa data, vince l'Excel.
   - `status`: `served` (servito), `free` (nessun pasto, es. ferie/festivo), `unknown` (`Bo`/`NV`/`-`),
     `pending` (non ancora noto). Più opzioni in una cella: `Pommes / Kartoffelsalat`.
3. **Sito → scheda "Eingabe"**: inserire il menù del giorno e/o la propria giocata dal telefono. Il sito
   fa un commit su `data/menus.csv` / `data/tips.csv` tramite l'API di GitHub con un token personale;
   il push avvia `on-data` e dopo ~2 minuti il sito mostra i dati aggiornati.

### Token personale (fine-grained PAT) per la scheda "Eingabe"

1. github.com → foto profilo → *Settings → Developer settings → Personal access tokens →
   Fine-grained tokens → Generate new token*.
2. Nome a piacere, **scadenza** (es. 90 giorni o 1 anno).
3. *Repository access → Only select repositories →* solo questo repository.
4. *Permissions → Repository permissions → Contents: Read and write* (nient'altro è necessario;
   opzionale *Actions: Read-only* perché il sito possa linkare l'esecuzione partita).
5. *Generate token*, copiarlo e incollarlo nel sito: *Einstellungen → GitHub-Token*.

Il token resta **solo nel localStorage di quel browser/telefono** e viene inviato solo a
`api.github.com`; non finisce mai nel repository. Per revocarlo: sul sito *Einstellungen → Löschen*
e su github.com *Settings → Developer settings → Personal access tokens → Fine-grained tokens →*
token → *Delete* (subito invalido ovunque). Su dispositivi altrui cancellarlo dopo l'uso.

## Come leggere il consiglio del giorno (scheda "Tipp", prima "Heute")

- **Il tipp grande** in alto: V / H / B consigliati, con pulsante *Tipp kopieren* (testo
  `V / H / B` pronto da incollare nella chat).
- **Probabilità** (*Wahrsch.*) per piatto: stima del modello che quel piatto venga servito.
- **Punti attesi (EV)**: `EV = 1·P(V) + 0,5·P(H) + 0,5·P(B) + 1·P(tutti e tre)`
  (il bonus del menù completo vale 3 − 2 = 1 punto in più). `P(tutti e tre)` ≈
  `P(V) · P(H) · P(B | H)`: il contorno dipende molto dal piatto principale
  (es. Champignonschnitzel → Reis).
- **Badge regola 4**: le alternative (top per categoria) mostrano se un piatto è *gesperrt*
  (già giocato 2 volte questa settimana o giocato il giorno lavorativo adiacente) e perché.
- **Fisch / Fastenzeit**: fuori dalla Quaresima tutti i piatti di pesce (tranne Scombri) sono raggruppati
  in "Fisch" (regola 9.6); in Quaresima (Mercoledì delle Ceneri → Pasqua) serve il nome esatto e il
  consiglio usa il nome esatto.
- **Wochenplan vs. gierig**: il consiglio principale viene dal *pianificatore settimanale*, che
  distribuisce i "jolly" della regola 4 sui giorni rimanenti della settimana (a volte conviene tenere un
  piatto per un giorno migliore). *Gierig* (greedy) è la migliore combinazione valida solo per oggi;
  entrambe sono mostrate.
- **Countdown fino alle 12:00** (ora di Roma). Dopo le 12:00, nel weekend, in un giorno libero o se il
  menù di oggi è già inserito, il consiglio vale per il **prossimo giorno lavorativo**.
- La scheda **Woche** mostra la settimana: menù noti, mie giocate, previsioni per i giorni ancora
  aperti e quante volte posso ancora giocare ogni piatto.

## Piano (giornata, cene, allenamento, peso)

Il sito contiene anche il **Piano**: tab *Oggi*, *Training* e *Corpo*, impostazioni in *Altro*.
La barra in basso è *Oggi · Tipp · Woche · Training · Corpo · Altro*; Statistik, Rangliste,
Backtest, Daten ed Eingabe sono in *Altro*. Tutti i vecchi indirizzi (`#/heute`, `#/woche`, …)
funzionano ancora.

- **Oggi**: la giornata in ordine – colazione, Tipp compatto (con countdown e *Copia*), pranzo,
  merenda nei giorni di allenamento, allenamento, cena, check della sera e serie dei giorni.
  - Il **pranzo** viene dal menù del giorno (o appena inserito da *Eingabe*), altrimenti dalla
    previsione del modello (etichetta «stima»): kcal/proteine stimate e livello rosso/giallo/verde.
  - La **cena** segue il livello del pranzo (un livello in più nei giorni di allenamento).
    Budget = obiettivo − colazione − merenda − caffè − pranzo, tra 500 e 1100 kcal, con 3 proposte
    dal ricettario.
  - Weekend, giorni liberi del Tippspiel o giorni impostati «a casa»: niente tracciamento del cibo.
- **Training**: piano della settimana, regole e schede.
- **Corpo**: pesate ogni 1–2 settimane, circonferenza vita, tendenza in kg/settimana.
- **Privacy**: profilo, pesate e check restano **solo nel browser** (localStorage, chiavi
  `tsp.piano.*`). Non finiscono nel repository e non vengono inviati da nessuna parte.
  *Impostazioni del piano → I tuoi dati*: esporta (JSON), importa, cancella. Conviene esportare
  ogni tanto e usare il sito dalla schermata Home: su iPhone Safari può cancellare i dati dei siti
  non aperti per 7 giorni.
- Contenuti statici (non personali) in `docs/piano/`:
  - `dish_nutrition.json`: kcal, proteine e tag per piatto, più regole regex per i piatti nuovi;
  - `dinners.json`: ricette e spesa base;
  - `workouts.json`: schede.
- Logica pura in `docs/piano-core.js`, testata con `node --test "tests/js/*.test.js"`.
- Tutti i valori sono stime da tarare sull'andamento reale del peso.

## Regole implementate e scelte di interpretazione

| Regola | Implementazione |
|---|---|
| R2 – pranzi aziendali esclusi | giorni `Frei` = `status: free`, non sono giorni di gioco (né per i punti né per la regola 4) |
| R3 – giocate entro le 12:00 | countdown sul sito; dopo le 12:00 il consiglio passa al prossimo giorno lavorativo |
| R4 – stesso piatto max 2× per settimana lavorativa, mai giorni consecutivi | `engine/rules.py::R4`, per categoria, sulle **mie** giocate; consiglio e pianificatore sono sempre conformi |
| R5 – un solo piatto per categoria | il consiglio contiene esattamente un piatto per V, H, B |
| R6 – niente sbirciare / copiare | le giocate degli altri **non** vengono mai usate dal modello (nemmeno come feature); quelle degli altri per oggi o date future non vengono pubblicate in `docs/data/tips.json` |
| R9.1–9.3 – punteggio | V = 1, H = 0,5, B = 0,5, menù completo = 3 (`rules.score_tip`, identico all'Excel) |
| R9.5 – seconde opzioni | **conta qualsiasi opzione annunciata** (così è tenuto l'Excel, es. righe `Pommes / Kartoffelsalat`); configurabile con `scoring.alt_options_count` |
| R9.6 – "Fisch" | fuori Quaresima "Fisch" vale per ogni piatto di pesce tranne Scombri; in Quaresima nome esatto |
| R9.8 – solo piatti finiti | componenti come `(und Blaukraut)` vengono tolti (`strip_patterns` in `aliases.json`) |
| R10 – fine stagione | ultimo giorno lavorativo dell'anno, al più tardi il 23.12 (`season_end_mmdd`) |
| R16 – Lachsforelle = Forelle | alias in `aliases.json` |

Numerazione del *Regelwerk* dall'Excel di novembre 2026 (la vecchia regola 10 vuota è sparita: fine
stagione era R11, Lachsforelle R17; il contenuto non è cambiato).

Scelte di interpretazione:

- **"Consecutivi"** = giorni *lavorativi* adiacenti **nella stessa settimana** (`r4.consecutive_mode =
  "workday_adjacent_same_week"`): lun→mar vietato; ven→lun della settimana dopo permesso; se martedì è
  libero, lun e mer contano come consecutivi. Alternative: `"workday_adjacent_any"` (anche ven→lun),
  `"calendar_adjacent"` (solo date a un giorno di distanza).
- **Settimana** = settimana ISO (lun–ven).
- Confronto dei nomi **senza distinzione tra maiuscole/minuscole** (come l'Excel); le varianti di
  scrittura vengono unite solo tramite `aliases.json`.
- Verifica: ricalcolando tutte le ~1500 giocate storiche il motore dà gli stessi punti dell'Excel,
  tranne 3 righe corrette a mano nel foglio (2025-10-09 Andreas e Johannes, 2025-12-19 Johannes) e
  2026-10-14 Andreas (`Schweinsschopfbraten` contro il menù `Schweinsschopf`: per l'alias è lo stesso
  piatto, l'Excel dà 0). **La classifica (scheda Rangliste, `leaderboard.json`) usa i punti ufficiali
  dell'Excel** dove ci sono, il ricalcolo solo per le righe inserite dal sito; backtest e confronto
  modello/giocatori usano il ricalcolo (stesse regole per tutti).
- **Punti senza tipp** (blocco giocatore con punti ma V/H/B vuoti) = punti di partenza o correzione:
  es. Lorenz, entrato il 02.11.2026 con **48 punti di partenza** (scritti il 30.10). Contano nella
  classifica e nella simulazione, non come giorno giocato (né nei punti/giorno né nelle statistiche).
- **Nome del giocatore cambiato nell'Excel**: da novembre 2026 la colonna "Johannes Paul III" si chiama
  "Giovanni". `config.json → player_aliases` (`"Giovanni": "Johannes Paul III"`) li unisce; l'ingest
  confronta i nomi dopo l'alias, quindi le righe nuove sostituiscono quelle vecchie invece di duplicarle.

## Risultati del backtest

Walk-forward onesto: per ogni giorno il modello usa solo i menù **precedenti**, rispetta la regola 4 sui
**propri** tipp simulati della settimana e viene valutato con le stesse regole di punteggio dell'Excel.
Iperparametri, modello e strategia sono stati scelti solo su 2025 (tuning gen–ago, validazione set–dic);
il **2026 non è mai stato usato per nessuna scelta** → è un vero test fuori campione.

| Chi | 2025 (in parte nel campione) | 2026 (test, fuori campione, 204 giorni fino al 16.11) |
|---|---|---|
| **Modello ensemble** (quello usato) | **65,5** | **67,0** |
| Modello euristico | 64,5 | 70,0 |
| Modello ML (regressione logistica) | 55,5 | 69,0 |
| Baseline frequenze | 36,0 | 39,5 |
| Andreas | 47,5 | 54,5 (54 ufficiali) |
| Johannes | 39,0 | 53,0 |
| Noah | 51,5 | 49,5 |
| Johannes Paul III / Giovanni (io) | – | 49,0 |
| Lorenz (dal 02.11) | – | 2,0 (+ 48 di partenza) |

**Verdetto onesto:** nel 2026 il modello avrebbe fatto **+12,5 punti** rispetto al migliore (Andreas) e **+18**
rispetto a me, ma con ~200 giorni e punti giornalieri molto variabili l'intervallo bootstrap al 95 % contro
Andreas è **[−4; +30]**: il vantaggio è probabile (≈ 92 %) ma **non statisticamente garantito**.
Il modello è un po' troppo ottimista sulle proprie probabilità (2026: 71,7 punti attesi, 67 reali).
Il pianificatore settimanale vale poco più della scelta giorno per giorno (+1,5 punti nel 2026).
Dettagli, calibrazione e intervalli: [`reports/backtest.md`](reports/backtest.md) e la scheda **Backtest** del sito.

## Aggiornamento novembre 2026 (dati fino al 16.11)

- **Dati**: nuovo Excel con i menù dal 10.10 al 16.11, il nuovo giocatore **Lorenz** (48 punti di
  partenza) e la colonna rinominata "Giovanni" (vedi sopra). Classifica ufficiale al 16.11: Andreas 54,
  Johannes 53, Lorenz 50, Noah 49,5, Johannes Paul III 49.
- **Menù mancanti = consigli peggiori.** Dal 10.10 al 16.11 i menù non erano nel repository: i consigli
  pubblicati ogni mattina (calcolati senza conoscere la rotazione recente) avrebbero fatto **8,5 punti**
  in 26 giorni; lo stesso modello con i menù aggiornati (backtest) **12,5**. Per questo la scheda
  "Heute" ora mostra un avviso quando mancano menù dei giorni di gioco passati (`today.json →
  missing_menus`, ultimi 28 giorni). Inserire il menù ogni giorno (scheda Eingabe) è la cosa più utile.
- **Parametri del modello: invariati, dopo verifica.**
  - Ritaratura con i dati 2026 (tuning 13.01.2025–31.03.2026, validazione 01.04–31.08.2026) e confronto
    sul periodo 01.09–16.11.2026, mai visto da nessuno dei due set: i parametri nuovi sono **peggiori**
    (ensemble: log-loss pesata 2,946 contro 2,926; 21 contro 24,5 punti). Restano quelli del 2025.
  - Variante dell'algoritmo: nel modello ML (conditional logit) pesare di più i giorni recenti
    (half-life 60/120/250/500 giorni serviti). Nessun guadagno né sulla validazione 2025 (2,931 senza peso
    = il migliore) né sul 2026 (2,8811 contro 2,8812 al meglio): scartata, il codice resta com'era.
  - Il modello sceglie la stessa Vorspeise di Andreas solo nel 18 % dei giorni (Johannes/Noah 15 %):
    è già molto diverso dagli altri, una strategia "anti-leader" non porterebbe quasi niente (e
    richiederebbe di usare i tipp degli altri, cosa che il motore non fa – regola 6).
  - Le probabilità del giorno si aggiornano da sole a ogni nuovo menù (il modello è online).
- **Aufholjagd / rimonta** (`engine/race.py`, scheda Rangliste, `leaderboard.json → race`,
  `reports/backtest.md`): Monte Carlo sui giorni di gioco rimasti fino al 23.12. Ogni giorno simulato è
  un giorno *vero* della stagione estratto a caso, con i punti di tutti i giocatori e del modello nello
  stesso giorno: così resta la correlazione (spesso tutti indovinano la stessa cosa e il distacco non
  cambia). Due scenari per me: "seguo il modello" (punti del backtest) e "gioco come finora". I nuovi
  giocatori con meno di 30 giorni (Lorenz) sono simulati come un giocatore medio. Solo punti, mai i
  piatti giocati dagli altri. Al 16.11 (26 giorni rimasti, −5 da Andreas): **seguendo il modello ≈ 8 %
  di finire primo da solo (≈ 11 % primo o a pari merito), ≈ 1 % di essere in testa fra due settimane;
  giocando come finora ≈ 1 %**. Servirebbero ≈ 0,49 punti/giorno, il modello ne fa 0,33 nel backtest.
  `python -m engine.race` stampa la simulazione aggiornata.

## Privacy e limiti di GitHub Free

- **GitHub Pages con un account Free funziona solo con repository pubblici.** Un repository privato con
  Pages richiede GitHub Pro/Team/Enterprise, e anche in quel caso il *sito* resta pubblico su internet
  (solo GitHub Enterprise Cloud offre Pages private con controllo d'accesso). Quindi: **i dati nel
  repository (Excel, CSV con i nomi dei giocatori e le giocate, report) sono pubblici.**
- Mitigazioni presenti:
  - `noindex, nofollow` nelle pagine + `docs/robots.txt` (i motori di ricerca seri non indicizzano);
  - secret opzionale `SITE_PASSPHRASE`: i `docs/data/*.json` vengono cifrati con AES-256-GCM
    (chiave PBKDF2-SHA256) e il browser chiede la frase. **Attenzione:** cifra solo i dati del sito;
    `data/*.csv`, l'Excel e `reports/*.md` restano leggibili nel repository pubblico;
  - non condividere l'URL; usare nomi/abbreviazioni se serve più riservatezza.
- **Minuti di Actions**: illimitati per repository pubblici; 2.000 min/mese per repository privati
  (account Free). Un run completo dura ~1–2 minuti.
- **Workflow pianificati**: nei repository pubblici GitHub li **disattiva dopo 60 giorni senza attività**
  nel repository (i commit giornalieri del bot di solito bastano; se il sito smette di aggiornarsi:
  *Actions → daily → Enable workflow*). Il cron può partire con ritardo (anche decine di minuti) o
  saltare del tutto nei momenti di carico (soprattutto allo scoccare dell'ora): per questo gira alle
  05:17 UTC, molto prima delle 12:00, con un run di riserva alle 07:47 UTC. Se serve subito:
  *Actions → daily → Run workflow*.
- Limiti di Pages (soft): sito ≤ 1 GB, 100 GB/mese di traffico, ~10 build/ora – ampiamente sufficienti.

## Uso in locale

```bash
python -m pip install -r requirements.txt       # Python ≥ 3.11
python -m engine.pipeline                        # tutto: ingest → analisi → backtest → consiglio → JSON
python -m engine.pipeline --today 2026-10-09     # simula un altro giorno
python -m engine.pipeline --daily                # veloce: salta il backtest se backtest.json esiste
python -m engine.pipeline --tune                 # ri-ottimizza i parametri del modello (lento)
python -m engine.pipeline --force-ingest         # rilegge l'Excel anche se non è cambiato
python -m engine.backtest [--tune]               # solo backtest walk-forward (report in reports/backtest.md)
python -m engine.analyze                         # solo statistiche (reports/analysis.md)
python -m engine.race                            # simulazione della corsa al titolo (fine stagione)
python -m engine.ingest --xlsx percorso.xlsx     # solo import Excel → CSV
python -m pytest -q                              # test (nessuna rete, non modificano data/)
node --test "tests/js/*.test.js"                 # test JS del Piano (Node >= 22, nessuna dipendenza)
python -m http.server -d docs 8000               # anteprima del sito su http://localhost:8000
```

`SITE_PASSPHRASE=… python -m engine.pipeline` produce i JSON cifrati come in GitHub Actions.

## Configurazione

### `data/config.json`

| Chiave | Significato |
|---|---|
| `me` | giocatore per cui si calcola il consiglio e la regola 4 (`"Johannes Paul III"`) |
| `player_aliases` | nomi alternativi dei giocatori (es. `"Hannes": "Johannes"`, `"Giovanni": "Johannes Paul III"`); valgono anche nell'ingest |
| `timezone`, `deadline` | `Europe/Rome`, `12:00` |
| `season_end_mmdd` | fine stagione (`12-23`) |
| `scoring` | punti per categoria, `full_menu_total`, `alt_options_count` (true = conta ogni opzione annunciata) |
| `r4.max_per_week`, `r4.consecutive_mode` | regola 4 (vedi sopra) |
| `model` | valori di default; modello e parametri effettivi stanno in `data/model_params.json` (scritto da `--tune`, scelto sul periodo di validazione) |

### `data/aliases.json`

Normalizzazione dei nomi dei piatti, per categoria: chiave = scrittura come nell'Excel (maiuscole
indifferenti), valore = nome canonico (o lista = più opzioni). Inoltre: `missing_tokens` (`-`, `Bo`,
`NV`…), `free_tokens` (`Frei`), separatori delle opzioni (`" / "`, `" oder "`, `" + "`…),
`strip_patterns` (regola 9.8), `fish` (piatti/parole chiave di pesce, `Scombri` sempre esatto),
`keep_separate` (coppie da **non** unire, es. `Kartoffelstampf` ≠ `Püree`, decisione di Johannes Paul III).
Nuovi candidati alias vengono solo *proposti* in `reports/alias_candidates.md`, mai uniti in automatico.
Dopo una modifica basta il commit: `on-data` ricalcola tutto.

**Decisione aperta – Champignonschnitzel**: oggi `Truthahnschnitzel mit Champignonsauce`,
`Schnitzel mit Champignonsauce` e `Schweinsschnitzel mit Champignonsauce` (scritture 2024/inizio 2025)
sono unite in `Champignonschnitzel`. Per separarle: in `data/aliases.json`, sezione `"hauptspeise"`,
cancellare quelle tre righe (e aggiornare la voce corrispondente in `"review"`), poi commit.

## Struttura del repository

```
.github/workflows/   daily.yml, on-data.yml, tests.yml
data/
  raw/Tippspiel Essen.xlsx   Excel originale (sorgente principale)
  menus.csv, tips.csv        dati normalizzati (colonne grezze + derivate)
  config.json, aliases.json  configurazione e normalizzazione (da modificare a mano)
  model_params.json          parametri del modello (da --tune)
  state.json                 hash dell'ultimo Excel importato
docs/                        sito GitHub Pages (index.html, app.js, i18n.js, style.css, …)
  data/*.json                generati dalla pipeline: meta, menus, tips, dishes, today, week,
                             stats, leaderboard, backtest
  piano.js, piano-core.js,   Piano: viste, logica pura, stili
  piano.css
  piano/*.json               Piano: piatti (kcal/proteine), ricette, schede (statici)
engine/                      motore Python: ingest, normalize, rules, dates, data, analyze,
                             model, backtest, race, recommend, site, output, pipeline
reports/                     report Markdown generati (ingest, analisi, alias, backtest)
tests/                       pytest; tests/js/ = test node del Piano
CLAUDE.md                    note per Claude Code (architettura, comandi, regole)
requirements.txt, pytest.ini
index.html                   vecchio blog, non usato (si può cancellare)
```
