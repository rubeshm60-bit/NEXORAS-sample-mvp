# MODULE 07 — VENDOR NETWORK INTELLIGENCE

## Purpose
Build the entity-relationship intelligence layer mapping Members of Parliament (MPs), Projects (Works), Contractors (Vendors), and Implementing District Authorities (IDAs). Detect anti-competitive patterns, contractor cartels, local monopolies, and agency-level disbursement conduits with explainable, neutral audit signals.

## Why NEXORAS Needs It
Financial anomalies at the MP level often stem from downstream contractor dynamics. In the MPLADS open dataset:
- Over **28,200 distinct vendors** receive public funds across India.
- While most contractors serve a single constituency, a select group of commercial entities operates across multiple MPs, districts, and states.
- Certain constituencies exhibit extreme vendor concentration where a single vendor captures over 50% to 100% of all disbursed funds.
- Implementing District Authorities (IDAs) occasionally route disproportionate shares of their district budget to a single favored contractor.
- Unsupervised tree and neural models flag *aggregate constituency metrics*; Module 7 isolates *who* received the funds, *how* relationships are structured, and *which* contractors drive systemic risk.

## Entity-Relationship Architecture
```
   [ MP ]
     │
     │ recommends / allocates
     ▼
 [ Work / Project ] ──────────────► [ Implementing District Authority (IDA) ]
     │                                         │
     │ paid through disbursements              │ routes execution
     ▼                                         ▼
   [ Payment Transaction ] ──────────► [ Vendor / Contractor ]
```

### Entities Supported by Dataset:
1. **MP**: 774 Parliamentarians (Lok Sabha & Rajya Sabha).
2. **Vendor**: 28,206 commercial entities and contractors.
3. **IDA**: 765 Implementing District Authorities / Agencies.
4. **Disbursement / Payment**: 76,313 unique financial transactions.

## Risk Patterns Detected
All detection algorithms strictly employ objective, neutral audit terminology (`"unusual concentration"`, `"suspicious pattern"`, `"requires audit review"`):

| Pattern Name | Algorithmic Definition | Risk Weight | Audit Interpretation |
|---|---|---|---|
| **MULTI_MP_SYNDICATE** | Vendor active across $\ge 3$ MPs AND $\ge 2$ states with total payout $\ge ₹5\text{ Lakh}$ | +30 pts | Cross-constituency contractor footprint suggesting potential cartel or inter-district coordination. |
| **MONOPOLY_CONTRACTOR** | Vendor captures $\ge 50\%$ of an MP's total expenditures (with payout $\ge ₹5\text{ Lakh}$) | +25 pts | Extreme single-constituency vendor lock-in violating competitive procurement norms. |
| **IDA_EXCLUSIVE_CONDUIT** | Vendor captures $\ge 60\%$ of an IDA's total disbursements (with payout $\ge ₹5\text{ Lakh}$) | +20 pts | Disproportionate capture of a district administrative agency. |
| **HIGH_IN_PROGRESS_RISK** | In-progress payment ratio $\ge 25\%$ with $\ge 3$ pending disbursements | +15 pts | Stalled work or unliquidated financial advances requiring milestone inspection. |
| **HIGH_VALUE_OUTLIER** | Total payout in the top 1% nationwide ($\ge 99\text{th percentile}$) | +10 pts | Macro-volume contractor demanding high-tier scrutiny. |
| **EXTREME_MULTI_MP_FOOTPRINT** | Vendor active across $\ge 10$ distinct MPs | +10 pts | National-scale supplier operating across numerous parliamentary boundaries. |

## Scoring & Tiers
The composite **Vendor Risk Score** ($0.0 \text{ to } 100.0$) categorizes vendors into actionable audit bands:
- **HIGH_RISK** ($\text{Score} \ge 60$): Multi-dimensional risk (e.g. multi-MP syndicate + monopoly + top 1% payout).
- **MEDIUM_RISK** ($30 \le \text{Score} < 60$): Significant single or dual risk flag (e.g. cross-constituency syndicate or local monopoly).
- **LOW_RISK** ($0 < \text{Score} < 30$): Minor flags (e.g. high volume without cartel patterns).
- **BENIGN** ($\text{Score} = 0$): Standard local contractor servicing normal procurement workflows.

## Empirical Findings on MPLADS
- **Total Vendors Profiled**: 28,206
- **High-Risk Vendors**: 8
- **Medium-Risk Vendors**: 213
- **Total Vendors Requiring Audit Review**: 292 (1.0% of all vendors)
- **Cross-Constituency Syndicates**: 134 vendors active across $\ge 3$ MPs and $\ge 2$ states
- **Monopoly Contracts Detected**: 116 instances where one vendor captures $\ge 50\%$ of an MP fund
- **IDA Exclusive Conduits**: 88 instances where one vendor dominates $\ge 60\%$ of an agency's spend

### Prominent Case Studies Identified:
1. **KRIDL BHUSIRI ACCOUNT WORKS**: ₹20.28 Crore across 20 MPs and 17 IDAs (269 transactions).
2. **FORCE MOTORS LIMITED**: ₹15.92 Crore across 19 MPs and 9 States (15 IDAs, specialized vehicle procurements).
3. **RAMJI CONSTRUCTION**: ₹15.75 Crore across 6 MPs and 2 States.
4. **SAI ENTERPRISES**: ₹13.80 Crore across 9 MPs and 4 States.
5. **JF JAVID HUSSAIN**: ₹15.84 Crore in a single IDA across 3 MPs (164 transactions).

## Files
| File | Purpose |
|---|---|
| `backend/engine/vendor_intelligence.py` | `VendorNetworkIntelligence` profiler, relationship builder, risk scorer, and explainability APIs |
| `tests/test_vendor_intelligence.py` | 14-test comprehensive unit test suite |

## Tests & Verification
14 unit tests covering:
- Profile schema completeness and row count (28,206 rows, zero nulls)
- Mathematical bounds ($S \in [0.0, 100.0]$, in-progress ratio $\in [0.0, 1.0]$)
- Exact financial conservation across MP-Vendor and Vendor-IDA relationship matrices
- Syndicate, monopoly, and conduit detection accuracy
- Explainability APIs (`get_vendor_profile`, `get_mp_vendor_breakdown`, `get_top_risk_vendors`)
- Zero-expenditure edge case handling (e.g., Chavan Vasantrao Balwantrao)
- Strict compliance with neutral audit terminology

## Test Results
**14/14 PASS** (2026-09-10)

## Definition of Done
✅ Entity-relationship model constructed across MP, Vendor, IDA, and Payments  
✅ Profiles for all 28,206 contractors computed  
✅ Syndicates, local monopolies, and agency conduits systematically identified  
✅ Explainable Vendor Risk Score ($0-100$) and audit recommendations generated  
✅ 14/14 unit tests pass with zero warnings  
