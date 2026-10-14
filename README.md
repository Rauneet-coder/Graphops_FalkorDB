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
```

This Docker-only command uses a unique Compose project, fresh volume, no published
test ports, and an ordinary Redis negative control. It builds production images,
runs unit/live tests and lint, checks readiness/outage/startup recovery, and checks
that a non-fixture record survives stop/start and container replacement. Test
containers are removed; the unique test volume is retained and printed. Explicit
live tests fail if their required database is unavailable. See the
[verification report](docs/FOUNDATION_REVIEW.md) for actual results and limitations.

Pinned: FalkorDB **6.0.2**, Python **3.13** and Node **24** images by immutable
multi-platform digest; Next **16.4.0**, React **19.3.0**, exact Python dependencies,
and committed npm lockfile. Frontend lint uses the ESLint CLI. Current Next lint
plugins require ESLint 9; **9.39.5 is end-of-life**. Its development dependency
chain also has an unpatched braces advisory. Production npm audit reported zero
advisories; this is not a guarantee against future advisories. Recheck the
announced October 14 Next security update when published. Details and sources
are in the report.

## Remaining product work

The graph fixture/query templates still use the legacy model and are not loaded.
Stage 2 must make checkout → payment → Redis discoverable through real paths,
with provenance, earlier verified history, an unrelated change, and a competing
candidate. It must remove the active incident's confirmed answer and applied fix.
No graph-backed incident API, investigator, optional AI, or incident UI exists yet.

- [Project instructions](AGENTS.md)
- [Ordered tasks and acceptance checks](docs/TASKS.md)
- [Architecture and evidence contract](docs/ARCHITECTURE.md)
- [Target graph model and legacy mapping](docs/GRAPH_SCHEMA.md)
- [Implementation and validation report](docs/FOUNDATION_REVIEW.md)
- [API availability](docs/api/endpoints.md)
- [Setup, settings, operations and troubleshooting](docs/runbooks/quickstart.md)
- [Planned demo and submission checklist](docs/DEMO.md)

The [event rules](https://www.wemakedevs.org/hackathons/falkordb) specify October
15, 2026, 00:01 IST through October 18, 23:59 IST. Main FalkorDB domain implementation
and submission must be event work. Stop after Stage 1 under the latest user scope.
