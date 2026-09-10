# NEXORAS API STATE

## Status
NOT STARTED

## Planned Endpoints (FastAPI)
| Endpoint | Method | Purpose | Status |
|---|---|---|---|
| /health | GET | Health check | NOT STARTED |
| /dashboard/summary | GET | Overview stats | NOT STARTED |
| /projects | GET | List all projects with risk scores | NOT STARTED |
| /projects/{id} | GET | Single project details + explanation | NOT STARTED |
| /anomalies | GET | List flagged anomalies | NOT STARTED |
| /vendors | GET | Vendor list with concentration stats | NOT STARTED |
| /vendors/{id} | GET | Vendor detail + network | NOT STARTED |
| /network | GET | Graph data for visualization | NOT STARTED |
| /analyze | POST | Trigger fresh analysis run | NOT STARTED |

## API Framework
FastAPI (Python) — not yet initialized

## API Location (Planned)
`backend/api/`

## Next Action
Build AFTER core AI modules (Isolation Forest, Autoencoder, NetworkX) are working independently.
