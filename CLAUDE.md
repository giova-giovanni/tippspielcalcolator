# CLAUDE.md

Sito statico su GitHub Pages (`docs/`) + motore Python che ogni giorno ricalcola il consiglio del
Tippspiel. Il sito contiene anche il **Piano** (routine, pranzo → cena, allenamento, peso): i suoi
dati personali restano solo nel browser.

## Architettura

- `engine/` (Python 3.11): `python -m engine.pipeline` = ingest → analyze → backtest → recommend →
  site; scrive `docs/data/*.json` (cifrati AES-GCM se c'è `SITE_PASSPHRASE`).
- `docs/` (vanilla JS, niente framework/npm/build):
  - `app.js`: Tippspiel, router (`ROUTES` per il primo segmento dell'hash, `TABS` per la barra),
    helper (`h()`, `t()`, `store`), loader `load()` con decrittazione, `window.TSP` per il Piano;
  - `i18n.js`: testi DE/IT; `style.css`: variabili chiaro/scuro;
  - Piano: `piano-core.js` (logica pura senza DOM: `window.PianoCore` + `module.exports`),
    `piano.js` (viste `#/piano`, `#/piano/corpo`, `#/piano/training`, `#/piano/impostazioni`,
    registrate con `TSP.addRoute`), `piano.css`, contenuti statici `piano/*.json`.
- `.github/workflows/`: `daily.yml` e `on-data.yml` (pipeline + commit del bot su `main`),
  `tests.yml` (pytest + node per PR e branch).

## Comandi

```bash
python -m pip install -r requirements.txt
python -m pytest -q
node --test "tests/js/*.test.js"     # Node >= 22; "node --test tests/js" non accetta una cartella
python -m engine.pipeline --daily
python -m http.server -d docs 8000   # anteprima su http://localhost:8000
```

## Regole

- **Privacy (regola dura)**: repo e sito sono pubblici. Profilo, pesate, check e note del Piano
  stanno solo in `localStorage` con chiavi `tsp.piano.*` (via `TSP.pstore`): mai in file del repo,
  commit, URL/hash, log o test. Nei test solo profili fittizi. Export/import toccano solo
  `tsp.piano.*` (mai il token GitHub). Nei testi del repo niente nomi, misure, abitudini o luoghi
  personali. Prima di ogni commit controllare il diff.
- **CSP** (`docs/index.html`): script solo da `'self'` e `cdn.jsdelivr.net` (Chart.js 4.4.1 con SRI),
  `connect-src` solo `'self'` e `api.github.com`; niente script inline, nessun CDN o font nuovo.
- **i18n**: ogni testo nuovo in DE e IT in `docs/i18n.js` (Piano: chiavi `piano.*`); i nomi dei
  piatti restano in tedesco. `tests/js/content.test.js` controlla la parità delle chiavi.
- **Stile**: IIFE, `var`, `h()` (solo testo, mai `innerHTML` con dati), `t()`, `store`; CSS con le
  variabili esistenti; mobile-first a 360 px, tap target ≥ 44 px, niente scroll orizzontale.
- **Non toccare**: `engine/model.py`, `recommend.py`, `rules.py`, `race.py`, `backtest.py`,
  `analyze.py`, `ingest.py`; i file generati `docs/data/*.json`; `data/*.csv`; `index.html` nella
  root (progetto separato). Workflow: solo aggiunte minime e motivate.
- `tests/test_dish_nutrition.py` non deve mai fallire per un piatto nuovo (regole di riserva +
  avviso): fallisce solo con file malformati o valori non plausibili.
- **Git**: lavorare su un branch (es. `feature/piano`) con PR verso `main`; mai push diretto su
  `main`, mai `--force`. Il bot committa ogni giorno su `main`: prima di aprire o aggiornare una PR,
  `git fetch` e merge di `main` nel branch.
