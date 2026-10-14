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
[Next 16 upgrade guide](https://nextjs.org/docs/app/guides/upgrading/version-16),
[October security notice](https://nextjs.org/blog/upcoming-nextjs-security-update-october-2026).
No upgrade or version compatibility test has been performed in this docs pass.

### Stage 2 — Graph model, honest seed, and live query tests

- [ ] Implement the authoritative table and legacy mapping in
  [GRAPH_SCHEMA.md](GRAPH_SCHEMA.md), updating ontology, migration, fixtures,
  queries, loader validation, frontend types, and documentation together.
- [ ] Include nine labels and Redis as Service(kind=cache). Use AFFECTED for observed
  symptoms; verified causal/fix edges only for resolved history. Reconcile overloaded
  CHANGED_BY, DEPLOYED_BY, CAUSED_BY explicitly. Document any target-model deviation.
- [ ] Store consistent immutable application IDs on nodes and edges; outer fixture
  IDs equal property IDs. Return stable evidence/path references. Do not use graph
  internal numeric IDs. Optional ownership/authorship must not erase candidates.
- [ ] Identify ontology.json as custom metadata; implement typed fixture validation.
  Test required fields/enums, ID conflicts, endpoints, source/target directions,
  environment/time consistency, and absence of active cause/applied-fix answers.
- [ ] Use supported range indexes and explicitly validate uniqueness. Verify migration
  syntax, repeated initialization, and existing-index behavior on the pinned server.
  Provide explicit legacy migration guidance without routine destructive resets.
- [ ] Implement one backend loader and `graph/seed.py` CLI using parameterized MERGE
  operations and allowlisted labels/types. Seed twice without duplicate edges/nodes
  or erasing other records; init completes before readiness. Reset is explicit and
  refuses every graph except the designated demo graph (`graphops` initially).
- [ ] Primary dataset: checkout → payment → Redis, symptoms, recent pool-size change,
  commit diff/repository/pipeline/author/owner, earlier resolved cause and proven fix,
  unrelated recent deployment, and competing plausible candidate. Expected answers
  belong to tests, not active confirmed graph facts. Clock: 2026-10-15T06:30:00Z.
- [ ] Separate upstream and downstream tools. Correct blast-radius direction.
  Return actual ordered path nodes/edges with forward/reverse traversal direction.
- [ ] Include zero-hop direct-service changes; filter environment and explicit
  inclusive deployment window; exclude future/out-of-window changes. Bound hops,
  rows, timeout. Keep optional metadata, deduplicate candidates, preserve bounded
  supporting paths, and order deterministically. Timing remains correlation.
- [ ] Historical matches cover dependency services with compatible symptoms/category,
  strictly earlier start/resolution, verified cause/proven fix, relevance reasons
  and stable rank. Avoid same-service-only and unordered history lookups.
- [ ] Use the official client's read-only mechanism for investigation queries.
  Writes are restricted to initialization or future recorded resolutions.
- [ ] Acceptance: isolated live tests prove seed repeatability/isolation/identity,
  path direction/hop bounds/cycles, direct-service changes, exact time boundaries,
  future/environment filtering, duplicate paths, missing metadata, ambiguity,
  history ordering/relevance/fixes, and empty results. Requested live tests fail
  clearly if their DB is unavailable; cleanup refuses the demo graph.

Official references: [Python client](https://github.com/FalkorDB/falkordb-py),
[range indexes](https://docs.falkordb.com/cypher/indexing/range-index),
[read-only query](https://docs.falkordb.com/commands/graph.ro-query).

### Stage 3 — Graph-backed APIs

- [ ] Add thin routes, Pydantic request/response contracts, and graph repository:
  GET `/api/v1/services`, `/incidents`, `/incidents/{incident_id}`, `/topology`.
- [ ] Validate IDs, environment and result bounds; expose deterministic pagination
  or truncation for bounded results. Use parameterized query values.
- [ ] Unknown records return 404; invalid requests 422; graph failure a documented
  503 dependency error. Keep blocking I/O off the event loop.
- [ ] Acceptance: live API tests return actual seeded data/stable IDs, plus unknown
  IDs, empty collections, outage and recovery. Document only implemented routes
  as available; keep planned endpoints labelled.

### Stage 4 — Deterministic investigation engine

- [ ] Implement POST `/api/v1/incidents/{incident_id}/investigate` with bounded
  question/environment/window/hops/rows using validated repository operations.
- [ ] Return conclusion/status, observed evidence, upstream dependencies/downstream
  impact, deployment/commit/pipeline/repository/person candidates, actual paths,
  historical matches/proven fixes, recommendation with support, missing evidence,
  competing hypotheses, confidence rationale, and execution mode.
- [ ] Score graph evidence transparently; preserve ambiguity and insufficient
  evidence. Active hypotheses cannot become confirmed cause/fix facts.
- [ ] Acceptance: complete live API investigation finds the payment pool-change
  candidate and earlier fix while comparing a plausible rival; unrelated/future
  changes excluded. Missing evidence and graph outages are honest. No LLM needed.

### Stage 5 — Grounded AI tools and labelled fallback

- [ ] Add optional endpoint/model/key settings server-side in `.env.example` and
  Compose. No new service or agent framework required.
- [ ] Implement a bounded typed tool loop for incident context, dependencies, recent
  changes, historical fixes. Validate arguments; allowlist operations; no arbitrary
  LLM Cypher/shell. Bound calls, output bytes, per-call/overall timeout.
- [ ] Treat retrieved text as untrusted data. Require structured conclusions/actions
  with evidence/entity/path references and validate actual support, not just ID
  membership. Reject unsupported conclusions even with valid citations.
- [ ] Absent/unavailable/invalid LLM returns labelled deterministic mode and reason,
  based on successful graph retrieval. Graph unavailability always returns 503.
- [ ] Acceptance: demonstrate a real configured LLM invoking tools and supported
  synthesis when credentials are available. Tests exercise missing credentials,
  timeouts, malformed responses, fabricated refs, unsupported claims/actions,
  oversized output/call budget, and hostile retrieved text. Record any unavailable
  real-LLM verification as a blocker; mocks do not prove endpoint integration.

### Stage 6 — Incident UI and exact evidence visualization

- [ ] Replace ontology cards/static ready badge with dashboard, actual readiness,
  service states, incident list/detail, bounded question and investigate action.
- [ ] Display status/conclusion, evidence, competing candidates, missing evidence,
  confidence rationale, historical fixes, recommendations, and mode/fallback reason.
- [ ] Use one directed graph library and exactly backend-returned paths/directions.
  Clickable and keyboard-accessible nodes expose evidence; no guessed edges.
- [ ] Support loading, empty, unknown incident, dependency failure, insufficient
  evidence, ambiguity, fallback, responsive layouts, and keyboard-accessible controls.
- [ ] Acceptance: lint/type/build pass; browser walkthrough investigates checkout,
  verifies exact returned paths, and exercises graph/LLM failures honestly.

### Stage 7 — Validation and CI

- [ ] Consolidate tests under `backend/tests/`, using isolated prefixed test graphs
  and cleanup guards that cannot delete demo data. Preserve existing user volumes.
- [ ] Run Stage 1–6 regression/failure coverage and one complete live API flow.
  Explicit live mode must fail, not silently skip, when its DB is unavailable.
- [ ] CI runs backend checks, pinned live FalkorDB tests, frontend ESLint CLI/type
  check/build, and Compose validation. Record exact commands and results.
- [ ] Acceptance: meaningful unit/live/API suites and browser smoke pass. No mock-only
  evidence substitutes for graph query correctness or live endpoint integration.

### Stage 8 — Complete Docker verification

- [ ] Verify `docker compose up --build` from a fresh isolated clone/project with
  fresh isolated volumes, no host packages/source mounts, all graph assets in image,
  validated init before backend readiness, and a working investigable frontend.
- [ ] Stop/restart the same isolated stack: preserve non-seed records and stable
  fixture IDs/counts, verify persistence config and repeated initialization.
- [ ] Exercise graph stop/recovery and optional LLM failures through the UI.
- [ ] Verify documented demo-only reset rejects test/other graphs and preserves
  unrelated user volumes; never use broad volume deletion for routine startup.
- [ ] Acceptance: record live commands, image versions, initialization, readiness,
  end-to-end investigation, restart evidence, and reset behavior. Compose parsing,
  volume declarations, and regenerated seeds alone cannot satisfy acceptance.

### Stage 9 — Documentation, demo, and submission

- [ ] Keep README/architecture/schema/API/settings/runbook aligned with actual
  behavior as each stage lands. Repository-relative local links, no stale Git
  claims, unmeasured latency, automatic rollback/contact, or wipe-on-startup.
- [ ] Document Docker-only setup, optional LLM settings, test/live-mode commands,
  readiness/errors, browser/container URLs, persistence, demo reset and troubleshooting.
- [ ] Replace planned example paths with retrieved live evidence and explain why
  multi-hop/time/history reasoning makes FalkorDB essential for Track 01.
- [ ] Follow [DEMO.md](DEMO.md): incident → tools → candidate comparison → explanation
  → historical fix; record a working demo video and complete local instructions.
- [ ] Verify authenticated submission panel's actual required fields, URLs/video
  requirements, deadlines and track selection. Record panel evidence; do not
  claim it was checked from public FAQ alone. Prepare concrete materials before
  seeking any approval required for publication/submission.
- [ ] Acceptance: reviewer can launch and investigate checkout, understand paths
  and uncertainty, see honest failures, and reproduce documented checks. Repo,
  instructions, working video, and actual required submission fields are ready.

## Completion and handoff

The MVP is complete only after a fresh clone launches with the canonical command,
checkout investigation retrieves actual FalkorDB evidence and history, the UI
preserves uncertainty/failures, and required live checks pass. Finish each active
work session with changed files, tests actually run and exact results, blockers,
verified startup/reset commands, and demo walkthrough. Keep incomplete checks
unchecked; a date or successful scaffold build does not complete a stage.
