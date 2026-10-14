# GraphOps graph model

**Target contract, October 14, 2026; not implemented yet.** This is the authoritative
relationship table for Stage 2. Existing ontology metadata, fixture, migration,
query files, and frontend types still use the legacy eight-label model. Update
those representations together during the event and verify them against a pinned
FalkorDB version before marking the stage complete. See [TASKS.md](TASKS.md).

## Identity and node fields

Every node has a required immutable, globally unique application `id`. Every
fixture's outer `id` must equal `properties.id`; endpoints refer to that same ID.
Keep `INC-4091` as the primary incident ID. Names, emails, SHAs, and FalkorDB
internal numeric IDs are not portable public identifiers. Where a natural key is
useful, validate it separately (for example repository plus full commit SHA).

| Label | Required domain properties beyond `id` | Optional enrichment |
| --- | --- | --- |
| `Service` | `name`, `kind` (`application`, `database`, `cache`), `environment`, `status` | `tier`, `language`, descriptions |
| `Repository` | `name` | `url`, `default_branch` |
| `Developer` | `name` | `email`, `team`, `on_call` |
| `Commit` | `sha`, `timestamp`, `message` | `diff_summary`, structured change details |
| `Pipeline` | `run_id`, `status`, `timestamp` | `name`, `url` |
| `Deployment` | `version`, `environment`, `timestamp`, `status` | `namespace`, artifact URL |
| `Incident` | `title`, `severity`, `status`, `environment`, `timestamp`, `symptom_category` | `error_message`, `resolved_at` (required when resolved) |
| `RootCause` | `summary`, `category` | verification description |
| `Fix` | `action_type`, `description` | operator instructions, inert command text |

Use UTC integer Unix seconds and consistent enums validated by the loader. A
Pipeline node represents one concrete run on one commit, not a generic workflow.
Redis/Postgres are Service nodes distinguished by `kind`, not new labels.
Ownership, authorship, repository URL, or diff enrichment may be missing: return
the otherwise valid candidate with missing-evidence notes. Absence of optional
links is not a reason to discard deployments.

## Authoritative relationship table

All arrows below are stored source → target direction. Every edge requires a
stable `id` unique across the graph. Derive fixture edge IDs deterministically
from type, source, target, and a semantic discriminator when needed. Use one edge
per endpoint pair/type in the MVP; reject duplicate/conflicting IDs before writes.

| Source | Relationship | Target | Meaning | Required properties beyond `id` |
| --- | --- | --- | --- | --- |
| `Service` | `DEPENDS_ON` | `Service` | Caller depends on upstream provider in the same environment | `protocol`, `critical` |
| `Service` | `BELONGS_TO` | `Repository` | Source/config repository for service | none |
| `Service` | `OWNED_BY` | `Developer` | Operational owner; optional link | `role` |
| `Repository` | `OWNED_BY` | `Developer` | Repository maintainer; optional link | `role` |
| `Commit` | `BELONGS_TO` | `Repository` | Repository containing the revision | none |
| `Commit` | `AUTHORED_BY` | `Developer` | Revision author; optional link | none |
| `Pipeline` | `TRIGGERED_BY` | `Commit` | Exact revision that triggered this run | none |
| `Deployment` | `TRIGGERED_BY` | `Pipeline` | Concrete run that produced this release | none |
| `Service` | `DEPLOYED_BY` | `Deployment` | Release applied to this service; environment must match | none |
| `Incident` | `AFFECTED` | `Service` | Observed symptom on this service; environment must match | `observed_at` |
| `Incident` | `CAUSED_BY` | `RootCause` | Operator-verified diagnosis only | `verified_at`, `verification_ref` |
| `Incident` | `RESOLVED_BY` | `Fix` | Applied fix with recorded successful outcome | `applied_at`, `outcome`, `verification_ref` |
| `RootCause` | `RESOLVED_BY` | `Fix` | Historically proven remedy for this cause | `verified_at`, `verification_ref` |

Deployment → pipeline → commit supplies release revision provenance; do not add
a competing direct deployment/commit relationship with a second source of truth.
Missing provenance links remain visible as missing evidence. Author and owner
links do not imply that a person deployed a release. Causal/fix edges exist only
for verified historical diagnoses in the MVP. Verification references identify
synthetic recorded operator observations in demo data, never real telemetry.
`CHANGED_BY`, `CAUSED`, and `SIMILAR_TO` remain reserved vocabulary; no edge is
added merely to use a term.

## Legacy reconciliation

| Existing relation | Target change and rationale |
| --- | --- |
| `Commit → CHANGED_BY → Developer` | Replace with `AUTHORED_BY`; authorship is distinct from deployment execution |
| `Commit → CHANGED_BY → Repository` | Replace with `BELONGS_TO`; repository membership is distinct from authorship |
| `Deployment → DEPLOYED_BY → Service` | Reverse to `Service → DEPLOYED_BY → Deployment`; release is attached to the service it deployed |
| `Deployment → DEPLOYED_BY → Commit` | Replace with deployment → run → commit provenance through `TRIGGERED_BY` |
| `Deployment → DEPLOYED_BY → Developer` | Remove legacy implied operator link; retain only supported author/owner evidence |
| `Incident → CAUSED_BY → Service` | Replace with `AFFECTED`; observed symptoms are not confirmed causes |
| Active incident cause/fix links | Remove from the replacement active scenario; keep expected answers in tests |
| Historical verified cause/fix links | Retain with required verification/outcome properties |

Implement a versioned, explicit migration plan for any already populated legacy
demo graph; routine startup must not wipe it. Detect incompatible versions and
report readiness failure with migration guidance. Test migration/repeated init
on isolated graphs, then update fixtures, queries, loader, types, and docs as one
stage. Never silently mix legacy and target directions.

## Traversal and temporal semantics

Outgoing `DEPENDS_ON` finds upstream dependencies. Incoming traversal finds
downstream blast radius; keep separately named repository tools. A stored edge's
direction remains unchanged when traversed in reverse. Return ordered path nodes,
edge IDs, and per-step `forward`/`reverse` traversal direction.

Bound hop count, rows, time windows, and query timeout. Search the incident service
itself (zero hops) and its upstream services. Filter every relevant service and
deployment to the selected environment. Include the lower and upper deployment
window endpoints, exclude future changes, deduplicate deployments reached by
multiple paths while retaining bounded supporting paths, and order by timestamp
then stable ID. Optional metadata uses optional matches rather than mandatory
joins. Test cycles and zero-hop behavior on the selected server.

Historical matches require `status = RESOLVED`, start and resolution strictly
earlier than the active incident, a shared relevant service on the dependency
chain, and compatible recorded symptoms/categories. Retrieve verified cause and
successful applied fix paths, rank deterministically, and explain which facts
make the match relevant. Historical similarity does not confirm the active cause.

## Seed design and validation

The primary replacement fixture uses checkout → payment → Redis, an active
checkout timeout incident, a recent payment pool configuration change, its
commit/diff/repository/pipeline/author/owner evidence, and an earlier resolved
incident with a proven fix. Include an unrelated recent deployment and a competing
plausible candidate. Live test fixtures also exercise missing metadata, exact
boundaries, future/staging changes, duplicate paths, cycles, and empty results.
Schema drift and recurring deadlock scenarios wait until the primary flow works.

Use a documented fixed demo clock of **2026-10-15T06:30:00Z** (12:00 IST); encode
relative events against it, never the host's current clock. Query windows anchor
to the selected incident timestamp. Fixture observations are synthetic.

One loader and one CLI (`graph/seed.py`, planned) handle validation and idempotent
initialization. Before any write, check label/type allowlists, identity agreement,
required fields/enums, endpoint existence/direction, environment consistency,
temporal consistency, duplicate IDs, and absence of active confirmed causes/fixes.
Use parameterized values and allowlisted labels/types for MERGE operations.
Test twice for identical counts/IDs/properties and preserve non-fixture records.

## Metadata, indexes, and uniqueness

`graph/schema/ontology.json` is currently custom metadata despite its `$schema`
declaration. It is not a validated JSON Schema. Stage 2 will identify it as custom
metadata and validate fixtures through typed models; do not imply generic JSON
Schema validation has checked it.

Plan range indexes on each label's `id` and necessary service/environment/time
lookups. Verify syntax, existing-index behavior, and query results live against
the pinned server. The [official range-index documentation](https://docs.falkordb.com/cypher/indexing/range-index)
documents lookup syntax; index creation and metadata `unique: true` do not prove
identity uniqueness. Validate duplicates before/after writes and define a single
initialization writer for the local MVP. If supported constraints are selected,
test their enforcement explicitly rather than assuming it.

Evidence IDs identify facts by stable entity/edge ID plus field/source reference.
Path IDs derive from ordered stable node/edge IDs and traversal directions. Do
not expose the database's numeric IDs. All investigation reads use
[GRAPH.RO_QUERY](https://docs.falkordb.com/commands/graph.ro-query) through the
official client, with bounded timeouts/results; writes belong to initialization
or future explicitly recorded resolution operations.
