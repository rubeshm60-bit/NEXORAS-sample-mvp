# Module 14: Database

## Objective
Design and implement the storage structure and schemas for the NEXORAS system, capable of persisting raw operational data alongside computed intelligence outputs (risk scores, anomalies, explainability strings).

## Overview
As per architectural constraints, configuring complex infrastructure like PostgreSQL could delay the MVP. Thus, this module employs SQLAlchemy to define a highly normalized ORM schema, currently mapped to SQLite (`nexoras_mvp.db`). Because we use strict SQLAlchemy paradigms, migrating this to PostgreSQL later will require only changing the connection URL.

## Tables & Relationships
- **`mps`**: Stores parliamentarian profiles, aggregated statistics, and macro utilization behaviors.
- **`agencies`**: Stores Implementing District Authorities (IDAs).
- **`vendors`**: Stores contractor profiles and transaction aggregates.
- **`projects`**: The core MPLADS works. Linked via foreign keys to an MP, an Agency, and associated Payments.
- **`payments`**: Disbursement transactions bridging Projects, Vendors, and Agencies.
- **Intelligence Tables**:
  - **`project_risk_scores`**: Holds the unified risk score out of 100, the categorical risk tier, exact points from the 5 intelligence pillars, and the pre-computed "Why Flagged" multi-line explanation.
  - **`mp_risk_scores`**: Aggregated ML isolation scores at the MP entity level.
  - **`vendor_risk_profiles`**: Holds syndicate/monopoly flags for high-risk contractors.

## Status
- **Status**: COMPLETE
- **Code**: `backend/db/models.py`, `backend/db/database.py`
- **Tests**: `tests/test_database.py` (100% Pass Rate)
