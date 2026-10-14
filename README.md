# GraphOps

An SRE incident investigation agent using FalkorDB, FastAPI, Next.js App Router,
and Docker Compose. Target: Track 01, Agents That Act on Connected Data.

**Stage 1 infrastructure is implemented and live-verified.**
Incident investigation is not implemented. Stage 2 has not started. The pre-event
scaffold was `fc9739d50a025662ae208807e96781d12db6affd`; the user subsequently
authorized Stage 1 reusable infrastructure only before the event.

## Startup

Requires Docker Engine/Desktop running and Docker Compose. No host Python or Node
is needed for the canonical stack:

```bash
cp .env.example .env
docker compose up --build
```

Open [frontend](http://localhost:3000), [API docs](http://localhost:8000/docs), and
[readiness](http://localhost:8000/health/ready). All published ports bind to
`127.0.0.1`. If ports are occupied, set FALKORDB_PUBLISHED_PORT,
BACKEND_PUBLISHED_PORT, FRONTEND_PUBLISHED_PORT, and matching browser API/CORS
addresses in `.env`, then rebuild the frontend.

`GET /health/live` checks the process. `/health/ready` and `/health` require a
successful read-only FalkorDB query and completed infrastructure initialization;
they return 503 before initialization or during graph failures. Initialization
creates only an empty graph, with no domain schema/seed. The response explicitly
reports `scope: infrastructure` and `demo_data_loaded: false`. This is not a claim
that the incident demo is ready. Stage 2 must extend initialization/readiness to
require its validated schema and seed.

Persistence uses the named volume at the effective server directory
`/var/lib/falkordb/data`, AOF enabled, fsync every second, and RDB snapshots. Stop
without deleting the volume:

```bash
docker compose down
```

There is no supported demo reset command yet. Stage 2 must implement an explicit
graph-only reset restricted to the designated demo graph. Never erase existing
user volumes for startup or tests.

## Checks

```bash
scripts/verify-stage1.sh
