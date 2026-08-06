# BigQuery User Guide — patenter_ext/bigquery_patents.py

This module adds **bulk landscape / portfolio analysis** via Google Patents
Public Datasets on BigQuery — capability the free `xhr` endpoint (Mode A)
cannot serve at scale.

> ⚠️ **Not an API-key tool.** BigQuery authenticates with **GCP credentials
> (Application Default Credentials / ADC)**, not a single API key string.
> Follow the setup below — it's a one-time ~5 min process.

---

## 1. Prerequisites (one-time setup)

1. **A Google Cloud Project** with **BigQuery API enabled**:
   - Go to <https://console.cloud.google.com/apis/library/bigquery.googleapis.com>
   - Select your project → **Enable**
2. **Google Cloud CLI (`gcloud`)** installed:
   ```bash
   # Debian/Ubuntu
   sudo apt-get install google-cloud-cli
   # or via the install script: https://cloud.google.com/sdk/docs/install
   ```
3. **Python client library**:
   ```bash
   pip install google-cloud-bigquery
   ```
4. **Authenticate (ADC)** — this is the step that replaces an "API key":
   ```bash
   gcloud auth application-default login
   ```
   Opens a browser → sign in with the GCP account that owns the project.

> The BigQuery Public Dataset (`patents-public-data.patents.publications`) is
> **free to query** up to a monthly quota. You only pay if you exceed the
> free-tier scanning bytes (see Cost Control below).

---

## 2. Enable the module

BigQuery is **OFF by default** (keeps patenter lite). Set two env vars:

```bash
export PATENTER_BQ=1                          # enable BigQuery mode
export GOOGLE_CLOUD_PROJECT=my-gcp-project    # for cost accounting
```

Optional: pin a billing project even when ADC is from another project:
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

---

## 3. Usage

### CLI (standalone)
```bash
python3 -m modules.bigquery \
  --cpc G06N,G06V \
  --date-from 2024-01-01 \
  --date-to 2024-12-31 \
  --countries US,EP \
  --row-limit 5000 \
  --output landscape.json
```

### As a Python library
```python
import sys
sys.path.insert(0, "scripts")
from patenter_ext.bigquery_patents import fetch_landscape

res = fetch_landscape(
    cpc_prefixes=["G06N", "G06V"],
    date_from="2024-01-01",
    date_to="2024-12-31",
    countries=["US", "EP"],
    row_limit=5000,
)
print(res["row_count"], "records")
```

### Required arguments
| Arg | Required | Notes |
|-----|----------|-------|
| `--cpc` | ✅ | Comma-separated CPC prefixes, e.g. `G06N,G06V`. **Mandatory for cost control.** |
| `--date-from` | ✅ | `YYYY-MM-DD` filing date start |
| `--date-to` | ✅ | `YYYY-MM-DD` filing date end |
| `--countries` | ❌ | Comma-separated country codes (`US,EP,CN,...`) |
| `--row-limit` | ❌ | Default `5000` |
| `--max-bytes` | ❌ | Cost ceiling in bytes; default `20_000_000_000` (20 GB) |

---

## 4. Cost control (important)

BigQuery bills by **bytes scanned**, not rows returned. This module:

- **Rejects unbounded queries** — you MUST supply CPC prefixes + date range.
- Sets `maximum_bytes_billed=20GB` by default → the query **fails instead of
  racking up cost** if it would scan more than 20 GB.
- Raises/lowers the ceiling with `--max-bytes`.

A typical CPC-prefixed, date-bounded landscape scan is a few GB at most and
**falls inside the free monthly quota** for most use.

---

## 5. What the query returns

For each patent record:
- `publication_number`, `country_code`, `kind_code`
- `filing_date`, `priority_date`, `family_id`
- `title` (English)
- `assignees` (harmonized names)
- `cpc_codes` (list)

---

## 6. Failure modes (graceful)

If anything is missing, the module returns an error dict and **does NOT break
the rest of the CLI**:

| Symptom | Cause | Fix |
|---------|-------|-----|
| `BigQuery disabled or deps missing` | `PATENTER_BQ` not `1` OR lib missing | `export PATENTER_BQ=1` + `pip install google-cloud-bigquery` |
| `DefaultCredentialsError` | No ADC auth | `gcloud auth application-default login` |
| `Project not found / permission denied` | Wrong project / no BigQuery API | Set `GOOGLE_CLOUD_PROJECT`, enable BigQuery API, check IAM |
| `Query exceeded limit` | Would scan > `--max-bytes` | Narrow CPC/date, or raise `--max-bytes` |

---

## 7. Why not an API key?

The BigQuery Public Datasets require a **Google Cloud project + authorized
credentials** (IAM), not a bearer API key. If you only have a plain API key
and want "paste-a-key-and-search", use instead:

- **Mode A** (`xhr`) — free, no key, structured (default)
- **Mode B** (`web-search-api`) — Brave / Exa / Tavily / SerpAPI, paste key & search

BigQuery is the right choice **only** when you need bulk/analytical scans the
free endpoint can't do — and that needs the GCP setup above.
