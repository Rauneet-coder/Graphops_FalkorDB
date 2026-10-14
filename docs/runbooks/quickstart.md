# Local setup and operations

**Current status — October 14, 2026:** scaffold startup only. The canonical
Docker-only investigation workflow is a Stage 1–8 acceptance target, not yet
verified. Docker engine is currently unavailable. See
[the exact review scope](../FOUNDATION_REVIEW.md).

## Current scaffold command

Requires Docker Engine/Desktop running and Docker Compose:

```bash
cp .env.example .env
docker compose config --quiet
docker compose up --build
```

Check `docker compose ps`; open `http://localhost:3000` and
`http://localhost:8000/docs`. `/health` is currently misleading: HTTP 200 does not
prove graph connectivity. The UI's ready badge is static. There is no seed loader
or investigation API. Existing Compose uses dev bind mounts/reload and publishes
ports beyond loopback. It must be corrected before calling this a reliable demo.

Routine stop preserves the volume:

```bash
docker compose down
```

Do not delete existing user volumes to test startup or reset the demo.

## Docker-only target (not available yet)

During implementation, update this section with exact verified image versions,
startup/initialization commands, readiness probes, and reset/test commands.
Canonical launch remains `docker compose up --build`, using image-packaged graph
assets, production runners, explicit settings, idempotent initialization, loopback
ports, and no host Python/Node/source mounts. A separate optional development
configuration may provide mounts and reload.

Readiness will be `GET /health/ready` (and `/health` alias), returning 503 before
required init or while graph queries fail. `GET /health/live` checks the process.
A Redis PONG alone never proves FalkorDB graph capability.

## Settings and API addresses

The current `.env.example` lists FALKORDB_HOST/PORT/GRAPH, API_HOST/PORT,
ENVIRONMENT, CORS_ORIGINS, and NEXT_PUBLIC_API_URL. Not all are implemented or
forwarded by Compose: API_HOST/PORT are not consumed by current Python settings,
Compose hardcodes graph/environment and omits CORS. Copying the example does not
currently configure every container setting.

Stage 1 must document and forward all supported settings with validated ranges,
connection/socket/query timeouts, initialization options, and explicit persistence
settings. Stage 5 adds optional LLM endpoint/model/server-side key plus bounded
timeouts/call limits. Missing optional LLM settings must not block the deterministic
graph demo. No credentials belong in public frontend environment variables.

Browser-facing API URL: `http://localhost:8000`. Container-side Next.js server API
URL: `http://backend:8000`. Container FalkorDB host: `falkordb`; host-side access:
`localhost:6379`. `NEXT_PUBLIC_*` values may be embedded at build time: wire build
arguments as required. CORS must allow the actual browser origin and reject
malformed values. The committed example must match implemented settings as stages
land, including removal of unused variables.

## Persistence, initialization, and reset target

Use a separate named Compose project and fresh volumes for acceptance testing.
Never operate on the user's existing demo volume during clean-start verification.
Confirm the effective persistence configuration, create an extra non-fixture probe
record, restart, and retrieve that same record. Repeated seed counts alone cannot
prove persistence because startup could recreate fixtures. Test fixture idempotency
separately and ensure initialization preserves unrelated records.

The proposed single seed/reset CLI is `graph/seed.py` calling the backend loader;
**it does not exist yet**. Reset must explicitly require the designated demo graph,
refuse other graphs, and never delete other graphs or volumes. No verified reset
command can be supplied at this revision. Publish the exact container CLI command
only after its restrictions and behavior pass live tests.

## Tests currently available

For an already prepared host environment (not canonical Docker verification):

```bash
PYTHONDONTWRITEBYTECODE=1 backend/.venv/bin/python -m pytest backend/tests -q -p no:cacheprovider
npm --prefix frontend run lint
npm --prefix frontend run build
docker compose config --quiet
```

The virtualenv is local and not included in a clone. The current lint script uses
`next lint`; it must migrate to ESLint CLI when upgrading to Next 16. Stage 7 must
provide container/CI commands for unit tests, explicitly required live graph tests,
type checking, and build. Live tests must fail clearly when their DB is missing
and use isolated test graphs whose cleanup rejects the demo graph.

## Troubleshooting

- Absent Docker socket/engine: start Docker Engine/Desktop, then inspect `docker info`
  before attempting container validation. This review could not run containers.
- Redis responds but readiness fails: inspect graph module/query capability and
  schema/seed initialization; do not substitute PING for graph verification.
- UI cannot reach backend: distinguish browser address from Compose DNS and inspect
  browser-origin CORS and build-time API settings.
- Missing graph assets: verify backend image build context includes graph/; a host
  bind mount does not establish that a fresh image contains them.
- No historical match/missing provenance: report absent evidence rather than
  guessing relationships or confirmed causes.
- Optional LLM failure: deterministic mode must explain the same successfully
  retrieved graph evidence and show a fallback reason; graph failure returns 503.
