#!/usr/bin/env python3
"""M5: Continuous Competitor Monitoring & Daily/Weekly Briefs.

Shipped as a *script* (not a core CLI command) to respect patenter's stateless
CLI architecture. Run on a schedule (cron / systemd timer / OpenClaw cron).
It calls the existing `search` / `portfolio` machinery, diffs results against a
persistent state file, and emits Markdown + HTML briefs of new competitor IP
movements (new filings, new CPC activity).

Key idea — state-diff monitoring:
- State file: JSON with { assignee: { pub_number: first_seen_date } }.
- On each run: fetch current portfolio set for each watched assignee.
- New pub_numbers not in state => "new filings" alerts.
- CPC counts per assignee tracked over time => filing-velocity + tech drift.

No daemon. Stateless per invocation. Idempotent. Fail-open.

Usage:
    python3 watch_brief.py --watch "Company A,Company B" \
        --state ~/.cache/patenter/watch_state.json \
        --out ./briefs --since 30

    # cron example (daily 08:00):
    # 0 8 * * *  cd /path/to/patenter && python3 scripts/watch_brief.py \
    #     --watch "Company A,Company B" --state ~/.cache/patenter/watch_state.json \
    #     --out ./briefs --format md,html
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Allow running from repo root or scripts/ dir
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from modules.cache import ResponseCache, fetch_json, dedup_patents
    from modules.google_patents import google_patents_xhr_url
except Exception:  # noqa: BLE001 - allow partial usage if modules not importable
    ResponseCache = None
    fetch_json = None
    dedup_patents = None


def _default_state_path() -> Path:
    return Path(os.environ.get("PATENTER_CACHE_DIR", "~/.cache/patenter")).expanduser() / "watch_state.json"


def load_state(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            return {}
    return {}


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def fetch_assignee_portfolio(assignee: str, date_from: str = "", date_to: str = "") -> list[dict]:
    """Fetch current portfolio set for one assignee via Google Patents xhr."""
    if fetch_json is None or google_patents_xhr_url is None:
        # fallback: no-op (offline/unit) — return empty
        return []
    query = f'assignee:"{assignee}"'
    url = google_patents_xhr_url(query, "", date_from, date_to, page=0)
    data = fetch_json(url)
    results = data.get("results", {})
    cluster = results.get("cluster", [])
    patents = []
    for c in cluster:
        for item in c.get("result", []):
            p = item.get("patent", {})
            patents.append({
                "pub_number": p.get("publication_number", "").strip(),
                "title": p.get("title", "").strip(),
                "filing_date": p.get("filing_date", ""),
                "publication_date": p.get("publication_date", ""),
                "assignee": p.get("assignee", ""),
                "cpc": [x.get("code") for x in p.get("cpc", []) if x.get("code")],
            })
    return dedup_patents(patents) if dedup_patents else patents


def compute_delta(prev: dict, curr: list[dict], since_days: int = 0) -> dict:
    """Diff previous state vs current portfolio. Returns new filings + velocity."""
    cutoff = datetime.utcnow() - timedelta(days=since_days) if since_days > 0 else None
    prev_pubs = set(prev.get("_publications", []))
    curr_pubs = {p["pub_number"] for p in curr if p.get("pub_number")}

    new_filings = []
    for p in curr:
        if p["pub_number"] not in prev_pubs:
            # optionally filter by recency
            if cutoff is not None:
                fd = p.get("filing_date", "")
                try:
                    fdate = datetime.strptime(str(fd)[:10], "%Y-%m-%d")
                except Exception:  # noqa: BLE001
                    fdate = None
                if fdate and fdate < cutoff:
                    continue
            new_filings.append(p)

    # CPC velocity: count current CPC occurrences
    cpc_counts: dict[str, int] = {}
    for p in curr:
        for code in p.get("cpc", []):
            cpc_counts[code] = cpc_counts.get(code, 0) + 1
    top_cpc = sorted(cpc_counts.items(), key=lambda kv: kv[1], reverse=True)[:10]

    return {
        "new_filings": new_filings,
        "top_cpc": top_cpc,
        "portfolio_size": len(curr_pubs),
        "delta_size": len(curr_pubs) - len(prev_pubs),
    }


def render_md(assignee: str, delta: dict, generated: str) -> str:
    lines = [
        f"# Competitor IP Brief — {assignee}",
        f"_Generated: {generated} UTC_",
        "",
        f"- Portfolio size: **{delta['portfolio_size']}**",
        f"- Delta vs last run: **{delta['delta_size']:+d}**",
        f"- New filings detected: **{len(delta['new_filings'])}**",
        "",
        "## New Filings",
    ]
    if delta["new_filings"]:
        for p in delta["new_filings"]:
            lines.append(f"- **{p['pub_number']}** — {p['title']} "
                         f"(filed {p.get('filing_date', 'n/a')})")
    else:
        lines.append("- None in this window.")
    lines += ["", "## Top CPC Activity", ""]
    if delta["top_cpc"]:
        for code, n in delta["top_cpc"]:
            lines.append(f"- `{code}` × {n}")
    else:
        lines.append("- No CPC data.")
    return "\n".join(lines) + "\n"


def render_html(assignee: str, delta: dict, generated: str) -> str:
    rows = "".join(
        f"<tr><td>{p['pub_number']}</td><td>{p['title']}</td>"
        f"<td>{p.get('filing_date', '')}</td></tr>"
        for p in delta["new_filings"]
    ) or "<tr><td colspan='3'>None in this window.</td></tr>"
    cpc_rows = "".join(
        f"<tr><td><code>{code}</code></td><td>{n}</td></tr>"
        for code, n in delta["top_cpc"]
    ) or "<tr><td colspan='2'>No CPC data.</td></tr>"
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<title>Competitor IP Brief — {assignee}</title>
<style>body{{font-family:system-ui,sans-serif;max-width:820px;margin:2rem auto;padding:0 1rem}}
table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ddd;padding:6px 10px;text-align:left}}
th{{background:#f5f5f5}}h1{{color:#1a1a1a}}</style></head><body>
<h1>Competitor IP Brief — {assignee}</h1>
<p><em>Generated: {generated} UTC</em></p>
<h2>Snapshot</h2>
<table><tr><th>Portfolio size</th><th>Delta</th><th>New filings</th></tr>
<tr><td>{delta['portfolio_size']}</td><td>{delta['delta_size']:+d}</td><td>{len(delta['new_filings'])}</td></tr></table>
<h2>New Filings</h2>
<table><tr><th>Pub #</th><th>Title</th><th>Filed</th></tr>{rows}</table>
<h2>Top CPC Activity</h2>
<table><tr><th>CPC</th><th>Count</th></tr>{cpc_rows}</table>
</body></html>"""


def main() -> None:
    ap = argparse.ArgumentParser(description="Competitor patent watch (state-diff).")
    ap.add_argument("--watch", required=True, help="Comma-separated assignees to monitor")
    ap.add_argument("--state", default=str(_default_state_path()), help="State JSON path")
    ap.add_argument("--out", default="./briefs", help="Output dir for briefs")
    ap.add_argument("--format", default="md,html", help="Comma-separated: md,html")
    ap.add_argument("--since", type=int, default=0, help="Only alert filings within N days (0=all new)")
    ap.add_argument("--date-from", default="", help="Fetch date range (YYYYMMDD), optional")
    ap.add_argument("--date-to", default="", help="Fetch date range (YYYYMMDD), optional")
    args = ap.parse_args()

    assignees = [a.strip() for a in args.watch.split(",") if a.strip()]
    state = load_state(Path(args.state))
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    generated = datetime.utcnow().strftime("%Y-%m-%d %H:%M")

    for assignee in assignees:
        prev = state.get(assignee, {})
        curr = fetch_assignee_portfolio(assignee, args.date_from, args.date_to)
        delta = compute_delta(prev, curr, args.since)
        # update state: remember all seen pub numbers
        state[assignee] = {
            "_publications": [p["pub_number"] for p in curr],
            "_last_run": generated,
            "_last_size": delta["portfolio_size"],
        }
        # emit briefs
        safe = assignee.replace(" ", "_").replace("/", "_")
        for fmt in [f.strip() for f in args.format.split(",") if f.strip()]:
            if fmt == "md":
                (out_dir / f"{safe}_brief.md").write_text(
                    render_md(assignee, delta, generated), encoding="utf-8")
            elif fmt == "html":
                (out_dir / f"{safe}_brief.html").write_text(
                    render_html(assignee, delta, generated), encoding="utf-8")
        print(f"[watch_brief] {assignee}: {delta['portfolio_size']} patents, "
              f"{len(delta['new_filings'])} new, delta {delta['delta_size']:+d}")

    save_state(Path(args.state), state)
    print(f"[watch_brief] state saved: {args.state}")
    print("[watch_brief] done.")


if __name__ == "__main__":
    main()
