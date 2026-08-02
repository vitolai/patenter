---
name: patent-summary
description: >
  Structured patent summary with stat tiles, applicant leaderboard, filing trends,
  and technology breakdown. Mode A required for full structured output.
  Mode C/B produce best-effort summaries.
---

# Patent Summary

## Intake
1. Confirm search mode (C default / A / B)
2. Get technology area (2-3 sentence description)
3. Get date range
4. If Mode A → confirm jurisdictions

## Execution

### Mode A (google-patents)
1. Fetch Google Patents results for technology query
2. Extract: patent number, title, assignee, filing date, CPC, abstract
3. Normalize assignee names (see `references/name-normalization.md`)
4. Translate CPC codes (see `references/cpc-translation.md`)
5. Calculate stat tiles, applicant leaderboard, filing trends, tech breakdown
6. Apply trailing-year exclusion heuristic
7. Render using `templates/summary-template.md`

### Mode C/B (agent-search / web-search-api)
1. Run web searches for technology + "patent"
2. Extract patent numbers and metadata from text results
3. Best-effort stat tiles (may be incomplete)
4. Render using `templates/summary-template.md` with caveats

## Stat Tiles
- Patent families count
- Distinct applicants count
- Jurisdictions count
- Peak filing year

## Output
Use `templates/summary-template.md`. Include methodology section with:
- Data source, query, date range, jurisdictions, document types
- Name merges applied
- Caveats (row-cap, snapshot-lag, trailing-year exclusion)