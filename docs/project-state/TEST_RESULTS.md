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

