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
    create_res = client.post("/api/sessions", json={"title": "Test Growth Consultation"})
    assert create_res.status_code == 200
    session = create_res.json()
    assert "id" in session
    assert session["title"] == "Test Growth Consultation"

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

def test_out_of_scope_query():
    # Create session
    create_res = client.post("/api/sessions", json={"title": "Off Topic Test"})
    session_id = create_res.json()["id"]

    # Send off-topic question
    chat_res = client.post("/api/chat", json={
        "session_id": session_id,
        "message": "What is the weather and recipe for pizza in Paris?",
        "provider": "fallback"
    })
    assert chat_res.status_code == 200
    res_data = chat_res.json()
    assert res_data["intent"] == "out_of_scope"
    assert "strictly grounded in Lenny's Podcast" in res_data["content"]

def test_database_url_sanitization():
    from backend.app.config import Settings
    s = Settings(DATABASE_URL="postgres://user:pass@localhost/db")
    assert s.sanitized_database_url == "postgresql+pg8000://user:pass@localhost/db"
    s2 = Settings(DATABASE_URL="postgresql://user:pass@localhost/db")
    assert s2.sanitized_database_url == "postgresql+pg8000://user:pass@localhost/db"


