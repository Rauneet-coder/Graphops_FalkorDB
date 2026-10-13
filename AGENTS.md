# GraphOps

AI-powered SRE / DevOps incident investigation agent for the FalkorDB hackathon.
Optimize for fast implementation, clear evidence, a reliable local demo, and small
maintainable modules.

## Stack and scope

- Frontend: Next.js App Router, TypeScript, Tailwind CSS (planned).
- Backend: FastAPI, Python 3.11+, Pydantic models.
- Database: FalkorDB, accessed through its Python client over Redis protocol.
- AI: a small tool-calling layer with a configurable LLM endpoint; no agent framework required.
- Runtime: Docker Compose. Canonical startup: `docker compose up --build`.
- Keep the core stack local. Support a graph-based deterministic demo without an
  LLM; optional API credentials come from environment variables.
- Do not add databases, queues, ingestion frameworks, or other services without
  explaining why the current stack cannot meet the requirement.

## Graph reasoning rules

- FalkorDB must be essential. Dependency traversal, deployment time-window
  filtering, historical matching, and evidence paths run in Cypher.
- Do not replace graph reasoning with SQL or an in-memory copy of the graph.
  Python may validate, format, and score evidence returned by FalkorDB.
- Primary labels: `Service`, `Repository`, `Developer`, `Commit`, `Pipeline`,
  `Deployment`, `Incident`, `RootCause`, `Fix`. Model databases and caches as
  `Service` nodes with a distinguishing property.
- Relationship vocabulary: `DEPENDS_ON`, `OWNED_BY`, `BELONGS_TO`, `CHANGED_BY`,
  `AUTHORED_BY`, `TRIGGERED_BY`, `DEPLOYED_BY`, `CAUSED`, `CAUSED_BY`, `AFFECTED`,
  `RESOLVED_BY`, and optional `SIMILAR_TO`.
- Stage 2 must document source label, target label, direction, required properties,
  and stable identifiers for every implemented relationship. Reconcile existing
  overloaded `CHANGED_BY`, `DEPLOYED_BY`, and `CAUSED_BY` usage explicitly before
  updating fixtures and queries together. Do not add edges just to use every term.
- Traverse outgoing `DEPENDS_ON` to investigate upstream dependencies; incoming
  edges find downstream blast radius. Bound hops, rows, and time windows.
- A recent deployment is a candidate, not proof of causation. Separate observed
  facts, hypotheses, and confirmed causes; preserve ambiguous candidates.
- Active demo incidents must not contain their confirmed answer or applied fix.
  Resolved historical incidents may contain verified causes and fixes.
- Seed idempotently using stable keys. Never erase a graph on routine startup;
  an explicit reset command may target only the designated demo graph.

## Evidence and AI contract

- Return a conclusion, evidence, graph reasoning paths, related historical
  incidents, recommended action, and confidence with an explanation.
- Give evidence and path nodes/edges stable references. Every factual LLM claim
  and recommended graph-derived action must cite retrieved evidence.
- Never invent nodes, relationships, logs, commits, fixes, or historical matches.
  Validate structured LLM output and references against retrieved evidence.
- Expose only typed, allowlisted graph tools with validated arguments. Do not
  execute arbitrary LLM-generated Cypher or shell commands.
- Bound tool calls and timeouts. Return explicit insufficient-evidence, graph
  unavailable, or LLM-unavailable results; label deterministic fallback mode.
- Confidence is an explained evidence score, not a calibrated probability.
- AI suggestions do not automatically become confirmed `CAUSED_BY` / `RESOLVED_BY`
  facts. MVP remediation recommends actions; infrastructure execution is outside
  scope. Any demo resolution writeback must be explicitly recorded.

## Code organization

- Keep routes thin: request validation, service call, response model.
- Put Cypher execution and result conversion in `backend/app/graph/`; keep reusable
  query files in `graph/queries/` with one authoritative copy.
- Use `core/falkordb.py` for connection lifecycle/configuration, `services/` for
  investigation orchestration, `models/` for typed contracts, and `agent/` for
  tools, prompts, and LLM integration.
- Use Python type hints, parameterized query values, and allowlisted labels/edges.
- Keep synchronous database/LLM I/O off the FastAPI async event loop.
- No hardcoded secrets. Document settings in `.env.example`; keep credentials
  server-side and out of `NEXT_PUBLIC_*` variables.
- Keep backend and graph tests in `backend/tests/`; avoid a second test tree.

## Validation and workflow

- Add meaningful live FalkorDB tests for important queries, including path
  directions, temporal boundaries, historical matching, and empty results.
  Mock tests alone do not demonstrate graph correctness.
- Test seed repeatability/isolation, graph outages, ambiguous evidence, malformed
  LLM responses, and fabricated evidence references as stages land.
- Verify health/readiness against actual dependencies and startup from clean
  volumes without relying on host-installed packages or seeded state.
- Do not claim checks passed without running them or invent latency targets.
- Follow `docs/TASKS.md` in order. Update architecture/schema/API docs alongside
  relevant changes; use repository-relative links.
- Do not silently change architecture. Explain material changes and their reasons.
- Current authorization is planning only. After updating guidance and tasks, stop
  and wait for the next user instruction before starting Stage 1.
