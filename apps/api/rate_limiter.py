import time
from typing import Any

import redis.asyncio as aioredis  # type: ignore[import-untyped]
import structlog
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

from apps.api.core.config import settings

logger = structlog.get_logger()


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, app: Any, max_requests: int | None = None, window_seconds: int | None = None
    ) -> None:
        super().__init__(app)
        self._max_requests = max_requests or settings.rate_limit_max
        self._window = window_seconds or settings.rate_limit_window
        self._redis = aioredis.from_url(
            settings.redis_url,
            decode_responses=True,
            max_connections=10,
            socket_connect_timeout=2,
        )

    async def dispatch(self, request: Request, call_next: Any) -> Any:
        tenant_id = request.headers.get("X-Tenant-ID", "default")
        window_key = int(time.time() / self._window)
        key = f"ratelimit:{tenant_id}:{window_key}"

        try:
            count = await self._redis.incr(key)
            if count == 1:
                await self._redis.expire(key, self._window * 2)
        except Exception:
            count = 1

        if count > self._max_requests:
            logger.warning("rate_limit_exceeded", tenant_id=tenant_id, count=count)
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        response = await call_next(request)
        remaining = max(0, self._max_requests - count)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Limit"] = str(self._max_requests)
        return response
