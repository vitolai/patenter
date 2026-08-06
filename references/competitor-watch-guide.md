# Competitor IP Watch — patenter_ext/watch_brief.py

Automated **competitor patent monitoring** with delta detection and brief
generation. Cron-friendly: run periodically, it compares against the previous
run's state and reports only what's **new**.

## When to use
- Track a competitor's new filings week-over-week.
- Get an alert-style brief (HTML + Markdown) of only the delta.

## What it does
1. Fetches a company's recent patents (via `google_patents.py` hardened xhr).
2. Compares against the **persisted state** from the previous run.
3. Reports **new filings detected** (delta vs last run).
4. Writes an HTML + Markdown brief to disk.

## Usage
```bash
# CLI
python3 scripts/patenter_ext/watch_brief.py --watch "Company A,Company B"

# Or as a module
import sys; sys.path.insert(0, "scripts")
from patenter_ext.watch_brief import run_watch
run_watch(["Company A", "Company B"])
```

## Cron example
```
# every Monday 08:00 — competitor watch brief
0 8 * * 1  cd /path/to/patenter && python3 scripts/patenter_ext/watch_brief.py \
  --watch "Company A,Company B" --out-dir ./briefs
```

## Output
- `{Company}_brief.md` — Markdown brief
- `{Company}_brief.html` — HTML brief
- Persistent state file (JSON) tracking last-seen patents for delta detection

## Notes
- First run has no prior state → reports all fetched patents as "new".
- Subsequent runs only flag the delta.
- See `references/fetch-hardening.md` for the underlying fetch layer.
