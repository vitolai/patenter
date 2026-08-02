# Search Strategy — Query Patterns per Sub-Use-Case

## Source Priority (Mode A)
1. **Google Patents** (`patents.google.com`) — workhorse, no auth, broad coverage
2. **Espacenet** (`worldwide.espacenet.com`) — global coverage, non-US art
3. **USPTO PPS** (`ppubs.uspto.gov`) — US deep dive
4. **Lens.org** (`www.lens.org`) — citation graph, BYOK API key optional

## Source Priority (Mode B)
1. **Brave Search** — fast web results
2. **Exa** — semantic search, good for technical concepts
3. **Tavily** — research-focused, good snippets
4. **SerpAPI** — Google Patents via SerpAPI (paid)

## Query Patterns

### Novelty
- 3 narrow queries: invention-specific terminology (Google Patents)
- 2 broad concept queries with synonyms (Google Patents)
- 1 CPC-class query (Espacenet)
- 1 US deep dive (USPTO PPS)
- Rank: closest art first, claim-differentiation emphasis

### FTO
- 2 broad queries: core concept (Google Patents)
- Filter: active patents only, target jurisdictions
- 2 assignee-focused queries: known competitors
- 1 CPC-class sweep (Espacenet)
- Rank: claim-by-claim risk emphasis

### Landscape
- 2 broad technology queries (Google Patents)
- 1 CPC trend query (Espacenet)
- 1 applicant sweep: top filers
- Filing-trend analysis by year and jurisdiction
- Rank: filer map + investment hotspots

### Diligence
- Assignee-specific query: portfolio scope
- Assignment chain verification (USPTO assignment search)
- Jurisdiction coverage check
- Legal status audit
- Rank: portfolio table + ownership verification

### Litigation
- Target patent number → full record fetch
- Backward citation search (who it cites)
- Forward citation search (who cites it)
- Adjacent art before priority date
- Rank: knock-out candidates by relevance

## Rate Limits
- Google Patents: no auth but rate-limits per IP (~1 req/sec safe)
- Espacenet: similar rate limits
- USPTO PPS: no documented limit, be conservative
- Lens.org: free tier = 1000 queries/month
- Mode B: follow each search API's rate limits

## URL Patterns (Mode A)
- Google Patents search: `https://patents.google.com/?q=[query]&country=[CC]&before=filing:[date]&after=filing:[date]&type=PATENT`
- Google Patents detail: `https://patents.google.com/patent/[PATENT_NUMBER]/en`
- Espacenet search: `https://worldwide.espacenet.com/patent/search?q=[query]`
- USPTO PPS: `https://ppubs.uspto.gov/dirsearch-public/print/downloadDirect?fileName=pat_biblio_[number]`