from typing import Any

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.models import ApiRequest, ApiResponse
from app.transport import get_request_executor


class StubExecutor:
    async def execute(self, request: ApiRequest) -> ApiResponse:
        return ApiResponse(
            status_code=200,
            headers={"content-type": "application/json"},
            body=f'{{"requested_url":"{request.url}"}}',
            content_type="application/json",
            size_bytes=40,
            duration_ms=12.5,
        )


def request_payload(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "method": "POST",
        "url": "https://api.example.com/items",
        "query": {"page": "1"},
        "headers": {"accept": "application/json"},
        "json_body": {"name": "example"},
        "timeout_seconds": 5,
    }
    payload.update(overrides)
    return payload


def test_request_endpoint_uses_typed_executor() -> None:
    app.dependency_overrides[get_request_executor] = StubExecutor
    try:
        response = TestClient(app).post("/api/v1/requests", json=request_payload())
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["status_code"] == 200
    assert "https://api.example.com/items" in response.json()["body"]


def test_live_outbound_execution_is_disabled() -> None:
    response = TestClient(app).post("/api/v1/requests", json=request_payload())

    assert response.status_code == 503
    assert "SSRF protections" in response.json()["detail"]


@pytest.mark.parametrize("url", ["ftp://example.com", "https://user:pass@example.com"])
def test_request_rejects_unsafe_url_forms(url: str) -> None:
    with pytest.raises(ValidationError):
        ApiRequest(**request_payload(url=url))


@pytest.mark.parametrize("timeout", [0.9, 30.1])
def test_request_rejects_timeout_outside_bounds(timeout: float) -> None:
    response = TestClient(app).post(
        "/api/v1/requests", json=request_payload(timeout_seconds=timeout)
    )

    assert response.status_code == 422
