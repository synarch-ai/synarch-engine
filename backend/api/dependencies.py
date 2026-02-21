"""API dependency providers."""

from fastapi import Depends, Request

from api.middleware.errors import SynarchError
from container import Container
from ports.persistence import MissionRepository


def get_container(request: Request) -> Container:
    """Get application container from app state."""
    container = getattr(request.app.state, "container", None)
    if container is None:
        raise SynarchError(
            "CONTAINER_UNAVAILABLE",
            "Application container is not initialized.",
            status_code=503,
        )
    return container


def get_mission_repository(
    container: Container = Depends(get_container),
) -> MissionRepository:
    """Get mission repository adapter from container."""
    if container.mission_repo is None:
        raise SynarchError(
            "MISSION_REPOSITORY_UNAVAILABLE",
            "Mission repository is not initialized.",
            status_code=503,
        )
    return container.mission_repo
