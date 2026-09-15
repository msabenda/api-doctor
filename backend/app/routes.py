from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.models import ApiRequest, ApiResponse
from app.transport import ExecutionDisabledError, RequestExecutor, get_request_executor

router = APIRouter(prefix="/api/v1", tags=["requests"])
Executor = Annotated[RequestExecutor, Depends(get_request_executor)]


@router.post("/requests", response_model=ApiResponse)
async def send_request(request: ApiRequest, executor: Executor) -> ApiResponse:
    try:
        return await executor.execute(request)
    except ExecutionDisabledError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Outbound requests are disabled until SSRF protections are enabled.",
        ) from error
