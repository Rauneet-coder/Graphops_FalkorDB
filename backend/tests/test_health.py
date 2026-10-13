from app.core.config import settings
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_settings_load():
    assert settings.PROJECT_NAME == "GraphOps API"
    assert settings.FALKORDB_PORT == 6379
    assert settings.FALKORDB_GRAPH == "graphops"
    assert "http://localhost:3000" in settings.CORS_ORIGINS


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == settings.PROJECT_NAME
    assert data["database"]["type"] == "FalkorDB"
    assert data["database"]["port"] == 6379


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["docs"] == "/docs"
