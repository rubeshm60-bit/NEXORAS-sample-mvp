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
Module 5 — Anomaly Ensemble

## Current Task
Combine Isolation Forest (Module 4A) and Neural Autoencoder (Module 4B) into an explainable multi-signal anomaly ensemble

## Last Completed Module
Module 4B — Autoencoder

## Last Stable Checkpoint
v0.5-autoencoder (2026-09-10)

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
- Model 1 (Isolation Forest): COMPLETE (MPIsolationForest + WorkIsolationForest, 25/25 PASS)
- Model 2 (Autoencoder): COMPLETE (MPAutoencoder in PyTorch, 26/26 PASS)
- Model 3 (Anomaly Ensemble): IN PROGRESS next

## Backend
- `backend/ingestion/loader.py`: Raw CSV loading, snake_case normalization, date parsing
- `backend/ingestion/validator.py`: Integrity validation
- `backend/cleaning/cleaner.py`: Deduplication, missing value imputation, string stripping
- `backend/features/builder.py`: Multi-grain feature engineering (MP, work, vendor)
- `backend/engine/isolation_forest.py`: MPIsolationForest & WorkIsolationForest anomaly models
- `backend/engine/autoencoder.py`: Deep neural reconstruction Autoencoder in PyTorch

## Frontend
Not started

## Database
Not decided — SQLite for MVP, PostgreSQL for production

## Completed Modules
- Module 0: System Understanding & Workspace Init
- Module 1: Data Ingestion (21/21 PASS, checkpoint: v0.1-data-ingestion)
- Module 2: Data Cleaning & Validation (25/25 PASS, checkpoint: v0.2-data-cleaning)
- Module 3: Feature Engineering (27/27 PASS, checkpoint: v0.3-feature-engineering)
- Module 4A: Isolation Forest (25/25 PASS, checkpoint: v0.4-isolation-forest)
- Module 4B: Autoencoder (26/26 PASS, checkpoint: v0.5-autoencoder)

## Modules In Progress
- Module 5: Anomaly Ensemble

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
- DECISION-001 through DECISION-009 documented in `docs/project-state/DECISIONS.md`

## Latest Test Status
- Module 1 test suite (`tests/test_ingestion.py`): 21/21 PASS
- Module 2 test suite (`tests/test_cleaning.py`): 25/25 PASS
- Module 3 test suite (`tests/test_features.py`): 27/27 PASS
- Module 4A test suite (`tests/test_isolation_forest.py`): 25/25 PASS
- Module 4B test suite (`tests/test_autoencoder.py`): 26/26 PASS

## Next 3 Actions
1. Implement Module 5 (`backend/engine/ensemble.py`): combine Isolation Forest & Neural Autoencoder scores with agreement scoring
2. Create unit tests (`tests/test_ensemble.py`) verifying calibrated ensemble scores, signal disagreement identification, and confidence intervals
3. Document in `docs/modules/module-05-anomaly-ensemble.md`

## EXACT NEXT TASK
Implement Module 5 — Anomaly Ensemble: combine Isolation Forest and Autoencoder scores, generate multi-model consensus flags, and expose dual-signal explainability.

## Last Updated
2026-09-10T20:14 IST
