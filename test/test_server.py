from datetime import datetime,timezone

from fastapi.testclient import TestClient
from server.main import app


client = TestClient(app)

# Testing vars
g_session_id:str = ""
test_subject = "test_subject"

# Session Creation
def test_create_session():
    # To store for later use
    global g_session_id  
    # Create session call
    response = client.post("/sessions", json={"subject_id": test_subject})
    # Check response
    assert response.status_code == 201
    data = response.json()
    assert "session_id" in data
    assert isinstance(data["session_id"], str)
    # Save generated id for later tests
    g_session_id = data["session_id"]

# Get Session
def test_get_session():
    response = client.get(f"/sessions/{g_session_id}")
    assert response.status_code == 200
    
def test_get_session_F():
    response = client.get("/sessions/failed_respose")
    assert response.status_code == 404

# Get All Sessions
def test_get_sessions():
    response = client.get(f"/sessions/all")
    assert response.status_code == 200

# Start Session
def test_start_session():
    response = client.put(f"/sessions/start/{g_session_id}")
    assert response.status_code == 200

def test_start_session_F():
    response = client.put(f"/sessions/start/{g_session_id}")
    assert response.status_code == 400

def test_start_session_F2():
    response = client.put("/sessions/start/failed_respose")
    assert response.status_code == 404

# End Session
def test_end_session():
    response = client.put(f"/sessions/end/{g_session_id}")
    assert response.status_code == 200

def test_end_session_F():
    response = client.put(f"/sessions/end/{g_session_id}")
    assert response.status_code == 400

def test_end_session_F2():
    response = client.put("/sessions/start/failed_respose")
    assert response.status_code == 404

def test_enter_log():
    test_data = {
        "target_time": None,
        "client_time": datetime.now(timezone.utc).isoformat(),
        "source": "client",
        "target": "pytest",
        "event": "success_test",
        "data": {'message':"this is a test"}
    }
    response = client.post(f"/logs/{g_session_id}", json=test_data)
    assert response.status_code == 201

def test_enter_logF():
    test_data = {
        "client_time": datetime.now(timezone.utc).isoformat(),
        "source": "client",
        "event": "fail_test",
        "data": {'message':"this is a test"}
    }
    response = client.post(f"/logs/{g_session_id}", json=test_data)
    assert response.status_code == 422

def test_enter_logF2():
    test_data = {
        "target_time": None,
        "client_time": datetime.now(timezone.utc).isoformat(),
        "source": "client",
        "target": "pytest",
        "event": "fail_test",
        "data": {'message':"this is a test"}
    }
    response = client.post(f"/logs/failed_respose", json=test_data)
    assert response.status_code == 404

# Subscribe to websocket
def test_websocket_connect():
    with client.websocket_connect(
        f"/logs/{g_session_id}/ws"
    ) as websocket:
        assert websocket is not None

# Recive log
def test_websocket_receive():
    with client.websocket_connect(
        f"/logs/{g_session_id}/ws"
    ) as websocket:
        # Post log entery
        test_data = {
            "target_time": None,
            "client_time": datetime.now(timezone.utc).isoformat(),
            "source": "client",
            "target": "pytest",
            "event": "socket_test",
            "data": {"message": "hello websocket"}
        }
        response = client.post(
            f"/logs/{g_session_id}",
            json=test_data
        )
        assert response.status_code == 201
        # Recive on subscriber
        message = websocket.receive_json()
        assert message["event"] == "socket_test"
        assert message["data"]["message"] == "hello websocket"

def test_websocket_multi_recive():
    with client.websocket_connect(
        f"/logs/{g_session_id}/ws"
    ) as websocket:
        # Post log entery
        for i in range(5):
            response = client.post(
                f"/logs/{g_session_id}",
                json={
                    "target_time": None,
                    "client_time": datetime.now(timezone.utc).isoformat(),
                    "source": "client",
                    "target": "pytest",
                    "event": f"log_{i}",
                    "data": {
                        "value": i
                    }
                }
            )
            assert response.status_code == 201
        # Recive on subscriber
        for i in range(5):
            message = websocket.receive_json()
            assert message["event"] == f"log_{i}"
            assert message["data"]["value"] == i