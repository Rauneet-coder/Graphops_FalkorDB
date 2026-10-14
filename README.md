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
