# NEXORAS DATA STATE

## Dataset Location
`D:\sih 2026\mplads dataset\`

## Files
| File | Size | Status |
|---|---|---|
| mplads_mp_summary_2026-09-10.csv | 104 KB | NOT INSPECTED |
| mplads_completed_works_2026-09-10.csv | 11.7 MB | NOT INSPECTED |
| mplads_expenditures_2026-09-10.csv | 26.4 MB | NOT INSPECTED |
| mplads_recommended_works_2026-09-10.csv | 23 MB | NOT INSPECTED |
| json_2026-09-10.json | 796 bytes | INSPECTED (summary stats only) |

## JSON Summary Stats (Confirmed)
```json
{
  "totalAllocated": 116819035627.53,
  "totalExpenditure": 39953382732.14,
  "totalRecommendedAmount": 79081497846.06,
  "utilizationPercentage": 67.69,
  "expenditurePercentage": 34.20,
  "totalMPs": 774,
  "totalWorksCompleted": 44028,
  "totalWorksRecommended": 131141,
  "completionRate": 33.57,
  "totalTransactions": 108695,
  "pendingWorks": 87113,
  "paymentGap": 39.71
}
```

## Column Names
**TODO** — Run `python inspect_data.py` to populate this section.

## Data Types
**TODO**

## Missing Values
**TODO**

## Duplicate Records
**TODO**

## Invalid Records
**TODO**

## Text Fields (for NLP feasibility)
**TODO** — critical for deciding whether NLP/spaCy module is useful

## Numerical Features (Available)
**TODO**

## Categorical Features (Available)
**TODO**

## Date Features (Available)
**TODO**

## Derived Features (Planned)
- `expenditure_ratio` = actual_spent / sanctioned_amount
- `cost_deviation` = (work_cost - category_median) / category_std
- `unspent_ratio` = unspent_balance / total_available
- `admin_ratio` = admin_expense / total_expense
- `vendor_concentration` = Herfindahl index

## Synthetic Data
None currently. All data is real MPLADS data from dataful.in (14th-17th Lok Sabha).

## Cleaning Applied
None yet

## Feature Engineering Applied
None yet

## EXACT NEXT STEP
Run: `python notebooks/01_inspect_data.py` to populate TODO sections above.
