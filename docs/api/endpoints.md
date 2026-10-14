# GraphOps API contract

Reviewed October 14, 2026. Browser development base: `http://localhost:8000`.
Internal Next.js server requests in Compose must use `http://backend:8000`.
Only `/` and `/health` are implemented at the reviewed baseline.

## Route availability

| Method and path | Current state | Intended behavior |
| --- | --- | --- |
| GET `/` | Implemented | API metadata/docs links |
| GET `/health` | Implemented, misleading | Stage 1 readiness alias, 503 on graph/init failure |
| GET `/health/live` | Planned, Stage 1 | Process liveness, 200 even when graph unavailable |
| GET `/health/ready` | Planned, Stage 1 | Read-only graph query and initialization checks; 200 ready or 503 unavailable |
| GET `/api/v1/services` | Planned, Stage 3 | Bounded services filtered by environment |
| GET `/api/v1/incidents` | Planned, Stage 3 | Bounded active and historical incident list |
| GET `/api/v1/incidents/{incident_id}` | Planned, Stage 3 | Incident and observed symptoms; 404 unknown |
| GET `/api/v1/topology` | Planned, Stage 3 | Bounded actual service nodes and directed dependency edges |
| POST `/api/v1/incidents/{incident_id}/investigate` | Planned, Stage 4 | Read-only deterministic graph investigation, later optional AI |

There is no implemented GET investigation endpoint, trigger/scenario endpoint,
or resolution endpoint. Resolution writeback is deferred and would require an
explicitly recorded operator outcome. No route executes infrastructure actions.

## Planned request bounds

Finalize these limits in typed models/tests as Stage 3–4 lands. Proposed defaults:
IDs 1–128 characters with allowlisted characters; question 1–1000 characters when
supplied; environment from a configured allowlist; deployment window default
3600 seconds, allowed 60–86400; hops default 3, allowed 1–5; returned row limit
default 50, allowed 1–200. Tool-specific limits may be smaller. Bound total paths,
evidence records, bytes, and query/request/tool timeouts as well. A path includes
zero-hop incident-service change coverage even if dependency hop bounds start at 1.

Example **planned** request body:

```json
{
  "question": "Why is checkout timing out, and which change should we inspect?",
  "environment": "production",
  "window_seconds": 3600,
  "max_hops": 3,
  "limit": 50
}
```

Reject unsupported environments, mismatches with the incident, invalid IDs/ranges,
and excessive questions through typed validation. Read queries use parameters;
IDs/questions can never become arbitrary Cypher or shell commands.

## Planned response

An investigation includes `incident_id`, explicit `status` (supported hypothesis,
ambiguous, insufficient evidence), `conclusion`, `evidence`, `paths`, upstream
services, downstream impact, candidates with deployment/commit/pipeline/repository/
person provenance, historical matches/proven fixes with relevance reasons,
recommendations/support references, missing evidence, competing hypotheses,
confidence score/rationale, and `execution_mode` (deterministic or LLM-assisted).
Return a fallback reason when an optional LLM is absent or rejected/unavailable.

Every node/edge/evidence/path has a stable application reference. Paths contain
ordered node and edge IDs and traversal direction for each step. Facts identify
retrieved field values and support; conclusions/actions cannot cite a valid ID
while asserting unsupported content. Recommendations remain operator suggestions.
Confidence is an explained evidence score, not a calibrated probability. Bounded
collections expose truncation/limit metadata rather than implying completeness.

Document the exact Pydantic/OpenAPI schema when implemented rather than treating
this target as an available wire format.

## Errors and readiness

Planned domain errors use an envelope with `code`, `message`, and bounded `details`:
404 `not_found`; 503 `graph_unavailable` or `initialization_unavailable`. Request
validation uses FastAPI's 422 validation response; do not document that as the same
domain envelope unless explicitly implemented. Do not expose secrets in errors.

LLM failures after successful graph retrieval yield a labelled deterministic
response. Graph failure yields 503 and never a fabricated successful explanation.
Empty collections differ from unknown incident IDs. See
[architecture](../ARCHITECTURE.md) and [task checks](../TASKS.md).
