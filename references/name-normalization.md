# Applicant Name Normalization Rules

## Legal Suffix Stripping (100+)

Strip these suffixes from assignee names before counting/distinct:

### English
- Inc., Inc, Corp., Corp, Corporation, Co., Co, Company, Ltd., Ltd, Limited
- LLC, L.L.C., LLP, L.L.P., LP, L.P.
- PLC, Plc, AG, S.A., SA, S.A.S, SAS
- GmbH, GmbH & Co. KG, KG
- B.V., BV, B.V., N.V., NV
- Pte., Pte Ltd, Pte. Ltd.
- Pty., Pty Ltd, Pty. Ltd.
- S.r.l., SRL, S.p.A., SpA
- Oy, Ab, A/S
- AS, A/S, ApS
- K.K., KK, Kabushiki Kaisha
- Ltda., Ltda
- S.C., SC
- PBC, P.B.C.
- Corp, Corporation, Group, Holdings, Holding

### Chinese
- 公司, 有限公司, 股份有限公司, 集团, 控股

### Japanese
- 株式会社, 有限会社, 合同会社

### Korean
- 주식회사, 유한회사

### German
- GmbH, AG, KG, GmbH & Co. KG, oHG, GbR

### French
- S.A., S.A.S., S.A.R.L., S.N.C., S.C.S.

### Italian
- S.p.A., S.r.l., S.n.c., S.a.s.

### Spanish
- S.A., S.L., S.L.U., S.A.U.

### Dutch
- B.V., N.V.

### Nordic
- AB (Sweden), Oy (Finland), AS (Norway/Denmark), ApS (Denmark), HF (Iceland)

### Russian
- ООО, ОАО, ЗАО, ПАО, ИП

## Rules
1. Strip all legal suffixes first (case-insensitive, iterative)
2. Every merge must be logged in Methodology section
3. If unsure, keep original name and flag for review
