# NEXORAS — MPLADS AI Watchdog Platform
**Team:** Syntropians | **Event:** Smart India Hackathon 2026
**PS ID:** 26102 | **Organization:** MoSPI (Ministry of Statistics & Programme Implementation)
**Category:** Software | **Theme:** Miscellaneous

---

## 🎯 What We Are Building
An **AI-powered monitoring and analytics platform for MPLADS** that:
- Detects **trends, anomalies, irregularities, and potential fraud** in fund utilization and project execution
- Analyzes data on **sanctions, expenditures, cost estimates, work progress, payments, and asset creation**
- Detects **unusual patterns, cost overruns, duplicate works, delayed projects**
- Generates **risk-based alerts, predictive insights, and decision-support dashboards**
- Serves: MPs, State Nodal Authorities, District Authorities, and the Ministry

---

## 📁 Key Files & Locations
| File/Folder | Path | Purpose |
|---|---|---|
| MPLADS Dataset (CSV) | `D:\sih 2026\mplads dataset\` | Real data to build ML models on |
| Dataset JSON metadata | `D:\sih 2026\mplads dataset\json_2026-09-10.json` | Stats summary (774 MPs, 131K works) |
| Project plan (HackMD) | https://hackmd.io/@zP3T-TSAR2iE-AjU52TZUw/r1MWU-qwfl | Full technical breakdown |
| Repo root | `D:\sih 2026\sample mvp\NEXORAS-sample-mvp\` | This project |

### Dataset Files
- `mplads_completed_works_2026-09-10.csv` — ~11.7MB
- `mplads_expenditures_2026-09-10.csv` — ~26.4MB
- `mplads_recommended_works_2026-09-10.csv` — ~23MB
- `mplads_mp_summary_2026-09-10.csv` — ~104KB

### Dataset Stats (Real Numbers)
- **774 MPs**, **131,141 total works** recommended
- **44,028 works completed** (33.57% completion rate)
- **₹1,168 Crore** total allocated, **₹399 Crore** actual expenditure
- **87,113 pending works**, **34.2% expenditure rate**

---

## 🏗️ System Architecture

### 5 ML Detection Engines
| Engine | Model | What It Detects |
|---|---|---|
| 1 | **Isolation Forest** | Statistical anomalies in expenditure, cost, timeline |
| 2 | **Autoencoder** | Unusual feature combinations (reconstruction error) |
| 3 | **XGBoost** | Supervised risk classification using proxy labels |
| 4 | **GNN (Graph Neural Network)** | Vendor cartels, MP-Vendor-IA collusion networks |
| 5 | **NLP Pipeline** | Work description similarity, copy-paste fraud, doc analysis |

### Data Flow
```
eSAKSHI / dataful.in CSV
        ↓
  Data Ingestion Layer (Pandas)
        ↓
  Feature Engineering
        ↓
  ML Engine (5 models in parallel)
        ↓
  Risk Scoring & Alert Engine (0-100 score)
        ↓
  Dashboard & Reporting (React + D3.js + MapboxGL)
```

---

## 🛠️ Mandatory Tech Stack

### Backend
| Layer | Tech |
|---|---|
| API Framework | FastAPI (Python) |
| ML Pipeline | scikit-learn, PyTorch, PyTorch Geometric |
| Graph Database | Neo4j (community edition) |
| Data Processing | Pandas, NumPy |
| NLP | spaCy, sentence-transformers |
| Task Queue | Celery + Redis |

### Frontend
| Layer | Tech |
|---|---|
| Framework | React + TypeScript |
| Charts | D3.js / Recharts |
| Maps | Mapbox GL JS / Leaflet |
| Graph Viz | Cytoscape.js / vis.js |
| UI Kit | shadcn/ui + Tailwind CSS |

### Infrastructure
| Layer | Tech |
|---|---|
| Database | PostgreSQL |
| Cache | Redis |
| Deployment | Railway / Render / Vercel |

---

## 📂 Project Folder Structure
```
NEXORAS-sample-mvp/
├── AGENTS.md              ← This file (agent instructions)
├── PROJECT_STATE.md       ← Current build progress
├── backend/
│   ├── api/               ← FastAPI routes
│   ├── ingestion/         ← Data loading & cleaning
│   ├── features/          ← Feature engineering
│   ├── engine/            ← 5 ML models
│   │   ├── isolation_forest.py
│   │   ├── autoencoder.py
│   │   ├── xgboost_classifier.py
│   │   ├── gnn.py
│   │   └── nlp_pipeline.py
│   ├── scoring/           ← Risk score aggregation
│   └── db/                ← DB models & connections
├── frontend/
│   ├── src/
│   │   ├── components/    ← UI components
│   │   ├── pages/         ← Dashboard screens
│   │   └── lib/           ← API client, utils
│   └── public/
├── data/                  ← Symlink or copies of dataset CSVs
├── notebooks/             ← EDA & model prototyping
├── tests/
└── docker-compose.yml
```

---

## ✅ Agent Coding Rules (Always Follow)
1. **Python** for all backend and ML code
2. **React + TypeScript** for frontend
3. **FastAPI** for all API endpoints — include docstrings on every route
4. **Every risk flag must have an explainable reason** — no black-box outputs
5. Use **mock/CSV data** for prototype — simulate eSAKSHI API
6. **Never hardcode** credentials — use `.env` files
7. Commit with prefixes: `feat:`, `fix:`, `data:`, `ml:`, `docs:`, `test:`
8. **Run tests** after implementing each module
9. Keep modules isolated by folder: `ingestion/`, `engine/`, `scoring/`, `api/`
10. See `PROJECT_STATE.md` before starting any task to avoid duplication

---

## 📌 Project State
See [PROJECT_STATE.md](./PROJECT_STATE.md) for current progress, completed tasks, and next steps.
