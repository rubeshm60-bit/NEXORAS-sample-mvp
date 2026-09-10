# NEXORAS MASTER STATE

## Project
NEXORAS

## Problem Statement
SIH26102 — Development of an AI-powered system to detect anomalies, fraud, and inefficiencies in MPLAD Scheme implementation.

## Current Overall Status
IN PROGRESS

## Current Phase
Phase 2 — AI / ML Anomaly Engines

## Current Module
Module 4A — Isolation Forest

## Current Task
Implement unsupervised Isolation Forest anomaly detection engine on MP-level and Work-level features

## Last Completed Module
Module 3 — Feature Engineering

## Last Stable Checkpoint
v0.3-feature-engineering (2026-09-10)

## Repository Structure
```
NEXORAS-sample-mvp/
├── AGENTS.md
├── PROJECT_STATE.md (deprecated — see docs/project-state/)
├── docs/
│   ├── project-state/      ← All state files live here
│   └── modules/            ← Per-module documentation
├── backend/
│   ├── ingestion/
│   ├── cleaning/
│   ├── features/
│   ├── engine/
│   ├── scoring/
│   ├── api/
│   └── db/
├── frontend/src/
├── notebooks/
└── tests/
```

## Current Architecture
```
PROPOSED (not yet implemented):
CSV Dataset → Ingestion → Cleaning → Feature Engineering
→ Isolation Forest + Autoencoder (Anomaly Ensemble)
→ NetworkX Graph Engine
→ Risk Scoring Engine → SHAP/Explainability
→ FastAPI Backend → React Frontend
```

## Dataset
- Location: D:\sih 2026\mplads dataset\
- Files: mplads_completed_works, mplads_expenditures, mplads_recommended_works, mplads_mp_summary (CSVs)
- Stats: 774 MPs, 131,141 works recommended, 44,028 completed (33.57%)
- Status: RAW — not yet loaded or cleaned

## Implemented Models
- Module 4A (Isolation Forest) next

## Backend
- `backend/ingestion/loader.py`: Raw CSV loading, snake_case normalization, date parsing
- `backend/ingestion/validator.py`: Integrity validation
- `backend/cleaning/cleaner.py`: Deduplication, missing value imputation, string stripping
- `backend/features/builder.py`: Multi-grain feature engineering (MP, work, vendor)

## Frontend
Not started

## Database
Not decided — SQLite for MVP, PostgreSQL for production

## Completed Modules
- Module 0: System Understanding & Workspace Init
- Module 1: Data Ingestion (21/21 PASS, checkpoint: v0.1-data-ingestion)
- Module 2: Data Cleaning & Validation (25/25 PASS, checkpoint: v0.2-data-cleaning)
- Module 3: Feature Engineering (27/27 PASS, checkpoint: v0.3-feature-engineering)

## Modules In Progress
- Module 4A: Isolation Forest

## Blocked Modules
None

## Deferred Modules
- GNN (feasibility TBD after NetworkX is working)
- Airflow (not needed for prototype)
- Redis (deferred — not critical for MVP)

## Known Bugs
None

## Known Limitations
- No labeled fraud data — unsupervised models only for now

## Important Decisions
- DECISION-001: Use SQLite for MVP, not PostgreSQL (avoid infra overhead)
- DECISION-002: Start with Isolation Forest + Autoencoder before GNN
- DECISION-003: GNN deferred until NetworkX proves graph data is sufficient
- DECISION-004: Remove Airflow and Redis from MVP scope
- DECISION-005: Drop `average_rating` column (>99% null)
- DECISION-006: Treat duplicate records in raw expenditures as WARNING for cleaning
- DECISION-007: Preserve zero-allocation MPs with audit warning
- DECISION-008: Impute missing descriptions rather than dropping rows
- DECISION-009: Standardize missing categories to `"Uncategorized"`

## Latest Test Status
- Module 1 test suite (`tests/test_ingestion.py`): 21/21 PASS
- Module 2 test suite (`tests/test_cleaning.py`): 25/25 PASS
- Module 3 test suite (`tests/test_features.py`): 27/27 PASS

## Next 3 Actions
1. Implement Module 4A (`backend/engine/isolation_forest.py`): train unsupervised Isolation Forest models on MP features and work features
2. Create unit tests (`tests/test_isolation_forest.py`) verifying scoring, contamination thresholds, and reproducibility
3. Document in `docs/modules/module-04a-isolation-forest.md`

## EXACT NEXT TASK
Implement Module 4A — Isolation Forest: build unsupervised outlier isolation model and test anomaly scoring pipeline.

## Last Updated
2026-09-10T19:46 IST
