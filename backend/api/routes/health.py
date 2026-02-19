"""Health check endpoint."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check. Enhanced version will check all dependencies."""
    return {
        "status": "ok",
        "service": "synarch-backend",
        "version": "0.1.0",
        "dependencies": {
            "postgresql": {"status": "pending"},
            "nats": {"status": "pending"},
            "qdrant": {"status": "pending"},
            "ollama": {"status": "pending"},
        },
    }
