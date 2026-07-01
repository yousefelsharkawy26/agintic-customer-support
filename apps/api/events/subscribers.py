from datetime import UTC, datetime
from typing import Any

import structlog

from apps.api.core.interfaces import Event
from apps.api.events.redis_bus import RedisStreamEventBus

logger = structlog.get_logger()


class AnalyticsSubscriber:
    async def handle(self, event: Event) -> None:
        logger.info("analytics_event", event_type=event.type, data=event.data)


class BillingSubscriber:
    async def track_usage(self, tenant_id: str, model: str, tokens: int) -> None:
        logger.info("billing_usage", tenant_id=tenant_id, model=model, tokens=tokens)


class AuditSubscriber:
    async def log(
        self, action: str, actor: str, resource: str, metadata: dict[str, Any] | None = None
    ) -> None:
        logger.info(
            "audit_log",
            action=action,
            actor=actor,
            resource=resource,
            metadata=metadata,
            timestamp=datetime.now(UTC).isoformat(),
        )


async def register_subscribers(bus: RedisStreamEventBus) -> None:
    analytics = AnalyticsSubscriber()
    bill = BillingSubscriber()
    audit = AuditSubscriber()

    async def on_analytics(event: Event) -> None:
        await analytics.handle(event)

    async def on_billing(event: Event) -> None:
        data = event.data
        await bill.track_usage(
            data.get("tenant_id", "unknown"),
            data.get("model", "unknown"),
            data.get("tokens", 0),
        )

    async def on_audit(event: Event) -> None:
        data = event.data
        await audit.log(
            data.get("action", "unknown"),
            data.get("actor", "system"),
            data.get("resource", "unknown"),
            data.get("metadata"),
        )

    await bus.subscribe("chat.message_sent", on_analytics)
    await bus.subscribe("billing.token_usage", on_billing)
    await bus.subscribe("audit.action", on_audit)
    logger.info("event_subscribers_registered")
