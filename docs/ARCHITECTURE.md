# GraphOps architecture

Reviewed October 14, 2026 against `fc9739d50a025662ae208807e96781d12db6affd`.
Stage 1 infrastructure is now live-verified. Domain investigation sections below
remain the target architecture; see [the review](FOUNDATION_REVIEW.md) for exact
implemented scope and checks. Acceptance follows
[TASKS.md](TASKS.md), in order.

## Stack and responsibilities

Keep three local services: FalkorDB, FastAPI, and Next.js App Router. FalkorDB is
the only domain datastore. No queue, vector store, agent framework, or external
ingestion service is needed for the MVP. Docker Compose is the canonical runtime;
optional LLM credentials remain server-side.

```mermaid
flowchart LR
    Browser[Browser] --> UI[Next.js incident UI]
    UI --> API[FastAPI thin routes]
    API --> Investigation[Investigation service]
    Investigation --> Repository[Typed graph repository]
    Repository -->|Read-only bounded Cypher over Redis protocol| Graph[(FalkorDB)]
    Init[Validated idempotent initializer] -->|Explicit writes| Graph
    Investigation --> Agent[Optional bounded LLM tool loop]
    Agent --> Repository
```

Routes validate requests, invoke services, and return Pydantic models. Put driver
lifecycle/configuration in `backend/app/core/`, query execution and conversion in
`backend/app/graph/`, orchestration in `services/`, and tools/prompts/LLM integration
in `agent/`. Reusable Cypher has one authoritative copy in `graph/queries/`.
Tests live in `backend/tests/`. Avoid runtime import-path mutation.

## Infrastructure and readiness

Manage the official Python client through FastAPI lifespan and close its pool at
shutdown. Use the supported async interface or a bounded threadpool for blocking
graph/LLM I/O; a coroutine containing synchronous calls is not sufficient.
Bound connection, socket, query, request, and tool-loop timeouts and concurrency.
Missing required packages fail startup clearly. Invalid CORS configuration fails
validation rather than becoming an arbitrary allowed-origin string.

Liveness (`GET /health/live`) indicates that the process responds. Readiness
(`GET /health/ready`, with `/health` as its compatibility alias) requires actual
read-only Cypher capability and successful required initialization. Stage 1
initializes only an empty graph and explicitly reports `scope: infrastructure`,
`demo_data_loaded: false`. Stage 2 must add schema/seed validation before reporting
demo readiness.
Return 503 before initialization or during graph failure, and recover after graph
capability returns. Ordinary Redis `PING` is not graph readiness. Investigation
graph failures return a dependency error; no fabricated success is permitted.

Pin and record compatible server/client versions only after live verification.
Stage 1 uses a root backend build context to include `backend/` and `graph/` assets. Build
the frontend with `npm ci` and its committed lockfile, then run a production
server. Lock Python dependencies, exclude local artifacts/secrets with appropriate
`.dockerignore` files, and use supported Node/Next/React/ESLint/types together.
Bind published demo ports to `127.0.0.1`. Canonical Compose uses image contents,
not host source mounts; reload and bind mounts belong in an optional dev override.

Forward documented settings explicitly in Compose. Browser requests use a
browser-reachable URL such as `http://localhost:8000`; server-side Next.js requests
use `http://backend:8000` on the Compose network. Public build-time configuration
must be passed at build time when required. Never expose keys through
`NEXT_PUBLIC_*`. Add backend/frontend healthchecks and dependency ordering.

The Stage 2 initializer will validate fixtures before writes, create supported
indexes, seed idempotently, and verify identity/schema invariants before demo
readiness. Stage 1 lifecycle initialization performs only `RETURN 1`, then a
read-only probe. Its worker retries after failed probes, including empty-graph
keys absent after AOF replay; no domain records or extra labels are created. Configure
FalkorDB persistence explicitly, inspect its effective configuration, and prove
restart survival with an extra record distinct from fixture records. A volume or
recreated seed alone does not establish persistence. Routine startup never erases
the graph; an explicit reset is constrained to the designated demo graph.

## Why FalkorDB is essential

The target model in [GRAPH_SCHEMA.md](GRAPH_SCHEMA.md) permits this evidence path:

```text
Incident --AFFECTED--> checkout --DEPENDS_ON--> payment --DEPENDS_ON--> Redis
payment --DEPLOYED_BY--> deployment --TRIGGERED_BY--> pipeline run
pipeline run --TRIGGERED_BY--> commit --BELONGS_TO--> repository
commit --AUTHORED_BY--> developer
earlier Incident --AFFECTED--> payment
earlier Incident --CAUSED_BY--> verified RootCause --RESOLVED_BY--> proven Fix
```

Cypher must retrieve dependency paths, filter changes by environment/time, and
