---
name: portfolio-comparison
description: >
  Side-by-side multi-portfolio comparison. Mode A required for structured
  comparison. Supports 2+ companies. Mode C/B for best-effort overview.
---

# Portfolio Comparison

## Intake
1. Confirm search mode (A recommended; C/B for quick overview)
2. Get company names (2+)
3. Get technology area / CPC scope
4. Get date window
5. Confirm known aliases for each company

## Execution

### Mode A (google-patents)
1. For each company:
   - Fetch all patents (assignee search with normalized name)
   - Apply triage matrix (see `references/portfolio-triage.md`)
   - Calculate metrics
2. Compare side-by-side:
   - Filing velocity (5-year trend)
   - Technology overlap (shared CPC subclasses)
   - Technology divergence (unique CPC areas)
   - White-space identification (uncovered technology areas)
   - Geographic coverage comparison
   - Portfolio size comparison
   - Citation impact comparison
3. Strategic positioning analysis
4. Render report

### Mode C/B
1. Search for each company + "patent portfolio" / "patents held"
2. Extract available portfolio data
3. Best-effort comparison
4. Render with caveats

## Comparison Matrix

| Dimension | Company A | Company B | Company C | Winner |
|-----------|----------|----------|-----------|--------|
| Total patents | N | N | N | — |
| Filing velocity | N/yr | N/yr | N/yr | — |
| Tech diversity | X.X | X.X | X.X | — |
| Geographic spread | X.X | X.X | X.X | — |
| Citation impact | X.X | X.X | X.X | — |
| Active % | X% | X% | X% | — |
| Maintenance burden | $XXX | $XXX | $XXX | — |

## White-Space Identification
List technology areas (CPC subclasses) where NO company has coverage.

## Output Format
```markdown
## Portfolio Comparison — [Company A] vs [Company B] vs [Company C]

### Overview Table
[Comparison matrix above]

### Filing Velocity Comparison
[5-year trend chart for each company]

### Technology Overlap
[Venn diagram description: shared and unique CPC areas]

### White-Space Opportunities
- [CPC area] — [plain English] — no coverage from any company

### Strategic Positioning
- [Company A]: [strengths/weaknesses]
- [Company B]: [strengths/weaknesses]
- [Company C]: [strengths/weaknesses]

### Recommendations
1. [Priority action for each company]

---
*This is a technical assessment, not legal advice.*
```