from __future__ import annotations

import hashlib
import hmac
import json
import time
import uuid
from datetime import UTC, datetime
from typing import Any

import httpx
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.webhooks.models import WebhookConfig, WebhookDelivery

logger = structlog.get_logger()


SUPPORTED_PROVIDERS = {
    "slack",
    "zendesk",
    "intercom",
    "hubspot",
}

SUPPORTED_EVENTS = {
    "conversation.created",
    "conversation.assigned",
    "conversation.resolved",
    "conversation.message_received",
    "ticket.created",
    "ticket.updated",
    "ticket.resolved",
    "feedback.received",
    "agent.status_changed",
    "contact.created",
}

PROVIDER_EVENTS = {
    "slack": ["conversation.created", "conversation.assigned", "feedback.received"],
    "zendesk": ["ticket.created", "ticket.updated", "ticket.resolved"],
    "intercom": ["conversation.created", "conversation.message_received"],
    "hubspot": ["ticket.created", "ticket.updated", "contact.created"],
}


def sign_payload(payload: str, secret: str) -> str:
    return hmac.new(
        secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


async def list_active_configs(
    db: AsyncSession, tenant_id: str | None = None, event_type: str | None = None
) -> list[WebhookConfig]:
    query = select(WebhookConfig).where(WebhookConfig.is_active.is_(True))
    if tenant_id:
        query = query.where(WebhookConfig.tenant_id == tenant_id)
    if event_type:
        query = query.where(WebhookConfig.events.contains(event_type))
    result = await db.execute(query)
    return list(result.scalars().all())


async def deliver(
    config: WebhookConfig,
    event_type: str,
    payload: dict[str, Any],
    db: AsyncSession | None = None,
) -> WebhookDelivery:
    delivery_id = str(uuid.uuid4())
    delivery = WebhookDelivery(
        id=delivery_id,
        config_id=config.id,
        tenant_id=config.tenant_id,
        event_type=event_type,
        request_body=json.dumps(payload),
        status="pending",
    )

    serialized = json.dumps(payload, default=str)
    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "User-Agent": "CustomerSupport-Webhook/1.0",
        "X-Webhook-ID": delivery_id,
        "X-Event-Type": event_type,
    }

    if config.secret:
        signature = sign_payload(serialized, config.secret)
        headers["X-Signature-256"] = signature

    started_at = time.monotonic()
    attempt = 1
    max_attempts = config.retry_count
    last_error: str | None = None
    status_code = 0

    async with httpx.AsyncClient(timeout=httpx.Timeout(config.timeout_ms / 1000)) as client:
        for attempt in range(1, max_attempts + 1):
            try:
                response = await client.post(
                    config.url,
                    content=serialized,
                    headers=headers,
                )
                status_code = response.status_code
                delivery.response_code = status_code
                delivery.response_body = response.text[:5000]

                if status_code < 500:
                    delivery.status = "delivered"
                    delivery.error = None
                    break

                last_error = f"HTTP {status_code}: {response.text[:200]}"

            except httpx.TimeoutException:
                last_error = "timeout"
            except httpx.RequestError as e:
                last_error = str(e)

            logger.warning(
                "webhook_retry",
                config_id=config.id,
                attempt=attempt,
                error=last_error,
            )

            if attempt < max_attempts:
                wait = min(2**attempt, 30)
                delivery.attempt = attempt
                if db:
                    db.add(delivery)
                    await db.commit()
                await _sleep(wait)

        if not delivery.status or delivery.status == "pending":
            delivery.status = "failed"
            delivery.error = last_error
            delivery.response_code = status_code

    delivery.duration_ms = int((time.monotonic() - started_at) * 1000)
    delivery.attempt = attempt

    if db:
        db.add(delivery)
        await db.commit()

    logger.info(
        "webhook_delivery_complete",
        config_id=config.id,
        event_type=event_type,
        status=delivery.status,
        duration_ms=delivery.duration_ms,
    )

    return delivery


async def _sleep(seconds: float) -> None:
    import asyncio

    await asyncio.sleep(seconds)


async def fire_event(
    event_type: str,
    tenant_id: str,
    data: dict[str, Any],
    db: AsyncSession,
) -> list[WebhookDelivery]:
    configs = await list_active_configs(db, tenant_id=tenant_id, event_type=event_type)
    deliveries: list[WebhookDelivery] = []
    for config in configs:
        provider_payload = _format_for_provider(config.provider, event_type, data)
        delivery = await deliver(config, event_type, provider_payload, db)
        deliveries.append(delivery)
    return deliveries


def _format_for_provider(provider: str, event_type: str, data: dict[str, Any]) -> dict[str, Any]:
    match provider:
        case "slack":
            return _format_slack(event_type, data)
        case "zendesk":
            return _format_zendesk(event_type, data)
        case "intercom":
            return _format_intercom(event_type, data)
        case "hubspot":
            return _format_hubspot(event_type, data)
        case _:
            return data


def _format_slack(event_type: str, data: dict[str, Any]) -> dict[str, Any]:
    event_names = {
        "conversation.created": "New Conversation",
        "conversation.assigned": "Conversation Assigned",
        "feedback.received": "Feedback Received",
    }
    title = event_names.get(event_type, event_type)

    return {
        "text": f"*{title}*",
        "attachments": [
            {
                "color": _slack_color(event_type),
                "fields": [
                    {
                        "title": k.replace("_", " ").title(),
                        "value": str(v),
                        "short": len(str(v)) < 50,
                    }
                    for k, v in data.items()
                ],
                "ts": datetime.now(UTC).timestamp(),
            }
        ],
    }


def _slack_color(event_type: str) -> str:
    if "resolved" in event_type:
        return "good"
    if "created" in event_type:
        return "#36a64f"
    if "feedback" in event_type:
        return "#daa038"
    return "#3b82f6"


def _format_zendesk(_event_type: str, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "ticket": {
            "subject": data.get("subject", f"Support: {data.get('conversation_id', '')}"),
            "description": data.get("message", data.get("summary", "")),
            "priority": data.get("priority", "normal"),
            "tags": data.get("tags", ["api"]),
            "external_id": data.get("conversation_id"),
        }
    }


def _format_intercom(event_type: str, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "event_name": event_type,
        "user_id": data.get("user_id"),
        "conversation_id": data.get("conversation_id"),
        "metadata": {
            "source": "customer_support_api",
            "summary": data.get("summary", data.get("message", "")),
            **{
                k: v
                for k, v in data.items()
                if k not in ("user_id", "conversation_id", "message", "summary")
            },
        },
    }


def _format_hubspot(event_type: str, data: dict[str, Any]) -> dict[str, Any]:
    properties = {
        "customer_support_tier": data.get("tier", "standard"),
        "last_contacted": datetime.now(UTC).isoformat(),
        "notes": data.get("summary", data.get("message", "")),
    }
    return {
        "properties": [{"property": k, "value": v} for k, v in properties.items()],
        "event_type": event_type,
    }
