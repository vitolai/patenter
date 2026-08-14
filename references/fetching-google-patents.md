# Fetching Google Patents — Pitfalls & Workarounds (Mode A)

Practical notes on reliably querying Google Patents' `xhr` endpoint for
portfolio enumeration and prior-art search. These pitfalls were observed
empirically and are the reason the CLI offers both `assignee` and `inventor`
query paths.

## Pitfall 1: double-encoding of the `url` parameter

The `xhr/query` endpoint takes a `url` parameter that is itself a URL-encoded
query string. If you encode the whole thing twice (or fail to encode the inner
query), Google Patents returns an empty or malformed result set.

- Correct: `https://patents.google.com/xhr/query?url=<urlencoded(query)>`
- The inner query (e.g. `q=...&country=US`) must be encoded once, then the
  whole `url=...` value encoded again.

The CLI's `google_patents_xhr_url()` handles this correctly — do not hand-roll
the URL when calling the endpoint directly.

## Pitfall 2: Firecrawl / 503 bypass

The `xhr` endpoint can return HTTP 503 (rate-limit / bot protection) when hit
with a bare `urllib` request. Workarounds, in order of preference:

1. Send a realistic `User-Agent` + `Referer: https://patents.google.com/`
   header set (the CLI does this).
2. If 503 persists, fall back to a page-scrape of the browser URL
   (`patents.google.com/patent/<id>/en`) and parse the rendered HTML.
3. As a last resort, route the fetch through a headless browser (Playwright)
   or a scraping service.

The `patenter_ext/google_patents.py` module implements retries + the
page-scrape fallback — prefer it over a raw `urllib` call for production use.

## Pitfall 3: the `assignee` facet is unreliable — don't trust 0 or noise

`assignee:"<Company>"` (quoted exact phrase) returns **0 results** even when
the company owns patents; `assignee:<Company>` (unquoted) is fuzzy and noisy.
Verified on a small AI-chip portfolio (anonymized as "Acme Chips"):

- `assignee:"Acme Chips"` → `total_num_results: 0` (matching quirk)
- `assignee:Acme Chips` → many results, but only 1 is a real Acme patent; the
  rest are substring/transliteration false-positives (e.g. unrelated
  historical names that merely share a token)
- `inventor:"<Founder Name>"` → complete patent family, clean

**Workaround** — enumerate a company's portfolio by inventor, not assignee:
`inventor:"<First Last>"`. Inventor names are stable across the family even
when the assignee string is recorded inconsistently (esp. for PCT/WO filings
and companies whose assignee isn't normalized). Combine multiple named
founders with OR to catch the whole portfolio.

> **Rule of thumb:** never treat a 0-result (or a noisy one) from the
> `assignee` facet as evidence of no IP. Always cross-check with an
> `inventor:"<founder>"` sweep before concluding a company has no patents in
> a field.
