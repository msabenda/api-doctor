from enum import StrEnum
from typing import Any

from pydantic import AnyHttpUrl, BaseModel, Field, field_validator


class HttpMethod(StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class ApiRequest(BaseModel):
    method: HttpMethod = HttpMethod.GET
    url: AnyHttpUrl
    query: dict[str, str] = Field(default_factory=dict)
    headers: dict[str, str] = Field(default_factory=dict)
    json_body: Any | None = None
    timeout_seconds: float = Field(default=10, ge=1, le=30)

    @field_validator("url")
    @classmethod
    def reject_url_credentials(cls, url: AnyHttpUrl) -> AnyHttpUrl:
        if url.username or url.password:
            raise ValueError("credentials must not be embedded in the URL")
        return url


class ApiResponse(BaseModel):
    status_code: int = Field(ge=100, le=599)
    headers: dict[str, str]
    body: str
    content_type: str | None = None
    size_bytes: int = Field(ge=0)
    duration_ms: float = Field(ge=0)
