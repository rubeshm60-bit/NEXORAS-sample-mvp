# MODULE 02 — DATA CLEANING & VALIDATION

## Purpose
Clean raw DataFrames from Module 1. Remove duplicates, fill nulls, standardize categories.

## Why NEXORAS Needs It
Dirty data = garbage ML models. Expenditures had 29.8% duplicates that would massively skew anomaly detection.

## Dependencies
- Module 1 (backend/ingestion/loader.py)
- pandas

## Input
4 raw DataFrames from `loader.load_all()`

## Output
4 cleaned DataFrames with:
- Zero duplicate rows
- Zero null work_descriptions (filled with "[No description]")
- Zero NaN categories (filled with "Uncategorized")
- Stripped whitespace on all string columns
- No rows removed from mp_summary (every MP preserved)

## Cleaning Operations Performed

| Dataset | Operation | Before | After | Impact |
|---|---|---|---|---|
| expenditures | Deduplication | 108,695 | 76,313 | 32,382 removed (29.8%) |
| completed_works | Fill null descriptions | 85 nulls | 0 nulls | — |
| completed_works | Fill null categories | 5 nulls | 0 nulls → "Uncategorized" |
| recommended_works | Fill null descriptions | 52 nulls | 0 nulls | — |
| recommended_works | Fill null categories | 5 nulls | 0 nulls → "Uncategorized" |
| mp_summary | Flag zero allocation | 1 MP flagged | Preserved (not removed) | CHAVAN VASANTRAO BALWANTRAO |
| ALL | Strip whitespace | — | — | Clean strings |

## Files
| File | Purpose |
|---|---|
| backend/cleaning/__init__.py | Package init |
| backend/cleaning/cleaner.py | All cleaning functions |
| tests/test_cleaning.py | 25 tests |
| notebooks/02_cleaning_analysis.py | Pre-cleaning analysis |

## Tests
25 tests covering:
- Expenditure deduplication (reduced, no remaining dupes, correct count)
- MP summary preservation (no rows lost)
- Null work_description filling
- Category standardization (no NaN, Uncategorized present)
- Financial integrity (no negatives)
- No empty columns
- DataFrames not empty
- Column counts unchanged

## Test Results
**25/25 PASS** (2026-09-10)

## Edge Cases
- 1 MP (CHAVAN VASANTRAO BALWANTRAO, Nanded) has zero allocation — flagged but preserved
- 85 + 52 = 137 null work_descriptions across datasets — filled, not removed

## Known Problems
None after cleaning.

## Known Limitations
- Deduplication uses exact row matching only — partial duplicates or near-duplicates not detected
- No standardization of MP name variants (e.g., "Shri X" vs "X")

## Decisions
- DECISION-007: Keep zero-allocation MPs (real data, don't remove)
- DECISION-008: Fill null descriptions with "[No description]" instead of dropping rows
- DECISION-009: NaN categories → "Uncategorized" (not dropped)

## Definition of Done
✅ Expenditures deduplicated (108,695 → 76,313)
✅ All null work_descriptions filled
✅ All NaN categories standardized
✅ No negative financial values
✅ No empty columns
✅ 25/25 tests pass
✅ Documentation exists

## Current Status
COMPLETE

## Last Stable Checkpoint
v0.2-data-cleaning

## Next Action
Module 3 — Feature Engineering
