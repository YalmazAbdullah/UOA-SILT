import pytest
from fastapi.testclient import TestClient
from server.main import app

client = TestClient(app)

def test_create_session():
    response = client.post("/sessions", json={"subject_id": "test_subject"})
    assert response.status_code == 201
    data = response.json()
    assert "session_id" in data
    assert isinstance(data["session_id"], str)

def test_start_session():
    response = client.post("/sessions", json={"subject_id": "test_subject"})
    data = response.json()
    session_id = data["session_id"]
    response = client.put(f"/sessions/start", json={"session_id": session_id})
    assert response.status_code == 200

def test_end_session():
    response = client.post("/sessions", json={"subject_id": "test_subject"})
    data = response.json()
    session_id = data["session_id"]
    response = client.put(f"/sessions/start", json={"session_id": session_id})
    response = client.put(f"/sessions/end", json={"session_id": session_id})
    assert response.status_code == 200