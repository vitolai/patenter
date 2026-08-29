# Portfolio Triage Matrix

## Vitality Classification

### Active
- **Criteria**: Filed or granted within last 20 years, maintenance fees current
- **Sub-types**:
  - **Strategic** — core technology, actively enforced or licensed
  - **Defensive** — held to deter suits, not actively monetized
  - **Commercial** — directly tied to a revenue-generating product
- **Action**: Monitor, maintain, leverage

### Dormant
- **Criteria**: Granted but no recent activity (no continuations, no enforcement, no licensing in 3+ years)
- **Risk**: Maintenance fees draining budget without ROI
- **Action**: Review for abandonment or reactivation

### Expired
- **Criteria**: > 20 years from filing OR maintenance fees lapsed
- **Action**: Archive, public domain contribution

## Coverage Gap Analysis

### Product-to-Patent Mapping
| Product Feature | Relevant CPC | Patents Covering | Gap? |
|---------------|-------------|-----------------|------|
| Feature A | G06N 3/04 | 5 patents | No |
| Feature B | H01L 21/00 | 0 patents | YES — GAP |
| Feature C | H04W 12/00 | 1 patent | Fragile — 1 patent only |

### Geographic Intent — Designated vs Entered

Do not confuse a patent's **designated** jurisdictions (from PCT/WO filings) with
**entered** national phases. A WO application designates many states, but only
those actually entered within the 30/31-month deadline from priority provide
protection.

| Patent | Priority | 31-mo EP/CN/US deadline | Status today | Entered? |
|--------|----------|-------------------------|--------------|----------|
| P1 | 2023-07-20 | 2026-02-20 | Passed | Verify (EPO/CNIPA/USPTO) |
| P2 | 2024-07-19 | 2027-02-19 | Open (~6 mo) | Pending |

- **Designated** = listed in the family's `country_status`; NOT protected.
- **Entered** = national phase actually filed; protected.
- Flag lapsed/expired entry windows as **coverage gaps**, not protected markets.
- Verify actual entry against EPO Register, CNIPA, USPTO PAIR, WIPO PatentScope.

See `references/pct-national-phase.md` for the full methodology.

### Gap Severity
- **Critical**: Core product feature with no coverage
- **High**: Core feature with single-patent coverage (fragile)
- **Medium**: Non-core feature with no coverage
- **Low**: Non-core feature with single-patent coverage

## Risk Exposure

### Inbound Risk (Others' patents blocking us)
- Search competitor portfolios in our CPC space
- Identify active patents with overlapping claims
- Classify: HIGH / MEDIUM / LOW based on claim overlap

### Outbound Risk (Our patents being infringed)
- Identify portfolio patents likely infringed by competitors
- Classify enforcement opportunity: STRONG / MODERATE / WEAK

### Validity Risk (Our patents vulnerable to challenge)
- Patents with thin prior art differentiation
- Patents with broad claims likely to face validity challenges
- Patents in heavily litigated technology areas

## Metrics

| Metric | Formula | Benchmark |
|--------|---------|-----------|
| Filing velocity | Patents/year (5-year trend) | ↑ or → healthy |
| Tech diversity | Distinct CPC subclasses / total patents | > 0.3 healthy |
| Geographic spread | Distinct jurisdictions / total | > 0.5 healthy |
| Citation impact | Avg forward citations per patent | > 5 strong |
| Maintenance burden | Active patents × avg annual fee | < 5% of R&D budget healthy |