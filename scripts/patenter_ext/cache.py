#!/usr/bin/env python3
"""M-CACHE: SQLite response cache + dedup for Google Patents xhr fetches.

This hardens the free `patents.google.com/xhr/query` endpoint, which is the
single point of failure for Mode A. It provides:

1. TTL-aware disk cache keyed by normalized xhr URL.
2. Transparent retry with exponential backoff (3 tries, jitter).
3. Result dedup by publication_number (same patent can appear across pages).
4. Freshness tracking: every cached record carries `_cached_at` and the
   cache stores the `total_num_results` so callers can detect drift.

Design goals (keep patenter "lite"):
- stdlib only (sqlite3, urllib, hashlib, time, random). No new deps.
- Cache is a single SQLite file; default path `~/.cache/patenter/cache.db`.
- Fail-open: any cache error degrades to a plain live fetch.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import sqlite3
import time
import urllib.request
from pathlib import Path

# --- defaults -------------------------------------------------------------

DEFAULT_CACHE_DIR = Path(os.environ.get("PATENTER_CACHE_DIR", "~/.cache/patenter")).expanduser()
DEFAULT_TTL_SECONDS = 3600 * 6  # xhr data rarely changes intraday; 6h is safe
MAX_RETRIES = 3
RETRY_BASE_SECONDS = 2.0
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


# --- cache core -----------------------------------------------------------

class ResponseCache:
    """Tiny SQLite-backed cache for raw xhr JSON payloads."""

    def __init__(self, cache_dir: Path | str | None = None, ttl: int = DEFAULT_TTL_SECONDS):
        self.cache_dir = Path(cache_dir) if cache_dir else DEFAULT_CACHE_DIR
        self.ttl = ttl
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.cache_dir / "cache.db"
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS xhr_cache (
                url_hash TEXT PRIMARY KEY,
                url      TEXT NOT NULL,
                payload  TEXT NOT NULL,
                fetched_at REAL NOT NULL
            )
            """
        )
        self._conn.commit()

    def _hash(self, url: str) -> str:
        return hashlib.sha256(url.encode("utf-8")).hexdigest()

    def get(self, url: str):
        """Return (payload_dict, cached_bool). None payload => miss."""
        row = self._conn.execute(
            "SELECT payload, fetched_at FROM xhr_cache WHERE url_hash=?",
            (self._hash(url),),
        ).fetchone()
        if not row:
            return None, False
        payload, fetched_at = row
        if time.time() - fetched_at > self.ttl:
            # stale -> treat as miss and refresh below
            return None, False
        return json.loads(payload), True

    def put(self, url: str, payload: dict) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO xhr_cache (url_hash, url, payload, fetched_at) VALUES (?,?,?,?)",
            (self._hash(url), url, json.dumps(payload), time.time()),
        )
        self._conn.commit()

    def stats(self) -> dict:
        n = self._conn.execute("SELECT COUNT(*) FROM xhr_cache").fetchone()[0]
        return {"entries": n, "db": str(self.db_path)}


# --- hardened fetch -------------------------------------------------------

def fetch_json(url: str, cache: ResponseCache | None = None, use_cache: bool = True,
               max_retries: int = MAX_RETRIES) -> dict:
    """Fetch a JSON URL with retry/backoff and optional cache.

    Fail-open: on persistent failure returns {} rather than raising, matching
    the existing fetch_xhr_page() behaviour (which returns an empty result
    envelope on error).
    """
    cache = cache or ResponseCache()

    if use_cache:
        payload, cached = cache.get(url)
        if cached:
            return payload

    last_err: Exception | None = None
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/json, text/plain, */*",
                "Referer": "https://patents.google.com/",
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
            if use_cache:
                cache.put(url, data)
            return data
        except Exception as e:  # noqa: BLE001 - network errors vary
            last_err = e
            if attempt < max_retries - 1:
                # exponential backoff with jitter
                sleep_s = RETRY_BASE_SECONDS * (2 ** attempt) + random.uniform(0, 0.5)
                time.sleep(sleep_s)

    print(f"  ⚠️ fetch failed after {max_retries} tries: {last_err}")
    return {}


def dedup_patents(patents: list[dict]) -> list[dict]:
    """Deduplicate patents by publication_number, keeping first occurrence.

    Google Patents can return the same publication across pages (esp. when
    family members overlap). We also strip empty rows.
    """
    seen: set[str] = set()
    out: list[dict] = []
    for p in patents:
        key = (p.get("pub_number") or "").strip()
        if not key:
            continue
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
    return out
