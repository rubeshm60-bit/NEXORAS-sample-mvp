# MODULE 03 — FEATURE ENGINEERING

## Purpose
Construct mathematical, financial, execution, and graph-adjacent feature matrices across three operational grains: MPs, individual works, and contractors/vendors.

## Why NEXORAS Needs It
Raw transactional records cannot directly train anomaly detection algorithms. Feature engineering transforms unstructured, disparate tables into mathematically normalized representations of behavior, concentration, and cost variation.

## Dependencies
- Module 1 (`backend/ingestion/loader.py`)
- Module 2 (`backend/cleaning/cleaner.py`)
- `numpy`, `pandas`

## Input
Cleaned DataFrames output by `clean_all()`:
- `mp_summary`: 774 rows
- `expenditures`: 76,313 rows (deduplicated)
- `completed_works`: 44,028 rows
- `recommended_works`: 87,272 rows

## Output
Dictionary of engineered feature matrices:
1. `mp_features` (774 rows × 33 columns):
   - `utilization_rate`: `total_expenditure / allocated_amount`
   - `recommendation_rate`: `amount_recommended / allocated_amount`
   - `unspent_ratio`: `(allocated_amount - total_expenditure) / allocated_amount`
   - `completion_rate`: `completed_works / recommended_works`
   - `unpaid_balance_ratio`: `balance_not_yet_paid_to_vendors / total_expenditure`
   - `pending_payment_ratio`: `pending_payments / transaction_count`
   - `avg_transaction_size`: `total_expenditure / transaction_count`
   - `vendor_count`: Number of distinct vendors engaged by the MP
   - `vendor_hhi`: Herfindahl-Hirschman Index (`sum(s_i^2)`) of vendor payment concentration
   - `top_vendor_share`: Fraction of expenditure claimed by the MP's #1 vendor
   - `avg_spend_per_vendor`: `total_expenditure / vendor_count`
   - `avg_work_cost`: Mean cost of completed works
   - `work_cost_std`: Standard deviation of completed work costs
   - `image_compliance_rate`: Fraction of completed works with geo-tagged images
   - `ida_count`: Number of distinct IDAs involved

2. `work_features` (44,028 rows × 19 columns):
   - `cat_median`, `cat_mean`, `cat_std`, `cat_iqr`: Category baselines
   - `cost_deviation_z`: Z-score deviation from category mean
   - `cost_to_median_ratio`: Ratio of work cost to category median
   - `is_extreme_cost_outlier`: Boolean indicator for `final_amount > median + 3*IQR`
   - `image_missing`: Boolean indicator for missing audit imagery

3. `vendor_features` (28,206 rows × 13 columns):
   - `total_payout`: Cumulative funds awarded to vendor
   - `transaction_count`: Number of transactions
   - `mp_count`: Number of distinct MPs awarding contracts
   - `state_count`: Number of states operating in
   - `ida_count`: Number of IDAs engaging vendor
   - `in_progress_ratio`: Percentage of transactions stalled in "Payment In-Progress"
   - `multi_mp_vendor`: Flag for vendors serving 3+ MPs (cartel/collusion signal)
   - `high_value_vendor`: Flag for top 5% highest-earning contractors

## Files
| File | Purpose |
|---|---|
| `backend/features/__init__.py` | Package initializer |
| `backend/features/builder.py` | Feature extraction pipeline for MP, work, and vendor grains |
| `tests/test_features.py` | 27-test validation suite |

## Tests & Verification
27 tests covering:
- Exact row counts (774 MPs, 44,028 works, 28,206 vendors)
- Verification that zero NaNs or Infinite values exist in engineered numeric columns
- Boundary checks for ratios and indices (`vendor_hhi`, `top_vendor_share`, `image_compliance_rate` all strictly in [0.0, 1.0])
- Outlier detection functionality
- Flagging logic for multi-MP and high-value contractors

## Test Results
**27/27 PASS** (2026-09-10)

## Edge Cases Handled
- Safe element-wise division guarding against zero denominators (e.g., zero allocation MP)
- Missing expenditure or completed works records for newly elected MPs imputed with zeros
- Robust IQR-based category baseline calculations preventing division by zero for single-work categories

## Definition of Done
✅ All feature functions execute deterministically
✅ Zero NaNs or Infs in engineered numeric columns
✅ Bounded ratios strictly conform to mathematical limits
✅ 27/27 unit tests pass
✅ Documentation exists

## Current Status
COMPLETE

## Last Stable Checkpoint
v0.3-feature-engineering

## Next Action
Module 4A — Isolation Forest (Statistical Anomaly Detection Engine)
