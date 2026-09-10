# MODULE 01 — DATA INGESTION

## Purpose
Load the 4 raw MPLADS CSV datasets into normalized pandas DataFrames.

## Why NEXORAS Needs It
This is the entry point for ALL downstream ML models and analysis. Without clean, reliable data loading, nothing else works.

## Dependencies
- pandas (Python package)
- Dataset CSVs at `D:\sih 2026\mplads dataset\`

## Input
4 CSV files:
- mplads_mp_summary_2026-09-10.csv (774 rows)
- mplads_completed_works_2026-09-10.csv (44,028 rows)
- mplads_expenditures_2026-09-10.csv (108,695 rows)
- mplads_recommended_works_2026-09-10.csv (87,272 rows)

## Output
4 pandas DataFrames with:
- Snake_case column names (no spaces, no ₹ symbol, no parentheses)
- Date columns parsed to datetime
- Useless columns dropped (average_rating)

## Architecture
```
CSV files → loader.py (load + normalize) → validator.py (integrity checks) → DataFrames
```

## Files
| File | Purpose |
|---|---|
| backend/ingestion/__init__.py | Package init |
| backend/ingestion/loader.py | Load + normalize all 4 CSVs |
| backend/ingestion/validator.py | Validate DataFrames for issues |
| tests/test_ingestion.py | 21 tests for loading, normalization, parsing |
| notebooks/01_inspect_data.py | Initial data profiling script |

## Configuration
- DATASET_DIR in loader.py = `D:\sih 2026\mplads dataset`

## Tests
21 tests covering:
- Row counts per dataset
- Column name normalization (snake_case)
- Date column parsing (datetime64)
- Useless column dropping (average_rating)
- Non-empty DataFrames
- Validation passes

## Test Results
**21/21 PASS** (2026-09-10)

## Edge Cases
- Expenditures has 32,382 duplicate rows (29.8%) — flagged as WARNING, deferred to Module 2 for deduplication
- 1 null work_description in recommended_works — non-critical

## Known Problems
- Expenditure duplicates need deduplication in Module 2

## Known Limitations
- Loader hardcodes dataset filenames (dated 2026-09-10)
- No streaming/chunked loading for very large files

## Decisions
- Dropped average_rating (>99% null across all datasets)
- Duplicate threshold set to WARNING at 29.8%, not CRITICAL — they are true duplicates from data export

## Definition of Done
✅ All 4 CSVs load successfully
✅ Date columns parsed as datetime
✅ Column names normalized to snake_case
✅ Useless columns dropped
✅ Validation reports issues correctly
✅ 21/21 tests pass
✅ Documentation exists

## Current Status
COMPLETE (pending checkpoint commit)

## Last Stable Checkpoint
v0.1-data-ingestion (pending)

## Next Action
Commit, tag, and move to Module 2 — Data Cleaning
