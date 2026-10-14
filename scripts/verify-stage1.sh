#!/usr/bin/env bash
# Docker-only, no host Python/Node, no access to an existing GraphOps volume.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
project="graphops-stage1-check-$(date +%s)-$$"
cold_backend="${project}-cold-backend"
compose=(docker compose --project-name "$project" --env-file .env.example -f docker-compose.yml -f docker-compose.test.yml)
cleanup() {
  docker rm --force "$cold_backend" >/dev/null 2>&1 || true
  # Preserve the uniquely named verification volume for inspection; never -v.
  "${compose[@]}" down --remove-orphans
  echo "Verification volume retained: ${project}_falkordb_data"
}
trap cleanup EXIT
"${compose[@]}" config --quiet
"${compose[@]}" up --build -d --wait --wait-timeout 120
"${compose[@]}" exec -T backend python -m pytest -q -p no:cacheprovider --live-graph
"${compose[@]}" exec -T backend ruff check --no-cache app tests
"${compose[@]}" exec -T backend python -m tests.stage1_checks ready
"${compose[@]}" exec -T backend python -m tests.stage1_checks frontend
probe_token=$("${compose[@]}" exec -T backend python -m tests.stage1_checks write-probe)
"${compose[@]}" stop falkordb
"${compose[@]}" exec -T backend python -m tests.stage1_checks outage
# Explicit live mode must fail instead of skipping/succeeding when its DB is down.
if "${compose[@]}" exec -T backend python -m pytest -q -p no:cacheprovider --live-graph -k live_probe; then
  echo 'ERROR: explicitly required live test unexpectedly succeeded during outage' >&2
  exit 1
fi
"${compose[@]}" run -d --no-deps --name "$cold_backend" backend
# Give the HTTP process a bounded startup opportunity, without requiring readiness.
for attempt in {1..30}; do
  if docker exec "$cold_backend" python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/live', timeout=1)" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done
docker exec "$cold_backend" python -m tests.stage1_checks uninitialized
"${compose[@]}" start --wait --wait-timeout 90 falkordb
"${compose[@]}" exec -T backend python -m tests.stage1_checks ready
docker exec "$cold_backend" python -m tests.stage1_checks ready
"${compose[@]}" exec -T backend python -m tests.stage1_checks read-probe "$probe_token"
"${compose[@]}" up -d --no-deps --force-recreate --wait --wait-timeout 90 falkordb
"${compose[@]}" exec -T backend python -m tests.stage1_checks ready
"${compose[@]}" exec -T backend python -m tests.stage1_checks read-probe "$probe_token"
"${compose[@]}" exec -T backend python --version
"${compose[@]}" exec -T frontend node --version
"${compose[@]}" exec -T falkordb redis-cli --raw MODULE LIST
printf '%s\n' 'Stage 1 live verification passed; Stage 2 domain schema/seed was not loaded.'
