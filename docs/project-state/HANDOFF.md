# NEXORAS HANDOFF

## READ THIS FIRST
This document allows a new AI session to immediately continue NEXORAS development without re-reading the entire conversation history.

---

## PROJECT
NEXORAS

## PROBLEM
SIH26102 — AI-powered anomaly, fraud and inefficiency detection in MPLAD Scheme

## CURRENT STATUS
Phase 0 COMPLETE — Workspace initialized, project state system created, folder scaffold built.
Ready to begin Module 1 — Data Ingestion.

## CURRENT MODULE
Module 0 (complete) → Starting Module 1 — Data Ingestion

## CURRENT TASK
Inspect the 4 CSV datasets, profile their columns/types/missing values, and update DATA_STATE.md

## WHAT WAS JUST COMPLETED
- GitHub repo cloned to `D:\sih 2026\sample mvp\NEXORAS-sample-mvp\`
- AGENTS.md created with correct project context
- Full docs/project-state/ system created (12 files)
- Full folder scaffold created (backend/, frontend/, notebooks/, tests/)
- First commit pushed to GitHub

## FILES CHANGED
- AGENTS.md
- docs/project-state/MASTER_STATE.md
- docs/project-state/CURRENT_SESSION.md
- docs/project-state/MODULE_STATUS.md
- docs/project-state/ARCHITECTURE_STATE.md
- docs/project-state/DATA_STATE.md
- docs/project-state/MODEL_STATE.md
- docs/project-state/API_STATE.md
- docs/project-state/UI_STATE.md
- docs/project-state/BUGS_AND_ISSUES.md
- docs/project-state/DECISIONS.md
- docs/project-state/TEST_RESULTS.md
- docs/project-state/HANDOFF.md
- docs/project-state/CHANGELOG.md

## IMPORTANT CODE LOCATIONS
- Dataset CSVs: `D:\sih 2026\mplads dataset\`
- Repo root: `D:\sih 2026\sample mvp\NEXORAS-sample-mvp\`
- State files: `docs/project-state/`

## CURRENT ARCHITECTURE
Nothing implemented yet. See ARCHITECTURE_STATE.md.

## DATASET STATE
- 4 CSV files available, NOT yet inspected for columns/types
- See DATA_STATE.md for planned inspection

## MODEL STATE
All models NOT STARTED. See MODEL_STATE.md.

## API STATE
Not started. See API_STATE.md.

## UI STATE
Not started. See UI_STATE.md.

## TEST STATUS
No tests run yet.

## KNOWN BUGS
None.

## KNOWN LIMITATIONS
- No labeled fraud data — unsupervised only
- Dataset is state-level summary (work-level vendor/IA data TBD)

## IMPORTANT DECISIONS
- SQLite for MVP (DECISION-001)
- Unsupervised models first (DECISION-002)
- GNN deferred (DECISION-003)
- Airflow/Redis removed from MVP (DECISION-004)

## LAST STABLE CHECKPOINT
v0.0-workspace-init (2026-09-10)

## WHAT MUST NOT BE CHANGED
- Project identity: NEXORAS, SIH26102, MPLADS fraud detection
- Core proposed models: Isolation Forest + Autoencoder (both required)
- HackMD document architecture reference

## WHAT IS SAFE TO CHANGE
- Tech stack choices (SQLite ↔ PostgreSQL, etc.)
- Feature engineering specifics (once data is inspected)
- Module implementation details

## EXACT NEXT STEP
1. Run: `python notebooks/01_inspect_data.py` (create this script first)
2. Load each CSV and print: shape, columns, dtypes, null counts, sample rows
3. Update DATA_STATE.md with findings
4. Determine which features are feasible for ML models
5. Begin Module 1 — Data Ingestion implementation

## COMMAND TO VERIFY CURRENT STATE
```bash
git -C "D:\sih 2026\sample mvp\NEXORAS-sample-mvp" log --oneline
git -C "D:\sih 2026\sample mvp\NEXORAS-sample-mvp" status
```

## HOW TO CONTINUE
1. Read docs/project-state/MASTER_STATE.md
2. Read docs/project-state/MODULE_STATUS.md
3. Read this HANDOFF.md
4. Read docs/project-state/DATA_STATE.md
5. Inspect Git status
6. Create and run `notebooks/01_inspect_data.py`
7. Continue from EXACT NEXT STEP above
