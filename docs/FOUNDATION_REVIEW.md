# Stage 1 infrastructure verification

October 14, 2026. **Stage 1 completed and live-verified. Stage 2 has not started.**
Original reviewed baseline: `fc9739d50a025662ae208807e96781d12db6affd` (initially
matched local HEAD and remote main). Later commits appeared during this session;
existing changes, including API tag metadata, were preserved. This report covers
Stage 1 infrastructure only, not a working investigation MVP.

The user explicitly authorized “Start Stage 1 only” and “continue” before the
event. [AGENTS.md](../AGENTS.md) records that exception. Main domain graph work
remains later event work. No fixture, ontology, migration, investigation query,
or frontend domain type was changed in Stage 1.

## Implemented behavior

- Lifespan-owned client, bounded connection/socket/query timeouts, no automatic
  driver retries, a four-worker default graph limiter, and shutdown pool cleanup.
  Required imports fail clearly; no success fallback when the interface is missing.
- Process liveness at `/health/live`; actual read-only Cypher readiness at
  `/health/ready` and `/health`, returning 503 on graph failure or incomplete init.
- Strict CORS/settings validation; no runtime application `sys.path` modification.
- Empty-graph infrastructure initialization/retry, with `scope: infrastructure`
  and `demo_data_loaded: false`. No domain data, schema, or extra runtime label.
- Three production services, immutable base/server image digests, exact dependency
  locks, production runners, non-root app users, loopback published ports, explicit
  settings, graph assets in backend image, and context-specific `.dockerignore`.
- AOF (`appendonly=yes`, `appendfsync=everysec`) and RDB snapshots on a named volume
  mounted at the effective `/var/lib/falkordb/data` directory.
- Optional dev source/reload override; separate test override without published
  ports and with a plain-Redis negative control. One Docker-only verification script.
- Next 16 / React 19 production build, ESLint CLI, type checking, standalone runner,
  frontend process health route, and removal of the static engine-ready claim.

## Versions actually tested

Tested on Docker's Linux arm64 platform. An amd64 image manifest exists, but no
amd64 run was performed in this session.

| Component | Tested pin |
| --- | --- |
| Docker Engine / Compose | 29.5.2 / 5.1.4 |
| FalkorDB | 6.0.2; module version 60002; bundled Redis reports 8.10.2 |
| FalkorDB image digest | `sha256:107455e862a824e45e8e9f5a7fbfdf5e00a08b14e13eae2577c72fd9e3f59ba6` |
| Python | 3.13.16, image index `sha256:a1165e272e578941b84abc79e4ab38a0305cd12803a5c4247979ac7655f4d641` |
| Node | 24.21.0, image index `sha256:d6aa754f16b3197301076f047b5def2f02ea1dbbc2ca920407d46d7ec7f87b20` |
| Backend | FastAPI 0.143.0, FalkorDB client 1.7.1, Redis client 8.1.0; all transitive pins in requirements.txt |
| Frontend | Next 16.4.0, React/React DOM 19.3.0, TypeScript 5.9.3, ESLint 9.39.5, eslint-config-next 16.4.0 |

Python dependencies were resolved/frozen inside the pinned Python image, then
installed and checked in a fresh backend build. The final npm lockfile was
resolved from package.json in a clean container directory using strict peer
validation, then installed with npm ci in the production build. Host virtualenv,
node_modules, build output, and source mounts were not used by that build/run.

## Exact validation results

Final command: `scripts/verify-stage1.sh` — **exit 0**. Project:
`graphops-stage1-check-1791978202-44498`, using a fresh isolated volume and no
published test ports. Its complete log is retained locally at
`/tmp/graphops-stage1-verification.log`.
