from __future__ import annotations

from typing import Any

import structlog
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.database import get_db
from apps.api.tenants.quota import (
    check_quota,
    get_tenant_config,
    upsert_tenant_config,
)

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/tenants", tags=["tenants"])


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
async def get_config(tenant_id: str, db: AsyncSession = Depends(get_db)) -> TenantConfigResponse:
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
    tenant_id: str, body: TenantConfigUpdate, db: AsyncSession = Depends(get_db)
) -> TenantConfigResponse:
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
async def get_quota(tenant_id: str, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    passed, info = await check_quota(db, tenant_id)
    return {"within_quota": passed, **info}
