# Module 15: FastAPI Backend

## Objective
Provide RESTful endpoints to expose the computed risk intelligence, anomaly signals, graph structures, and project metadata to the frontend application.

## Overview
This module wraps the SQLAlchemy database queries inside a lightweight, asynchronous `FastAPI` application. It standardizes the API responses using strictly typed `Pydantic` schemas, guaranteeing that the frontend receives predictable payloads regardless of database schema changes. 

## Endpoints Implemented
- `GET /health`: Verifies API functionality and successful connection to the SQLite database.
- `GET /dashboard/summary`: Aggregates the macro state of the platform (total projects, sanctioned amounts, high-risk counts).
- `GET /projects`: Paginated listing of all works, with optional filtering by `risk_tier`.
- `GET /projects/{project_id}`: Deep dive into a specific project, returning base metadata joined with its comprehensive `ProjectRiskScore` and the raw "Why Flagged" report.
- `GET /anomalies`: Syntactic sugar over the `/projects` endpoint, pre-filtered and ordered to show `CRITICAL_RISK` and `HIGH_RISK` entities first.
- `GET /vendors`: Paginated listing of contractors and their aggregated statistics.
- `GET /vendors/{vendor_id}`: Vendor-level dive returning specific `VendorRiskProfile` flags (e.g., Cartel signals).
- `GET /network`: Mock graph topology endpoint formatted for immediate consumption by Cytoscape.js on the frontend.

## Schema Validation
All requests and responses strictly adhere to `Pydantic` v2 models (`backend/api/schemas.py`). 
This guarantees that missing or anomalous DB rows fall back gracefully without causing server 500 crashes (via `Optional[]`).

## Status
- **Status**: COMPLETE
- **Code**: `backend/api/main.py`, `backend/api/schemas.py`
- **Tests**: `tests/test_api.py` (100% Pass Rate)
