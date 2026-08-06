#!/usr/bin/env python3
"""M2: Automated Claim-Gap & Design-Around Analyzer.

Extends the FTO workflow with a `--design-around` capability. Reuses the
existing claim-element parsing idea from `patent-comparison` + the
`references/fto-process.md` Design-Around framework (Omit / Replace /
Reorganize / Combine).

What it does:
1. Parse a target patent's independent claims into discrete technical
   elements/limitations (Element A + Element B + Element C).
2. For each element, classify it as structural / functional / quantifiable.
3. Identify "white space": technical dimensions the independent claims do
   NOT explicitly claim (unclaimed limitations) -> candidate design-around
   surface.
4. Generate non-infringing structural alternatives per element using the
   Omit / Replace / Reorganize / Combine playbook.

Design notes:
- Pure stdlib + regex. No ML dependency. Claims text is passed in as
  structured input (e.g., from Mode A detail xhr or a user-pasted claims).
- This is a *technical screening aid*, not legal advice (matches the repo's
  existing disclaimer posture).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict

# --- claim parsing ---------------------------------------------------------

# Split on the classic claim preamble markers: "comprising", "consisting of",
# "consisting essentially of", and semicolon-separated limitations.
_ELEMENT_SPLIT_RE = re.compile(
    r"\b(?:comprising|consisting of|consisting essentially of|further comprising)\b",
    re.IGNORECASE,
)

# Limitation separators within a claim body (semicolons + newlines)
_LIMIT_SEP_RE = re.compile(r"[;\n]+")

# Heuristic markers for element type
_STRUCTURAL_MARKERS = (
    "a ", "an ", "the ", "said ", "layer", "substrate", "electrode", "circuit",
    "module", "sensor", "element", "member", "unit", "body", "surface",
    "comprising", "means for", "portion",
)
_FUNCTIONAL_MARKERS = (
    "configured to", "adapted to", "for ", "operatively", "coupled to",
    "connected to", "arranged to", "capable of", "wherein", "such that",
    "causing", "to generate", "to detect", "to receive", "to transmit",
)


@dataclass
class ClaimElement:
    """A discrete technical limitation parsed from a claim."""

    text: str
    kind: str = "structural"  # structural | functional | quantifiable | mixed
    required: bool = True

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class IndependentClaim:
    """A parsed independent claim with its elements."""

    number: int
    preamble: str = ""
    elements: list[ClaimElement] = field(default_factory=list)
    raw_text: str = ""

    def to_dict(self) -> dict:
        return {
            "number": self.number,
            "preamble": self.preamble,
            "elements": [e.to_dict() for e in self.elements],
        }


def _classify_element(text: str) -> str:
    t = text.strip().lower()
    # quantifiable: contains a number/range/percentage
    if re.search(r"\b\d+(?:\.\d+)?\s*(?:nm|um|µm|mm|cm|%|to|–|-)\s*\d*", t) or \
       re.search(r"\b(?:at least|no more than|between|less than|greater than)\b", t):
        return "quantifiable"
    functional_hits = sum(1 for m in _FUNCTIONAL_MARKERS if m in t)
    structural_hits = sum(1 for m in _STRUCTURAL_MARKERS if m in t)
    if functional_hits > structural_hits:
        return "functional"
    if functional_hits and structural_hits:
        return "mixed"
    return "structural"


def parse_claims(claims_text: str) -> list[IndependentClaim]:
    """Parse independent claims from raw claims text.

    Expects claims separated by blank lines or numbered "1." / "Claim 1"
    markers. Returns a list of IndependentClaim with parsed elements.
    """
    if not claims_text or not claims_text.strip():
        return []

    # Normalize: split into claim blocks by numbered markers. Match both
    # "1. ..." at line start and inline "1. ..." after a newline.
    blocks = re.split(r"(?:^|\n)\s*(?:Claim\s*)?(\d+)[\.\)]\s*", claims_text)
    claims: list[IndependentClaim] = []
    # blocks alternates: [pre, num, body, num, body, ...]
    i = 1
    while i + 1 < len(blocks):
        num_raw = blocks[i]
        body = blocks[i + 1].strip()
        try:
            num = int(num_raw)
        except ValueError:
            num = len(claims) + 1

        preamble = ""
        elements: list[ClaimElement] = []

        # Split preamble off the first "comprising"/"consisting"
        m = _ELEMENT_SPLIT_RE.search(body)
        if m:
            preamble = body[: m.start()].strip()
            rest = body[m.end():]
        else:
            rest = body

        # Split remaining into limitation segments
        segments = [s.strip() for s in _LIMIT_SEP_RE.split(rest) if s.strip()]
        # A segment may itself contain "comprising X, Y, Z" -> split further on commas
        for seg in segments:
            parts = [p.strip() for p in re.split(r",\s*", seg) if p.strip()]
            for part in parts:
                if len(part) < 3:
                    continue
                elements.append(
                    ClaimElement(text=part, kind=_classify_element(part))
                )

        claims.append(IndependentClaim(number=num, preamble=preamble,
                                       elements=elements, raw_text=body))
        i += 2

    # Fallback: if no numbered blocks matched, treat whole text as one claim
    if not claims:
        claims.append(IndependentClaim(number=1, raw_text=claims_text.strip()))

    return claims


# --- white space + design-around ------------------------------------------

# Playbook from references/fto-process.md
DESIGN_AROUND_PLAYBOOK = {
    "structural": [
        ("Replace", "Swap the claimed structure for a functionally equivalent "
                     "one (e.g., a different material, geometry, or arrangement)."),
        ("Omit", "Remove the element entirely if the claimed function can be "
                 "achieved without a dedicated structure."),
        ("Reorganize", "Move the structure to a different subsystem / location "
                       "in the architecture."),
    ],
    "functional": [
        ("Replace", "Achieve the same function through a different mechanism "
                    "(e.g., replace encryption with hashing, sensor with model)."),
        ("Combine", "Merge two claimed functional limitations into a single "
                    "combined operation to avoid a distinct claim element."),
        ("Reorganize", "Shift the function from hardware to software (or vice "
                       "versa) to fall outside the claim's recitation."),
    ],
    "quantifiable": [
        ("Omit", "Drop the numeric range and use an unbounded / different "
                 "magnitude outside the claimed range."),
        ("Replace", "Use a different unit or threshold (e.g., time-based vs "
                    "size-based) that the claim does not recite."),
    ],
    "mixed": [
        ("Replace", "Redesign the element so its structural and functional "
                    "aspects no longer co-occur as claimed."),
        ("Reorganize", "Decouple the structural and functional aspects into "
                       "separate, differently-claimed components."),
    ],
}


@dataclass
class DesignAroundOption:
    element_text: str
    element_kind: str
    strategy: str
    suggestion: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class WhiteSpace:
    """An unclaimed technical dimension identified from the claims."""

    dimension: str
    note: str

    def to_dict(self) -> dict:
        return asdict(self)


# Common dimensions patent claims often leave open (white space candidates)
_WHITE_SPACE_DIMENSIONS = [
    ("scale / magnitude", "Claim does not recite a size/range for this element — "
                          "unbounded magnitudes are design-around surface."),
    ("material / composition", "No material selection is claimed — material swaps "
                               "may avoid literal infringement."),
    ("integration / packaging", "No claim on how elements are integrated — "
                                "packaging-level changes fall outside."),
    ("control / software", "No algorithmic or control-loop limitation — "
                           "software-side implementation may be unclaimed."),
    ("fabrication process", "No process/method limitation — different "
                            "manufacturing route is likely clear."),
]


def analyze_design_around(claims_text: str,
                          target_patent: str = "") -> dict:
    """Full M2 analysis: parse claims, find white space, suggest alternatives."""
    claims = parse_claims(claims_text)
    if not claims:
        return {"error": "No claims parsed. Provide independent claim text.", "claims": []}

    options: list[DesignAroundOption] = []
    white_spaces: list[WhiteSpace] = []
    element_kinds: dict[str, int] = {}

    # 1) Design-around per element
    for claim in claims:
        for el in claim.elements:
            kind = el.kind
            element_kinds[kind] = element_kinds.get(kind, 0) + 1
            playbook = DESIGN_AROUND_PLAYBOOK.get(kind, DESIGN_AROUND_PLAYBOOK["structural"])
            for strategy, suggestion in playbook:
                options.append(DesignAroundOption(
                    element_text=el.text,
                    element_kind=kind,
                    strategy=strategy,
                    suggestion=suggestion,
                ))

    # 2) White-space detection (dimensions absent from all claims)
    all_text = claims_text.lower()
    claimed_dims = set()
    if re.search(r"\b\d+\s*(?:nm|um|µm|mm|cm|%)\b", all_text):
        claimed_dims.add("scale / magnitude")
    if re.search(r"\b(?:material|compos|polymer|metal|silicon|oxide|nitride)\b", all_text):
        claimed_dims.add("material / composition")
    if re.search(r"\b(?:packag|integrat|module|housing|enclosure)\b", all_text):
        claimed_dims.add("integration / packaging")
    if re.search(r"\b(?:control|algorithm|software|processor|program|logic)\b", all_text):
        claimed_dims.add("control / software")
    if re.search(r"\b(?:method|process|depositing|etching|forming|fabricat)\b", all_text):
        claimed_dims.add("fabrication process")

    for dim, note in _WHITE_SPACE_DIMENSIONS:
        if dim not in claimed_dims:
            white_spaces.append(WhiteSpace(dimension=dim, note=note))

    return {
        "target_patent": target_patent,
        "claims": [c.to_dict() for c in claims],
        "element_kind_counts": element_kinds,
        "design_around_options": [o.to_dict() for o in options],
        "white_spaces": [w.to_dict() for w in white_spaces],
        "disclaimer": (
            "Technical screening aid only, not legal advice. "
            "Doctrine of equivalents may still apply; consult counsel."
        ),
    }


def analyze_design_around_from_file(claims_path: str,
                                    target_patent: str = "") -> dict:
    with open(claims_path, "r", encoding="utf-8") as f:
        return analyze_design_around(f.read(), target_patent)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    inp = sys.argv[1]
    patent = sys.argv[2] if len(sys.argv) > 2 else ""
    if inp.endswith(".txt") or inp.endswith(".md") or inp.endswith(".json"):
        result = analyze_design_around_from_file(inp, patent)
    else:
        result = analyze_design_around(inp, patent)
    print(json.dumps(result, indent=2, ensure_ascii=False))
