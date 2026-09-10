# NEXORAS ARCHITECTURE STATE

## PROPOSED ARCHITECTURE (From HackMD + Prompt)
The original proposal describes a full system:
```
eSAKSHI / dataful.in Data
        ↓
  Data Ingestion Layer
        ↓
  Feature Engineering
        ↓
  ┌─────────────────────────────┐
  │ Isolation Forest            │
  │ Autoencoder                 │  ← Anomaly Ensemble
  │ XGBoost (if labels exist)   │
  └─────────────────────────────┘
        ↓
  NetworkX Graph Engine → (GNN future)
        ↓
  NLP / spaCy (if text data exists)
        ↓
  Risk Scoring Engine (0-100)
        ↓
  SHAP / "Why Flagged?" Explainability
        ↓
  PostgreSQL Database
        ↓
  FastAPI Backend (REST APIs)
        ↓
  React + D3.js + Mapbox Frontend
```

## CURRENT MVP ARCHITECTURE (Actually Implemented)
```
NOTHING IMPLEMENTED YET
Status: Workspace initialized only
```

## FUTURE ARCHITECTURE (Not Yet Implemented)
All components above are future. Starting with data ingestion → ML engine.

## Architecture Decisions
- See DECISIONS.md for rationale on each component choice
- GNN deferred until NetworkX proves feasibility
- SQLite for MVP instead of PostgreSQL
- Redis/Airflow not needed for hackathon prototype

## Change Log
| Date | Change | Reason |
|---|---|---|
| 2026-09-10 | Initial architecture defined | Project kickoff |
