# GraphOps implementation plan

Status: planning complete; Stage 1 awaits the next user instruction.
Existing files are scaffolding, not evidence that a stage has passed acceptance.
No application implementation is authorized by this planning task.

## Repository assessment

| Area | Existing files and behavior | Gap |
| --- | --- | --- |
| Infrastructure | Compose, both Dockerfiles, `.env.example`, `.gitignore` | Three services defined; only FalkorDB has a Compose healthcheck. No automatic schema/seed setup. Image uses `latest`; Python dependencies have lower bounds only. |
| Backend | `app/main.py`, `core/config.py`, `core/falkordb.py`; empty API/model/service initializers | Only `/` and `/health` exist. Health always reports `healthy`, even when `connected` is false. Synchronous driver calls run inside an async route. |
| Graph | `schema/ontology.json`, `migrations/001_initial_schema.cypher`, `seeds/sample_graph.json`, three query files | Eight labels, no `Pipeline`; no seed runner. Twelve seed nodes and fourteen edges include an active incident with its answer/fix attached and no resolved historical incident. |
| Frontend | App Router page/layout/styles, graph types, Next/TS/ESLint configs, npm lockfile | Static ontology page with unconditional engine-ready badge; no API integration. Tailwind and graph visualization are not installed. |
| Tests | `backend/tests/test_health.py`, backend/root `pyproject.toml` | Three basic tests; no live graph tests. Health test does not prove DB connectivity. No root `tests/` directory. |
| Docs | README, AGENTS, architecture/schema/task/foundation docs; API/architecture/runbook subdocs; pipeline README | Old roadmap replaced here. Other docs contain conflicting edge semantics, premature rollback features, and verification/performance claims not reverified in this planning pass. |

Local generated artifacts include Node dependencies, Next build output, the backend
virtual environment, and caches. Exclude these from source and Docker build contexts.
The inspected workspace has no Git repository metadata; initialize version control
before collaborative implementation. No tests or containers ran for this docs-only task.

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

Complete each acceptance check before advancing. Add relevant tests as behavior
lands; Stage 7 consolidates coverage rather than deferring tests.

### Stage 1 — Infrastructure

- Review Compose/Dockerfiles; retain FalkorDB, backend, and frontend only.
- Select a tested FalkorDB image version; verify persistence and graph-query
  capability, not just Redis `PING`.
- Fix backend readiness to reflect DB failures; add dependency-aware healthchecks,
  startup ordering, and bounded connection timeouts.
- Wire env settings into Compose; document container vs host URLs.
- Acceptance: DB starts, trivial Cypher succeeds, readiness reflects a stopped DB,
  and persistent data survives restart.

### Stage 2 — Graph

- Reconcile ontology, schema docs, queries, and seed edge directions together.
  Add `Pipeline` with stable ID, run/status/time properties.
- Define explicit service/repository, commit/author, pipeline/commit, and
  deployment/service/commit/pipeline links. Use `AFFECTED` for symptoms and reserve
  causal links for confirmed causes. Timing alone must not create `CAUSED`.
- Document each edge's source, target, direction, and properties; demonstrate a
  multi-hop service → dependency → change → pipeline/deployment evidence path.
- Implement `graph/seed.py` through a small loader: supported indexes, validated
  labels/keys/endpoints, parameterized writes. Validate uniqueness explicitly;
  do not assume a lookup index provides a uniqueness constraint.
- Begin with checkout → payment → Redis, a recent pool-size change, and an earlier
  resolved incident with a proven fix. Add unrelated recent changes and a schema
  drift scenario afterward. Anchor relative demo times to a repeatable clock.
- Keep active answers out of the investigable seed; store expected answers in tests.
  Seed idempotently; require explicit demo-only reset.
- Add validation Cypher for counts, required fields, duplicate identifiers, invalid
  endpoints, evidence paths, and historical fixes.
- Acceptance: seeding twice creates no duplicates; live queries return correct
  paths, pipeline provenance, time ordering, and a distinct resolved historical match.

### Stage 3 — Backend

- Improve existing connection lifecycle/settings; add the graph repository and
  Pydantic node, edge, incident, and evidence models.
- Add thin `GET /api/v1/services`, `/incidents`, `/incidents/{id}`, and `/topology`
  routes backed by FalkorDB. Keep blocking driver calls off the async event loop.
- Acceptance: API returns seeded data with stable IDs; unknown IDs return 404 and
  graph outages return a documented dependency error.

### Stage 4 — Investigation engine

- Execute bounded Cypher for upstream investigation and downstream blast radius,
  including the incident service and an explicit deployment time window.
- Retrieve candidate deployment, commit, pipeline, repository, author/owner, and
  historical cause/fix paths without requiring every optional link to exist.
- Return actual path nodes/edges, evidence IDs, competing candidates, missing
  evidence, and an explained confidence score; distinguish correlation from proof.
- Add `POST /api/v1/incidents/{id}/investigate`; investigation stays read-only for MVP.
- Acceptance: checkout finds the relevant change with reconstructable paths;
  unrelated/future changes are excluded and insufficient evidence is explicit.

### Stage 5 — AI agent

- Implement a bounded tool loop with typed allowlisted tools for incident context,
  dependencies, recent changes, and related historical fixes through the repository.
- Pass only retrieved graph evidence to a configurable LLM client; no arbitrary
  generated Cypher. Validate structured conclusions, citations, paths, historical
  matches, actions, and confidence; reject unsupported claims/fabricated references.
- Document optional endpoint/model/key in `.env.example`. Without an LLM or after
  timeout, return a labelled deterministic explanation of the same FalkorDB evidence.
- Acceptance: an LLM integration invokes graph tools and returns grounded output;
  local fallback needs no credentials. Graph failure cannot produce a successful
  fabricated RCA. No autonomous rollback or confirmed-cause writeback.

### Stage 6 — Frontend

- Add Tailwind; connect the page to real service/incident status and investigation.
- Display conclusion, evidence, historical fixes, confidence rationale, loading,
  dependency failures, and fallback/insufficient-evidence states.
- Use one lightweight visualization library for directed paths, clickable nodes,
  and highlighted evidence.
- Acceptance: checkout renders exactly the returned backend evidence paths and
  handles loading, missing records, and unavailable dependencies clearly.

### Stage 7 — Testing

- Consolidate repository/service/API tests and live FalkorDB integration tests in
  an isolated test graph with explicit cleanup that cannot target demo data.
- Cover hop direction/bounds, direct-service deployments, temporal boundaries,
  cycles, missing metadata, ambiguity, historical ordering/matching, repeatable
  seeding, DB outages, LLM timeout/invalid output, and fabricated evidence.
- Add one API investigation flow test and a documented browser smoke check.
- Acceptance: unit and live graph suites pass via documented commands; mocks
  alone cannot satisfy important graph-query validation.

### Stage 8 — Docker integration

- Integrate idempotent schema/seed initialization before backend readiness using
  the backend image; include graph assets without depending on host mounts.
- Make builds reproducible, exclude local artifacts, verify browser API addressing,
  and prevent optional LLM configuration from blocking the graph demo.
- Acceptance: `docker compose up --build` from clean volumes launches a seeded,
  investigable UI without host Python/Node; restarting preserves data without
  duplicate seeds. Document explicit demo reset separately.

### Stage 9 — Hackathon submission

- Update README, canonical architecture/schema docs, and `docs/DEMO.md`; remove
  contradictory claims/machine-specific links and distinguish planned features.
- Explain why FalkorDB is essential with real evidence paths, demo questions,
  installation/configuration, health/test commands, and reset instructions.
- Capture checkout/pool exhaustion and historical-fix examples; extra scenarios
  follow a working primary investigation. Measure performance before claiming it.
- Acceptance: a reviewer runs the canonical command using the README and sees
  a graph-grounded investigation, its path, and its limitations.

## Scope and major risks

- Schema/direction drift can return plausible but incorrect evidence. Reconcile
  representations and test actual FalkorDB queries in Stage 2.
- The current seed reveals its answer. Remove active cause/fix links and include
  historical and distracting changes to demonstrate investigation rather than lookup.
- Deployment timing is not causation. Preserve uncertainty through engine, AI, and UI.
- Current health/ready indicators mislead; correct them before relying on startup checks.
- LLM availability, grounded output, and local model resource demands threaten the
  demo. Keep AI optional and use the same graph evidence in fallback mode.
- Unpinned dependencies, existing local artifacts, and missing initialization can
  hide clean-machine failures. Verify compatibility and clean-volume startup.
- Defer auth, real GitHub/Kubernetes integrations, streaming, vector search,
  automatic remediation, and ingestion frameworks. Prioritize one strong evidence path.

Next action: wait for user instruction before starting Stage 1.
