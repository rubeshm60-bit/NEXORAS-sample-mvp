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

## DECISION-005
**Date:** 2026-09-10
**Topic:** Dropping unpopulated rating column
**Decision:** Drop `average_rating` column across all datasets during ingestion
**Reason:** The column is >99% null across all datasets (100% in completed works, 770/774 in mp_summary) and provides no diagnostic value for fraud detection.
**Alternatives Considered:** Keep and impute with 0 or mean
**Consequence:** Cleaner DataFrame schemas without misleading null-heavy columns
**Future Migration:** If rating system becomes active in future eSAKSHI exports, column can be re-enabled

---

## DECISION-006
**Date:** 2026-09-10
**Topic:** Duplicate threshold in data validator
**Decision:** Treat duplicate percentage in expenditures as WARNING rather than CRITICAL in raw ingestion
**Reason:** Raw expenditure export from eSAKSHI contains 32,382 exact duplicate rows (29.8%) due to multi-batch export artifacts. Raising CRITICAL threshold to 50% allows raw loading to pass while handing deduplication to Module 2.
**Alternatives Considered:** Block ingestion on duplicates
**Consequence:** Ingestion accepts raw government exports and cleaning stage explicitly cleans them
**Future Migration:** Validator retains warnings for visibility

---

## DECISION-007
**Date:** 2026-09-10
**Topic:** Zero-allocation MP records
**Decision:** Flag but preserve MPs with zero allocated amount (e.g. Chavan Vasantrao Balwantrao)
**Reason:** MPs with zero allocation are valid representatives (e.g. newly elected, bye-elections, or unallocated portfolios). Dropping them distorts overall constituency coverage and national aggregates.
**Alternatives Considered:** Drop zero-allocation MP records
**Consequence:** Downstream models must handle division by zero (e.g. expenditure / allocation) using safe division safeguards
**Future Migration:** Keep audit flags for zero-allocation MPs

---

## DECISION-008
**Date:** 2026-09-10
**Topic:** Imputation of missing work descriptions
**Decision:** Impute null `work_description` with `"[No description]"` rather than dropping rows
**Reason:** Only 85 rows in completed_works and 52 in recommended_works lack text descriptions. The financial values and IDs are valid. Dropping them would discard legitimate financial data.
**Alternatives Considered:** Drop rows with missing descriptions
**Consequence:** Financial analysis retains full transaction volume; NLP pipeline will treat `"[No description]"` as neutral
**Future Migration:** Flag missing description works as documentation irregularities in risk engine

---

## DECISION-009
**Date:** 2026-09-10
**Topic:** Standardization of missing work categories
**Decision:** Impute NaN work categories as `"Uncategorized"`
**Reason:** 5 rows in completed_works and 5 in recommended_works have NaN category. Standardizing to a string `"Uncategorized"` prevents categorical grouping and encoding errors in feature engineering.
**Alternatives Considered:** Drop rows or impute to mode ("Normal/Others")
**Consequence:** Explicit categorization allows tracking works that lacked administrative classification
**Future Migration:** Can use NLP on description to automatically predict category in future
