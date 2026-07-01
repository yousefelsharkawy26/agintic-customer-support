import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from apps.api.auth.router import router as auth_router
from apps.api.conversation.router import router as chat_router
from apps.api.core.config import configure_logging, settings
from apps.api.events.redis_bus import RedisStreamEventBus
from apps.api.events.subscribers import register_subscribers
from apps.api.monitoring.router import router as monitoring_router
from apps.api.rag.router import router as rag_router
from apps.api.rate_limiter import RateLimiterMiddleware
from apps.api.tenants.router import router as tenants_router
from apps.api.tools.router import router as tools_router
from apps.api.tools.webhooks import router as webhooks_router
from apps.api.widget.router import router as widget_router

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    try:
        bus = RedisStreamEventBus(settings.redis_url)
        await register_subscribers(bus)
        app.state.event_bus = bus
    except Exception:
        logger.warning("event_bus_unavailable", exc_info=True)
        app.state.event_bus = None
    logger.info("app_starting", app_name=settings.app_name)
    yield
    logger.info("app_stopping")


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(RateLimiterMiddleware)

app.include_router(chat_router)
app.include_router(auth_router)
app.include_router(rag_router)
app.include_router(tenants_router)
app.include_router(monitoring_router)
app.include_router(tools_router)
app.include_router(webhooks_router)
app.include_router(widget_router)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next: Any) -> Any:
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    with structlog.contextvars.bound_contextvars(request_id=request_id):
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


@app.middleware("http")
async def log_requests(request: Request, call_next: Any) -> Any:
    logger.info(
        "request_started",
        method=request.method,
        path=request.url.path,
        query=str(request.url.query),
    )
    response = await call_next(request)
    logger.info(
        "request_finished",
        status_code=response.status_code,
    )
    return response


@app.exception_handler(Exception)
async def global_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled_error", exc=str(exc))
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error", "message": "An unexpected error occurred."},
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
async def readiness() -> dict[str, str]:
    return {"status": "ready"}
