from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from domain.security.context import reset_actor, set_actor


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Authentication Middleware that supports multiple modes:
    - NOAUTH: Allows all requests and sets actor to 'anonymous'
    - API_KEY: Validates against a configured API key
    - PROXY_HEADER: Trusts a specific HTTP header for attribution
    """

    def __init__(
        self,
        app,
        auth_mode: str = "NOAUTH",
        api_key: str | None = None,
        proxy_header: str = "x-synarch-user",
        exclude_paths: list[str] | None = None
    ):
        super().__init__(app)
        self.auth_mode = auth_mode.upper()
        self.api_key = api_key
        self.proxy_header = proxy_header.lower()
        self.exclude_paths = exclude_paths or ["/health", "/docs", "/openapi.json"]

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Bypass auth for excluded paths
        if any(request.url.path.startswith(p) for p in self.exclude_paths):
            return await call_next(request)

        actor = None

        if self.auth_mode == "NOAUTH":
            actor = "anonymous"

        elif self.auth_mode == "API_KEY":
            auth_header = request.headers.get("Authorization")
            api_key_header = request.headers.get("X-API-Key")

            # Extract Bearer token
            if auth_header and auth_header.startswith("Bearer "):
                provided_key = auth_header.split(" ")[1]
            else:
                provided_key = api_key_header

            if not self.api_key or provided_key != self.api_key:
                return Response(content="Unauthorized: Invalid API Key", status_code=401)

            # Optionally extract user if passed in custom header alongside API Key
            actor = request.headers.get("x-synarch-user", "api-user")

        elif self.auth_mode == "PROXY_HEADER":
            # Trust the proxy header entirely
            actor = request.headers.get(self.proxy_header)
            if not actor:
                return Response(
                    content=f"Unauthorized: Missing proxy header '{self.proxy_header}'",
                    status_code=401
                )

        else:
            return Response(content="Internal Server Error: Unknown Auth Mode", status_code=500)

        # Set the actor in the ContextVar for this request
        token = set_actor(actor)

        try:
            response = await call_next(request)
            return response
        finally:
            reset_actor(token)
