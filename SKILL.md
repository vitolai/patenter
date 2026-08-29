---
name: patenter
description: >
  Unified patent intelligence skill — prior art search, patent summary, comparison,
  core patent finding, portfolio study, portfolio comparison, FTO analysis, and
  landscape visualization. No MCP required. Three search modes: google-patents
  (Mode A, default), web-search-api (Mode B), agent-search (Mode C). Triggers:
  "patent", "prior art", "patent search", "patent landscape", "patent portfolio",
  "patent comparison", "core patent", "FTO", "freedom to operate", "patent
  analysis", "IP landscape".
---

# Patenter — Unified Agent Skill

A comprehensive patent research and analysis skill covering 8 sub-skills with
three selectable search modes. No MCP server required.

## Three Search Modes

| Mode | Flag | Data Source | API Keys | Structured | Landscape Viz | Default |
|------|------|-------------|----------|-----------|---------------|---------|
| A | `google-patents` | Google Patents `xhr` JSON endpoint | ❌ None | ✅ Yes | ✅ Enabled | ✅ Yes |
| B | `web-search-api` | Direct API → Brave / Exa / Tavily / SerpAPI | ✅ `.env` | ❌ No | ❌ Disabled | No |
| C | `agent-search` | Agent's built-in `web_search` tool | ❌ None | ❌ No | ❌ Disabled | No |

### Mode A — `google-patents` (Default, recommended)

Uses the Google Patents `xhr` JSON endpoint (`patents.google.com/xhr/query?url=...`)
which returns structured patent data without authentication:

- **Search endpoint**: `https://patents.google.com/xhr/query?url=q%3D{query}`
- **Detail endpoint**: `https://patents.google.com/xhr/patent/{patent_id}/en`
- Also fetches from **Espacenet** (`worldwide.espacenet.com`) and **USPTO PPS**
  (`ppubs.uspto.gov`) for complementary data.

Returns: patent number, title, assignee, filing date, publication date, CPC
classes, abstract, claims text, citations, legal status, jurisdiction, country
status, figures, PDF links.

Enables: landscape visualization, portfolio comparison, core patent finding
with structured scoring.

**Mode A+ (BigQuery / "BQ")**: Google Patents Public Datasets on BigQuery for
bulk landscape analysis — requires GCP credentials. **NOT a default mode.**

> **BQ policy (MANDATORY)**: The agent runs **Mode A / B / C by default** and
> **NEVER invokes BigQuery unless the user explicitly says "BQ"** (or
> "BigQuery"). BigQuery is a heavy, cost-billed opt-in — see the cost note
> below. When the user does request BQ, it runs only on a node that has GCP
> credentials + the `google-cloud-bigquery` library installed. This is an
> **opt-in per node** — set up once on any node the user enables; NOT a
> per-node template concern.

### Mode B — `web-search-api` (API-powered broad research)

Uses general web search APIs directly (with keys from `.env`):
- Brave Search API, Exa Search API, Tavily Search API, SerpAPI

Returns: unstructured text snippets with URLs. Faster for bulk searches.

Limitations: cannot generate visualizations or structured portfolio analytics.

### Mode C — `agent-search` (Fallback / quick research)

Uses the AI agent's built-in `web_search` tool. No API keys needed — the agent
handles search internally. Best for quick research and general patent discovery.

Returns: unstructured text snippets with URLs, agent-curated results.

Limitations: same as Mode B — no visualizations or structured analytics.

## Mode Priority

1. **Mode A** (default) — structured data, enables all features
2. **Mode B** — when Mode A unavailable or for supplementary search
3. **Mode C** — fallback when no API keys available
4. **BQ (BigQuery)** — **ONLY on explicit user request** ("BQ"). Never default.

## BigQuery Cost Note (2026-08-10)

- The Google Patents public tables are **unpartitioned (~170M rows)** — every
  query scans the **full table (~34 GB)** regardless of filters.
- Each BQ query burns ~34 GB of the **1 TB/month free quota** (~29 queries
  free), then **~$0.17/query** over quota.
- The module's default cost ceiling is **45 GB** (raised from 20 GB) so queries
  actually run; it fails instead of over-billing if a query would exceed it.
- **Deployment (opt-in per node)**: GCP credentials + the
  `google-cloud-bigquery` library are installed only on node(s) that opt in.
  Any node may be enabled at the user's discretion. Other nodes no-op
  gracefully. This is NOT a per-node template concern.
- Use BQ only for bulk/analytical landscape scans the free xhr endpoint can't
  do. For typical lookups, Mode A is free and sufficient.

## Sub-Skills

### 1. prior-art-search
Multi-source prior art search with 5 sub-use-case routing:
- **Novelty** — narrow + claims-text focused
- **FTO** — broad + active patents only, jurisdiction-filtered
- **Landscape** — breadth + filer tally + CPC trends
- **Diligence** — specific assignee + portfolio scope + assignment chain
- **Litigation** — target patent + adjacent art before priority date

### 2. patent-summary
Structured patent summary with:
- Plain-language headline + 4 stat tiles
- Applicant leaderboard (normalized names)
- Filing trend analysis (trailing-year exclusion heuristic)
- Technology-area breakdown (CPC → plain English)
- Methodology section with caveats

### 3. patent-comparison
Claim-level and technology-route comparison:
- Side-by-side claim element mapping
- Technology route comparison with evidence
- Differentiation scoring (novel feature identification)

### 4. core-patent-finder
Core/foundational patent identification:
- Foundational patents (earliest in technology window)
- Cross-disciplinary patents (most CPC subclasses)
- Distinctiveness scoring (0-13 scale across 4 dimensions)
- Top applicants' newest patents in the field

> **PCT guardrail:** Google Patents `country_status` lists *designated* states, not
> *entered* national phases. Do not rank importance by country-status breadth
> alone; verify national-phase entry against EPO/USPTO/CNIPA and account for
> 30/31-month deadlines. See `references/pct-national-phase.md`.

### 5. portfolio-study
Portfolio health assessment via triage matrix:
- Vitality: active / dormant / expired
- Coverage gaps: unprotected innovation areas
- Risk exposure: FTO threats
- Filing velocity, tech-area distribution, maintenance cost analysis

> **PCT guardrail:** Google Patents `country_status` lists *designated* states, not
> *entered* national phases. Distinguish designated vs entered jurisdictions and
> account for 30/31-month national-phase deadlines when assessing geographic
> coverage. See `references/pct-national-phase.md`.

### 6. portfolio-comparison
Side-by-side multi-portfolio comparison:
- Filing velocity comparison
- Tech-area overlap / divergence mapping
- White-space identification (uncovered areas)
- Strategic positioning analysis

### 7. fto-analysis
Freedom-to-operate screening:
- Blocking patent identification
- Claim-by-claim risk assessment
- Design-around suggestions
- Jurisdiction-filtered (active patents only)

### 8. landscape-visualizer (Mode A only)
Interactive self-contained HTML report (Jinja2-rendered):
- World map with EPC member-state overlay
- Filing trends (stacked area chart by jurisdiction)
- Technology breakdown (CPC translated to plain English)
- Notable patents spotlight (4 views)
- Export: PNG, SVG, CSV, PDF

## Extension Modules (scripts/patenter_ext/)

Additional capability modules bundled under `scripts/patenter_ext/`:

| Module | Purpose |
|--------|---------|
| `design_around.py` | **Claim-gap & design-around analysis** — parse independent claims into elements, classify kind (structural/functional/quantifiable/mixed), flag unclaimed white-space dimensions, generate Omit/Replace/Reorganize/Combine alternatives |
| `watch_brief.py` | **Competitor IP watch** — delta detection vs prior run, HTML/MD brief generation, persistent state (cron-friendly) |
| `docx_export.py` | **DOCX export** — export report context (JSON) to a formatted `.docx` memo |
| `google_patents.py` | **Fetch hardening** — robust Google Patents xhr fetch with retries, dedup, page-scrape fallback (detail endpoint rate-limit 503 handling) |
| `cache.py` | **Fetch hardening** — SQLite/FTS5 cache for fetched patents + embeddings (avoids re-fetch/re-embed per run) |
| `bigquery_patents.py` | **BigQuery** — optional bulk landscape queries over Google Patents Public Datasets (requires GCP credentials); graceful no-op if absent |

These extend the CLI workflow; the existing `patenter.py` CLI remains the entry point, with these modules importable for programmatic or cron-driven use.

## Intake Protocol

Before any analysis, confirm:
1. **Search mode**: Mode A (`google-patents`, default) / B (`web-search-api`) / C (`agent-search`)
2. **Sub-use-case**: Which of the 8 skills to invoke
3. **Technology area**: Invention/concept description in 2-3 sentences
4. **Jurisdictions**: US / EP / CN / JP / KR / PCT / worldwide
5. **Time window**: Date range for analysis
6. **Known prior art**: Any known patent numbers (anchoring)

If any is unknown, ASK — do not assume. Stop rule: ask only the 2-3 that
most change the output.

## Execution Discipline

- Sequential search calls only (1 query/sec rate limit)
- Cite only patents returned by THIS session's tool calls
- Training knowledge labeled `[Not from search — reference information]`
- Three-count tracking: queries sent / patents received / patents cited
- Retry policy: on failure → wait 3s → retry once → log. After 3 consecutive
  failures: stop, alert user

## Legal Disclaimer

This skill produces search signal and technical assessment, not legal advice.
Always consult a qualified patent attorney before filing or licensing decisions.

## References

- `references/search-strategy.md` — Query patterns per sub-use-case
- `references/claim-mapping.md` — Claim analysis methodology
- `references/fto-process.md` — FTO process + design-around framework
- `references/portfolio-triage.md` — Triage matrix specification
- `references/cpc-translation.md` — CPC → plain English map (250+ classes)
- `references/name-normalization.md` — Applicant name normalization rules
- `references/design-around-guide.md` — Claim-gap / design-around engine
- `references/competitor-watch-guide.md` — Competitor watch module
- `references/docx-export-guide.md` — DOCX memo export module
- `references/fetch-hardening.md` — Hardened fetch + cache layer
- `references/bigquery-guide.md` — BigQuery setup + usage (ADC auth, cost control)

## Extension Dependencies

- `docx_export.py` requires `python-docx`
- `bigquery_patents.py` requires `google-cloud-bigquery` (optional; module no-ops without it)

## Templates

- `templates/summary-template.md` — Patent summary output
- `templates/comparison-template.md` — Comparison report output
- `templates/portfolio-report-template.md` — Portfolio study output
- `templates/landscape-html-template.jinja` — Interactive HTML report (Mode A, Jinja2)

## Agents

- `agents/prior-art-searcher.md` — Autonomous multi-strategy search agent
- `agents/patent-analyst.md` — Analysis + comparison agent
- `agents/portfolio-auditor.md` — Portfolio health assessment agent