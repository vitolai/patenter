#!/usr/bin/env python3
"""patenter: Unified patent intelligence CLI and library.

Usage:
    python3 patenter.py search --mode A --use-case novelty --query "wireless power transfer"
    python3 patenter.py summary --mode A --technology "3D printing" --date-from 20200101 --date-to 20261231
    python3 patenter.py compare --mode A --patents US12345678B2,US87654321B2
    python3 patenter.py core --mode A --technology "hybrid bonding" --date-from 20200101 --date-to 20261231
    python3 patenter.py portfolio --mode A --company "Example Corporation"
    python3 patenter.py portfolio-compare --mode A --companies "Company A,Company B"
    python3 patenter.py fto --mode A --technology "wireless charging" --jurisdictions US,EP
    python3 patenter.py landscape --mode A --technology "additive manufacturing" --date-from 20200101 --date-to 20261231
    python3 patenter.py render --template landscape-html-template.jinja --output report.html
"""

import argparse
import sys
import re
import json
from pathlib import Path
from urllib.parse import quote_plus

VERSION = "0.4.0"
SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent

# --- Mode A: Google Patents URL Builders ---

def google_patents_url(query, jurisdiction="", date_from="", date_to="", doc_type=""):
    """Google Patents browser URL (Mode A, human-facing)."""
    base = "https://patents.google.com/?q=" + quote_plus(query)
    if jurisdiction:
        base += f"&country={jurisdiction}"
    if date_from:
        base += f"&before=filing:{date_from}"
    if date_to:
        base += f"&after=filing:{date_to}"
    if doc_type:
        base += f"&type={doc_type}"
    return base

def google_patents_xhr_url(query, jurisdiction="", date_from="", date_to="", doc_type="", page=0):
    """Google Patents xhr JSON endpoint (Mode A, structured API).

    Returns structured JSON without authentication. Used by web_fetch.
    """
    params = [f"q={quote_plus(query)}"]
    if jurisdiction:
        params.append(f"country={jurisdiction}")
    if date_from:
        params.append(f"before=filing:{date_from}")
    if date_to:
        params.append(f"after=filing:{date_to}")
    if doc_type:
        params.append(f"type={doc_type}")
    if page > 0:
        params.append(f"page={page}")
    encoded = "&".join(params)
    return f"https://patents.google.com/xhr/query?url={quote_plus(encoded)}"

def google_patents_detail_xhr_url(patent_id):
    """Google Patents detail xhr JSON endpoint (Mode A).

    patent_id example: 'US12345678B2' or 'patent/US12345678B2/en'
    """
    # Normalize: strip 'patent/' prefix and '/en' suffix if present
    pid = patent_id.replace("patent/", "")
    if pid.endswith("/en"):
        pid = pid[:-3]
    return f"https://patents.google.com/xhr/patent/{pid}/en"

def espacenet_url(query):
    """Espacenet search URL (Mode A supplementary)."""
    return "https://worldwide.espacenet.com/patent/search?q=" + quote_plus(query)

def uspto_url(query):
    """USPTO PPS search URL (Mode A supplementary)."""
    return "https://ppubs.uspto.gov/dirsearch-public/search?q=" + quote_plus(query)

# --- Mode B: Web Search API Hints ---

def web_search_api_hint(query, api="brave"):
    """Return search URL hint for Mode B (direct API calls)."""
    hints = {
        "brave": f"Brave Search API: GET https://api.search.brave.com/res/v1/web/search?q={quote_plus(query)}",
        "exa": f"Exa Search API: POST https://api.exa.ai/search with query={query}",
        "tavily": f"Tavily API: POST https://api.tavily.com/search with query={query}",
        "serpapi": f"SerpAPI: GET https://serpapi.com/search?q={quote_plus(query)}",
    }
    return hints.get(api, hints["brave"])

# --- Mode C: Agent Search Hint ---

def agent_search_hint(query):
    """Return hint for Mode C (agent's built-in web_search)."""
    return f"Use agent's built-in web_search tool with query: patent {query}"

# --- Utility Functions ---

def normalize_assignee(name):
    """Normalize assignee name by stripping legal suffixes (iteratively)."""
    suffixes = [
        "股份有限公司", "有限公司", "株式会社", "有限会社", "合同会社",
        "주식회사", "유한회사",
        "GmbH & Co. KG", "S.A.R.L.", "S.A.S.", "S.A.U.", "S.L.U.",
        "S.p.A.", "S.r.l.", "S.n.c.", "S.a.s.",
        "L.L.C.", "L.L.P.", "L.P.",
        "Pte. Ltd.", "Pte Ltd", "Pty. Ltd.", "Pty Ltd",
        "N.V.", "B.V.", "S.A.",
        "Co., Ltd.", "Co.,Ltd.", "Co., Ltd",
        "Inc.", "Corp.", "Ltd.",
        "Corporation", "Limited", "Company",
        "Inc", "Corp", "Ltd", "Co.", "Co",
        "LLC", "LLP", "LP", "PLC", "AG", "SA", "GmbH", "KG",
        "BV", "NV", "Pte.", "Pty.", "K.K.", "KK",
        "公司", "集团", "Oy", "Ab", "AS", "ApS",
    ]
    result = name.strip().rstrip(',').strip()
    changed = True
    while changed:
        changed = False
        for suffix in suffixes:
            if result.endswith(suffix):
                result = result[:-len(suffix)].rstrip(',').strip()
                changed = True
                break
    return result

def translate_cpc(code):
    """Translate a CPC subclass code to plain English."""
    cpc_map_path = BASE_DIR / "references" / "cpc-translation.md"
    if not cpc_map_path.exists():
        return code
    with open(cpc_map_path, "r") as f:
        content = f.read()
    pattern = rf'\| {re.escape(code)} \| ([^|]+) \|'
    match = re.search(pattern, content)
    if match:
        return match.group(1).strip()
    return code

def render_jinja2(template_name, context, output_path=None):
    """Render a Jinja2 template with context data."""
    try:
        from jinja2 import Environment, FileSystemLoader
    except ImportError:
        print("❌ Jinja2 not installed. Run: pip install jinja2")
        sys.exit(1)

    template_dir = BASE_DIR / "templates"
    env = Environment(loader=FileSystemLoader(str(template_dir)), autoescape=True)
    template = env.get_template(template_name)
    rendered = template.render(**context)

    if output_path:
        Path(output_path).write_text(rendered, encoding="utf-8")
        print(f"✅ Rendered: {output_path}")
    return rendered

def fetch_xhr_page(query, date_from="", date_to="", page=0):
    """Fetch one page of Google Patents xhr JSON results (Mode A pagination).

    Returns parsed JSON dict. Requires requests library or falls back to urllib.
    """
    import urllib.request

    url = google_patents_xhr_url(query, "", date_from, date_to, "", page)
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://patents.google.com/',
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"⚠️ xhr fetch failed (page {page}): {e}")
        return {"results": {"total_num_results": 0, "cluster": []}}

def fetch_all_xhr_pages(query, date_from="", date_to="", max_pages=10):
    """Fetch multiple pages of Google Patents xhr results.

    Returns list of patent dicts with total count.
    """
    all_patents = []
    total = 0
    total_pages = 0

    for page in range(max_pages):
        data = fetch_xhr_page(query, date_from, date_to, page)
        results = data.get("results", {})
        if page == 0:
            total = results.get("total_num_results", 0)
            total_pages = results.get("total_num_pages", 0)
            print(f"  Total: {total} results across {total_pages} pages")

        cluster = results.get("cluster", [])
        if not cluster:
            break

        for c in cluster:
            for item in c.get("result", []):
                p = item.get("patent", {})
                countries = [cs.get("country_code") for cs in p.get("family_metadata", {}).get("aggregated", {}).get("country_status", [])]
                all_patents.append({
                    "title": p.get("title", "").strip(),
                    "pub_number": p.get("publication_number", ""),
                    "filing_date": p.get("filing_date", ""),
                    "publication_date": p.get("publication_date", ""),
                    "assignee": p.get("assignee", ""),
                    "inventor": p.get("inventor", ""),
                    "countries": countries,
                    "link": f"https://patents.google.com/patent/{p.get('publication_number', '')}/en",
                })

        if page + 1 >= total_pages:
            break

    return {"total": total, "pages": total_pages, "patents": all_patents}

# --- CLI Commands ---

def cmd_search(args):
    """Prior art search."""
    print(f"[patenter] Prior art search — Mode {args.mode}, Use-case: {args.use_case}")
    print(f"  Query: {args.query}")
    if args.mode == "A":
        print(f"  Google Patents (xhr JSON): {google_patents_xhr_url(args.query, args.jurisdiction or '', str(args.date_from or ''), str(args.date_to or ''))}")
        print(f"  Google Patents (browser):  {google_patents_url(args.query, args.jurisdiction or '', str(args.date_from or ''), str(args.date_to or ''))}")
        print(f"  Espacenet:      {espacenet_url(args.query)}")
        print(f"  USPTO PPS:      {uspto_url(args.query)}")
    elif args.mode == "B":
        for api in ["brave", "exa", "tavily", "serpapi"]:
            print(f"  {web_search_api_hint(args.query, api)}")
    else:
        print(f"  {agent_search_hint(args.query)}")
    print("\n  ⚠️ This CLI generates search URLs/hints. Use an AI agent with web_search/web_fetch")
    print("  to execute the actual searches and compile results.")

def cmd_summary(args):
    """Patent summary."""
    print(f"[patenter] Patent summary — Mode {args.mode}, Technology: {args.technology}")
    date_from = args.date_from or str(args.from_year)
    date_to = args.date_to or str(args.to_year)
    print(f"  Date range: {date_from}–{date_to}")
    if args.mode == "A":
        print(f"  Search URL (xhr): {google_patents_xhr_url(args.technology, '', date_from, date_to)}")
        print(f"  Search URL (web): {google_patents_url(args.technology, '', date_from, date_to)}")
    tmpl = BASE_DIR / "templates" / "summary-template.md"
    print(f"  Template: {tmpl}")

def cmd_compare(args):
    """Patent comparison."""
    patents = args.patents.split(",")
    print(f"[patenter] Patent comparison — Mode {args.mode}")
    print(f"  Patents: {patents}")
    if args.mode == "A":
        for p in patents:
            pid = p.strip()
            print(f"  Detail (xhr): {google_patents_detail_xhr_url(pid)}")
            print(f"  Detail (web): https://patents.google.com/patent/{pid}/en")
    tmpl = BASE_DIR / "templates" / "comparison-template.md"
    print(f"  Template: {tmpl}")

def cmd_core(args):
    """Core patent finding."""
    print(f"[patenter] Core patent finder — Mode {args.mode}")
    print(f"  Technology: {args.technology}")
    date_from = args.date_from or str(args.from_year)
    date_to = args.date_to or str(args.to_year)
    print(f"  Date range: {date_from}–{date_to}")
    if args.mode == "A":
        print(f"  Search URL (xhr): {google_patents_xhr_url(args.technology, '', date_from, date_to)}")
        print(f"  Search URL (web): {google_patents_url(args.technology, '', date_from, date_to)}")

def cmd_portfolio(args):
    """Portfolio study."""
    print(f"[patenter] Portfolio study — Mode {args.mode}")
    print(f"  Company: {args.company}")
    normalized = normalize_assignee(args.company)
    print(f"  Normalized: {normalized}")
    if args.mode == "A":
        query = f'assignee:"{args.company}"'
        print(f"  Search URL (xhr): {google_patents_xhr_url(query)}")
        print(f"  Search URL (web): {google_patents_url(query)}")
    elif args.mode == "B":
        for api in ["brave", "exa", "tavily", "serpapi"]:
            print(f"  {web_search_api_hint(f'patent {args.company}', api)}")
    else:
        print(f"  {agent_search_hint(f'patent {args.company}')}")
    tmpl = BASE_DIR / "templates" / "portfolio-report-template.md"
    print(f"  Template: {tmpl}")

def cmd_portfolio_compare(args):
    """Portfolio comparison."""
    companies = [c.strip() for c in args.companies.split(",")]
    print(f"[patenter] Portfolio comparison — Mode {args.mode}")
    print(f"  Companies: {companies}")
    if args.mode == "A":
        for c in companies:
            query = f'assignee:"{c}"'
            print(f"  {c} (xhr): {google_patents_xhr_url(query)}")
            print(f"  {c} (web): {google_patents_url(query)}")
    elif args.mode == "B":
        for c in companies:
            for api in ["brave", "exa", "tavily", "serpapi"]:
                print(f"  {web_search_api_hint(f'patent {c}', api)}")
    else:
        for c in companies:
            print(f"  {agent_search_hint(f'patent {c}')}")

def cmd_fto(args):
    """FTO analysis."""
    print(f"[patenter] FTO analysis — Mode {args.mode}")
    print(f"  Technology: {args.technology}")
    print(f"  Jurisdictions: {args.jurisdictions}")
    if args.mode == "A":
        print(f"  Search URL (xhr): {google_patents_xhr_url(args.technology, args.jurisdictions)}")

def cmd_landscape(args):
    """Landscape visualization (Mode A only)."""
    if args.mode != "A":
        print("[patenter] ❌ Landscape visualizer requires Mode A (google-patents).")
        sys.exit(1)
    print(f"[patenter] Landscape visualizer — Mode A")
    print(f"  Technology: {args.technology}")
    date_from = args.date_from or str(args.from_year)
    date_to = args.date_to or str(args.to_year)
    print(f"  Date range: {date_from}–{date_to}")
    tmpl = BASE_DIR / "templates" / "landscape-html-template.jinja"
    print(f"  Template: {tmpl}")
    print(f"  Render with: python3 scripts/patenter.py render --template landscape-html-template.jinja --output landscape.html")

def cmd_render(args):
    """Render a Jinja2 template."""
    context = {}
    if args.context_json:
        context = json.loads(args.context_json)
    elif args.context_file:
        with open(args.context_file) as f:
            context = json.load(f)
    render_jinja2(args.template, context, args.output)

def cmd_fetch_xhr(args):
    """Fetch patent data from Google Patents xhr endpoint with pagination."""
    print(f"[patenter] Fetch xhr — Mode A pagination")
    print(f"  Query: {args.query}")
    print(f"  Date range: {args.date_from} to {args.date_to}")
    print(f"  Max pages: {args.max_pages}")
    result = fetch_all_xhr_pages(args.query, args.date_from, args.date_to, args.max_pages)
    print(f"  Fetched: {len(result['patents'])} patents from {result['pages']} pages (total: {result['total']})")
    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"  Saved: {args.output}")
    else:
        print(json.dumps(result, indent=2))

# --- CLI Main ---

def main():
    parser = argparse.ArgumentParser(
        prog="patenter",
        description=f"Unified patent intelligence CLI v{VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    def add_common_args(p):
        p.add_argument("--mode", choices=["A", "B", "C"], default="A",
                       help="Search mode: A=google-patents (default), B=web-search-api, C=agent-search")
        p.add_argument("--jurisdiction", default="", help="Jurisdiction code (US, EP, CN, JP, KR, PCT)")

    # search
    p = subparsers.add_parser("search", help="Prior art search")
    add_common_args(p)
    p.add_argument("--use-case", choices=["novelty", "fto", "landscape", "diligence", "litigation"], default="novelty")
    p.add_argument("--query", required=True, help="Search query / invention description")
    p.add_argument("--date-from", default="", help="Start date YYYYMMDD")
    p.add_argument("--date-to", default="", help="End date YYYYMMDD")
    p.set_defaults(func=cmd_search)

    # summary
    p = subparsers.add_parser("summary", help="Patent summary")
    add_common_args(p)
    p.add_argument("--technology", required=True, help="Technology area")
    p.add_argument("--from-year", type=int, default=2010, help="Start year (deprecated, use --date-from)")
    p.add_argument("--to-year", type=int, default=2025, help="End year (deprecated, use --date-to)")
    p.add_argument("--date-from", default="", help="Start date YYYYMMDD (overrides --from-year)")
    p.add_argument("--date-to", default="", help="End date YYYYMMDD (overrides --to-year)")
    p.set_defaults(func=cmd_summary)

    # compare
    p = subparsers.add_parser("compare", help="Patent comparison")
    add_common_args(p)
    p.add_argument("--patents", required=True, help="Comma-separated patent numbers")
    p.set_defaults(func=cmd_compare)

    # core
    p = subparsers.add_parser("core", help="Core patent finding")
    add_common_args(p)
    p.add_argument("--technology", required=True, help="Technology area")
    p.add_argument("--from-year", type=int, default=2010, help="Start year (deprecated, use --date-from)")
    p.add_argument("--to-year", type=int, default=2025, help="End year (deprecated, use --date-to)")
    p.add_argument("--date-from", default="", help="Start date YYYYMMDD (overrides --from-year)")
    p.add_argument("--date-to", default="", help="End date YYYYMMDD (overrides --to-year)")
    p.set_defaults(func=cmd_core)

    # portfolio
    p = subparsers.add_parser("portfolio", help="Portfolio study")
    add_common_args(p)
    p.add_argument("--company", required=True, help="Company name")
    p.set_defaults(func=cmd_portfolio)

    # portfolio-compare
    p = subparsers.add_parser("portfolio-compare", help="Portfolio comparison")
    add_common_args(p)
    p.add_argument("--companies", required=True, help="Comma-separated company names (2+)")
    p.set_defaults(func=cmd_portfolio_compare)

    # fto
    p = subparsers.add_parser("fto", help="FTO analysis")
    add_common_args(p)
    p.add_argument("--technology", required=True, help="Technology/product description")
    p.add_argument("--jurisdictions", default="US", help="Comma-separated jurisdiction codes")
    p.set_defaults(func=cmd_fto)

    # landscape
    p = subparsers.add_parser("landscape", help="Landscape visualization (Mode A only)")
    add_common_args(p)
    p.add_argument("--technology", required=True, help="Technology area")
    p.add_argument("--from-year", type=int, default=2010, help="Start year (deprecated, use --date-from)")
    p.add_argument("--to-year", type=int, default=2025, help="End year (deprecated, use --date-to)")
    p.add_argument("--date-from", default="", help="Start date YYYYMMDD (overrides --from-year)")
    p.add_argument("--date-to", default="", help="End date YYYYMMDD (overrides --to-year)")
    p.set_defaults(func=cmd_landscape)

    # render
    p = subparsers.add_parser("render", help="Render a Jinja2 template")
    p.add_argument("--template", required=True, help="Template filename in templates/")
    p.add_argument("--output", default=None, help="Output file path")
    p.add_argument("--context-json", default=None, help="JSON context string")
    p.add_argument("--context-file", default=None, help="JSON context file path")
    p.set_defaults(func=cmd_render)

    # fetch-xhr (pagination)
    p = subparsers.add_parser("fetch-xhr", help="Fetch patent data from Google Patents xhr (Mode A)")
    p.add_argument("--query", required=True, help='Search query (e.g. assignee:"Example Corporation")')
    p.add_argument("--date-from", default="", help="Start date YYYYMMDD")
    p.add_argument("--date-to", default="", help="End date YYYYMMDD")
    p.add_argument("--max-pages", type=int, default=10, help="Max pages to fetch")
    p.add_argument("--output", default=None, help="Output JSON file path")
    p.set_defaults(func=cmd_fetch_xhr)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)

if __name__ == "__main__":
    main()
