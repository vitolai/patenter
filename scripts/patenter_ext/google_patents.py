#!/usr/bin/env python3
"""Shared Google Patents URL builders + hardened paginated fetch.

Thin wrapper around the xhr endpoint with the cache/dedup layer applied.
Kept importable standalone so watch_brief.py and other modules share one
source of truth for URL construction (mirrors patenter.py's builders).
"""

from __future__ import annotations

import re
import time
import urllib.request
from pathlib import Path as _Path
from urllib.parse import quote_plus

try:
    from modules.cache import ResponseCache, fetch_json, dedup_patents, USER_AGENT, MAX_RETRIES, RETRY_BASE_SECONDS
except ImportError:  # in-repo layout (scripts/ on sys.path)
    from patenter_ext.cache import ResponseCache, fetch_json, dedup_patents, USER_AGENT, MAX_RETRIES, RETRY_BASE_SECONDS


def google_patents_xhr_url(query: str, jurisdiction: str = "",
                           date_from: str = "", date_to: str = "",
                           doc_type: str = "", page: int = 0) -> str:
    params = [f"q={quote_plus(query)}"]
    if jurisdiction:
        params.append(f"country={jurisdiction}")
    if date_from:
        params.append(f"before=filing:{date_from}")
    if date_to:
        params.append(f"after=filing:{date_to}")
    if doc_type:
        params.append(f"type={doc_type}")
    if page > 0:
        params.append(f"page={page}")
    return f"https://patents.google.com/xhr/query?url={quote_plus('&'.join(params))}"


def google_patents_detail_xhr_url(patent_id: str) -> str:
    pid = patent_id.replace("patent/", "")
    if pid.endswith("/en"):
        pid = pid[:-3]
    return f"https://patents.google.com/xhr/patent/{pid}/en"


USPTO_PDF_BASE = "https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf"


def uspto_pdf_url(pub_number: str) -> str | None:
    """Direct USPTO full-text PDF URL. US publications/grants ONLY.

    Returns None for non-US identifiers (this endpoint serves USPTO
    documents only). Normalizes "US20260349174A1" / "US12422726B2" /
    "patent/US20260349174A1/en" to the bare numeric portion.
    """
    token = pub_number.split()[0].replace("patent/", "").strip("/").upper().split("/")[0]
    if not token.startswith("US"):
        return None
    body = token[2:]
    # strip kind code suffix (A1, A9, B1, B2, ...) so its digit does not
    # leak into the numeric portion, e.g. US20260349174A1 -> 20260349174
    body = re.sub(r"[A-Z]+\d*$", "", body)
    digits = re.sub(r"\D", "", body)
    if not digits:
        return None
    return f"{USPTO_PDF_BASE}/{digits}"


def fetch_uspto_pdf(pub_number, dest, timeout=120, max_retries=MAX_RETRIES):
    import random
    url = uspto_pdf_url(pub_number)
    if url is None:
        print(f"  USPTO PDF fetch skipped (non-US identifier): {pub_number}")
        return None
    dest = _Path(dest)
    last_err = None
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/pdf,*/*"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
            if not data.startswith(b"%PDF"):
                raise ValueError("response is not a PDF")
            if b"%%EOF" not in data[-64:]:
                raise ValueError("truncated PDF (missing %%EOF)")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            return str(dest)
        except Exception as e:
            last_err = e
            if attempt < max_retries - 1:
                time.sleep(RETRY_BASE_SECONDS * (2 ** attempt) + random.uniform(0, 0.5))
    print(f"  USPTO PDF fetch failed for {pub_number}: {last_err}")
    return None



def fetch_patents(query: str, date_from: str = "", date_to: str = "",
                  jurisdiction: str = "", max_pages: int = 10,
                  cache: ResponseCache | None = None,
                  use_cache: bool = True) -> dict:
    """Paginated, cached, deduped fetch across Google Patents xhr pages.

    Returns {"total", "pages", "patents"} where patents are deduped by
    publication_number.
    """
    cache = cache or ResponseCache()
    all_patents: list[dict] = []
    total = 0
    total_pages = 0

    for page in range(max_pages):
        url = google_patents_xhr_url(query, jurisdiction, date_from, date_to, "", page)
        data = fetch_json(url, cache=cache, use_cache=use_cache)
        results = data.get("results", {})
        if page == 0:
            total = results.get("total_num_results", 0)
            total_pages = results.get("total_num_pages", 0)

        cluster = results.get("cluster", [])
        if not cluster:
            break

        for c in cluster:
            for item in c.get("result", []):
                p = item.get("patent", {})
                countries = [
                    cs.get("country_code")
                    for cs in p.get("family_metadata", {}).get("aggregated", {})
                    .get("country_status", [])
                ]
                all_patents.append({
                    "title": p.get("title", "").strip(),
                    "pub_number": p.get("publication_number", ""),
                    "filing_date": p.get("filing_date", ""),
                    "publication_date": p.get("publication_date", ""),
                    "assignee": p.get("assignee", ""),
                    "inventor": p.get("inventor", ""),
                    "countries": countries,
                    "cpc": [x.get("code") for x in p.get("cpc", []) if x.get("code")],
                    "link": f"https://patents.google.com/patent/{p.get('publication_number', '')}/en",
                })

        if page + 1 >= total_pages:
            break

    return {
        "total": total,
        "pages": total_pages,
        "patents": dedup_patents(all_patents),
    }
