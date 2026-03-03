"""Error handling middleware — consistent error envelope (FR-14)."""
import logging
from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class SynarchError(Exception):
    """Base error with code and HTTP status."""
    def __init__(self, code: str, message: str, status_code: int = 400, details: dict | None = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class MissionNotFoundError(SynarchError):
    def __init__(self, mission_id: str):
        super().__init__("MISSION_NOT_FOUND", f"Mission '{mission_id}' not found.", 404)


class MissionNotRunningError(SynarchError):
    def __init__(self, mission_id: str):
        super().__init__("MISSION_NOT_RUNNING", f"Mission '{mission_id}' is not running.", 409)


class ApprovalNotFoundError(SynarchError):
    def __init__(self, approval_id: str):
        super().__init__("APPROVAL_NOT_FOUND", f"Approval '{approval_id}' not found.", 404)


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", str(uuid4()))


async def synarch_error_handler(request: Request, exc: SynarchError) -> JSONResponse:
    """Convert SynarchError to standard error envelope."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
                "request_id": _request_id(request),
            }
        },
    )


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unhandled exceptions."""
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An internal error occurred.",
                "details": {},
                "request_id": _request_id(request),
            }
        },
    )
