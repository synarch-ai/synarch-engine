"""API-key authentication dependency (SYN-015)."""
import hmac

from fastapi import Header, Request

from api.middleware.errors import SynarchError


def _extract_key(authorization: str | None, x_api_key: str | None) -> str | None:
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return x_api_key


def make_api_key_dependency(api_key: str | None):
    """Return a FastAPI dependency enforcing ``api_key`` when one is configured.

    With no key configured the dependency is a no-op; the server then relies on
    its loopback-only default bind (see ``resolve_bind``).
    """

    async def require_api_key(
        request: Request,
        authorization: str | None = Header(default=None),
        x_api_key: str | None = Header(default=None),
    ) -> None:
        if not api_key or request.method == "OPTIONS":
            return
        provided = _extract_key(authorization, x_api_key)
        if not provided or not hmac.compare_digest(provided.encode(), api_key.encode()):
            raise SynarchError(
                "UNAUTHORIZED",
                "Missing or invalid API key.",
                status_code=401,
            )

    return require_api_key


LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


def resolve_bind(host: str, api_key: str | None) -> str:
    """Refuse to bind a non-loopback interface without an API key."""
    if host not in LOOPBACK_HOSTS and not api_key:
        raise RuntimeError(
            f"Refusing to bind {host}: set API_KEY (settings.api_key) before exposing the API."
        )
    return host
