"""
MindOS AI - Health Check Router
"""

from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.config import settings

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Liveness check."""
    return HealthResponse(
        status="ok",
        version="0.1.0",
        services={
            "openai": settings.has_openai,
            "elevenlabs": settings.has_elevenlabs,
            "pinecone": settings.has_pinecone,
        },
    )
