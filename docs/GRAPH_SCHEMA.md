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
