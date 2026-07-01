from datetime import date
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.monitoring.models import CostRecord

logger = structlog.get_logger()

MODEL_COST_PER_1K_TOKENS = {
    "gpt-4o": {"input": 0.0025, "output": 0.01},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "claude-3-5-sonnet": {"input": 0.003, "output": 0.015},
    "gemini-1.5-pro": {"input": 0.00125, "output": 0.005},
}

DEFAULT_COST = {"input": 0.002, "output": 0.008}


async def record_usage(
    db: AsyncSession,
    tenant_id: str,
    input_tokens: int,
    output_tokens: int,
    model: str = "gpt-4o",
) -> CostRecord:
    today_str = date.today().isoformat()
    rates = MODEL_COST_PER_1K_TOKENS.get(model, DEFAULT_COST)
    cost = (input_tokens / 1000 * rates["input"]) + (output_tokens / 1000 * rates["output"])

    result = await db.execute(
        select(CostRecord).where(
            CostRecord.tenant_id == tenant_id,
            CostRecord.date == today_str,
            CostRecord.model == model,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.request_count += 1
        existing.input_tokens += input_tokens
        existing.output_tokens += output_tokens
        existing.cost_usd = round(existing.cost_usd + cost, 6)
        record = existing
    else:
        record = CostRecord(
            tenant_id=tenant_id,
            date=today_str,
            request_count=1,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=round(cost, 6),
            model=model,
        )
        db.add(record)

    await db.commit()
    await db.refresh(record)
    return record


async def get_tenant_costs(
    db: AsyncSession,
    tenant_id: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[dict[str, Any]]:
    stmt = select(CostRecord).where(CostRecord.tenant_id == tenant_id)
    if start_date:
        stmt = stmt.where(CostRecord.date >= start_date)
    if end_date:
        stmt = stmt.where(CostRecord.date <= end_date)
    stmt = stmt.order_by(CostRecord.date)

    result = await db.execute(stmt)
    records = result.scalars().all()
    return [
        {
            "date": r.date,
            "model": r.model,
            "requests": r.request_count,
            "input_tokens": r.input_tokens,
            "output_tokens": r.output_tokens,
            "cost_usd": round(r.cost_usd, 4),
        }
        for r in records
    ]
