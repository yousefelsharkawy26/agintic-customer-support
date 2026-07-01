from __future__ import annotations

from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.auth.deps import get_current_tenant, verify_tenant_access
from apps.api.core.database import get_db
from apps.api.monitoring.alerts import evaluate_alerts
from apps.api.monitoring.cost_tracker import get_tenant_costs, record_usage
from apps.api.monitoring.models import AlertEvent, AlertRule

logger = structlog.get_logger()

router = APIRouter(
    prefix="/api/v1/monitoring", tags=["monitoring"], dependencies=[Depends(get_current_tenant)]
)


class AlertRuleCreate(BaseModel):
    name: str
    metric: str
    operator: str
    threshold: float
    window_minutes: int = 5


class UsageRecordRequest(BaseModel):
    tenant_id: str
    input_tokens: int
    output_tokens: int
    model: str = "gpt-4o"


@router.post("/alerts/rules")
async def create_alert_rule(
    tenant_id: str,
    body: AlertRuleCreate,
    db: AsyncSession = Depends(get_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> dict[str, Any]:
    verify_tenant_access(tenant_id, tenant)
    if body.operator not in ("gt", "gte", "lt", "lte"):
        raise HTTPException(status_code=400, detail="Invalid operator")
    rule = AlertRule(
        tenant_id=tenant_id,
        name=body.name,
        metric=body.metric,
        operator=body.operator,
        threshold=body.threshold,
        window_minutes=body.window_minutes,
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return {"id": rule.id, "name": rule.name, "metric": rule.metric}


@router.get("/alerts/rules")
async def list_alert_rules(
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> list[dict[str, Any]]:
    verify_tenant_access(tenant_id, tenant)
    result = await db.execute(select(AlertRule).where(AlertRule.tenant_id == tenant_id))
    return [
        {
            "id": r.id,
            "name": r.name,
            "metric": r.metric,
            "operator": r.operator,
            "threshold": r.threshold,
            "window_minutes": r.window_minutes,
            "enabled": r.enabled,
        }
        for r in result.scalars().all()
    ]


@router.post("/alerts/evaluate")
async def evaluate(
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> dict[str, Any]:
    verify_tenant_access(tenant_id, tenant)
    fired = await evaluate_alerts(db, tenant_id)
    return {"fired": len(fired), "alerts": [e.message for e in fired]}


@router.get("/alerts/events")
async def list_alert_events(
    tenant_id: str,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> list[dict[str, Any]]:
    verify_tenant_access(tenant_id, tenant)
    result = await db.execute(
        select(AlertEvent)
        .where(AlertEvent.tenant_id == tenant_id)
        .order_by(AlertEvent.created_at.desc())
        .limit(limit)
    )
    return [
        {
            "id": e.id,
            "rule_name": e.rule_name,
            "metric": e.metric,
            "value": e.value,
            "threshold": e.threshold,
            "message": e.message,
            "resolved": e.resolved,
            "created_at": e.created_at.isoformat(),
        }
        for e in result.scalars().all()
    ]


@router.post("/usage/record")
async def record_usage_endpoint(
    body: UsageRecordRequest,
    db: AsyncSession = Depends(get_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> dict[str, Any]:
    verify_tenant_access(body.tenant_id, tenant)
    record = await record_usage(
        db, body.tenant_id, body.input_tokens, body.output_tokens, body.model
    )
    return {
        "tenant_id": record.tenant_id,
        "date": record.date,
        "cost_usd": record.cost_usd,
        "model": record.model,
    }


@router.get("/costs")
async def get_costs(
    tenant_id: str,
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> dict[str, Any]:
    verify_tenant_access(tenant_id, tenant)
    records = await get_tenant_costs(db, tenant_id, start_date, end_date)
    total_cost = sum(r["cost_usd"] for r in records)
    return {"records": records, "total_cost": round(total_cost, 4)}


@router.get("/costs/summary")
async def cost_summary(
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> dict[str, Any]:
    verify_tenant_access(tenant_id, tenant)
    records = await get_tenant_costs(db, tenant_id)
    total_cost = sum(r["cost_usd"] for r in records)
    total_requests = sum(r["requests"] for r in records)
    return {
        "tenant_id": tenant_id,
        "total_cost": round(total_cost, 4),
        "total_requests": total_requests,
        "daily_avg_cost": round(total_cost / max(len(records), 1), 4),
    }
