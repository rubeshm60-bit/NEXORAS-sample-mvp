# NEXORAS TEST RESULTS

> No tests run yet. This file will be updated after each testing session.

## Format

---
# TEST SESSION — 2026-09-10 (Module 1: Data Ingestion)

## Module
Module 1 — Data Ingestion

## Command
```bash
python tests/test_ingestion.py
```

## Tests Run
21

## Passed
21

## Failed
0

## Edge Cases Tested
- Snake_case column renaming with Unicode ₹ symbol and parenthesis stripping
- ISO 8601 date parsing for multiple datetime formats
- Removal of >99% null average_rating column
- Detection of 32,382 duplicate rows in expenditures

## Output
```
RESULTS: 21/21 tests passed, 0 failed
ALL TESTS PASSED
```

## Bugs Found
- Test threshold for completed_works row count was set to 45,000 based on raw newline counting, whereas actual parsed DataFrame row count was 44,028. Fixed threshold in `test_ingestion.py`.
- Unicode encode error on Windows console cp1252 for ₹ character. Fixed with UTF-8 wrapper.

## Final Status
PASS

## Commit / Checkpoint
v0.1-data-ingestion

---
# TEST SESSION — 2026-09-10 (Module 2: Data Cleaning & Validation)

## Module
Module 2 — Data Cleaning & Validation

## Command
```bash
python tests/test_cleaning.py
```

## Tests Run
25

## Passed
25

## Failed
0

## Edge Cases Tested
- Complete deduplication of expenditures (108,695 -> 76,313 rows, removing 32,382 exact duplicate records)
- Zero-loss integrity for mp_summary (774 rows preserved despite 1 zero-allocation MP)
- Missing work description imputation with `"[No description]"` (85 in completed, 52 in recommended)
- Missing category standardization to `"Uncategorized"` (5 in completed, 5 in recommended)
- Verification of zero negative monetary values across all tables
- Verification that no empty columns exist post-cleaning
- Verification of column structure preservation

## Output
```
CLEANING SUMMARY
  Total rows before: 240769
  Total rows after:  208387
  Rows removed:      32382

RESULTS: 25/25 tests passed, 0 failed
ALL TESTS PASSED
```

## Bugs Found
- None. All 25 checks passed on initial run.

## Final Status
PASS

## Commit / Checkpoint
v0.2-data-cleaning

---
# TEST SESSION — 2026-09-10 (Module 3: Feature Engineering)

## Module
Module 3 — Feature Engineering

## Command
```bash
python tests/test_features.py
```

## Tests Run
27

## Passed
27

## Failed
0

## Edge Cases Tested
- Multi-dataset aggregation with safe division guarding against zero denominators (e.g. zero-allocation MP)
- Missing expenditure or completed works records imputed cleanly without generating NaNs or Infs
- Bounded index mathematical validation: `vendor_hhi` strictly within [0.0, 1.0]
- Top contractor fund concentration: `top_vendor_share` strictly within [0.0, 1.0]
- Image compliance rate strictly within [0.0, 1.0]
- Cost deviation Z-score and ratio to category median calculation
- Identification of multi-constituency contractors (serving >= 3 MPs)
- Identification of high-value contractors (>= 95th percentile payout)

## Output
```
FEATURE ENGINEERING SUMMARY:
  mp_features: 774 rows, 33 columns (0 NaNs in features)
  work_features: 44028 rows, 19 columns (0 NaNs in features)
  vendor_features: 28206 rows, 13 columns (0 NaNs in features)

RESULTS: 27/27 tests passed, 0 failed
ALL TESTS PASSED
```

## Bugs Found
- None. All 27 checks passed on initial run.

## Final Status
PASS

## Commit / Checkpoint
v0.3-feature-engineering


