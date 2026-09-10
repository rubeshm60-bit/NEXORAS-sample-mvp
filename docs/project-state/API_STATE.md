# NEXORAS API STATE

## Status
COMPLETE

## Planned Endpoints (FastAPI)
| Endpoint | Method | Purpose | Status |
|---|---|---|---|
| /health | GET | Health check | COMPLETE |
| /dashboard/summary | GET | Overview stats | COMPLETE |
| /projects | GET | List all projects with risk scores | COMPLETE |
| /projects/{id} | GET | Single project details + explanation | COMPLETE |
| /anomalies | GET | List flagged anomalies | COMPLETE |
| /vendors | GET | Vendor list with concentration stats | COMPLETE |
| /vendors/{id} | GET | Vendor detail + network | COMPLETE |
| /network | GET | Graph data for visualization | COMPLETE |
| /analyze | POST | Trigger fresh analysis run | COMPLETE |

## API Framework
FastAPI (Python) — not yet initialized

## API Location (Planned)
`backend/api/`

## Next Action
Build AFTER core AI modules (Isolation Forest, Autoencoder, NetworkX) are working independently.

