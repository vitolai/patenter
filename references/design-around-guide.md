# Design-Around & Claim-Gap Analysis — patenter_ext/design_around.py

Systematic identification of **unclaimed design space** in a blocking patent
and generation of **non-infringing design-around strategies**. This is the
analytical engine behind FTO follow-up (see `fto-process.md`).

## When to use
- A Mode A search surfaced a HIGH/MEDIUM-risk blocking patent.
- You want concrete, technical alternatives before deciding build-around vs
  license vs kill.

## What it does
1. **Parses independent claims** into discrete technical elements.
2. **Classifies each element** by kind:
   - `structural` — a physical component/structure
   - `functional` — a behavior/function without structural recitation
   - `quantifiable` — a numeric range, size, or magnitude
   - `mixed` — structural + functional aspects
3. **Flags unclaimed white-space dimensions** — technical axes the claims do
   NOT recite (e.g. scale/magnitude, material/composition, integration/
   packaging, control/software). These are your primary non-infringing levers.
4. **Generates design-around options** per element using the Omit / Replace /
   Reorganize / Combine playbook:

| Strategy | Meaning | Example |
|----------|---------|---------|
| **Omit** | Remove the element entirely if its function can be achieved another way | Skip a caching layer |
| **Replace** | Swap the mechanism for a functionally equivalent one | Replace a hash with encryption |
| **Reorganize** | Move the element to a different subsystem/location | Move logic server→client |
| **Combine** | Merge/redistribute the element across other elements | Fold a module into an adjacent one |

## Usage
```python
import sys; sys.path.insert(0, "scripts")
from patenter_ext.design_around import analyze_design_around

res = analyze_design_around(claims_text, "US11604978B2")
# res["claims"]          -> parsed elements per independent claim
# res["element_kind_counts"] -> structural/functional/quantifiable/mixed tally
# res["white_spaces"]    -> unclaimed dimensions with notes
# res["design_around_options"] -> per-element Omit/Replace/Reorganize/Combine
```

## Output notes
- The parser is **heuristic** — always verify against the actual claim text.
- Dependent claims, Markush groups, and "means-for" limitations need attorney
  review.
- **Doctrine of equivalents may still apply** — a Replace strategy is a
  starting point, not a clearance guarantee.
- This is a **technical screening aid, not legal advice**.

## Integration
Pairs with:
- `fto-process.md` — the broader FTO decision flow
- `claim-mapping.md` — claim element mapping methodology
