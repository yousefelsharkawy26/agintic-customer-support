from __future__ import annotations

from typing import Any

import structlog
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import apps.api.conversation.models  # noqa: F401 — register tables
import apps.api.monitoring.models  # noqa: F401
import apps.api.prompts.models  # noqa: F401
import apps.api.rag.models  # noqa: F401
import apps.api.tenants.models_ext  # noqa: F401
import apps.api.tools.models  # noqa: F401
import apps.api.widget.models  # noqa: F401
import apps.api.widget.models_ext  # noqa: F401
from apps.api.auth.deps import get_current_tenant, verify_tenant_access
from apps.api.core.database import engine, get_db
from apps.api.tenants.models import Base, Tenant
from apps.api.tenants.quota import (
    check_quota,
    get_tenant_config,
    upsert_tenant_config,
)

logger = structlog.get_logger()

router = APIRouter(
    prefix="/api/v1/tenants", tags=["tenants"], dependencies=[Depends(get_current_tenant)]
)


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


@router.get("/{tenant_id}/config")
async def get_config(
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> TenantConfigResponse:
    verify_tenant_access(tenant_id, tenant)
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


@router.put("/{tenant_id}/config")
async def update_config(
    tenant_id: str,
    body: TenantConfigUpdate,
    db: AsyncSession = Depends(get_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> TenantConfigResponse:
    verify_tenant_access(tenant_id, tenant)
    kwargs = {k: v for k, v in body.model_dump().items() if v is not None}
    config = await upsert_tenant_config(db, tenant_id, **kwargs)
    return TenantConfigResponse(
        tenant_id=config.tenant_id,
        llm_model=config.llm_model,
        embeddings_model=config.embeddings_model,
        daily_request_limit=config.daily_request_limit,
        monthly_token_limit=config.monthly_token_limit,
    )


@router.get("/{tenant_id}/quota")
async def get_quota(
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> dict[str, Any]:
    verify_tenant_access(tenant_id, tenant)
    passed, info = await check_quota(db, tenant_id)
    return {"within_quota": passed, **info}


@router.post("/{tenant_id}/migrate")
async def migrate_tenant(
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> dict[str, Any]:
    verify_tenant_access(tenant_id, tenant)

    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    existing = result.scalar_one_or_none()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

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
