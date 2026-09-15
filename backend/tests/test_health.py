from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint() -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "api-doctor"}


def test_openapi_metadata() -> None:
    schema = TestClient(app).get("/openapi.json").json()
    assert schema["info"]["title"] == "API Doctor"
    assert schema["info"]["version"] == "0.1.0"
