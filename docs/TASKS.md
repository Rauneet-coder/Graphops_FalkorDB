# GraphOps implementation plan

Status: pre-event review/documentation complete; **no implementation stage has
passed acceptance**. Reviewed October 14, 2026 against local HEAD and remote
`main`, both `fc9739d50a025662ae208807e96781d12db6affd`. Existing work is reusable
scaffolding. The user's completion request authorizes implementation during the
event; the pre-event restriction remains in force until the opening time.

## Timing, scope, and schedule

The [official rules](https://www.wemakedevs.org/hackathons/falkordb) specify
October 15, 2026, 00:01 IST through October 18, 23:59 IST: UTC opening October 14,
18:31; UTC deadline October 18, 18:29. Main FalkorDB implementation and submission
must be new event work. Preserve the baseline and record event work separately.
Before opening, only research, review, planning, and documentation are authorized.

| IST window | Intended work, subject to preceding acceptance |
| --- | --- |
| October 14, before opening | Review current revision/rules, update guidance, evidence contracts, tasks, demo plan |
| October 15, from 00:01 | Stages 1–2: reliable infrastructure/readiness, consistent model, honest primary seed, live query tests |
| October 16 | Stages 3–4: graph-backed APIs and deterministic investigation |
| October 17 | Stages 5–6: grounded optional AI and incident UI with exact evidence paths |
| October 18, before 23:59 | Stages 7–9: finish validation/CI, isolated clean Docker proof, docs, video, panel verification and submission preparation |

This is a documented execution schedule, not a background job. At the next active
session during the event, recheck the clock, remote revision, working tree, and
completed checks, then proceed without repeating a planning-only response. Do
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
artifacts do not prove clean startup. Docker's engine is unavailable in this
review, preventing live verification. See [FOUNDATION_REVIEW.md](FOUNDATION_REVIEW.md)
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

- [ ] Separate `/health/live` and `/health/ready`; make `/health` a readiness alias.
  Liveness responds when graph is down; readiness is 503 until graph-query
  capability and required initialization are available.
- [ ] Probe actual read-only Cypher, not Redis PING. Remove missing-interface success
  fallback and missing-package masking. Use lifespan-managed client/pool with
  shutdown cleanup and bounded connection/socket/query timeouts.
- [ ] Keep blocking database/LLM I/O off the async event loop through supported async
  APIs or bounded workers; remove application runtime `sys.path` mutation.
- [ ] Reject malformed JSON/list/origin CORS input. Validate configuration and fail
  clearly for unavailable required packages.
- [ ] Bind all published demo ports to `127.0.0.1`; select and record a server/client
  version only after live testing. Lock Python dependencies; use `npm ci`.
- [ ] Upgrade unsupported locked Next 14.2.35 to a supported patched release after
  checking current official advisories. Align React/React DOM, ESLint/config,
  TypeScript/types, and a supported Node LTS. For Next 16 use ESLint CLI. Record
  exact versions and lint/type/build results, not a floating version claim.
- [ ] Add `.dockerignore` files covering virtualenvs, node_modules, .next, caches,
  Git metadata, secrets. Use a root backend build context to package graph assets.
- [ ] Canonical Compose uses production image contents without host source mounts,
  host Python/Node, or reload. Put dev mounts/reload in an optional override.
- [ ] Wire every documented setting explicitly; distinguish browser API address
  from `http://backend:8000` for server-side container requests and handle build-time
  public settings. Add backend/frontend healthchecks and startup ordering.
- [ ] Configure persistence and inspect effective settings. Verify a non-fixture
  probe record survives restart on a fresh isolated Compose project/volume.
- [ ] Unit checks cover graph failure/recovery, ordinary Redis without graph engine,
  readiness before initialization, missing interface/package, CORS and cleanup.
- [ ] Acceptance: live graph probe succeeds on the pinned image; outage/recovery
  and persistence work; builds/checks pass. Final demo readiness remains 503 until
  Stage 2's validated initializer exists. Do not fake initialization to pass.

Research on October 14 found Next 14 unsupported and an official security release
announcement for today. Recheck published patched versions at implementation time:
[support policy](https://nextjs.org/support-policy),
