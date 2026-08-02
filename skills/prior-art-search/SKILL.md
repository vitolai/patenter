---
name: prior-art-search
description: >
  Multi-source prior art search with 5 sub-use-case routing (novelty / FTO /
  landscape / diligence / litigation). Mode C uses agent's built-in web_search.
  Mode A uses web_fetch against Google Patents, Espacenet, USPTO.
  Mode B uses direct web search API calls (Brave/Exa/Tavily/SerpAPI).
---

# Prior Art Search

## Intake (3 forcing questions)

### Q1 — Invention description
Describe the invention in 2-3 sentences. What does it do, and what's new?
Refuse generic answers. Push: "What does it do that existing systems don't?"

### Q2 — Sub-use-case commitment
Pick one:
- **Novelty** — am I novel enough to file?
- **FTO** — will I get sued if I ship?
- **Landscape** — who else plays here?
- **Diligence** — does target really own X?
- **Litigation** — kill a specific patent

### Q3 — Search mode
- **Mode C** (`agent-search`, default): agent's built-in `web_search` — no API keys needed
- **Mode A** (`google-patents`): structured data from Google Patents / Espacenet / USPTO
- **Mode B** (`web-search-api`): direct API calls to Brave / Exa / Tavily / SerpAPI

If Mode A → ask jurisdictions (US / EP / CN / JP / KR / PCT / worldwide).
If Mode C or B → skip jurisdiction question.

## Search Strategy by Sub-Use-Case

### Novelty (Mode A)
1. 3 narrow queries on invention-specific terminology (Google Patents)
2. 2 broad concept queries with synonyms (Google Patents)
3. 1 CPC-class query (Espacenet)
4. 1 US deep dive (USPTO PPS)
Rank: closest art first, claim-differentiation emphasis.

### FTO (Mode A)
1. 2 broad queries on core concept (Google Patents)
2. Filter: active patents only, target jurisdictions
3. 2 assignee-focused queries on known competitors
4. 1 CPC-class sweep (Espacenet)
Rank: claim-by-claim risk emphasis.

### Landscape (Mode A)
1. 2 broad technology queries (Google Patents)
2. 1 CPC trend query (Espacenet)
3. 1 applicant sweep across top filers
4. Filing-trend analysis by year and jurisdiction
Rank: filer map + investment hotspots.

### Diligence (Mode A)
1. Assignee-specific query for portfolio scope
2. Assignment chain verification (USPTO assignment search)
3. Jurisdiction coverage check
4. Legal status audit
Rank: portfolio table + ownership verification.

### Litigation (Mode A)
1. Target patent number → full record fetch
2. Citation backward search (who does it cite)
3. Forward citation search (who cites it)
4. Adjacent art before priority date
Rank: knock-out candidates by relevance.

### Mode C (any sub-use-case)
1. 3-5 web_search queries combining invention + "patent" + competitor names
2. Extract patent numbers from results
3. Optional: follow-up web_fetch on Google Patents for specific patents
4. Best-effort summary from available text

### Mode B (any sub-use-case)
1. 3-5 API queries (Brave/Exa/Tavily/SerpAPI) with keys from `.env`
2. Extract patent numbers from API results
3. Optional: follow-up web_fetch on Google Patents for specific patents
4. Best-effort summary from available text

## Execution Rules
- 1 query/sec rate limit
- Cite only patents from this session's tool calls
- Three-count tracking: queries sent / patents received / patents cited
- Retry: failure → 3s wait → retry once → log. 3 consecutive failures → stop.

## Output Format
```markdown
## Prior Art Report — [Sub-Use-Case]

### Search Parameters
- Mode: C / A / B
- Jurisdictions: [list]
- Date range: [start] to [end]
- Queries sent: N | Patents received: N | Patents cited: N

### Closest Art (ranked)
1. **[Patent Number]** — [Title]
   - Assignee: [name]
   - Filing date: [date]
   - CPC: [classes]
   - Relevance: [High/Medium/Low] — [rationale]
   - Key difference from invention: [text]
   - URL: [link]

### Summary
[2-3 sentence plain-language summary]

### Caveats
- [snapshot-lag, publication-lag, row-cap, etc.]
```