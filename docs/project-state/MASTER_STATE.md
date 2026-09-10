# NEXORAS MASTER STATE

## Project
NEXORAS

## Problem Statement
SIH26102 — Development of an AI-powered system to detect anomalies, fraud, and inefficiencies in MPLAD Scheme implementation.

## Current Overall Status
IN PROGRESS

## Current Phase
Phase 3 — Network Intelligence & Risk Scoring

## Current Module
Module 7 — Vendor Network Intelligence

## Current Task
Implement vendor network intelligence, contractor concentration metrics, and cross-constituency cartel detection

## Last Completed Module
Module 5 — Anomaly Ensemble

## Last Stable Checkpoint
v0.6-anomaly-ensemble (2026-09-10)

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
- Model 3 (Anomaly Ensemble): COMPLETE (AnomalyEnsemble, 29/29 PASS)
- Model 4 (Vendor Intelligence & Network Graph): IN PROGRESS next

## Backend
- `backend/ingestion/loader.py`: Raw CSV loading, snake_case normalization, date parsing
- `backend/ingestion/validator.py`: Integrity validation
- `backend/cleaning/cleaner.py`: Deduplication, missing value imputation, string stripping
- `backend/features/builder.py`: Multi-grain feature engineering (MP, work, vendor)
- `backend/engine/isolation_forest.py`: MPIsolationForest & WorkIsolationForest anomaly models
- `backend/engine/autoencoder.py`: Deep neural reconstruction Autoencoder in PyTorch
- `backend/engine/ensemble.py`: AnomalyEnsemble dual-signal consensus engine

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
- Module 5: Anomaly Ensemble (29/29 PASS, checkpoint: v0.6-anomaly-ensemble)

## Modules In Progress
- Module 7: Vendor Network Intelligence (Module 6 XGBoost evaluated as unnecessary without ground-truth fraud labels)

## Blocked Modules
None

## Deferred Modules
- Module 6 (XGBoost): Supervised fraud labels do not exist in open portal data
- Module 9 (GNN): Feasibility evaluated following NetworkX graph analysis
- Airflow: Scheduled DAGs not required for hackathon MVP
- Redis: Memory caching deferred for hackathon MVP

## Known Bugs
None

## Known Limitations
- No labeled fraud data — unsupervised ensemble is the primary anomaly engine

## Important Decisions
- DECISION-001 through DECISION-009 documented in `docs/project-state/DECISIONS.md`

## Latest Test Status
- Module 1 test suite (`tests/test_ingestion.py`): 21/21 PASS
- Module 2 test suite (`tests/test_cleaning.py`): 25/25 PASS
- Module 3 test suite (`tests/test_features.py`): 27/27 PASS
- Module 4A test suite (`tests/test_isolation_forest.py`): 25/25 PASS
- Module 4B test suite (`tests/test_autoencoder.py`): 26/26 PASS
- Module 5 test suite (`tests/test_ensemble.py`): 29/29 PASS

## Next 3 Actions
1. Implement Module 7 (`backend/engine/vendor_intelligence.py`): vendor risk profiling, cross-constituency cartel detection, and payout concentration
2. Implement Module 8 (`backend/engine/network_graph.py`): NetworkX bipartite and multi-partite graph construction (MP-Vendor-Project)
3. Document in `docs/modules/` and tag checkpoints

## EXACT NEXT TASK
Implement Module 7 & 8: Vendor Network Intelligence and NetworkX Graph Engine.

## Last Updated
2026-09-10T20:28 IST
