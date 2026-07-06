from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_error_handler_returns_json():
    resp = client.get("/nonexistent-route")
    # Should either 404 or 500, but always JSON
    assert resp.status_code in (404, 500)
    assert "detail" in resp.json()
