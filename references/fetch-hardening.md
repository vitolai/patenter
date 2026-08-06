# Fetch Hardening & Cache — patenter_ext/google_patents.py + cache.py

Robustness layer over the free Google Patents `xhr` endpoint so fetches
survive rate-limits, drop-outs, and duplicates — and repeated runs don't
re-fetch or re-embed the same data.

## google_patents.py — hardened fetch

Wraps the raw xhr endpoint with:

- **Retries** — transient failures are retried with backoff.
- **Dedup** — duplicate patent numbers are dropped from results.
- **Page-scrape fallback** — when the xhr detail endpoint returns HTTP 503
  (rate-limited), falls back to scraping the patents.google.com page so the
  detail/claims fetch still completes (fail-open, not fail-hard).
- **Consistent headers** — browser-like User-Agent + Referer to avoid blocks.

### Usage
```python
import sys; sys.path.insert(0, "scripts")
from patenter_ext.google_patents import google_patents_xhr_url

# Build a search URL
url = google_patents_xhr_url("wireless power transfer", date_from="20200101",
                             date_to="20261231")
```
Pair with `cache.py` to persist results.

## cache.py — SQLite/FTS5 persistence

Stores fetched patents (and optionally embeddings) locally so a
**`--semantic` / repeated run does not re-fetch or re-embed the whole corpus**
every time.

### Why
- Avoids redundant network calls and redundant embedding computation.
- Keeps patenter **lite** — embeddings are computed on demand and persisted,
  not recomputed per run.

### Design
- **SQLite/FTS5** file cache (no external DB server).
- Keyed by patent/query so repeated lookups are near-instant.
- On-demand embed + persist; cache hit returns instantly.

### Usage
```python
import sys; sys.path.insert(0, "scripts")
from patenter_ext.cache import PatentCache

cache = PatentCache("patents.db")
# cache.get(key) -> hit or miss; cache.put(key, value) to store
```

## When it matters
- **Watch mode** (`watch_brief.py`) re-runs on a schedule — cache avoids
  hammering Google Patents every run.
- **Semantic search** — embeddings cached so only new patents get embedded.
- **Rate-limit recovery** — the 503 fallback + retries keep runs alive where
  a naive fetch would fail.

## Notes
- The xhr endpoint is free and keyless, but **rate-limited**; the hardening
  layer is what makes scheduled/repeated use practical.
- Cache files are local; add them to `.gitignore` (not committed).
