# NEXORAS HANDOFF

## READ THIS FIRST
This document allows a new AI session to immediately continue NEXORAS development.

---

## PROJECT
NEXORAS

## PROBLEM
SIH26102 — AI-powered anomaly, fraud and inefficiency detection in MPLAD Scheme

## CURRENT STATUS
**Module 1 — Data Ingestion: COMPLETE** (21/21 tests pass)
Ready to begin Module 2 — Data Cleaning & Validation.

## CURRENT MODULE
Module 1 (COMPLETE) → Starting Module 2 — Data Cleaning & Validation

## CURRENT TASK
Deduplicate expenditures dataset (32,382 duplicate rows) and validate all data

## WHAT WAS JUST COMPLETED
- Module 1 — Data Ingestion
- 4 CSV datasets profiled and loaded successfully
- loader.py: snake_case column normalization, date parsing, useless column dropping
- validator.py: integrity checks (empty cols, duplicates, nulls)
- 21/21 tests pass
- DATA_STATE.md populated with actual column profiles
- Tagged v0.1-data-ingestion

## FILES CHANGED (Module 1)
- backend/__init__.py (new)
- backend/ingestion/__init__.py (new)
- backend/ingestion/loader.py (new — core data loader)
- backend/ingestion/validator.py (new — data integrity checks)
- tests/test_ingestion.py (new — 21 tests)
- notebooks/01_inspect_data.py (new — profiling script)
- docs/modules/module-01-data-ingestion.md (new)
- docs/project-state/DATA_STATE.md (updated with real column profiles)
- docs/project-state/MODULE_STATUS.md (updated)
- .gitignore (new)

## IMPORTANT CODE LOCATIONS
- Data loader: `backend/ingestion/loader.py`
  - `load_all()` returns dict of 4 DataFrames
  - `load_mp_summary()`, `load_completed_works()`, `load_expenditures()`, `load_recommended_works()`
- Data validator: `backend/ingestion/validator.py`
- Tests: `tests/test_ingestion.py`
- Dataset CSVs: `D:\sih 2026\mplads dataset\`

## DATASET STATE (CONFIRMED)
| Dataset | Rows | Cols | Dupes | Key Fields |
|---|---|---|---|---|
| mp_summary | 774 | 15 | 0 | MP-level summary stats |
| completed_works | 44,028 | 11 | 0 | work_id, work_description, final_amount |
| expenditures | 108,695 | 10 | 32,382 (29.8%) | vendor (!), expenditure_amount |
| recommended_works | 87,272 | 11 | 0 | work_id, recommended_amount |

## MODEL STATE
All NOT STARTED. See MODEL_STATE.md.

## KNOWN BUGS
- expenditures has 32,382 true duplicate rows (to be removed in Module 2)

## IMPORTANT DECISIONS
- DECISION-001: SQLite for MVP
- DECISION-002: Unsupervised ML first
- DECISION-003: GNN deferred
- DECISION-004: Airflow/Redis removed
- DECISION-005: Dropped average_rating column (>99% null)
- DECISION-006: Expenditure duplicate threshold = WARNING at 29.8% (not CRITICAL — true export artifacts)

## LAST STABLE CHECKPOINT
**v0.1-data-ingestion** (2026-09-10)

## WHAT MUST NOT BE CHANGED
- loader.py column normalization logic (downstream code depends on snake_case names)
- Dataset file paths

## WHAT IS SAFE TO CHANGE
- Validation thresholds in validator.py
- Test expected row counts (data may be updated)

## EXACT NEXT STEP
1. Create `backend/cleaning/cleaner.py`
2. Deduplicate expenditures (drop_duplicates)
3. Handle the 1 null work_description in recommended_works
4. Validate cleaned data
5. Create tests for cleaning
6. Update state files
7. Tag v0.2-data-cleaning

## COMMAND TO VERIFY CURRENT STATE
```bash
git -C "D:\sih 2026\sample mvp\NEXORAS-sample-mvp" log --oneline -5
python "D:\sih 2026\sample mvp\NEXORAS-sample-mvp\tests\test_ingestion.py"
```

## HOW TO CONTINUE
1. Read docs/project-state/MASTER_STATE.md
2. Read docs/project-state/MODULE_STATUS.md
3. Read this HANDOFF.md
4. Read docs/project-state/DATA_STATE.md
5. Inspect Git status
6. Run tests/test_ingestion.py to verify current state
7. Continue from EXACT NEXT STEP above
