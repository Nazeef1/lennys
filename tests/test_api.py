import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.database import init_db

init_db()
client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "indexed_chunks" in data
    assert "active_provider" in data

def test_create_and_list_sessions():
    # Create session
    create_res = client.post("/api/sessions", json={"title": "Test Growth Consultation"})
    assert create_res.status_code == 200
    session = create_res.json()
    assert "id" in session
    assert session["title"] == "Test Growth Consultation"

    # List sessions
    list_res = client.get("/api/sessions")
    assert list_res.status_code == 200
    sessions = list_res.json()
    assert len(sessions) > 0
    assert any(s["id"] == session["id"] for s in sessions)

def test_models_endpoint():
    res = client.get("/api/models")
    assert res.status_code == 200
    data = res.json()
    assert "active" in data
    assert "providers" in data
    assert len(data["providers"]) >= 3

def test_select_model():
    res = client.post("/api/models/select", json={"provider": "fallback"})
    assert res.status_code == 200
    data = res.json()
    assert data["active_provider"] == "fallback"
