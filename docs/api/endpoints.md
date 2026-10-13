# API Specification & Endpoints

Base URL: `http://localhost:8000/api/v1`

## Health & System
- `GET /health` — Service health and FalkorDB connectivity check.
- `GET /` — API root information.

## SRE Incidents & Investigation
- `GET /api/v1/incidents` — List active and historical incidents.
- `GET /api/v1/incidents/{incident_id}` — Get specific incident details and symptoms.
- `GET /api/v1/investigate/{incident_id}` — Execute multi-hop causal graph traversal to isolate suspect deployments, commits, and authors.
- `POST /api/v1/incidents/{incident_id}/resolve` — Record resolution and write back `:RESOLVED_BY` fix relationship to FalkorDB.

## Topology & Scenarios
- `GET /api/v1/topology` — Retrieve complete service dependency subgraph for Next.js visualization.
- `POST /api/v1/scenarios/{scenario_id}/trigger` — Inject canned outage scenario (Bad Config, Schema Drift, Recurring Deadlock).
