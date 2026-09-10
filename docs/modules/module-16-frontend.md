# Module 16: React Frontend

## Objective
Provide an intuitive, responsive, and auditor-friendly web interface that surfaces the AI's complex findings, risk scores, and evidence via clear dashboards and interactive network graphs.

## Overview
This module acts as the presentational layer for the NEXORAS MVP. It is built using **React (Vite)** and standardizes routing via `react-router-dom`. It directly consumes the FastAPI endpoints established in Module 15. The UI favors dense data-tables and clean metric cards, enabling auditors to quickly scan for high-risk projects and drill down into the evidence.

## Key Views
1. **Executive Dashboard (`Dashboard.jsx`)**: 
   - High-level KPI aggregates (Total Funds, Project Counts).
   - Instant stratification of risk (Critical/High vs Medium vs Low).
2. **Project Explorer (`ProjectExplorer.jsx`)**:
   - A tabular ledger of all MPLADS works.
   - Distinct visual tagging for risk tiers.
   - Can be toggled to filter strictly for Anomalies.
3. **Investigation View (`ProjectInvestigation.jsx`)**:
   - Deep-dive into a single project.
   - Displays the 5-pillar mathematical breakdown of the unified risk score.
   - Renders the human-readable "Why Flagged" report (from Module 13) inside a stark Audit Evidence block.
4. **Vendor Intelligence (`VendorIntelligence.jsx`)**:
   - Surfaces contractor data, highlighting concentration risks (multi-MP syndicates).
5. **Network Topology (`NetworkVisualization.jsx`)**:
   - Employs **Cytoscape.js** (`react-cytoscapejs`) to map the bipartite relationships between MPs and Contractors, visually exposing structural cartels.

## Status
- **Status**: COMPLETE
- **Code**: `frontend/src/*` (React + Vite)
- **Tests**: Manual validation complete. Standard `vite build` executes with zero structural errors.
