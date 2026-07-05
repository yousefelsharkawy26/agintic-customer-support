from __future__ import annotations

from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.auth.deps import get_current_tenant, get_tenant_db
from apps.api.prompts.models import Prompt
from apps.api.prompts.registry import PromptRegistry

logger = structlog.get_logger()

router = APIRouter(
    prefix="/api/v1/prompts", tags=["prompts"], dependencies=[Depends(get_current_tenant)]
)


class PromptCreate(BaseModel):
    name: str
    template: str


class PromptResponse(BaseModel):
    id: int
    name: str
    version: int
    template: str
    is_active: bool
    created_at: str

    @classmethod
    def from_orm(cls, prompt: Prompt) -> PromptResponse:
        return cls(
            id=prompt.id,
            name=prompt.name,
            version=prompt.version,
            template=prompt.template,
            is_active=prompt.is_active,
            created_at=prompt.created_at.isoformat() if prompt.created_at else "",
        )


@router.get("")
async def list_prompts(
    db: AsyncSession = Depends(get_tenant_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> list[PromptResponse]:
    tenant_id = tenant["tenant_id"]
    from sqlalchemy import select

    # Subquery to get max version for each name
    result = await db.execute(
        select(Prompt)
        .where(Prompt.tenant_id == tenant_id, Prompt.is_active.is_(True))
        .order_by(Prompt.name, Prompt.version.desc())
    )
    prompts = result.scalars().all()

    # Filter to only get the latest version of each prompt
    latest_prompts = {}
    for p in prompts:
        if p.name not in latest_prompts:
            latest_prompts[p.name] = p

    return [PromptResponse.from_orm(p) for p in latest_prompts.values()]


@router.post("")
async def create_prompt_version(
    body: PromptCreate,
    db: AsyncSession = Depends(get_tenant_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> PromptResponse:
    tenant_id = tenant["tenant_id"]
    registry = PromptRegistry()
    prompt = await registry.create_prompt_version(
        db=db, name=body.name, template=body.template, tenant_id=tenant_id
    )
    return PromptResponse.from_orm(prompt)


@router.get("/{name}")
async def get_prompt(
    name: str,
    db: AsyncSession = Depends(get_tenant_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> PromptResponse:
    tenant_id = tenant["tenant_id"]
    registry = PromptRegistry()
    prompt = await registry.get_prompt(db=db, name=name, tenant_id=tenant_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return PromptResponse.from_orm(prompt)


@router.post("/{name}/rollback")
async def rollback_prompt(
    name: str,
    version: int,
    db: AsyncSession = Depends(get_tenant_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> PromptResponse:
    tenant_id = tenant["tenant_id"]
    registry = PromptRegistry()
    prompt = await registry.rollback(db=db, name=name, version=version, tenant_id=tenant_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt or version not found")
    return PromptResponse.from_orm(prompt)
