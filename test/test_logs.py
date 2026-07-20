# import pytest
# from fastapi.testclient import TestClient
# from server.main import app

# client = TestClient(app)

# def test_enter_log():
#     # Create session first
#     res = client.post("/sessions", json={"subject_id": "test_subject"}).json()
#     session_id = res["session_id"]
#     log_data = {"message": "test log"}
#     response = client.post(f"/sessions/{session_id}/logs", json=log_data)
#     assert response.status_code == 200 or response.status_code == 201
