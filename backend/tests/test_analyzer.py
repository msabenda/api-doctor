import pytest

from app.analyzer import AnalysisInput, Severity, analyze_response


def analyze(status: int, headers: dict[str, str] | None = None, body: str = ""):
    return analyze_response(
        AnalysisInput(
            request_url="https://api.example.com/resource",
            status_code=status,
            headers=headers or {},
            body=body,
        )
    )


@pytest.mark.parametrize(
    ("status", "code", "severity"),
    [
        (200, "http.success", Severity.INFO),
        (302, "http.redirect", Severity.INFO),
        (400, "client.error", Severity.ERROR),
        (401, "auth.unauthenticated", Severity.ERROR),
        (403, "auth.forbidden", Severity.ERROR),
        (429, "rate_limit.exceeded", Severity.WARNING),
        (503, "server.error", Severity.ERROR),
    ],
)
def test_explains_status_codes(status: int, code: str, severity: Severity) -> None:
    report = analyze(status, {"Content-Type": "application/json"}, "{}")

    assert report.findings[0].code == code
    assert report.findings[0].severity == severity


def test_reports_missing_content_type_and_hsts() -> None:
    codes = {finding.code for finding in analyze(200).findings}

    assert "headers.content_type_missing" in codes
    assert "headers.hsts_missing" in codes


def test_reports_invalid_json_case_insensitively() -> None:
    report = analyze(
        200,
        {
            "CONTENT-TYPE": "Application/JSON; charset=utf-8",
            "Strict-Transport-Security": "max-age=1",
        },
        "{broken",
    )

    assert [finding.code for finding in report.findings] == ["http.success", "body.invalid_json"]


def test_accepts_valid_json_without_json_finding() -> None:
    report = analyze(
        200,
        {"content-type": "application/json", "strict-transport-security": "max-age=1"},
        '{"ok":true}',
    )

    assert [finding.code for finding in report.findings] == ["http.success"]


def test_reports_unsafe_credentialed_wildcard_cors() -> None:
    report = analyze(
        200,
        {
            "content-type": "text/plain",
            "strict-transport-security": "max-age=1",
            "access-control-allow-origin": "*",
            "access-control-allow-credentials": "TRUE",
        },
    )

    assert "cors.wildcard_credentials" in {finding.code for finding in report.findings}


def test_detects_standard_and_legacy_rate_limit_headers() -> None:
    for name in ("Retry-After", "RateLimit-Limit", "X-RateLimit-Limit", "X-Rate-Limit-Limit"):
        report = analyze(
            200,
            {"content-type": "text/plain", "strict-transport-security": "max-age=1", name: "10"},
        )
        assert report.rate_limit_detected is True
        assert report.findings[-1].code == "rate_limit.headers_detected"


def test_http_does_not_require_hsts() -> None:
    report = analyze_response(
        AnalysisInput(
            request_url="http://api.example.com",
            status_code=204,
            headers={"content-type": "text/plain"},
        )
    )

    assert [finding.code for finding in report.findings] == ["http.success"]


def test_analysis_endpoint() -> None:
    from fastapi.testclient import TestClient

    from app.main import app

    response = TestClient(app).post(
        "/api/v1/analyze",
        json={
            "request_url": "https://api.example.com",
            "status_code": 401,
            "headers": {"content-type": "application/json"},
            "body": "{}",
        },
    )

    assert response.status_code == 200
    assert response.json()["findings"][0]["code"] == "auth.unauthenticated"
