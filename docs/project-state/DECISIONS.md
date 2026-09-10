# NEXORAS DECISIONS

## DECISION-001
**Date:** 2026-09-10
**Topic:** Database selection for MVP
**Decision:** Use SQLite for MVP prototype
**Reason:** PostgreSQL configuration (Docker, users, schema) would consume too much hackathon time. SQLite is zero-config, fast to set up, and migration-friendly.
**Alternatives Considered:** PostgreSQL (production-grade), MongoDB (document store)
**Consequence:** Some advanced query features won't be available. Migration to PostgreSQL required for production.
**Future Migration:** All models use SQLAlchemy ORM — switch dialect to PostgreSQL by changing DB_URL in .env

---

## DECISION-002
**Date:** 2026-09-10
**Topic:** Starting point for ML models
**Decision:** Start with Isolation Forest + Autoencoder (unsupervised) before attempting supervised models
**Reason:** No labeled fraud data exists in the MPLADS dataset. Unsupervised models don't require labels.
**Alternatives Considered:** XGBoost with proxy labels, rule-based scoring only
**Consequence:** Risk scores will be based on statistical deviation from normal, not "known fraud" patterns
**Future Migration:** XGBoost can be added later if proxy labels are validated

---

## DECISION-003
**Date:** 2026-09-10
**Topic:** GNN implementation timing
**Decision:** Defer GNN until NetworkX graph intelligence proves sufficient data and relationships exist
**Reason:** GNN requires sufficient graph structure, node features, and ideally labels — none confirmed yet
**Alternatives Considered:** Build GNN first (risky — may not work without proper data)
**Consequence:** MVP uses NetworkX only for graph intelligence
**Future Migration:** GNN as Module 9 if NetworkX shows rich enough graph data

---

## DECISION-004
**Date:** 2026-09-10
**Topic:** Infrastructure simplification
**Decision:** Remove Airflow and Redis from MVP scope
**Reason:** Not needed for a hackathon prototype. Adds infra overhead with no visible demo value.
**Alternatives Considered:** Keep Airflow for scheduled pipeline runs
**Consequence:** Pipeline runs as direct Python scripts, not scheduled DAGs
**Future Migration:** Airflow/Celery can be added for production scheduling

---
