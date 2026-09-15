from typing import Protocol

from app.models import ApiRequest, ApiResponse


class RequestExecutor(Protocol):
    async def execute(self, request: ApiRequest) -> ApiResponse: ...


class ExecutionDisabledError(RuntimeError):
    """Raised while outbound networking is disabled pending SSRF controls."""


class DisabledRequestExecutor:
    async def execute(self, request: ApiRequest) -> ApiResponse:
        del request
        raise ExecutionDisabledError


def get_request_executor() -> RequestExecutor:
    return DisabledRequestExecutor()
