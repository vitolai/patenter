# Claim Mapping Methodology

## Claim Parsing

### Independent Claims
1. Extract preamble + transitional phrase + body
2. Preambles: "A method comprising...", "A system including...", "An apparatus for..."
3. Transitional phrases: "comprising" (open), "consisting of" (closed), "consisting essentially of" (partially open)
4. Parse body into element list (numbered or bulleted)

### Dependent Claims
- Identify parent claim reference
- Extract additional limitations
- Map to parent element list

## Element Mapping (for Comparison)

### Match Categories
| Category | Definition | Implication |
|----------|-----------|-------------|
| Identical | Same wording, same function | Full overlap |
| Equivalent | Different wording, same function | Likely overlaps (doctrine of equivalents) |
| Different | Different element or function | No overlap |
| Unique | Element in only one patent | Differentiation point |

## Abstraction Principle

Patent claims benefit from conceptual descriptions, not implementation specifics:

| Code Says | Abstracted To |
|-----------|---------------|
| `bcrypt.compare()` | applies cryptographic one-way function |
| stores in PostgreSQL | persists to durable storage |
| REST API call | communicates via network interface |
| React component | renders user interface element |

Broader descriptions create stronger design-around barriers.

## Claim Differentiation Scoring

Score = (Unique elements / Total elements) × 10

- 0-3: High overlap — likely infringement or novelty issue
- 4-6: Moderate overlap — needs detailed analysis
- 7-10: Low overlap — likely distinct inventions