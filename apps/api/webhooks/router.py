from __future__ import annotations

import json
from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import apps.api.webhooks.models  # noqa: F401
from apps.api.auth.deps import get_current_tenant
from apps.api.core.database import get_db
from apps.api.webhooks.engine import (
    PROVIDER_EVENTS,
    SUPPORTED_EVENTS,
    SUPPORTED_PROVIDERS,
    fire_event,
)
from apps.api.webhooks.models import WebhookConfig, WebhookDelivery
from apps.api.webhooks.schemas import (
    WebhookConfigCreate,
    WebhookConfigResponse,
    WebhookConfigUpdate,
    WebhookDeliveryResponse,
)

logger = structlog.get_logger()

router = APIRouter(
    prefix="/api/v1/webhooks",
    tags=["webhooks"],
    dependencies=[Depends(get_current_tenant)],
)

PROVIDER_INFO = {
    "slack": {
        "label": "Slack",
        "available_events": PROVIDER_EVENTS["slack"],
        "docs_url": "https://api.slack.com/messaging/webhooks",
    },
    "zendesk": {
        "label": "Zendesk",
        "available_events": PROVIDER_EVENTS["zendesk"],
        "docs_url": "https://developer.zendesk.com/api-reference",
    },
    "intercom": {
        "label": "Intercom",
        "available_events": PROVIDER_EVENTS["intercom"],
        "docs_url": "https://developers.intercom.com/docs",
    },
    "hubspot": {
        "label": "HubSpot",
        "available_events": PROVIDER_EVENTS["hubspot"],
        "docs_url": "https://developers.hubspot.com/docs",
    },
}


@router.get("/providers")
async def list_providers() -> list[dict[str, Any]]:
    return [
        {
            "provider": p,
            **info,
        }
        for p, info in PROVIDER_INFO.items()
    ]


@router.get("/events")
async def list_events() -> list[dict[str, str]]:
    return [{"event": e, "description": _event_description(e)} for e in sorted(SUPPORTED_EVENTS)]


@router.post("/configs", status_code=201)
async def create_webhook_config(
    body: WebhookConfigCreate,
    db: AsyncSession = Depends(get_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> WebhookConfigResponse:
    if body.provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported provider '{body.provider}'. "
                f"Choose from: {', '.join(sorted(SUPPORTED_PROVIDERS))}"
            ),
        )

    valid_events = PROVIDER_EVENTS[body.provider]
    for ev in body.events:
        if ev not in SUPPORTED_EVENTS:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown event '{ev}'. See GET /api/v1/webhooks/events",
            )
        if ev not in valid_events:
            raise HTTPException(
                status_code=400,
                detail=f"Event '{ev}' is not supported by {body.provider}. Valid: {valid_events}",
            )

    config = WebhookConfig(
        tenant_id=tenant["tenant_id"],
        provider=body.provider,
        label=body.label,
        url=body.url,
        secret=body.secret,
        events=json.dumps(body.events),
        retry_count=body.retry_count,
        timeout_ms=body.timeout_ms,
    )
    db.add(config)
    await db.flush()
    logger.info(
        "webhook_config_created",
        provider=body.provider,
        tenant_id=config.tenant_id,
        config_id=config.id,
    )
    return _config_to_response(config)


@router.get("/configs")
async def list_webhook_configs(
    provider: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> list[WebhookConfigResponse]:
    query = select(WebhookConfig).where(WebhookConfig.tenant_id == tenant["tenant_id"])
    if provider:
        query = query.where(WebhookConfig.provider == provider)
    result = await db.execute(query)
    return [_config_to_response(c) for c in result.scalars().all()]


@router.get("/configs/{config_id}")
async def get_webhook_config(
    config_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> WebhookConfigResponse:
    config = await _get_config(db, config_id, tenant["tenant_id"])
    return _config_to_response(config)


@router.put("/configs/{config_id}")
async def update_webhook_config(
    config_id: str,
    body: WebhookConfigUpdate,
    db: AsyncSession = Depends(get_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> WebhookConfigResponse:
    config = await _get_config(db, config_id, tenant["tenant_id"])

    if body.label is not None:
        config.label = body.label
    if body.url is not None:
        config.url = body.url
    if body.secret is not None:
        config.secret = body.secret
    if body.events is not None:
        config.events = json.dumps(body.events)
    if body.is_active is not None:
        config.is_active = body.is_active
    if body.retry_count is not None:
        config.retry_count = body.retry_count
    if body.timeout_ms is not None:
        config.timeout_ms = body.timeout_ms

    logger.info("webhook_config_updated", config_id=config.id)
    return _config_to_response(config)


@router.delete("/configs/{config_id}")
async def delete_webhook_config(
    config_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> dict[str, bool]:
    config = await _get_config(db, config_id, tenant["tenant_id"])
    await db.delete(config)
    logger.info("webhook_config_deleted", config_id=config_id)
    return {"deleted": True}


@router.get("/deliveries")
async def list_deliveries(
    config_id: str | None = Query(None),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> list[WebhookDeliveryResponse]:
    query = (
        select(WebhookDelivery)
        .where(WebhookDelivery.tenant_id == tenant["tenant_id"])
        .order_by(WebhookDelivery.created_at.desc())
        .limit(limit)
    )
    if config_id:
        query = query.where(WebhookDelivery.config_id == config_id)
    result = await db.execute(query)
    return [
        WebhookDeliveryResponse(
            id=d.id,
            config_id=d.config_id,
            event_type=d.event_type,
            status=d.status,
            response_code=d.response_code,
            error=d.error,
            attempt=d.attempt,
            duration_ms=d.duration_ms,
            created_at=d.created_at,
        )
        for d in result.scalars().all()
    ]


@router.post("/test")
async def test_webhook(
    config_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> dict[str, Any]:
    await _get_config(db, config_id, tenant["tenant_id"])
    deliveries = await fire_event(
        event_type="conversation.created",
        tenant_id=tenant["tenant_id"],
        data={
            "conversation_id": "test-conversation",
            "message": "This is a test webhook payload.",
            "tenant_id": tenant["tenant_id"],
        },
        db=db,
    )
    if not deliveries:
        return {"status": "no_deliveries", "detail": "No delivery was attempted."}
    d = deliveries[0]
    return {
        "status": d.status,
        "response_code": d.response_code,
        "duration_ms": d.duration_ms,
        "error": d.error,
    }


async def _get_config(db: AsyncSession, config_id: str, tenant_id: str) -> WebhookConfig:
    result = await db.execute(
        select(WebhookConfig).where(
            WebhookConfig.id == config_id,
            WebhookConfig.tenant_id == tenant_id,
        )
    )
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="Webhook config not found")
    return config


def _config_to_response(config: WebhookConfig) -> WebhookConfigResponse:
    return WebhookConfigResponse(
        id=config.id,
        tenant_id=config.tenant_id,
        provider=config.provider,
        label=config.label,
        url=config.url,
        events=json.loads(config.events) if isinstance(config.events, str) else config.events,
        is_active=config.is_active,
        retry_count=config.retry_count,
        timeout_ms=config.timeout_ms,
        created_at=config.created_at,
        updated_at=config.updated_at,
    )


def _event_description(event: str) -> str:
    descriptions = {
        "conversation.created": "A new conversation has been started",
        "conversation.assigned": "A conversation was assigned to an agent",
        "conversation.resolved": "A conversation was marked as resolved",
        "conversation.message_received": "A new message was received in a conversation",
        "ticket.created": "A new support ticket was created",
        "ticket.updated": "An existing ticket was updated",
        "ticket.resolved": "A ticket was resolved",
        "feedback.received": "Customer feedback was submitted",
        "agent.status_changed": "An agent's status changed (online/offline)",
        "contact.created": "A new contact was created",
    }
    return descriptions.get(event, event)
