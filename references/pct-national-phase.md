# PCT National-Phase Awareness — Designation ≠ Entry

Methodology reference for correctly assessing geographic protection breadth in
portfolio studies and core-patent finding. This prevents a common analytical
error: treating a WO (PCT) application's **designated** countries as if they
were **entered** national phases.

## Core Rule

A WO (PCT) application **designates** many countries at filing. Designation is
**not** national-phase entry. Only the states actually **entered** within the
national-phase deadline provide patent protection.

## The 30/31-Month Deadline

- **31 months** from the earliest priority date is the standard national-phase
  entry deadline for most states (EP, CN, US, JP, KR, AU, etc.).
- **30 months** applies to some states (e.g., certain others / historical
  reservations). Always confirm the exact rule per target state.
- If the applicant does **not** enter national phase by the deadline, those
  designations **lapse** and provide **zero protection** in that state.

> **Operational rule:** when reporting "geographic breadth," compute the
> 31-month deadline from each patent's priority date and state whether it has
> passed, is approaching, or is still open. Do **not** report designated
> countries as protected markets.

## Reading Google Patents `country_status`

The `country_status` field returned by the Google Patents xhr endpoint lists the
**designated** states in the family — **not** the entered national phases.

- `"country_code": "WO"` → the PCT designation exists.
- `"country_code": "EP" / "CN" / "US"` etc. → the state is **designated**, NOT
  necessarily entered.
- A status of `ACTIVE` on a designation means the family member is alive — it
  does **not** confirm a granted/entered national-phase patent in that country.

**Do NOT use `country_status` as a proxy for geographic protection breadth.**

## Filing-Route Detection Heuristic

Use publication type + priority date to infer the filing route:

| Signal | Interpretation |
|--------|----------------|
| US/EP/CN/JP publication ~18 months after priority | **Direct filing** in that office |
| A **WO** publication | The **PCT application itself** (not a national-phase entry) |
| US/EP/CN publication citing a WO priority | Possible PCT **national-phase entry** (verify) |

## Verification Step

Before concluding a market is protected, confirm **actual national-phase entry**
against the authoritative registers:

- **EPO Register** (European Patent Register)
- **CNIPA** (China National Intellectual Property Administration)
- **USPTO PAIR / Patent Center** (US)
- **WIPO PatentScope** (for PCT status)

## Worked Example (anonymized)

A 6-publication family where one member is a WO/PCT application and the rest are
US direct filings. The `country_status` showed US/EP/CN/WO/TW for the earliest
member — but the EP/CN/TW national-phase windows (31 months from priority) had
already passed for the direct US filings, so those markets were **not** actually
protected. Only the members with still-open PCT deadlines retained geographic
options. Ranking by `country_status` breadth alone would have overstated the
earliest member's footprint.

---

*This is a search-signal and methodology reference, not legal advice. Consult a
qualified patent attorney before filing, licensing, or FTO decisions.*
