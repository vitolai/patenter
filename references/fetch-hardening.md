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

### USPTO PDF fallback (US patents only)

When Google Patents has no PDF link (recent publications not yet indexed,
page-scrape blocked), `uspto_pdf_url` / `fetch_uspto_pdf` pull the full-text
PDF straight from the USPTO image server:

```python
import sys; sys.path.insert(0, "scripts")
from patenter_ext.google_patents import uspto_pdf_url, fetch_uspto_pdf

uspto_pdf_url("US20260349174A1")
# -> https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/20260349174
path = fetch_uspto_pdf("US20260349174A1", "/tmp/US20260349174A1.pdf")
```

Notes:
- US publications/grants only — returns `None` for non-US identifiers.
- Uses plain urllib (HTTP/1.1); other clients hit HTTP/2 stream resets
  against this endpoint, so force HTTP/1.1 if reimplementing with curl.
- Validates `%PDF` magic + trailing `%%EOF`; fail-open (`None` on failure).
- Same retry/backoff constants as the xhr path; stdlib only, no new deps.

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
