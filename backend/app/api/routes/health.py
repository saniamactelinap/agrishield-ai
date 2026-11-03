from fastapi import APIRouter, status
from pydantic import BaseModel
from app.core.config import settings

router = APIRouter()


class HealthResponse(BaseModel):
    name: str
    status: str
    version: str


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Application Health Check",
    description="Returns the current operational status, name, and version of the API.",
)
async def get_health() -> HealthResponse:
    return HealthResponse(
        name=settings.PROJECT_NAME,
        status="healthy",
        version=settings.VERSION,
    )
