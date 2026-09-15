import json
from enum import StrEnum

from pydantic import AnyHttpUrl, BaseModel, Field


class Severity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class Finding(BaseModel):
    code: str
    severity: Severity
    title: str
    explanation: str
    recommendation: str


class AnalysisInput(BaseModel):
    request_url: AnyHttpUrl
    status_code: int = Field(ge=100, le=599)
    headers: dict[str, str] = Field(default_factory=dict)
    body: str = ""


class AnalysisReport(BaseModel):
    findings: list[Finding]
    rate_limit_detected: bool


def _finding(
    code: str, severity: Severity, title: str, explanation: str, recommendation: str
) -> Finding:
    return Finding(
        code=code,
        severity=severity,
        title=title,
        explanation=explanation,
        recommendation=recommendation,
    )


def _status_finding(status: int) -> Finding:
    if status == 401:
        return _finding(
            "auth.unauthenticated",
            Severity.ERROR,
            "Authentication failed",
            "The server could not validate the supplied credentials.",
            "Check the authentication scheme, token validity, audience, issuer, and clock skew.",
        )
    if status == 403:
        return _finding(
            "auth.forbidden",
            Severity.ERROR,
            "Request forbidden",
            "Credentials may be valid but lack permission for this operation.",
            "Verify scopes, roles, resource ownership, and authorization policy.",
        )
    if status == 429:
        return _finding(
            "rate_limit.exceeded",
            Severity.WARNING,
            "Rate limit exceeded",
            "The server is throttling requests.",
            "Honor Retry-After and use bounded exponential backoff with jitter.",
        )
    if status >= 500:
        return _finding(
            "server.error",
            Severity.ERROR,
            "Server-side failure",
            "The API failed while processing a validly delivered request.",
            "Capture the request ID, retry only idempotent operations, and inspect server logs.",
        )
    if status >= 400:
        return _finding(
            "client.error",
            Severity.ERROR,
            "Client request rejected",
            "The API rejected the request syntax, state, or target resource.",
            "Review the response body and compare the request with the OpenAPI contract.",
        )
    if status >= 300:
        return _finding(
            "http.redirect",
            Severity.INFO,
            "Redirect response",
            "The requested resource is available at another location.",
            "Inspect and validate the Location target before following it.",
        )
    return _finding(
        "http.success",
        Severity.INFO,
        "Request succeeded",
        "The API returned a successful response.",
        "Confirm that the response body still matches the expected contract.",
    )


def analyze_response(data: AnalysisInput) -> AnalysisReport:
    headers = {name.lower(): value.strip() for name, value in data.headers.items()}
    findings = [_status_finding(data.status_code)]

    content_type = headers.get("content-type", "")
    if not content_type:
        findings.append(
            _finding(
                "headers.content_type_missing",
                Severity.WARNING,
                "Content-Type is missing",
                "Clients cannot reliably determine how to parse the response.",
                "Return an accurate Content-Type header for every non-empty response.",
            )
        )
    elif "application/json" in content_type.lower() and data.body:
        try:
            json.loads(data.body)
        except json.JSONDecodeError:
            findings.append(
                _finding(
                    "body.invalid_json",
                    Severity.ERROR,
                    "Invalid JSON response",
                    "The response claims to be JSON but its body cannot be parsed.",
                    "Serialize the body with a JSON library and test it against the API schema.",
                )
            )

    if data.request_url.scheme == "https" and "strict-transport-security" not in headers:
        findings.append(
            _finding(
                "headers.hsts_missing",
                Severity.WARNING,
                "HSTS is missing",
                "Clients are not instructed to keep future connections on HTTPS.",
                "Add Strict-Transport-Security after confirming all subdomains support HTTPS.",
            )
        )

    origin = headers.get("access-control-allow-origin")
    credentials = headers.get("access-control-allow-credentials", "").lower()
    if origin == "*" and credentials == "true":
        findings.append(
            _finding(
                "cors.wildcard_credentials",
                Severity.ERROR,
                "Unsafe CORS configuration",
                "Credentialed cross-origin access must not use a wildcard origin.",
                "Allow only explicitly trusted origins and return Vary: Origin.",
            )
        )

    rate_limit_detected = any(
        name in headers
        for name in ("retry-after", "ratelimit-limit", "x-ratelimit-limit", "x-rate-limit-limit")
    )
    if rate_limit_detected:
        findings.append(
            _finding(
                "rate_limit.headers_detected",
                Severity.INFO,
                "Rate-limit metadata detected",
                "The API exposes information clients can use to avoid throttling.",
                "Use these values to pace requests and honor Retry-After when present.",
            )
        )

    return AnalysisReport(findings=findings, rate_limit_detected=rate_limit_detected)
