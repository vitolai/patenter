# FTO Process + Design-Around Framework

## FTO vs Patentability

| Dimension | Patentability | FTO |
|-----------|--------------|-----|
| Question | Can I get a patent? | Can I commercialize without infringing? |
| Direction | My invention vs prior art | My product vs others' patents |
| Scope | Any prior art (expired or active) | Active patents only |
| Jurisdiction | Priority date is portable | Jurisdiction-specific |
| Result | Novel/not novel | Infringe / clear / design-around needed |

## FTO Screening Process

### Step 1: Identify Candidate Blocking Patents
- Search by product's core technology + CPC classes
- Filter: active patents only (not expired, < 20 years from filing)
- Filter: target jurisdictions (where product will be sold/made/used)

### Step 2: Claim Construction
- Interpret claim terms by their ordinary and customary meaning
- Consider specification context (what does the patent describe?)
- Consider prosecution history (what did the applicant distinguish?)

### Step 3: Infringement Analysis
For each element of each independent claim:
- Does the product have an equivalent element?
- If ALL elements present → infringes
- If ANY element missing → does not infringe (but check doctrine of equivalents)

### Step 4: Design-Around Options

For each infringing element, identify:
| Strategy | Description | Example |
|----------|-----------|---------|
| Omit | Remove the element entirely | Skip caching layer |
| Replace | Use a different mechanism | Replace hash with encryption |
| Reorganize | Change the architecture | Move logic from server to client |
| Combine | Merge elements to avoid limitation | Combine authentication + authorization |

### Step 5: Invalidation Search
- Prior art before blocking patent's priority date
- Focus on elements causing infringement
- Rank knock-out candidates by relevance

## Legal Disclaimer
FTO analysis is a technical assessment. A formal FTO opinion requires
a qualified patent attorney. This skill arms you for that conversation,
not replaces it.