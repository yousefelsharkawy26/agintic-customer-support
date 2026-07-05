from __future__ import annotations

import structlog

from apps.api.core.database import async_session_factory
from apps.api.core.interfaces import Event
from apps.api.events.redis_bus import RedisStreamEventBus
from apps.api.webhooks.engine import fire_event

logger = structlog.get_logger()

WEBHOOK_EVENT_MAP: dict[str, str] = {
    "chat.message_sent": "conversation.message_received",
    "conversation.started": "conversation.created",
    "conversation.assigned": "conversation.assigned",
    "conversation.resolved": "conversation.resolved",
    "ticket.created": "ticket.created",
    "ticket.updated": "ticket.updated",
    "feedback.submitted": "feedback.received",
    "agent.status": "agent.status_changed",
}


async def handle_webhook_event(event: Event) -> None:
    webhook_type = WEBHOOK_EVENT_MAP.get(event.type)
    if not webhook_type:
        return

    tenant_id = event.tenant_id or event.data.get("tenant_id", "")
    if not tenant_id:
        logger.warning("webhook_event_missing_tenant", event_type=event.type)
        return

    from apps.api.core.rls import bind_session_to_tenant

    try:
        async with async_session_factory() as db:
            bind_session_to_tenant(db, tenant_id)
            await fire_event(
                event_type=webhook_type,
                tenant_id=tenant_id,
                data=event.data,
                db=db,
            )
            if db.in_transaction():
                await db.commit()
    except Exception:
        logger.exception(
            "webhook_subscriber_error",
            event_type=event.type,
            tenant_id=tenant_id,
        )


async def register_webhook_subscribers(bus: RedisStreamEventBus) -> None:
    for internal_event in WEBHOOK_EVENT_MAP:
        await bus.subscribe(internal_event, handle_webhook_event)

    logger.info("webhook_subscribers_registered", event_count=len(WEBHOOK_EVENT_MAP))
