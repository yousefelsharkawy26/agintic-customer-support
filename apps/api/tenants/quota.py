from __future__ import annotations

from datetime import date
from typing import Any

import structlog
from sqlalchemy import func as sa_func
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.tenants.models_ext import TenantConfig, UsageRecord

logger = structlog.get_logger()


async def get_tenant_config(db: AsyncSession, tenant_id: str) -> TenantConfig | None:
    result = await db.execute(select(TenantConfig).where(TenantConfig.tenant_id == tenant_id))
    return result.scalar_one_or_none()


async def upsert_tenant_config(db: AsyncSession, tenant_id: str, **kwargs: Any) -> TenantConfig:
    existing = await get_tenant_config(db, tenant_id)
    if existing:
        for k, v in kwargs.items():
            if hasattr(existing, k):
                setattr(existing, k, v)
        return existing
    config = TenantConfig(tenant_id=tenant_id, **kwargs)
    db.add(config)
    return config


async def check_quota(db: AsyncSession, tenant_id: str) -> tuple[bool, dict[str, Any]]:
    config = await get_tenant_config(db, tenant_id)
    if not config:
        return True, {"reason": "no_config"}

    today = date.today()
    result = await db.execute(
        select(sa_func.coalesce(sa_func.sum(UsageRecord.request_count), 0)).where(
            UsageRecord.tenant_id == tenant_id, UsageRecord.date == today
        )
    )
    daily_requests = result.scalar() or 0

    result = await db.execute(
        select(sa_func.coalesce(sa_func.sum(UsageRecord.token_count), 0)).where(
            UsageRecord.tenant_id == tenant_id
        )
    )
    monthly_tokens = result.scalar() or 0

    if daily_requests >= config.daily_request_limit:
        return False, {
            "reason": "daily_request_limit_exceeded",
            "limit": config.daily_request_limit,
        }
    if monthly_tokens >= config.monthly_token_limit:
        return False, {
            "reason": "monthly_token_limit_exceeded",
            "limit": config.monthly_token_limit,
        }

    return True, {"daily_requests": daily_requests, "monthly_tokens": monthly_tokens}


async def record_usage(db: AsyncSession, tenant_id: str, tokens: int = 0) -> None:
    today = date.today()
    result = await db.execute(
        select(UsageRecord).where(UsageRecord.tenant_id == tenant_id, UsageRecord.date == today)
    )
    record = result.scalar_one_or_none()
    if record:
        record.request_count += 1
        record.token_count += tokens
    else:
        record = UsageRecord(tenant_id=tenant_id, date=today, request_count=1, token_count=tokens)
        db.add(record)
