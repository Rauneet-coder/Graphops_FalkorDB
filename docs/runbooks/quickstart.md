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
