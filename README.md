# Patenter

Unified patent intelligence CLI — prior art search, patent summary,
comparison, core patent finding, portfolio study, portfolio comparison, FTO
analysis, and landscape visualization.

## Features

- **8 sub-skills** covering the full patent research lifecycle
- **3 search modes** (A: google-patents, B: web-search-api, C: agent-search)
- **No MCP required** — works with `web_search` and `web_fetch` tools
- **Landscape visualization** (Mode A) — interactive self-contained HTML via Jinja2
- **CPC translation** — 250+ subclass codes → plain English
- **Name normalization** — 100+ legal suffixes, multi-language
- **Full date precision** — YYYYMMDD across all commands

## Extension Modules (scripts/patenter_ext/)

| Module | Capability |
|--------|-----------|
| `design_around.py` | Claim-gap & design-around analysis (element parsing, white-space flags, Omit/Replace/Reorganize/Combine strategies) |
| `watch_brief.py` | Competitor IP watch (delta detection, HTML/MD brief, persistent state, cron-friendly) |
| `docx_export.py` | Export report context to a formatted `.docx` memo (needs `python-docx`) |
| `google_patents.py` | Fetch hardening — robust xhr fetch with retries, dedup, page-scrape fallback on 503 |
| `cache.py` | Fetch hardening — SQLite/FTS5 cache for patents + embeddings |
| `bigquery_patents.py` | Optional BigQuery bulk landscape (needs GCP creds; graceful no-op) |

## Quick Start

```bash
# Clone
git clone https://github.com/vitolai/patenter.git
cd patenter

# Install dependencies
pip install jinja2 pytest

# Run tests
python3 -m pytest tests/ -v

# CLI usage
python3 scripts/patenter.py search --mode A --use-case novelty --query "wireless power transfer"
python3 scripts/patenter.py portfolio-compare --mode A --companies "Company A,Company B"
python3 scripts/patenter.py landscape --mode A --technology "3D printing" --date-from 20200101 --date-to 20261231
```

## Search Modes

| Mode | Flag | Mechanism | Structured | Viz |
|------|------|-----------|-----------|-----|
| A | `google-patents` | Google Patents xhr + browser URLs | ✅ | ✅ |
| B | `web-search-api` | Brave / Exa / Tavily / SerpAPI | ❌ | ❌ |
| C | `agent-search` | Agent's built-in `web_search` | ❌ | ❌ |

## CLI Commands

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

## Repo Structure

```
patenter/
├── SKILL.md              # Master skill definition
├── skills/               # 8 sub-skills
├── references/           # 6 reference docs
├── templates/            # 5 output templates
├── agents/               # 3 agent definitions
├── scripts/patenter.py   # CLI + library
├── scripts/patenter_ext/ # design-around, competitor watch, DOCX export, fetch hardening, BigQuery modules
└── tests/                # smoke tests
```

## License

MIT
