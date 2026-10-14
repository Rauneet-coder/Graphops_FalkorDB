# GraphOps

An SRE incident investigation agent using FalkorDB, FastAPI, Next.js App Router,
and Docker Compose. Target: Track 01, Agents That Act on Connected Data.

**Status — October 14, 2026:** buildable scaffold, incomplete investigation
product. Local HEAD and remote `main` were checked and both match
`fc9739d50a025662ae208807e96781d12db6affd`. Before the event opens, changes are
limited to review, research, planning, and documentation.

The [official rules](https://www.wemakedevs.org/hackathons/falkordb) place the event
between October 15, 00:01 IST and October 18, 23:59 IST. General infrastructure
may be reused; the submission and main FalkorDB implementation must be new event
work. A local demo needs complete setup instructions and a working video if it
cannot be deployed.

## Implemented versus planned

| Implemented scaffold | Still required |
| --- | --- |
| FastAPI `/` and `/health`, settings, basic client wrapper | Truthful readiness, lifespan, bounded I/O, graph-backed domain APIs |
| Eight-label ontology metadata, fixture, migration, query templates | Nine-label reconciled model, honest seed loader, live query validation |
| Static Next.js ontology page | Incident dashboard, investigation, evidence and directed paths |
| Three-service Compose and Dockerfiles | Locked builds, graph assets, initialization, persistence verification |
| Three basic backend tests | Live graph, API, failure, grounded AI, browser and clean-volume checks |

`/health` currently returns HTTP 200 and `healthy` even with `connected: false`.
The UI's engine-ready badge is static. Neither proves graph readiness. No
investigation API, seed CLI, AI agent, or reset command currently exists.

## Local scaffold startup

Requires Docker with its engine running and Docker Compose. The canonical target
command is:

```bash
cp .env.example .env
docker compose up --build
```

The current Compose file uses source bind mounts and development runners; it does
not initialize the graph. Fresh-clone completion is unverified. Current addresses
are [frontend](http://localhost:3000), [API docs](http://localhost:8000/docs), and
FalkorDB at `localhost:6379`. Published ports currently listen beyond loopback;
Stage 1 must correct their bindings. Routine shutdown uses `docker compose down`
without deleting volumes. An explicit graph-only reset will be implemented and
verified during the event; there is no supported reset command yet.

## Intended investigation

A user selects checkout incident `INC-4091`. FalkorDB follows checkout → payment
→ Redis, retrieves bounded recent deployments and their pipeline/commit provenance,
and compares an earlier resolved incident and proven fix. The result cites actual
paths, compares plausible candidates, preserves uncertainty, and recommends an
operator action. Optional LLM synthesis must use the same retrieved evidence;
deterministic mode remains usable without credentials. No remediation executes
automatically. This flow is planned, not working at this revision.

## Validation and documentation

This review reran the existing backend suite: **3 passed, 1 deprecation warning**.
Compose configuration validation passed. Docker engine inspection failed because
its socket was absent; containers, Cypher, initialization, and persistence remain
unverified. Earlier frontend lint/build results are recorded as prior review
evidence, not fresh results from this pass.

- [Project instructions](AGENTS.md)
- [Ordered tasks and event schedule](docs/TASKS.md)
- [Architecture and evidence contract](docs/ARCHITECTURE.md)
- [Authoritative target graph model and legacy mapping](docs/GRAPH_SCHEMA.md)
- [Current assessment and exact validation scope](docs/FOUNDATION_REVIEW.md)
- [Implemented and planned API routes](docs/api/endpoints.md)
- [Setup, persistence, reset, and troubleshooting plan](docs/runbooks/quickstart.md)
- [Demo and submission checklist](docs/DEMO.md)
