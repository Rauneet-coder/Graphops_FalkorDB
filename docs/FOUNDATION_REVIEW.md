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

| Check | Actual result |
| --- | --- |
| Compose validation | Canonical, dev override, and test override parse successfully |
| Production image builds | Backend pip install/pip check and frontend npm ci succeeded |
| Backend unit/live suite | `python -m pytest -q -p no:cacheprovider --live-graph`: **25 passed, 1 warning in 1.40s**; no live skips |
| Backend lint | `ruff check --no-cache app tests`: **All checks passed** |
| Frontend checks in Dockerfile | ESLint CLI with zero allowed warnings, tsc --noEmit, Next production build: **passed** |
| Actual Cypher | `GRAPH.RO_QUERY graphops 'RETURN 1 AS graphops_ready' TIMEOUT 500` returned **1** |
| Ordinary Redis | PING succeeded, but graph initialization/readiness failed as required |
| Health before lifespan/init | 503 readiness, 200 liveness; live cold backend started while DB was stopped remained uninitialized/503 |
| Real outage/recovery | Stopping FalkorDB caused readiness/alias 503 while liveness remained 200; both existing and cold-started backend recovered after DB restart |
| Explicit live mode during outage | Intentionally selected live test failed with **pytest exit 1**, “Required live FalkorDB initialization failed”; harness required that failure |
| Persistence | A unique non-fixture record survived stop/start and a force-recreated graph container; read before any probe-graph initialization could recreate it |
| Effective disk settings | `dir=/var/lib/falkordb/data`, `appendonly=yes`, `appendfsync=everysec` |
| Production frontend | Actual page and health returned 200; obsolete engine-ready badge absent; lint dependencies absent from standalone runner |
| Missing dependency/config cases | Required-package import failure, missing driver interface, malformed CORS, invalid timeout order, graph-query failure and retry covered |
| Event loop/lifecycle | Blocking graph probe left liveness responsive; client/pool shutdown cleanup covered |

The TestClient warning is Starlette's deprecation of the httpx integration; tests
still pass. It is reported rather than hidden. No latency/SLO claim is made from
these test durations or the graph engine's diagnostic timings.

## Failures found and fixed during live verification

The initial suite passed, but the first full lifecycle script failed when replacing
the graph container. A constant RETURN query creates an empty graph key without
a durable graph mutation to replay from AOF. The non-fixture probe graph persisted,
but the empty readiness graph did not. Readiness now marks failed probes
uninitialized and the lifespan worker retries initialization; the readiness route
itself remains read-only. The final full replacement check passed.

The image exposes `/data` as a symlink to `/var/lib/falkordb/data`. Compose was
changed to mount the effective canonical directory explicitly. Test cleanup also
avoids GRAPH.DELETE on empty graphs without durable writes: that command errored
during AOF replay on 6.0.2. Guarded Redis DEL targets only freshly generated
`graphops_test_stage1_*` graph keys and is idempotent during replay. The demo graph
is never selected for test cleanup. Verification volumes are retained, not deleted.

An initial non-root Ruff invocation could not create its default cache in the
application directory; verification now uses --no-cache. An ESLint 10 trial passed
checks but produced plugin peer conflicts; it was replaced with the compatible
9.39.5 pin and a clean strict-peer lock resolution. These failed attempts are not
reported as final successful verification.

## Dependency advisories and limitations

The production npm audit (`npm audit --omit=dev --json`) reported **zero advisories**.
The full audit reported **five high entries for one development-chain advisory**:
[braces stack-exhaustion DoS, GHSA-vfj7-8cjw-p6xm](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm).
No patched braces version was published when checked. It is pulled through the
Next ESLint plugin's glob dependencies, not the standalone production runner.
Do not run npm audit fix --force: its suggested downgrade returns to unsupported
Next 14 tooling. Preserve the evidence rather than claiming a clean full audit.

[ESLint 9 is EOL](https://eslint.org/version-support/), but current Next lint
plugins' published peer ranges end at ESLint 9. The pin is a compatibility
limitation, not a claim of supported lint tooling. Revisit when upstream publishes
compatible plugin releases. The production app runs supported Node 24/Next 16.

