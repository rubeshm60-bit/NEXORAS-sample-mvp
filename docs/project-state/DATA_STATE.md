# NEXORAS DATA STATE

## Dataset Location
`D:\sih 2026\mplads dataset\`

## Files

### mplads_mp_summary_2026-09-10.csv
- **Size:** 0.10 MB | **Rows:** 774 | **Cols:** 15 (after dropping average_rating)
- **Duplicates:** 0
- **Columns:**

| Column | Type | Nulls | Description |
|---|---|---|---|
| mp_name | str | 0 | MP full name |
| constituency | str | 0 | Parliamentary constituency |
| state | str | 0 | State/UT |
| house | str | 0 | Lok Sabha / Rajya Sabha |
| allocated_amount | float64 | 0 | Total allocated (₹) |
| amount_recommended | float64 | 0 | Total recommended (₹) |
| total_expenditure | float64 | 0 | Total spent (₹) |
| utilization_pct | float64 | 0 | % of funds utilized |
| completed_works | int64 | 0 | Count of completed works |
| recommended_works | int64 | 0 | Count of recommended works |
| completion_rate_pct | float64 | 0 | Completion % |
| balance_not_yet_paid_to_vendors | float64 | 0 | Unpaid vendor balance (₹) |
| transaction_count | int64 | 0 | Total transaction count |
| successful_payments | int64 | 0 | Count of successful payments |
| pending_payments | int64 | 0 | Count of pending payments |

### mplads_completed_works_2026-09-10.csv
- **Size:** 11.16 MB | **Rows:** 44,028 | **Cols:** 11 (after dropping average_rating)
- **Duplicates:** 0
- **Columns:**

| Column | Type | Nulls | Description |
|---|---|---|---|
| work_id | int64 | 0 | Unique work identifier |
| work_description | str | 0 | Free-text description (NLP candidate!) |
| category | str | 0 | Normal/Others, SC, ST, etc. |
| mp_name | str | 0 | MP name |
| constituency | str | 0 | Constituency |
| state | str | 0 | State |
| house | str | 0 | Lok Sabha / Rajya Sabha |
| final_amount | int64 | 0 | Final amount paid (₹) |
| completed_date | datetime | 0 | When work was completed |
| has_images | bool | 0 | Whether photos uploaded |
| ida | str | 0 | Implementing District Authority |

### mplads_expenditures_2026-09-10.csv
- **Size:** 25.16 MB | **Rows:** 108,695 (76,313 unique) | **Cols:** 10
- **⚠️ Duplicates:** 32,382 (29.8%) — true duplicate rows from data export, to be removed in Module 2
- **Columns:**

| Column | Type | Nulls | Description |
|---|---|---|---|
| mp_name | str | 0 | MP name |
| constituency | str | 0 | Constituency |
| state | str | 0 | State |
| house | str | 0 | Lok Sabha / Rajya Sabha |
| work_description | str | 0 | Free-text description |
| vendor | str | 0 | **VENDOR NAME** (critical for network graph!) |
| ida | str | 0 | Implementing District Authority |
| expenditure_amount | int64 | 0 | Amount paid (₹) |
| expenditure_date | datetime | 0 | Payment date |
| payment_status | str | 0 | Payment Success / Payment In-Progress |

### mplads_recommended_works_2026-09-10.csv
- **Size:** 21.92 MB | **Rows:** 87,272 | **Cols:** 11
- **Duplicates:** 0
- **Columns:**

| Column | Type | Nulls | Description |
|---|---|---|---|
| work_id | int64 | 0 | Unique work identifier |
| work_description | str | ~1 | Free-text description |
| category | str | 0 | Work category |
| mp_name | str | 0 | MP name |
| constituency | str | 0 | Constituency |
| state | str | 0 | State |
| house | str | 0 | Lok Sabha / Rajya Sabha |
| recommended_amount | int64 | 0 | Recommended amount (₹) |
| recommendation_date | datetime | 0 | Date of recommendation |
| has_images | bool | 0 | Whether images exist |
| ida | str | 0 | Implementing District Authority |

---

## Feature Availability Summary

### Numerical Features
- allocated_amount, amount_recommended, total_expenditure, utilization_pct
- completed_works, recommended_works, completion_rate_pct
- balance_not_yet_paid_to_vendors, transaction_count, successful_payments, pending_payments
- final_amount, expenditure_amount, recommended_amount

### Categorical Features
- state, house, category, payment_status, constituency

### Text Features (NLP Candidates)
- work_description — exists in 3 datasets (completed, expenditures, recommended)
- vendor — exists in expenditures only

### Date Features
- completed_date, expenditure_date, recommendation_date

---

## Feasibility Assessment

| Capability | Feasible? | Data Source |
|---|---|---|
| **Isolation Forest** | ✅ YES | mp_summary numerical features |
| **Autoencoder** | ✅ YES | mp_summary numerical features |
| **NetworkX Graph** | ✅ YES | expenditures has vendor + MP + IDA |
| **NLP/spaCy** | ✅ YES | work_description text in 3 CSVs |
| **XGBoost** | ⚠️ TBD | No fraud labels — proxy labels possible |
| **GNN** | ⚠️ TBD | Depends on graph richness from NetworkX |

---

## Data Leakage Risks
- completed_works data must NOT be used as prediction target for models trained on recommended_works
- payment_status should NOT be a feature for anomaly detection (it's a result, not a predictor)

## Cleaning Needed (Module 2)
- Remove 32,382 duplicate rows from expenditures
- Parse all date columns (DONE in Module 1)
- Drop average_rating column (DONE in Module 1)
- Investigate work_description null in recommended_works (1 row only)

## Synthetic Data
None — all data is real MPLADS data from eSAKSHI/dataful.in

## Last Updated
2026-09-10T18:33 IST
