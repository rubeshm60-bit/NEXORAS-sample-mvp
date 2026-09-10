# Module 17: End-to-End Integration Pipeline

## Objective
Connect all individual modules created in Phases 1, 2, and 3 into a single, cohesive execution pipeline. The script must ingest raw data, execute data cleaning, build features, run anomaly detection, extract SHAP explanations, calculate unified risk scores, and seed the SQLite database to prepare the FastAPI backend.

## Overview
The `run_pipeline.py` script acts as the orchestrator for the entire system. It proves the functional viability of the MVP by taking real raw data from `D:\sih 2026\mplads dataset` and pushing it through the entire lifecycle.

## Pipeline Steps (`run_pipeline.py`)
1. **Initialize DB**: Connects to SQLAlchemy engine and resets tables via `Base.metadata.drop_all()` and `init_db()`.
2. **Ingestion & Cleaning**: Uses `loader.py` and `cleaner.py` to ingest 774 MPs, 44k Completed Works, and 76k Expenditures, deduplicating records safely.
3. **Feature Engineering**: Structures ML-ready data for works.
4. **Machine Learning & Explanations**: 
   - Fires up `WorkIsolationForest` to generate raw anomaly scores.
   - Triggers `ModelExplainer` (SHAP) to find attribution for anomalies.
   - Pushes output through `WhyFlaggedEngine` to generate English text audit reports.
5. **Unified Risk Scoring**: Feeds all modular signals (anomaly score, graph centrality, vendor risk) into the `UnifiedRiskEngine` to output normalized 0-100 `risk_tier` and `unified_score` values.
6. **Database Seeding**: Maps output rows to Pydantic/SQLAlchemy models (`MP`, `Project`, `Vendor`, `ProjectRiskScore`) and commits them to `nexoras_mvp.db`.

## Limitations for MVP
- Generating SHAP trees and Risk Scores for all 44,000 completed works iteratively in pure Python would take too long for rapid hackathon testing. The integration script isolates the computationally heavy steps (Modeling, Explaining, DB Seeding) to the **first 500 records**.

## Status
- **Status**: COMPLETE
- **Code**: `run_pipeline.py`
- **Tests**: Script executes with exit code 0. Database verified.
