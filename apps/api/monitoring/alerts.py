import structlog
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.monitoring.models import AlertEvent, AlertRule

logger = structlog.get_logger()

METRIC_QUERIES = {
    "error_rate": text("""
        SELECT COUNT(*) FILTER (WHERE is_error = true) * 100.0 / NULLIF(COUNT(*), 0) AS value
        FROM tool_audit_log
        WHERE created_at >= NOW() - :window * INTERVAL '1 minute'
    """),
    "latency_p99": text("""
        SELECT PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY duration_ms) AS value
        FROM tool_audit_log
        WHERE created_at >= NOW() - :window * INTERVAL '1 minute'
    """),
    "token_spike": text("""
        SELECT COALESCE(SUM(token_count), 0) AS value
        FROM messages
        WHERE created_at >= NOW() - :window * INTERVAL '1 minute'
    """),
    "retrieval_null_rate": text("""
        SELECT COUNT(*) FILTER (WHERE token_count IS NULL) * 100.0 / NULLIF(COUNT(*), 0) AS value
        FROM messages
        WHERE role = 'assistant' AND created_at >= NOW() - :window * INTERVAL '1 minute'
    """),
}


async def evaluate_alerts(db: AsyncSession, tenant_id: str) -> list[AlertEvent]:
    result = await db.execute(
        select(AlertRule).where(AlertRule.tenant_id == tenant_id, AlertRule.enabled.is_(True))
    )
    rules = result.scalars().all()
    fired: list[AlertEvent] = []

    for rule in rules:
        query = METRIC_QUERIES.get(rule.metric)
        if query is None:
            logger.warning("unknown_metric", metric=rule.metric)
            continue

        params: dict[str, object] = {"window": rule.window_minutes}
        params["tenant_id"] = tenant_id

        row = await db.execute(query, params)
        value = row.scalar_one_or_none()
        if value is None:
            continue

        triggered = (
            (rule.operator == "gt" and value > rule.threshold)
            or (rule.operator == "gte" and value >= rule.threshold)
            or (rule.operator == "lt" and value < rule.threshold)
            or (rule.operator == "lte" and value <= rule.threshold)
        )

        if triggered:
            event = AlertEvent(
                tenant_id=tenant_id,
                rule_id=rule.id,
                rule_name=rule.name,
                metric=rule.metric,
                value=round(float(value), 2),
                threshold=rule.threshold,
                message=(
                    f"Alert [{rule.name}]: {rule.metric} = {float(value):.2f} "
                    f"(threshold: {rule.operator} {rule.threshold})"
                ),
            )
            db.add(event)
            fired.append(event)
            logger.warning("alert_fired", rule=rule.name, value=float(value))

    if fired:
        await db.commit()

    return fired
