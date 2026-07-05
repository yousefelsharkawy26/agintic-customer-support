import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import structlog
from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from apps.api.agent.router import router as agents_router
from apps.api.auth.router import router as auth_router
from apps.api.conversation.router import router as chat_router
from apps.api.core.config import configure_logging, settings
from apps.api.events.redis_bus import RedisStreamEventBus
from apps.api.events.subscribers import register_subscribers
from apps.api.monitoring.router import router as monitoring_router
from apps.api.prompts.router import router as prompts_router
from apps.api.rag.router import router as rag_router
from apps.api.rate_limiter import RateLimiterMiddleware
from apps.api.tenants.router import router as tenants_router
from apps.api.tools.router import router as tools_router
from apps.api.tools.webhooks import router as tool_webhooks_router
from apps.api.webhooks.router import router as webhooks_router
from apps.api.webhooks.subscriber import register_webhook_subscribers
from apps.api.widget.router import router as widget_router

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    try:
        bus = RedisStreamEventBus(settings.redis_url)
        await register_subscribers(bus)
        await register_webhook_subscribers(bus)
        app.state.event_bus = bus
    except Exception:
        logger.warning("event_bus_unavailable", exc_info=True)
        app.state.event_bus = None
    logger.info("app_starting", app_name=settings.app_name)
    yield
    logger.info("app_stopping")


TAGS_METADATA = [
    {
        "name": "auth",
        "description": (
            "Authentication & API key management. Get JWT tokens or create "
            "API keys for programmatic access."
        ),
    },
    {
        "name": "chat",
        "description": (
            "Core chat endpoint. Send messages, get streaming responses " "with citations."
        ),
    },
    {
        "name": "rag",
        "description": (
            "Document ingestion & retrieval. Upload, list, search "
            "tenant-scoped documents for RAG."
        ),
    },
    {
        "name": "tenants",
        "description": (
            "Tenant configuration & quotas. Manage LLM models, rate limits, " "migration."
        ),
    },
    {
        "name": "monitoring",
        "description": (
            "Alerts, cost tracking, health metrics. View alert rules, firing "
            "alerts, cost per tenant."
        ),
    },
    {
        "name": "mcp",
        "description": (
            "Model Context Protocol servers. Register and manage external " "tool servers."
        ),
    },
    {
        "name": "prompts",
        "description": "Manage prompt templates and versions.",
    },
    {
        "name": "webhooks",
        "description": (
            "Outbound webhook integrations. Configure Slack, Zendesk, "
            "Intercom, HubSpot deliveries with HMAC signing & retries."
        ),
    },
    {
        "name": "agents",
        "description": (
            "Configurable AI Agents. Create, manage, and deploy specialized "
            "agents with their own prompts, models, tools, and knowledge bases."
        ),
    },
]

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
    openapi_tags=TAGS_METADATA,
    description="""
# Customer Support AI API

A multi-tenant AI customer support platform with RAG, webhooks,
and embeddable widgets.

## Authentication

**Bearer JWT** (recommended for servers):
```
Authorization: Bearer <jwt_token>
```
Obtain via `POST /api/v1/auth/token` with an API key.

**API Key** (simple, for scripts):
```
X-API-Key: <api_key>
```
Create via `POST /api/v1/auth/api-keys`.

**Widget (public, no auth)**:
Widget endpoints (`/api/v1/widget/*`) are public for embeddable chat.

## Rate Limiting

Default: 60 req/min per tenant. Headers:
`X-RateLimit-Limit`, `X-RateLimit-Remaining`.

## Error Format

```json
{"error": "error_code", "message": "Human readable description"}
```

## Webhooks

Configure at `/api/v1/webhooks/configs`. Events delivered with
HMAC-SHA256 signature in `X-Signature-256` header. Retries: 3x with
exponential backoff (max 30s).

## Widget Embedding

```html
<script data-tenant-id="your-tenant-id" src="/chat-widget.js"></script>
```
""",
)

app.add_middleware(RateLimiterMiddleware)

app.include_router(agents_router)
app.include_router(chat_router)
app.include_router(auth_router)
app.include_router(rag_router)
app.include_router(tenants_router)
app.include_router(monitoring_router)
app.include_router(tools_router)
app.include_router(prompts_router)
app.include_router(tool_webhooks_router)
app.include_router(webhooks_router)
app.include_router(widget_router)


def custom_openapi() -> dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema  # type: ignore[no-any-return]
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": (
                "JWT token from `POST /api/v1/auth/token`. "
                "Header: `Authorization: Bearer <token>`"
            ),
        },
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": (
                "API key from `POST /api/v1/auth/api-keys`. " "Header: `X-API-Key: <key>`"
            ),
        },
    }
    openapi_schema["security"] = [{"BearerAuth": []}, {"ApiKeyAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema  # type: ignore[no-any-return]


app.openapi = custom_openapi  # type: ignore[method-assign]


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
