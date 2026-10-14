# GraphOps implementation plan

Status: **Stage 1 infrastructure completed and live-verified.** Stage 2 has
not started. The latest user instruction authorizes Stage 1 infrastructure now
and requires stopping after Stage 1. The initial October 14 review found local
HEAD and remote `main` both at `fc9739d50a025662ae208807e96781d12db6affd`.
Stage 1 advances that scaffold; this is the reviewed baseline, not current HEAD. Stage 1 is an explicitly authorized infrastructure exception to the original
pre-event restriction; main domain graph implementation remains event work.

## Timing, scope, and schedule

The [official rules](https://www.wemakedevs.org/hackathons/falkordb) specify
October 15, 2026, 00:01 IST through October 18, 23:59 IST: UTC opening October 14,
18:31; UTC deadline October 18, 18:29. Main FalkorDB implementation and submission
must be new event work. Preserve the baseline and record event work separately.
Before opening, research/review/planning/documentation and the subsequently
authorized Stage 1 reusable infrastructure are in scope. Do not start Stage 2
without the next user instruction, and preserve the event boundary for domain work.

| IST window | Intended work, subject to preceding acceptance |
| --- | --- |
| October 14, before opening | Review/docs and explicitly authorized Stage 1 infrastructure only |
| October 15, from 00:01 | Stage 2 after user instruction: consistent model, honest primary seed, live query tests |
| October 16 | Stages 3–4: graph-backed APIs and deterministic investigation |
| October 17 | Stages 5–6: grounded optional AI and incident UI with exact evidence paths |
| October 18, before 23:59 | Stages 7–9: finish validation/CI, isolated clean Docker proof, docs, video, panel verification and submission preparation |

This is a documented execution schedule, not a background job. At the next active
session during the event, recheck the clock, remote revision, working tree, and
completed checks, then proceed only within the latest authorized stage. Do
not skip failed acceptance checks to meet dates. Aim to finish video/panel work
before the deadline, allowing upload time. Claim Track 01 only; do not claim MCP
tool selection unless implemented and demonstrated. Extra scenarios and external
integrations are deferred until the primary investigation works.

## Repository assessment

| Area | Actual baseline | Required change |
| --- | --- | --- |
| Infrastructure | Three-service Compose; latest DB image; all-interface ports; dev bind mounts/runners; graph assets excluded from backend build context | Pinned builds, loopback bindings, settings, healthchecks, image-contained assets, idempotent init, proven persistence |
| Backend | Only `/` and `/health`; health reports healthy even if DB is false; synchronous ping inside async route | Truthful liveness/readiness, lifespan, bounded I/O, graph-backed typed APIs |
| Graph | Eight labels, 12 nodes/14 edges, no loader/Pipeline/Redis/resolved history; active incident contains its cause/fix | Target model, stable identity, honest scenario, migration and live query validation |
| Queries | Upstream traversal named blast radius; mandatory author; no returned edge sequences; weak history filtering | Separate directions, bounded environment/time, optional enrichment, actual paths, ranked earlier matches |
| Frontend | Static ontology/ready badge; locked Next 14.2.35; no incident API/UI | Supported patched versions, real readiness, complete investigation and evidence rendering |
| Tests | Three scaffold backend tests pass; Compose parses; no live graph tests | Meaningful graph/API/AI/failure/clean-volume tests and CI |
| Docs | Previously asserted completed foundation, automatic rollback, wipe-on-startup, machine-local links | Accurate current/target separation and dated validation scope |

Git is initialized; `origin` is configured. Existing local dependencies/build
artifacts do not prove clean startup. Docker Desktop was started for Stage 1. The original pre-Stage 1 review could
not run live checks; current validation is recorded separately. See [FOUNDATION_REVIEW.md](FOUNDATION_REVIEW.md)
for exact checks and limits.

## Recommended final structure


Retain the current layout; add files when their stage begins. This is the target
structure, with ordinary framework configs and package initializers omitted.

```text
Graphops/
├── frontend/
│   ├── src/
│   │   ├── app/                    # Dashboard and investigation UI
│   │   ├── components/             # Evidence and graph views
│   │   ├── services/api.ts         # Typed backend requests
│   │   └── types/                  # API and graph contracts
│   ├── package.json
│   ├── package-lock.json
│   └── Dockerfile
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/                   # Settings and FalkorDB lifecycle
│   │   ├── api/v1/                 # Thin API routes
│   │   ├── models/                 # Pydantic response/evidence contracts
│   │   ├── graph/
│   │   │   ├── repository.py       # Cypher execution and result mapping
│   │   │   └── loader.py           # Schema and seed loading
│   │   ├── services/investigation.py
│   │   └── agent/                  # Typed tools, prompts, LLM client
│   ├── tests/                      # Unit, live graph, API integration
│   ├── requirements.txt
│   ├── pyproject.toml
│   └── Dockerfile
├── graph/
│   ├── seed.py                     # CLI invoking backend loader
│   ├── migrations/001_initial_schema.cypher
│   ├── schema/ontology.json
│   ├── seeds/sample_graph.json
│   └── queries/                    # Traversal, history, validation Cypher
├── docs/
│   ├── ARCHITECTURE.md
│   ├── GRAPH_SCHEMA.md
│   ├── TASKS.md
│   └── DEMO.md
├── docker-compose.yml
├── .env.example
├── .gitignore
├── pyproject.toml
├── AGENTS.md
└── README.md
```

Small deviations from the proposal: reuse the existing schema migration instead
of duplicating it as `graph/schema.cypher`; retain `backend/tests/` instead of
adding root `tests/`. Keep ingestion to the seed loader. `graph/pipelines/` is
reserved documentation, not an ETL framework or the `Pipeline` graph node.
Existing supplementary docs can remain but should link to canonical docs.

## Ordered stages

Keep the existing nine-stage structure. The requested six execution priorities
map to Stage 1, Stage 2, Stages 3–4, Stage 5, Stage 6, then Stages 7–9. Move
reproducible Docker design into Stage 1; Stage 8 proves the complete integration.
Add relevant tests as each stage lands. Record commands, timestamps, versions,
results, and remaining blockers beneath each stage before checking it off.

### Stage 1 — Infrastructure and truthful readiness

- [x] Separate `/health/live` and `/health/ready`; make `/health` a readiness alias.
  Liveness responds when graph is down; readiness is 503 until graph-query
  capability and required initialization are available.
- [x] Probe actual read-only Cypher, not Redis PING. Remove missing-interface success
  fallback and missing-package masking. Use lifespan-managed client/pool with
  shutdown cleanup and bounded connection/socket/query timeouts.
- [x] Keep blocking database/LLM I/O off the async event loop through supported async
  APIs or bounded workers; remove application runtime `sys.path` mutation.
- [x] Reject malformed JSON/list/origin CORS input. Validate configuration and fail
  clearly for unavailable required packages.
- [x] Bind all published demo ports to `127.0.0.1`; select and record a server/client
  version only after live testing. Lock Python dependencies; use `npm ci`.
- [x] Upgrade unsupported locked Next 14.2.35 to a supported patched release after
  checking current official advisories. Align React/React DOM, ESLint/config,
  TypeScript/types, and a supported Node LTS. For Next 16 use ESLint CLI. Record
  exact versions and lint/type/build results, not a floating version claim.
- [x] Add `.dockerignore` files covering virtualenvs, node_modules, .next, caches,
  Git metadata, secrets. Use a root backend build context to package graph assets.
- [x] Canonical Compose uses production image contents without host source mounts,
  host Python/Node, or reload. Put dev mounts/reload in an optional override.
- [x] Wire every documented setting explicitly; distinguish browser API address
  from `http://backend:8000` for server-side container requests and handle build-time
  public settings. Add backend/frontend healthchecks and startup ordering.
- [x] Configure persistence and inspect effective settings. Verify a non-fixture
  probe record survives restart on a fresh isolated Compose project/volume.
- [x] Unit checks cover graph failure/recovery, ordinary Redis without graph engine,
  readiness before initialization, missing interface/package, CORS and cleanup.
- [x] Acceptance: live graph probe succeeds on the pinned image; outage/recovery
  and persistence work; builds/checks pass. Stage 1 readiness is explicitly scoped
  to infrastructure (`demo_data_loaded: false`). Stage 2 must add schema/seed
  validation before any claim of demo readiness. This scope adjustment keeps
  Stage 1 operational without prematurely implementing/loading domain data.

Research on October 14 found Next 14 unsupported and an official security release
announcement for today. Recheck published patched versions at implementation time:
[support policy](https://nextjs.org/support-policy),
[Next 16 upgrade guide](https://nextjs.org/docs/app/guides/upgrading/version-16),
[October security notice](https://nextjs.org/blog/upcoming-nextjs-security-update-october-2026).
Stage 1 pins Next 16.4.0 / React 19.3.0 and migrates to ESLint CLI. Exact image
digests, compatibility limits, audit results, and checks are in FOUNDATION_REVIEW.md.
Next's current plugins do not support ESLint 10 peers: ESLint 9.39.5 is retained
