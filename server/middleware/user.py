"""X-User header 中间件"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class UserMiddleware(BaseHTTPMiddleware):
    VALID_USERS = {"sd", "sg"}
    SKIP_PATHS = {"/api/health"}

    async def dispatch(self, request: Request, call_next):
        # 只拦截 API 请求
        if not request.url.path.startswith("/api") or request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        user = request.headers.get("X-User")

        if user not in self.VALID_USERS:
            return Response(
                content='{"detail":"Missing or invalid X-User header"}',
                status_code=401,
                media_type="application/json",
            )

        request.state.user = user
        return await call_next(request)
