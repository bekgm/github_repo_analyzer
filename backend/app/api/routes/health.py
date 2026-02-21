"""
Health-check route — used by Docker HEALTHCHECK and load balancers.
"""

from fastapi import APIRouter

from app.api.schemas import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse()
