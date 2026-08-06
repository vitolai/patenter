# DOCX Report Export — patenter_ext/docx_export.py

Convert a report context (JSON) into a **formatted Word `.docx` memo** for
distribution to non-technical stakeholders.

## When to use
- You have a report context JSON (e.g. design-around analysis, landscape
  summary, FTO follow-up).
- You need a clean, printable Word document instead of Markdown/HTML.

## Usage

### CLI (module)
```bash
python3 scripts/patenter_ext/docx_export.py context.json memo.docx
```

### As a Python library
```python
import sys; sys.path.insert(0, "scripts")
from patenter_ext.docx_export import export_docx_memo

export_docx_memo(context, "memo.docx")
```

## Context JSON schema
The input is a flat context object with these fields:

| Field | Type | Purpose |
|-------|------|---------|
| `title` | string | Memo title |
| `subtitle` | string | Subtitle line |
| `meta` | object | Key/value metadata (date, patent #, assignee, ...) |
| `executive_summary` | string | Opening summary |
| `stats` | list | `{label, value}` stat tiles |
| `sections` | list | `{title, items[]}` — items are `{label, value}` rows or plain strings |
| `methodology` | string | Method section |
| `disclaimer` | string | Footer caveat |

## Dependencies
Requires **`python-docx`**:
```bash
pip install python-docx
```

## Notes
- Output is a valid `.docx` (verified as a zip container).
- Keeps formatting minimal and consistent with the report context — no heavy
  styling dependencies.
