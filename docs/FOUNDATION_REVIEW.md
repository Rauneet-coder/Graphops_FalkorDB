# GraphOps foundation review

Date: October 14, 2026. Status: **buildable scaffold; investigation MVP incomplete**.
Reviewed baseline: `fc9739d50a025662ae208807e96781d12db6affd`.
`git rev-parse HEAD` and `git ls-remote origin HEAD refs/heads/main` both returned
that revision; the initial working tree was clean. Git is initialized and `origin`
points to the requested repository. No newer remote `main` was found in this pass.

## Scope and confirmed gaps

Read [AGENTS.md](../AGENTS.md), [TASKS.md](TASKS.md), architecture/schema/API/runbook
and foundation documents, backend main/settings/client/tests, Dockerfiles/Compose,
package/config/type/page files, ontology, fixture, migration, and query templates.
Preserve the corrected FalkorDB + FastAPI + Next.js scaffold. The event has not
opened; this pass changes documentation and guidance only. No runtime fixes,
upgrades, fixture/query/migration edits, container setup, or graph writes occurred.

| Priority | Observed implementation | Required evidence before completion |
| --- | --- | --- |
| Readiness | `/health` always reports healthy; synchronous ping; missing-interface success; swallowed import errors; no lifespan/timeouts | True graph query probe, init-aware 503, outage/recovery, lifecycle and bounded I/O |
| Configuration/builds | Malformed CORS accepted; latest DB tag; unbounded Python dependency versions; npm install/dev; bind mounts; graph sibling absent from image | Strict config, pinned tested versions, production images, explicit env and loopback bindings |
| Graph | 12 nodes, 14 edges; eight labels; no Pipeline/Redis/history; fixture/property IDs disagree; active incident has answer/fix | Reconciled identities/provenance, honest active scenario, earlier verified history, validated idempotent loader |
| Queries | Outgoing dependencies misnamed blast radius; mandatory author; missing path edges/env bounds; history lacks earlier-time requirement/rank | Live direction/time/environment/metadata/history/path tests |
| Product | Only `/` and `/health`; ontology page/static ready badge; no graph-backed routes, investigator, AI, or incident UI | Complete live graph-backed checkout investigation and honest failure states |
| Operations | Compose parses; graph engine unavailable; no loader/reset CLI/CI | Fresh isolated-volume startup, init, persistence/restart/reset, live CI |

The target relationship reconciliation is now explicit in
[GRAPH_SCHEMA.md](GRAPH_SCHEMA.md). Its semantics remain a target contract until
all implementation representations and live checks are updated together.

## Checks actually run in this pass

| Check | Exact result | What it proves |
| --- | --- | --- |
| `git status --short`; `git rev-parse HEAD` | Clean at start; baseline HEAD | Local revision and initial working-tree state |
| `git ls-remote origin HEAD refs/heads/main` | Both refs equal baseline | Remote revision rechecked; initial sandbox DNS failure was retried with approval |
| `PYTHONDONTWRITEBYTECODE=1 backend/.venv/bin/python -m pytest backend/tests -q -p no:cacheprovider` | Exit 0; **3 passed, 1 warning in 0.43s** | Existing scaffold tests pass using host virtualenv (Python 3.14), not clean-container verification |
| Failure reproduction through TestClient, with `ping=False` | `/health`: **HTTP 200**, `status=healthy`, `database.connected=false` | Misleading health reproduced; controlled stub, not live graph outage |
| `Settings(CORS_ORIGINS="[invalid")` | Accepted as `['[invalid']` | Malformed CORS reproduced |
| `ping()` with `get_client()` returning an object without connection interface | **True** | Success fallback defect reproduced |
| `docker compose config --quiet` | Exit 0 | Configuration parses only |
| `docker info --format '{{.ServerVersion}}'` | Exit 1; Docker socket absent at `/Users/rauneetsingh/.docker/run/docker.sock` | Engine unavailable; no container/live-query/persistence check possible |
| Parsed committed frontend lock and seed | Next **14.2.35**, **12 nodes / 14 edges** | Version and fixture counts, not execution correctness |
| `git diff --check` | Exit 0 | Documentation diff has no whitespace errors |
| Repository-relative Markdown link validation | **30 links checked across 11 files; all targets exist** | Local documentation navigation is consistent |
