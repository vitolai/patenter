---
name: fto-analysis
description: >
  Freedom-to-operate screening with blocking patent identification and
  design-around suggestions. Mode A recommended for structured claim analysis.
  Mode C/B for preliminary screening.
---

# FTO Analysis

## Intake
1. Confirm search mode (A recommended for FTO; C/B for preliminary screening)
2. Get technology/product description (2-3 sentences)
3. Confirm jurisdictions (critical for FTO — patents are jurisdiction-specific)
4. Get known competitors or potential blockers (optional)

## Execution

### Mode A (google-patents)
1. Search for technology in target jurisdictions (active patents only)
2. For each potentially blocking patent:
   - Fetch full record with claims
   - Map product features to claim elements (see `references/fto-process.md`)
   - Assess risk: HIGH / MEDIUM / LOW
3. For HIGH risk patents:
   - Analyze design-around options
   - Check legal status (expired, lapsed, or active)
4. Render FTO report

### Mode C/B
1. Search for technology + "patent" + jurisdiction
2. Identify potentially relevant patents from text
3. Preliminary risk assessment (cannot do claim-level analysis)
4. Recommend Mode A follow-up for high-risk results

## Risk Levels

| Level | Criteria | Action |
|-------|----------|--------|
| HIGH | Product reads on independent claim | Design-around or license |
| MEDIUM | Product may read on dependent claim | Monitor or narrow product |
| LOW | No overlap | No action needed |

## Design-Around Framework
See `references/fto-process.md` for the design-around methodology.

## Output Format
```markdown
## FTO Screening Report — [Technology]

### Search Parameters
- Mode: C / A / B
- Jurisdictions: [list]
- Date range: [start] to [end]
- Queries sent: N | Patents received: N | Patents cited: N

### Blocking Patents
| Patent # | Title | Assignee | Risk | Overlapping CPC | Claim |
|----------|-------|----------|------|-----------------|-------|

### Design-Around Options (HIGH risk only)
| Patent # | Blocking Claim | Design-Around | Feasibility |
|----------|----------------|---------------|-------------|

### Clearance Summary
[2-3 sentence conclusion on FTO status]

---
*This is a technical assessment, not legal advice. Consult a patent attorney.*
```