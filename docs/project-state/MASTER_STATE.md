# NEXORAS MASTER STATE

## Project
NEXORAS

## Problem Statement
SIH26102 — Development of an AI-powered system to detect anomalies, fraud, and inefficiencies in MPLAD Scheme implementation.

## Current Overall Status
IN PROGRESS

## Current Phase
Phase 0 — Workspace Setup & Project Scaffolding

## Current Module
Module 0 — System Understanding

## Current Task
Initialize project state system and folder scaffold

## Last Completed Module
None

## Last Stable Checkpoint
v0.0-workspace-init (2026-09-10)

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
None

## Backend
Not started

## Frontend
Not started

## Database
Not decided — SQLite for MVP, PostgreSQL for production

## Completed Modules
None

## Modules In Progress
- Module 0: System Understanding / Workspace Init

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
- Dataset is state-level summary only (no work-level vendor/IA data yet)

## Important Decisions
- DECISION-001: Use SQLite for MVP, not PostgreSQL (avoid infra overhead)
- DECISION-002: Start with Isolation Forest + Autoencoder before GNN
- DECISION-003: GNN deferred until NetworkX proves graph data is sufficient

## Latest Test Status
No tests run yet

## Next 3 Actions
1. Inspect and profile the 4 CSV datasets (column names, types, missing values)
2. Create Module 1 — Data Ingestion script
3. Create DATA_STATE.md from real dataset inspection

## EXACT NEXT TASK
Run EDA on `mplads_mp_summary_2026-09-10.csv` first (smallest file), then the larger CSVs. Profile all 4 datasets and fill in DATA_STATE.md.

## Last Updated
2026-09-10T18:07 IST
