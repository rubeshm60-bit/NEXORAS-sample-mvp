# PROJECT_STATE.md — NEXORAS Build Tracker

> Last Updated: 2026-09-10
> Current Phase: **Step 0 — Workspace Setup**

---

## ✅ Completed

### Step 0 — Workspace Preparation
- [x] GitHub repo created: `rubeshm60-bit/NEXORAS-sample-mvp`
- [x] Repo cloned to `D:\sih 2026\sample mvp\NEXORAS-sample-mvp\`
- [x] AGENTS.md created with full verified project context
- [x] PROJECT_STATE.md initialized (this file)
- [x] Real MPLADS dataset confirmed available at `D:\sih 2026\mplads dataset\`
  - `mplads_completed_works_2026-09-10.csv` (11.7 MB)
  - `mplads_expenditures_2026-09-10.csv` (26.4 MB)
  - `mplads_recommended_works_2026-09-10.csv` (23 MB)
  - `mplads_mp_summary_2026-09-10.csv` (104 KB)
- [x] Project context verified from HackMD: https://hackmd.io/@zP3T-TSAR2iE-AjU52TZUw/r1MWU-qwfl

---

## 🔲 Not Started

### Step 1 — Project Scaffolding
- [ ] Initialize Python backend (FastAPI + folder structure)
- [ ] Initialize React + TypeScript frontend
- [ ] Set up `docker-compose.yml` (PostgreSQL + Redis)
- [ ] Create `.env.example`
- [ ] Set up `requirements.txt` and `package.json`

### Step 2 — Data Ingestion Layer
- [ ] Load and clean `mplads_mp_summary` CSV
- [ ] Load and clean `mplads_recommended_works` CSV
- [ ] Load and clean `mplads_completed_works` CSV
- [ ] Load and clean `mplads_expenditures` CSV
- [ ] Build EDA notebook (`notebooks/01_eda.ipynb`)
- [ ] Store processed data in PostgreSQL

### Step 3 — Feature Engineering
- [ ] Financial features: `cost_deviation`, `expenditure_ratio`, `admin_ratio`, `sc_st_compliance`, `unspent_ratio`
- [ ] Temporal features: `sanction_to_payment_days`, `expenditure_velocity`
- [ ] Network features: `vendor_concentration` (Herfindahl index)

### Step 4 — ML Engine (5 Models)
- [ ] Engine 1: Isolation Forest (anomaly scoring)
- [ ] Engine 2: Autoencoder (reconstruction error)
- [ ] Engine 3: XGBoost (risk classifier with proxy labels)
- [ ] Engine 4: GNN (collusion/cartel detection)
- [ ] Engine 5: NLP Pipeline (work description similarity)

### Step 5 — Risk Scoring & Alert Engine
- [ ] Composite risk score (0-100) aggregating all engines
- [ ] Alert generation with human-readable explanations
- [ ] FastAPI endpoints for risk scores

### Step 6 — Dashboard (Frontend)
- [ ] Screen 1: National Overview Map (India choropleth by risk)
- [ ] Screen 2: Anomaly Feed (real-time flagged transactions)
- [ ] Screen 3: Network Graph Viewer (MP-Vendor-IA relationships)
- [ ] Screen 4: MP/District Deep Dive
- [ ] Screen 5: Compliance Tracker (SC/ST mandate, unspent funds)

### Step 7 — Testing & Deployment
- [ ] Unit tests for each ML engine
- [ ] API integration tests
- [ ] Deploy backend to Railway/Render
- [ ] Deploy frontend to Vercel
- [ ] Final demo video & README

---

## 📊 Dataset Stats (Verified)
| Metric | Value |
|---|---|
| Total MPs | 774 |
| Total Works Recommended | 131,141 |
| Works Completed | 44,028 (33.57%) |
| Pending Works | 87,113 |
| Total Allocated | ₹1,168 Crore |
| Actual Expenditure | ₹399 Crore (34.2%) |
| Avg Allocation per MP | ₹15.09 Crore |

---

## 🗒️ Notes
- Dataset source: dataful.in (14th–17th Lok Sabha data)
- No labeled fraud data — use unsupervised models first (Isolation Forest, Autoencoder)
- Proxy labels for XGBoost: works where cost > 3σ from category mean = "suspicious"
- GNN requires Neo4j — spin up via Docker
