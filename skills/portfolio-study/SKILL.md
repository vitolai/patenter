---
name: portfolio-study
description: >
  Patent portfolio health assessment via triage matrix. Mode A required for
  structured triage. Mode C/B for best-effort overview.
---

# Portfolio Study

## Intake
1. Confirm search mode (A recommended for structured triage; C/B for quick overview)
2. Get company name
3. Get technology area / CPC scope (optional but recommended)
4. Get date window

## Execution

### Mode A (google-patents)
1. Fetch all patents for assignee (see `references/name-normalization.md` for name variants)
2. Classify each patent using triage matrix (see `references/portfolio-triage.md`):
   - **Active**: recent filings, maintained, in technology scope
   - **Dormant**: old filings, possibly lapsed, outside core tech
   - **Expired**: legal status expired
3. Calculate metrics:
   - Filing velocity (filings/year trend)
   - Tech diversity (Shannon entropy of CPC distribution)
   - Geographic spread (jurisdiction count)
   - Citation impact (avg forward citations)
   - Maintenance burden (est. annual cost)
4. Identify coverage gaps (product features with no patent coverage)
5. Assess risk exposure (inbound blocking patents, outbound enforcement, validity risk)
6. Render using `templates/portfolio-report-template.md`

### Mode C/B
1. Search for company + "patent portfolio" / "patents"
2. Extract available patent count and technology areas
3. Best-effort triage (may lack legal status data)
4. Render with caveats

## Triage Matrix
See `references/portfolio-triage.md` for full specification.

## Output
Use `templates/portfolio-report-template.md`. Include:
- Triage summary table (active/dormant/expired counts + maintenance cost)
- Filing velocity table
- Technology coverage table with gap analysis
- Geographic coverage table
- Risk exposure tables (inbound/outbound/validity)
- Metrics table with benchmarks
- Recommendations (3+ priority action items)
- Legal disclaimer