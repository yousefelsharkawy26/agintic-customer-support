import time
from typing import Any

import structlog
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

from apps.api.core.adapters.redis_cache import RedisCacheProvider
from apps.api.core.config import settings

logger = structlog.get_logger()


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Any, max_requests: int = 60, window_seconds: int = 60) -> None:
        super().__init__(app)
        self._cache = RedisCacheProvider(settings.redis_url)
        self._max_requests = max_requests
        self._window = window_seconds

    async def dispatch(self, request: Request, call_next: Any) -> Any:
        tenant_id = request.headers.get("X-Tenant-ID", "default")
        key = f"ratelimit:{tenant_id}:{int(time.time() / self._window)}"
        count = await self._cache.get(key) or 0
        count += 1
        await self._cache.set(key, count, ttl=self._window * 2)

        if count > self._max_requests:
            logger.warning("rate_limit_exceeded", tenant_id=tenant_id)
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(self._max_requests - count)
        return response
