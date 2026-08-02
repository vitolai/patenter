---
name: patent-comparison
description: >
  Claim-level and technology-route patent comparison. Mode A for structured
  claim text. Mode C/B for best-effort comparison from available text.
---

# Patent Comparison

## Intake
1. Confirm search mode (C default / A / B)
2. Get patent numbers (2+ for comparison)
3. Confirm comparison type: claim-level / tech-route / both

## Execution

### Mode A (google-patents)
1. Fetch full patent records from Google Patents for each patent number
2. Parse independent claims into elements (see `references/claim-mapping.md`)
3. Map elements side-by-side
4. Score differentiation (0-10)
5. Compare technology routes (approach, advantages, limitations)
6. Analyze citation overlap
7. Render using `templates/comparison-template.md`

### Mode C/B
1. Search for each patent number via web_search/API
2. Extract available claim text and metadata
3. Best-effort element mapping
4. Render using `templates/comparison-template.md` with caveats

## Claim Mapping Rules
- Parse independent claims only (claim 1 + any other independent)
- Map by concept, not exact wording
- Abstraction principle: compare concepts, not implementation specifics
- Differentiation score: 0=identical, 10=completely different

## Output
Use `templates/comparison-template.md`. Include:
- Overview table (patent #, title, assignee, filed, CPC, citations)
- Claim-level comparison table
- Technology-route comparison
- Citation comparison
- Summary assessment (2-3 sentences)