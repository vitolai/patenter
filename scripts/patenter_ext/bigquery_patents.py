#!/usr/bin/env python3
"""BQ: Optional Google Patents BigQuery module (gated, cost-aware).

Brings bulk analysis capability (landscape / portfolio at scale) that the free
xhr endpoint cannot serve. Design follows LeonardHope's
`Claude-Skill-for-Patent-Landscape-Analysis`:
  - Uses `patents-public-data.patents.publications` table.
  - Cost ceiling via `max_bytes_scanned` (BigQuery charges by bytes scanned).
  - Lazy import of `google-cloud-bigquery` + gcloud ADC auth.

CRITICAL design stance (keeps patenter "lite"):
  - This is OPTIONAL and OFF by default. patenter's default Mode A (xhr) still
    needs zero infra. BigQuery is an explicit opt-in via env/flag.
  - Unbounded queries are rejected (must supply CPC prefixes + date range)
    to prevent runaway cost — exactly like LeonardHope's `fetch_landscape`.
  - Fails gracefully to "BigQuery not available" if deps/auth missing, so the
    rest of the CLI keeps working.

Env:
  PATENTER_BQ=1                 # enable BigQuery mode
  GOOGLE_CLOUD_PROJECT=my-proj  # GCP project (for cost accounting)

Usage:
    python3 -m modules.bigquery --cpc G06N,G06V --date-from 2024-01-01 \
        --date-to 2024-12-31 --countries US,EP --row-limit 5000
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime

# --- optional dependency gate ---------------------------------------------

def _bq_available() -> bool:
    if os.environ.get("PATENTER_BQ") != "1":
        return False
    try:
        import google.cloud.bigquery  # noqa: F401
    except Exception:  # noqa: BLE001
        return False
    return True


# --- query builder (mirrors LeonardHope) ----------------------------------

_LANDSCAPE_QUERY = """
SELECT
  p.publication_number,
  p.country_code,
  p.kind_code,
  p.filing_date,
  p.priority_date,
  p.family_id,
  (SELECT t.text FROM UNNEST(p.title_localized) t WHERE t.language = 'en' LIMIT 1) AS title,
  ARRAY(SELECT DISTINCT a.name FROM UNNEST(p.assignee_harmonized) a WHERE a.name IS NOT NULL) AS assignees,
  ARRAY(SELECT DISTINCT c.code FROM UNNEST(p.cpc) c WHERE c.code IS NOT NULL) AS cpc_codes
FROM `patents-public-data.patents.publications` p
WHERE
  p.filing_date >= @date_from
  AND p.filing_date <= @date_to
  AND EXISTS (
    SELECT 1 FROM UNNEST(p.cpc) c WHERE {cpc_where}
  )
  {country_clause}
LIMIT @row_limit
"""


def _build_cpc_where(num_prefixes: int) -> str:
    if num_prefixes == 0:
        return "TRUE"
    return " OR ".join(f"c.code LIKE CONCAT(@cpc_prefix_{i}, '%')" for i in range(num_prefixes))


def _yyyymmdd(iso: str) -> int:
    return int(iso.replace("-", ""))


def _int_date_to_iso(v) -> str:
    if v is None:
        return ""
    s = str(int(v))
    if len(s) != 8:
        return ""
    return f"{s[0:4]}-{s[4:6]}-{s[6:8]}"


def fetch_landscape(cpc_prefixes: list[str], date_from: str, date_to: str,
                    countries: list[str] | None = None, row_limit: int = 5000,
                    max_bytes_scanned: int = 20_000_000_000) -> dict:
    """Run a cost-gated landscape query against Google Patents BigQuery.

    Returns a dict with records + metadata, or an error dict if BigQuery
    is unavailable / auth missing.
    """
    if not _bq_available():
        return {
            "error": "BigQuery disabled or deps missing. Set PATENTER_BQ=1 and "
                     "pip install google-cloud-bigquery; run "
                     "`gcloud auth application-default login`.",
            "records": [],
        }
    if not cpc_prefixes:
        return {"error": "At least one CPC prefix required (cost control).", "records": []}
    if not date_from or not date_to:
        return {"error": "date_from and date_to required (YYYY-MM-DD).", "records": []}

    from google.cloud import bigquery

    client = bigquery.Client(project=os.environ.get("GOOGLE_CLOUD_PROJECT"))

    cpc_where = _build_cpc_where(len(cpc_prefixes))
    country_clause = ""
    params = []
    for i, prefix in enumerate(cpc_prefixes):
        params.append(bigquery.ScalarQueryParameter(f"cpc_prefix_{i}", "STRING", prefix.strip().upper()))
    params.append(bigquery.ScalarQueryParameter("date_from", "INT64", _yyyymmdd(date_from)))
    params.append(bigquery.ScalarQueryParameter("date_to", "INT64", _yyyymmdd(date_to)))
    if countries:
        placeholders = ", ".join(f"@country_{i}" for i in range(len(countries)))
        country_clause = f"AND p.country_code IN ({placeholders})"
        for i, c in enumerate(countries):
            params.append(bigquery.ScalarQueryParameter(f"country_{i}", "STRING", c.strip().upper()))
    params.append(bigquery.ScalarQueryParameter("row_limit", "INT64", int(row_limit)))

    sql = _LANDSCAPE_QUERY.format(cpc_where=cpc_where, country_clause=country_clause)

    job_config = bigquery.QueryJobConfig(
        query_parameters=params,
        maximum_bytes_billed=max_bytes_scanned,
    )
    job = client.query(sql, job_config=job_config)
    rows = list(job.result())

    records = []
    for r in rows:
        filing = _int_date_to_iso(r.get("filing_date"))
        records.append({
            "publication_number": r.get("publication_number") or "",
            "country_code": (r.get("country_code") or "").upper(),
            "filing_date": filing,
            "priority_date": _int_date_to_iso(r.get("priority_date")),
            "family_id": str(r.get("family_id") or ""),
            "title": r.get("title") or "",
            "assignees": [a for a in (r.get("assignees") or []) if a],
            "cpc_codes": [c for c in (r.get("cpc_codes") or []) if c],
        })

    return {
        "source": "google_patents_bigquery",
        "table": "patents-public-data.patents.publications",
        "cpc_prefixes": cpc_prefixes,
        "date_from": date_from,
        "date_to": date_to,
        "countries": countries or [],
        "row_count": len(records),
        "truncated": len(rows) >= row_limit,
        "records": records,
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Google Patents BigQuery landscape fetch (gated).")
    ap.add_argument("--cpc", required=True, help="Comma-separated CPC prefixes, e.g. G06N,G06V")
    ap.add_argument("--date-from", required=True, help="YYYY-MM-DD")
    ap.add_argument("--date-to", required=True, help="YYYY-MM-DD")
    ap.add_argument("--countries", default="", help="Comma-separated country codes")
    ap.add_argument("--row-limit", type=int, default=5000)
    ap.add_argument("--max-bytes", type=int, default=20_000_000_000)
    ap.add_argument("--output", default="", help="Output JSON path")
    args = ap.parse_args()

    res = fetch_landscape(
        [c.strip() for c in args.cpc.split(",") if c.strip()],
        args.date_from, args.date_to,
        countries=[c.strip() for c in args.countries.split(",") if c.strip()],
        row_limit=args.row_limit, max_bytes_scanned=args.max_bytes,
    )
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2, ensure_ascii=False)
        print(f"✅ BigQuery result saved: {args.output}")
    else:
        print(json.dumps(res, indent=2, ensure_ascii=False)[:2000])
