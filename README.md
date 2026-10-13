# GraphOps 🌐

**AI-powered SRE incident investigation system using FalkorDB.**

Built for the **FalkorDB Hackathon**. GraphOps bridges topology-aware graph reasoning, multi-hop causal dependency tracing, and automated root-cause analysis to dramatically reduce Mean Time to Resolution (MTTR).

---

## 🛠️ Stack

- **Frontend:** Next.js (App Router, React 18, TypeScript)
- **Backend:** FastAPI (Python 3.11+, async architecture)
- **Database:** FalkorDB (Ultra-fast Redis-based Graph DB using Cypher)
- **Runtime:** Docker & Docker Compose (100% Local Deployment)

---

## 📐 Graph Schema

### Graph Nodes
- `Service` — Microservice, datastore, or cache component
- `Repository` — Git source code repository
- `Commit` — Code commit or manifest diff
- `Developer` — Service owner, committer, and on-call engineer
- `Deployment` — Released environment artifact
- `Incident` — SRE outage or alert
- `RootCause` — Diagnosed technical failure reason
- `Fix` — Remediation action or rollback command

### Relationships
- `[:DEPENDS_ON]` — Upstream service dependency calls
- `[:OWNED_BY]` — Developer ownership of services & repositories
- `[:CHANGED_BY]` — Author and repo linkage for commits
- `[:DEPLOYED_BY]` — Service, commit, and developer linkage for deployments
- `[:CAUSED_BY]` — Symptom service and root cause linkage for incidents
- `[:RESOLVED_BY]` — Remediation fix applied to incidents and root causes

---

## 🚀 Quickstart

### Prerequisites
- [Docker](https://www.docker.com/) & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### 1. Configure Environment
```bash
cp .env.example .env
```

### 2. Launch Complete Stack via Docker Compose
```bash
docker compose up -d
```

Services will be accessible at:
- **Next.js Frontend:** [http://localhost:3000](http://localhost:3000)
- **FastAPI API & Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **FalkorDB Engine:** `localhost:6379` (`redis-cli -p 6379`)

### 3. Verify Health
```bash
curl http://localhost:8000/health
```

---

## 📚 Documentation
- [AGENTS.md](file:///Users/rauneetsingh/Developer/Graphops/AGENTS.md) — SRE agent rules & conventions
- [docs/ARCHITECTURE.md](file:///Users/rauneetsingh/Developer/Graphops/docs/ARCHITECTURE.md) — Complete MVP architecture specification
- [docs/GRAPH_SCHEMA.md](file:///Users/rauneetsingh/Developer/Graphops/docs/GRAPH_SCHEMA.md) — Ontology definitions and Cypher queries
- [docs/TASKS.md](file:///Users/rauneetsingh/Developer/Graphops/docs/TASKS.md) — 4-day hackathon sprint execution plan
- [docs/FOUNDATION_REVIEW.md](file:///Users/rauneetsingh/Developer/Graphops/docs/FOUNDATION_REVIEW.md) — Verification results & next steps
