# Local setup and operations

Stage 1 infrastructure is live-verified. Domain initialization and investigation
are not implemented; do not load the legacy answer-revealing fixture as an honest
demo. See [the verification report](../FOUNDATION_REVIEW.md) for exact scope/results.

## Canonical Docker-only startup

Requires Docker Engine/Desktop and Docker Compose running. No host Python or Node:

```bash
cp .env.example .env
docker compose config --quiet
docker compose up --build
```

The three production services use image contents without source mounts or reload.
Open frontend `http://localhost:3000` and API docs `http://localhost:8000/docs`.
All published ports bind to `127.0.0.1`. Inspect `docker compose ps` and logs.

```bash
curl --fail http://localhost:8000/health/live
curl --fail http://localhost:8000/health/ready
docker compose exec falkordb redis-cli --raw GRAPH.RO_QUERY graphops 'RETURN 1' TIMEOUT 500
```

Liveness returns 200 while the process responds. Readiness and `/health` require
actual read-only Cypher and successful infrastructure initialization; otherwise
503. Infrastructure scope reports `demo_data_loaded: false`. Stage 2 must add
schema/seed validation before claiming a usable incident demo.

The backend starts after the graph process starts, retries bounded initialization,
then both graph/backend read-only healthchecks become healthy. Frontend starts
after backend health. A read-only graph probe needs an existing key, so backend
startup deliberately does not wait on graph health before initializing it. Starting
only `falkordb` may leave it unhealthy until the backend initializes the graph key.

Routine stop retains the volume:

```bash
docker compose down
```

## Settings and addresses

| Setting | Default / purpose |
| --- | --- |
| FALKORDB_HOST / PORT | `falkordb` / `6379` on Compose network |
| FALKORDB_GRAPH | `graphops`; validated application graph name |
| FALKORDB_CONNECT_TIMEOUT_SECONDS | `1`, maximum connect wait per attempt |
| FALKORDB_SOCKET_TIMEOUT_SECONDS | `2`, maximum socket wait |
| FALKORDB_QUERY_TIMEOUT_MS | `500`, shorter than socket timeout |
| GRAPH_WORKERS | `4`, graph worker and connection bound |
| GRAPH_INIT_RETRY_SECONDS | `1`, bounded initialization retry interval |
| ENVIRONMENT | `production`; also accepts development/test |
| CORS_ORIGINS | JSON list or comma-separated HTTP(S) origins, strict validation |
| FALKORDB_PUBLISHED_PORT | `6379`, loopback host port |
| BACKEND_PUBLISHED_PORT | `8000`, loopback host port |
| FRONTEND_PUBLISHED_PORT | `3000`, loopback host port |
| NEXT_PUBLIC_API_URL | Browser-reachable `http://localhost:8000`, passed at build time; reserved for domain UI |
| API_INTERNAL_URL | Server-only `http://backend:8000`, passed at runtime; reserved for domain UI |

Every setting in `.env.example` is explicitly forwarded or consumed by Compose.
The browser/internal API settings are reserved for Stage 6; there are no domain
API requests yet. Browser localhost must never become the Next server's container
API address. Rebuild to change public build-time values. Native backend development
must override FALKORDB_HOST to localhost. API_HOST/API_PORT were removed from the
example because they were not implemented settings; internal ports are fixed.
LLM settings are deferred to Stage 5. No credentials belong in NEXT_PUBLIC variables.

For occupied default ports, update the three published ports plus browser API URL
and CORS origins before rebuilding. The current session's dedicated demonstration
uses frontend 13000, backend 18000, and graph 16379 to avoid another application.

## Persistence and reset

The named volume mounts at `/var/lib/falkordb/data`; AOF is enabled with fsync every
second and RDB snapshots enabled. Verify effective settings, not just the YAML:

```bash
docker compose exec falkordb redis-cli --raw CONFIG GET dir appendonly appendfsync
```

The live verification script writes a unique non-fixture record in a separate
probe graph, then reads it after stop/start and after container replacement before
any initialization can recreate that probe graph. It also confirms the effective
directory/AOF settings. Fixture recreation would not prove persistence.

There is no supported demo reset command yet. Stage 2 will add the single loader
and explicit demo-only reset. Do not use volume deletion for routine startup or
reset. Never target an existing user volume for clean-start tests. On the tested
server, empty graph keys with no durable write may be absent after AOF replay;
the infrastructure lifecycle worker safely initializes the empty key again.

## Verification and development

```bash
scripts/verify-stage1.sh
```

This uses a unique Compose project/fresh volume, no published test ports, no host
source mounts, and only Docker plus ordinary shell utilities. The test override's
`!reset` syntax requires a compatible Compose implementation (tested: 5.1.4).
A plain-Redis negative control proves PING alone is insufficient. The script runs
backend unit/live checks and lint, production frontend checks, actual API readiness,
graph outages, cold-start recovery, read-only enforcement, and persistence. It
intentionally requires one live test to fail during an outage; that expected
pytest exit 1 is part of the successful script. Requested live mode never skips
an absent graph dependency. Test cleanup refuses demo IDs; generated test keys
are deleted safely. Unique verification volumes are retained and printed.

Unit-only checks against a running backend image:

```bash
docker compose exec backend python -m pytest tests/test_health.py -q -p no:cacheprovider
docker compose exec backend ruff check --no-cache app tests
```

Optional source mounts and reload:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

Frontend lint/type/build run inside its production Docker build using npm ci.
Current lint-tool EOL/advisory limitations and the TestClient deprecation warning
are recorded in the report. The standalone runner excludes lint dependencies.

## Troubleshooting

- Missing Docker socket: start Docker Engine/Desktop and inspect docker info.
- Readiness 503: inspect graph module/query capability and lifecycle initialization;
  a Redis PONG cannot establish graph readiness. Ordinary Redis is rejected.
- Graph stopped/replaced: readiness returns 503, liveness remains 200, and lifecycle
  retry plus connection recovery restore readiness after the graph returns.
- Published port in use: change host port settings and matching browser/CORS values;
  do not stop unrelated application containers.
- UI cannot call a future domain API: distinguish browser URL from Compose DNS and
  rebuild public API configuration when changed.
- Missing domain records: Stage 1 loads none. Do not invent incidents or RCA output.
- Ruff cannot write cache: use --no-cache with the non-root image.
- npm audit flags development tooling: consult the report; do not force downgrade
  to unsupported Next 14. Recheck scheduled Next advisories when published.

## Current session stack

The isolated three-service infrastructure is running as `graphops-stage1-demo`.
Frontend: http://localhost:13000; API/docs: http://localhost:18000/docs; graph:
127.0.0.1:16379. These alternate ports avoid another existing application.
Equivalent startup (preserves this project's volume on repeated runs):

```bash
FALKORDB_PUBLISHED_PORT=16379 \
BACKEND_PUBLISHED_PORT=18000 \
FRONTEND_PUBLISHED_PORT=13000 \
NEXT_PUBLIC_API_URL=http://localhost:18000 \
CORS_ORIGINS='["http://localhost:13000","http://127.0.0.1:13000"]' \
docker compose --project-name graphops-stage1-demo --env-file .env.example up --build -d --wait
```

Stop only this session's stack, preserving its volume:

```bash
docker compose --project-name graphops-stage1-demo down
```

No incident investigation is available yet. This is an infrastructure walkthrough:
open readiness, execute RETURN 1 through GRAPH.RO_QUERY, then run the verification
script for isolated outage/recovery and persistence checks. The incident/evidence/
historical-fix walkthrough remains Stage 2 onward.
