---
name: core-patent-finder
description: >
  Core/foundational patent identification with distinctiveness scoring (0-13).
  Mode A for structured data and scoring. Mode C/B for best-effort identification.
---

# Core Patent Finder

## Intake
1. Confirm search mode (C default / A / B)
2. Get technology area and date window
3. Confirm scoring dimensions priority

## Execution

### Mode A (google-patents)
1. Fetch all patents in technology area + date window
2. For each patent, calculate:
   - **Foundational score**: how early in the technology window
   - **Cross-disciplinary score**: number of distinct CPC subclasses
   - **Distinctiveness score**: 0-13 across 4 dimensions:
     - Claim breadth (0-3)
     - Citation density (0-3)
     - Assignee prominence (0-3)
     - Technology novelty (0-4)
   - **Overall score**: weighted sum
3. Rank and identify:
   - Foundational patents (earliest, highest backward citations)
   - Cross-disciplinary patents (most CPC subclasses)
   - Top applicants' newest patents
4. Render report

### Mode C/B
1. Search for technology + "foundational patent" / "core patent"
2. Extract available patents with dates and assignees
3. Best-effort scoring (may lack citation data)
4. Render report with caveats

## Scoring Dimensions (0-13 total)

| Dimension | Range | Description |
|-----------|-------|-------------|
| Claim breadth | 0-3 | How broad are the independent claims? |
| Citation density | 0-3 | Backward + forward citation count |
| Assignee prominence | 0-3 | Is the assignee a major player? |
| Technology novelty | 0-4 | How novel was this at filing time? |

## Output Format
```markdown
## Core Patent Report — [Technology]

### Foundational Patents
| Patent # | Title | Assignee | Filed | Score | Rationale |
|----------|-------|----------|-------|-------|----------|

### Cross-Disciplinary Patents
| Patent # | Title | CPC Subclasses | Assignee | Score |
|----------|-------|----------------|----------|-------|

### Top Applicants' Newest
| Patent # | Title | Assignee | Filed | Score |
|----------|-------|----------|-------|-------|

### Distinctiveness Leaderboard
| Rank | Patent # | Score | Foundational | Cross-Disc | Novelty |
|------|----------|-------|--------------|------------|---------|
```