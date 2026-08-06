#!/usr/bin/env python3
"""Shared Google Patents URL builders + hardened paginated fetch.

Thin wrapper around the xhr endpoint with the cache/dedup layer applied.
Kept importable standalone so watch_brief.py and other modules share one
source of truth for URL construction (mirrors patenter.py's builders).
"""

from __future__ import annotations

from urllib.parse import quote_plus

from modules.cache import ResponseCache, fetch_json, dedup_patents


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
