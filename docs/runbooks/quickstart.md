# Quickstart Runbook

This guide steps through bootstrapping GraphOps locally with Docker Compose.

## 1. Environment Preparation
Ensure Docker is installed and running. Create your local environment file:
```bash
cp .env.example .env
```

## 2. Launching Services
Start the full stack:
```bash
docker compose up -d --build
```

Verify service statuses:
```bash
docker compose ps
```

Services exposed:
- **Frontend UI:** `http://localhost:3000`
- **Backend API:** `http://localhost:8000/docs`
- **FalkorDB:** `localhost:6379`

## 3. Database Verification
Verify FalkorDB connectivity:
```bash
docker compose exec falkordb redis-cli ping
# Expected output: PONG
```

Run initial index migrations:
```bash
docker compose exec falkordb redis-cli GRAPH.QUERY graphops "CREATE INDEX FOR (s:Service) ON (s.name)"
```

## 4. Local Development without Docker
If running services natively:
- **Backend**:
  ```bash
  cd backend
  source .venv/bin/activate
  uvicorn app.main:app --reload --port 8000
  ```
- **Frontend**:
  ```bash
  cd frontend
  npm run dev
  ```
