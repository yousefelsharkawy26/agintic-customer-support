from __future__ import annotations

from typing import Any

import structlog
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.auth.deps import get_current_tenant, get_tenant_db
from apps.api.tenants.models import Tenant
from apps.api.tenants.quota import (
    check_quota,
    get_tenant_config,
    upsert_tenant_config,
)

logger = structlog.get_logger()

router = APIRouter(
    prefix="/api/v1/tenants", tags=["tenants"], dependencies=[Depends(get_current_tenant)]
)


class MonitoringStatsResponse(BaseModel):
    conversations: int
    messages: int
    avg_response_time: float
    deflection_rate: float
    conversations_this_week: int
    messages_this_week: int
    response_time_p95: float
    deflection_rate_change: float


class TenantConfigResponse(BaseModel):
    tenant_id: str
    llm_model: str
    embeddings_model: str
    daily_request_limit: int
    monthly_token_limit: int


class TenantConfigUpdate(BaseModel):
    llm_api_key: str | None = None
    llm_model: str | None = None
    embeddings_model: str | None = None
    daily_request_limit: int | None = None
    monthly_token_limit: int | None = None


@router.get("/monitoring")
async def get_monitoring_data(
    db: AsyncSession = Depends(get_tenant_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> MonitoringStatsResponse:
    # This should query actual monitoring metrics, alerts, etc.
    pass


@router.get("/engagement")
async def get_user_engagement(
    db: AsyncSession = Depends(get_tenant_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
    since: str | None = None,
) -> dict[str, Any]:
    # Returns user behavior analytics
    pass


@router.get("/config")
async def get_config(
    db: AsyncSession = Depends(get_tenant_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> TenantConfigResponse:
    tenant_id = tenant["tenant_id"]
    config = await get_tenant_config(db, tenant_id)
    if not config:
        config = await upsert_tenant_config(db, tenant_id)
    return TenantConfigResponse(
        tenant_id=config.tenant_id,
        llm_model=config.llm_model,
        embeddings_model=config.embeddings_model,
        daily_request_limit=config.daily_request_limit,
        monthly_token_limit=config.monthly_token_limit,
    )


@router.put("/config")
async def update_config(
    body: TenantConfigUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> TenantConfigResponse:
    tenant_id = tenant["tenant_id"]
    kwargs = {k: v for k, v in body.model_dump().items() if v is not None}
    config = await upsert_tenant_config(db, tenant_id, **kwargs)
    return TenantConfigResponse(
        tenant_id=config.tenant_id,
        llm_model=config.llm_model,
        embeddings_model=config.embeddings_model,
        daily_request_limit=config.daily_request_limit,
        monthly_token_limit=config.monthly_token_limit,
    )


@router.get("/quota")
async def get_quota(
    db: AsyncSession = Depends(get_tenant_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> dict[str, Any]:
    tenant_id = tenant["tenant_id"]
    passed, info = await check_quota(db, tenant_id)
    return {"within_quota": passed, **info}


@router.post("/migrate")
async def migrate_tenant(
    db: AsyncSession = Depends(get_tenant_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> dict[str, Any]:
    tenant_id = tenant["tenant_id"]

    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    existing = result.scalar_one_or_none()

    # Tables are strictly managed by Alembic.

    if not existing:
        db.add(Tenant(id=tenant_id, name=tenant_id, slug=tenant_id, api_key="migrated"))
        await db.flush()

    config = await upsert_tenant_config(db, tenant_id)
    await db.commit()

    return {
        "tenant_id": tenant_id,
        "tables_created": True,
        "config_initialized": True,
        "tenant_exists": existing is not None,
        "plan": config.llm_model,
    }
