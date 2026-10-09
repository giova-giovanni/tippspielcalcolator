"""Whole pipeline, as run by the GitHub Actions.

    python -m engine.pipeline                    # ingest (if xlsx changed) -> analysis -> backtest -> recommendation
    python -m engine.pipeline --daily            # fast: skip the backtest when backtest.json exists
    python -m engine.pipeline --tune             # also re-optimise the model hyper-parameters (slow)
    python -m engine.pipeline --today 2026-10-09 # pretend another day (debugging)
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import sys
import time
import zoneinfo

from .config import REPORTS, SITE_DATA, load_config


def now_local(cfg) -> dt.datetime:
    return dt.datetime.now(zoneinfo.ZoneInfo(cfg.get("timezone", "Europe/Rome")))


def _backtest_reusable() -> bool:
    """--daily may skip the backtest only if its outputs exist with the current encryption state."""
    import json

    want_enc = bool(os.environ.get("SITE_PASSPHRASE"))
    for name in ("backtest.json", "leaderboard.json"):
        path = SITE_DATA / name
        if not path.exists():
            return False
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            return False
        is_enc = isinstance(obj, dict) and "enc" in obj
        if is_enc != want_enc:
            return False
        if is_enc:
            from .output import read_site_json
            try:
                if read_site_json(name) is None:
                    return False
            except Exception:  # wrong passphrase / corrupt file
                return False
    return True


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--today", type=dt.date.fromisoformat)
    ap.add_argument("--daily", action="store_true", help="skip backtest if results exist")
    ap.add_argument("--tune", action="store_true", help="hyper-parameter search (slow)")
    ap.add_argument("--force-ingest", action="store_true")
    a = ap.parse_args(argv)

    cfg = load_config()
    now = now_local(cfg)
    today = a.today or now.date()
    t0 = time.time()

    from . import ingest
    ingest.run(if_changed=not a.force_ingest, today=today)

    from .data import refresh_csvs
    ds = refresh_csvs()
    print(f"[{time.time() - t0:5.1f}s] Daten: {len(ds.served)} servierte Menüs, {len(ds.tips)} Tipps")

    from . import analyze
    analyze.run(ds, today=today)
    print(f"[{time.time() - t0:5.1f}s] Analyse fertig")

    from . import backtest
    if a.tune:
        backtest.tune(ds)
        print(f"[{time.time() - t0:5.1f}s] Tuning fertig")
    if not (a.daily and not a.tune and _backtest_reusable()):
        backtest.run(ds, today=today)
        print(f"[{time.time() - t0:5.1f}s] Backtest fertig")

    from . import recommend
    recommend.run(ds, today=today, now=now if not a.today else None)
    print(f"[{time.time() - t0:5.1f}s] Empfehlung fertig")

    from . import site
    site.run(ds, today=today, now=now)
    print(f"[{time.time() - t0:5.1f}s] Website-Daten geschrieben ({'verschlüsselt' if os.environ.get('SITE_PASSPHRASE') else 'unverschlüsselt'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
