import os
import sys

from fastapi.testclient import TestClient

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.server import app

client = TestClient(app)


def test_root():
    resp = client.get("/api/")
    assert resp.status_code == 200
    assert resp.json()["message"] == "Hello World"


def test_status_post_and_get():
    # Post a new status
    post_resp = client.post("/api/status", json={"client_name": "pytest"})
    assert post_resp.status_code == 200
    data = post_resp.json()
    assert data["client_name"] == "pytest"
    # Get status list
    get_resp = client.get("/api/status")
    assert get_resp.status_code == 200
    assert any(s["client_name"] == "pytest" for s in get_resp.json())


def test_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert "status" in resp.json()


def test_ready():
    resp = client.get("/api/ready")
    assert resp.status_code in (200, 503)
