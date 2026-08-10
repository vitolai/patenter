# BigQuery User Guide — patenter_ext/bigquery_patents.py

This module adds **bulk landscape / portfolio analysis** via Google Patents
Public Datasets on BigQuery — capability the free `xhr` endpoint (Mode A)
cannot serve at scale.

> ⚠️ **Not an API-key tool.** BigQuery authenticates with **GCP credentials
> (Application Default Credentials / ADC)**, not a single API key string.
> Follow the setup below — it's a one-time ~5 min process.

> **GCP-hosted nodes (e.g. gcpn) — different auth path (2026-08-10, verified):**
> If the node is itself a GCP VM, ADC comes from the **metadata service
> account** — you do NOT run `gcloud auth application-default login`.
> BUT the VM's **OAuth scopes must include BigQuery**
> (`https://www.googleapis.com/auth/bigquery`). The default compute scopes
> (devstorage.read_only, logging.write, monitoring.write, etc.) do NOT include
> BigQuery → you get `403 ACCESS_TOKEN_SCOPE_INSUFFICIENT`. To fix, recreate
> the VM with the `bigquery` scope, or use a service-account key via
> `GOOGLE_APPLICATION_CREDENTIALS`. Also, `gcloud` is usually pre-installed
> via apt on GCP VMs (just not on PATH — use
> `/usr/lib/google-cloud-sdk/bin/gcloud`).

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
3. **Python client library** (use a **venv** — Debian 12's pip is
   externally-managed / PEP 668 and blocks system-wide installs):
   ```bash
   cd ~/repos/skills/patenter
   python3 -m venv .venv
   .venv/bin/pip install google-cloud-bigquery
   ```
   Then run patenter's BQ module with `.venv/bin/python` (not bare `python3`).
4. **Authenticate (ADC)** — this is the step that replaces an "API key":
   ```bash
   gcloud auth application-default login
   ```
   Opens a browser → sign in with the GCP account that owns the project.
5. **Set the project** (ADC login alone leaves it unset):
   ```bash
   gcloud config set project <your-gcp-project>
   ```

> ⚠️ **Cost reality (2026-08-10, verified)**: The Google Patents public tables
> (`patents.publications` and `google_patents_research.publications_*`) are
> **UNPARTITIONED (~170M rows)** — every query scans the **full table
> (~34-42 GB)** regardless of date/CPC filters. So each query burns ~34-42 GB
> of the **1 TB/month free quota** (~24-29 queries free), then ~$0.17-0.21/query
> over quota. It is NOT "a few GB" — budget accordingly.

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
cd ~/repos/skills/patenter
.venv/bin/python scripts/patenter_ext/bigquery_patents.py \
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
| `--max-bytes` | ❌ | Cost ceiling in bytes; default `45_000_000_000` (45 GB) |

---

## 4. Cost control (important)

BigQuery bills by **bytes scanned**, not rows returned. This module:

- **Rejects unbounded queries** — you MUST supply CPC prefixes + date range.
- Sets `maximum_bytes_billed=45GB` by default → the query **fails instead of
  racking up cost** if it would scan more than 45 GB.
- Raises/lowers the ceiling with `--max-bytes`.

> ⚠️ Because the patents table is **unpartitioned**, even a narrow
> CPC-prefixed, date-bounded query scans the **full table (~34-42 GB)**. The
> 45 GB default ceiling is set so real queries actually run. Each query burns
> ~34-42 GB of the 1 TB/month free quota (~24-29 queries free), then
> ~$0.17-0.21/query over quota.

---

## 5. What the query returns

For each patent record:
- `publication_number`, `country_code`, `kind_code`
- `filing_date`, `priority_date`, `family_id`
- `title` (English — from `title_localized`, an ARRAY of STRUCTs; the module
  extracts the `en` text)
- `assignees` (harmonized names)
- `cpc_codes` (list)

---

## 6. Failure modes (graceful)

If anything is missing, the module returns an error dict and **does NOT break
the rest of the CLI**:

| Symptom | Cause | Fix |
|---------|-------|-----|
| `BigQuery disabled or deps missing` | `PATENTER_BQ` not `1` OR lib missing | `export PATENTER_BQ=1` + install lib in the venv (`.venv/bin/pip install google-cloud-bigquery`) |
| `DefaultCredentialsError` | No ADC auth | `gcloud auth application-default login` |
| `Project not found / permission denied` | Wrong project / no BigQuery API | `gcloud config set project <proj>` + enable BigQuery API, check IAM |
| `Query exceeded limit` | Would scan > `--max-bytes` (unpartitioned table needs ~34-42 GB) | Narrow CPC/date, or raise `--max-bytes` above 45 GB |

---

## 7. Why not an API key?

The BigQuery Public Datasets require a **Google Cloud project + authorized
credentials** (IAM), not a bearer API key. If you only have a plain API key
and want "paste-a-key-and-search", use instead:

- **Mode A** (`xhr`) — free, no key, structured (default)
- **Mode B** (`web-search-api`) — Brave / Exa / Tavily / SerpAPI, paste key & search

BigQuery is the right choice **only** when you need bulk/analytical scans the
free endpoint can't do — and that needs the GCP setup above.
