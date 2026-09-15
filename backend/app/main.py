from fastapi import FastAPI
from pydantic import BaseModel

from app.routes import router


class HealthResponse(BaseModel):
    status: str
    service: str


app = FastAPI(
    title="API Doctor",
    description="Diagnose API failures and explain secure fixes.",
    version="0.1.0",
)


app.include_router(router)


@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health() -> HealthResponse:
    return HealthResponse(status="ok", service="api-doctor")
