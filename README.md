# Patenter

Unified patent intelligence CLI — prior art search, patent summary,
comparison, core patent finding, portfolio study, portfolio comparison, FTO
analysis, landscape visualization, claim design-around, competitor watch,
DOCX report export, and optional BigQuery bulk analysis.

## Features

- **8 sub-skills** covering the full patent research lifecycle
- **3 search modes** (A: google-patents, B: web-search-api, C: agent-search)
  **+ optional BigQuery bulk mode**
- **No MCP required** — works with `web_search` and `web_fetch` tools
- **Landscape visualization** (Mode A) — interactive self-contained HTML via Jinja2
- **CPC translation** — 250+ subclass codes → plain English
- **Name normalization** — 100+ legal suffixes, multi-language
- **Full date precision** — YYYYMMDD across all commands
- **Extension modules** — claim design-around, competitor watch, DOCX export,
  hardened fetch + cache, BigQuery (see below)

## Extension Modules (scripts/patenter_ext/)

| Module | Capability | Guide |
|--------|-----------|-------|
| `design_around.py` | Claim-gap & design-around analysis (element parsing, white-space flags, Omit/Replace/Reorganize/Combine) | `references/design-around-guide.md` |
| `watch_brief.py` | Competitor IP watch (delta detection, HTML/MD brief, persistent state, cron-friendly) | `references/competitor-watch-guide.md` |
| `docx_export.py` | Export report context to a formatted `.docx` memo (needs `python-docx`) | `references/docx-export-guide.md` |
| `google_patents.py` | Fetch hardening — robust xhr fetch with retries, dedup, page-scrape fallback on 503 | `references/fetch-hardening.md` |
| `cache.py` | Fetch hardening — SQLite/FTS5 cache for patents + embeddings | `references/fetch-hardening.md` |
| `bigquery_patents.py` | Optional BigQuery bulk landscape (needs GCP creds; graceful no-op) | `references/bigquery-guide.md` |

## Quick Start

```bash
# Clone
git clone https://github.com/vitolai/patenter.git
cd patenter

# Install core dependencies
pip install jinja2 pytest

# Optional: DOCX export
pip install python-docx

# Optional: BigQuery bulk mode (see references/bigquery-guide.md)
pip install google-cloud-bigquery
gcloud auth application-default login
export PATENTER_BQ=1
export GOOGLE_CLOUD_PROJECT=my-gcp-project

# Run tests
python3 -m pytest tests/ -v

# CLI usage
python3 scripts/patenter.py search --mode A --use-case novelty --query "wireless power transfer"
python3 scripts/patenter.py portfolio-compare --mode A --companies "Company A,Company B"
python3 scripts/patenter.py landscape --mode A --technology "3D printing" --date-from 20200101 --date-to 20261231
```

## Search Modes

| Mode | Flag | Mechanism | Structured | Viz | Key? |
|------|------|-----------|-----------|-----|------|
| A | `google-patents` | Google Patents xhr + browser URLs | ✅ | ✅ | No |
| B | `web-search-api` | Brave / Exa / Tavily / SerpAPI | ❌ | ❌ | Yes (`.env`) |
| C | `agent-search` | Agent's built-in `web_search` | ❌ | ❌ | No |
| BQ | `bigquery` | Google Patents Public Dataset (bulk landscape) | ✅ | ✅ | GCP creds (ADC) |

Mode A is the default and needs **zero infrastructure**. BigQuery (BQ) is an
explicit opt-in for bulk/analytical scans; see `references/bigquery-guide.md`
for the ADC setup (it is **not** a paste-an-API-key flow).

## CLI Commands

Core CLI (`scripts/patenter.py`):

| Command | Description |
|---------|-------------|
| `search` | Prior art search (novelty, FTO, landscape, diligence, litigation) |
| `summary` | Patent summary by technology area |
| `compare` | Side-by-side patent comparison |
| `core` | Core patent finder |
| `portfolio` | Portfolio study for a company |
| `portfolio-compare` | Multi-company portfolio comparison |
| `fto` | Freedom to operate analysis |
| `landscape` | Technology landscape visualization (HTML) |
| `render` | Jinja2 template renderer |
| `fetch-xhr` | Paginated Google Patents xhr fetcher |

Extension modules run standalone (`python3 scripts/patenter_ext/<mod>.py ...`)
or as Python libraries — see each module's guide in `references/`.

## Repo Structure

```
patenter/
├── SKILL.md              # Master skill definition
├── skills/               # 8 sub-skills
├── references/           # 11 reference docs (methodology + module guides)
├── templates/            # 5 output templates
├── agents/               # 3 agent definitions
├── scripts/patenter.py   # CLI + library
├── scripts/patenter_ext/ # design-around, competitor watch, DOCX export, fetch hardening, BigQuery modules
└── tests/                # smoke tests
```

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
- `references/bigquery-guide.md` — BigQuery setup + usage (ADC, cost control)

## License

MIT
