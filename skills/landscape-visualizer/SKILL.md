---
name: landscape-visualizer
description: >
  Interactive self-contained HTML patent landscape report. Mode A ONLY —
  requires structured data (filing dates, CPC classes, assignees, jurisdictions).
  Jinja2-rendered template. No external dependencies in output HTML.
---

# Landscape Visualizer

## Constraint
**Mode A ONLY.** Modes C and B cannot generate landscape visualizations
because they lack structured patent data (filing dates, CPC classes, assignees,
jurisdictions).

If user requests landscape with Mode C or B:
- Explain that Mode A is required
- Offer to switch to Mode A
- Or offer a text-only summary as alternative

## Intake
1. Confirm Mode A (google-patents)
2. Get technology area
3. Get date range
4. Confirm jurisdictions (default: worldwide)

## Execution

### Step 1: Data Collection (Mode A)
1. Fetch Google Patents results for technology query
2. For each patent, extract:
   - Patent number, title, assignee (normalized)
   - Filing date, publication date
   - CPC subclasses
   - Jurisdiction
   - Abstract
3. Apply trailing-year exclusion heuristic
4. Track three-count: queries sent / patents received / patents cited

### Step 2: Data Aggregation
1. Applicant leaderboard (top 20, normalized names)
2. Filing trends by year (with jurisdiction breakdown)
3. Technology breakdown by CPC subclass (translated to plain English)
4. Notable patents: most recent, foundational, cross-disciplinary

### Step 3: Template Rendering (Jinja2)
1. Load `templates/landscape-html-template.jinja`
2. Render with Jinja2:
   ```python
   from jinja2 import Environment, FileSystemLoader
   env = Environment(loader=FileSystemLoader("templates/"), autoescape=True)
   template = env.get_template("landscape-html-template.jinja")
   html = template.render(
       technology="...",
       headline="...",
       family_count=N,
       applicant_count=N,
       jurisdiction_count=N,
       peak_year="YYYY",
       applicants=[...],
       trends=[...],
       cpc_breakdown=[...],
       # ... see template for all variables
   )
   ```
3. Output: self-contained `.html` file (inline CSS/JS, no external dependencies)

## Output
Single `.html` file containing:
- Hero section with 4 stat tiles
- Filter bar (All / Granted / Applications / Utility / Design)
- Applicant leaderboard with CSV export
- Filing trends table
- Technology breakdown table
- Notable patents spotlight (4 switchable views)
- Methodology section with caveats
- Footer with generation date and mode

## Legal Disclaimer
Include in output: "This is a technical assessment, not legal advice."