from __future__ import annotations

from datetime import datetime
from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.agent.models import AgentModel
from apps.api.auth.deps import get_current_tenant, get_tenant_db

logger = structlog.get_logger()

router = APIRouter(
    prefix="/api/v1/agents", tags=["agents"], dependencies=[Depends(get_current_tenant)]
)


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class AgentCreate(BaseModel):
    name: str
    description: str = ""
    model: str = "gpt-4o"
    status: str = "draft"
    system_prompt: str = ""
    temperature: float = Field(default=0.3, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, ge=256, le=16384)
    enabled_tool_ids: list[str] = []
    knowledge_collection_ids: list[str] = []


class AgentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    model: str | None = None
    status: str | None = None
    system_prompt: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    enabled_tool_ids: list[str] | None = None
    knowledge_collection_ids: list[str] | None = None


class AgentResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    description: str
    model: str
    status: str
    system_prompt: str
    temperature: float
    max_tokens: int
    enabled_tool_ids: list[str]
    knowledge_collection_ids: list[str]
    created_at: str
    updated_at: str


def _agent_to_response(agent: AgentModel) -> dict[str, Any]:
    return {
        "id": agent.id,
        "tenant_id": agent.tenant_id,
        "name": agent.name,
        "description": agent.description,
        "model": agent.model,
        "status": agent.status,
        "system_prompt": agent.system_prompt,
        "temperature": agent.temperature,
        "max_tokens": agent.max_tokens,
        "enabled_tool_ids": agent.enabled_tool_ids or [],
        "knowledge_collection_ids": agent.knowledge_collection_ids or [],
        "created_at": agent.created_at.isoformat()
        if isinstance(agent.created_at, datetime)
        else str(agent.created_at),
        "updated_at": agent.updated_at.isoformat()
        if isinstance(agent.updated_at, datetime)
        else str(agent.updated_at),
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("")
async def list_agents(
    db: AsyncSession = Depends(get_tenant_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> list[dict[str, Any]]:
    """List all agents for the current tenant."""
    tenant_id = tenant["tenant_id"]
    result = await db.execute(
        select(AgentModel)
        .where(AgentModel.tenant_id == tenant_id)
        .order_by(AgentModel.created_at.desc())
    )
    return [_agent_to_response(a) for a in result.scalars().all()]


@router.post("", status_code=201)
async def create_agent(
    body: AgentCreate,
    db: AsyncSession = Depends(get_tenant_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> dict[str, Any]:
    """Create a new agent for the current tenant."""
    tenant_id = tenant["tenant_id"]
    agent = AgentModel(
        tenant_id=tenant_id,
        name=body.name,
        description=body.description,
        model=body.model,
        status=body.status,
        system_prompt=body.system_prompt,
        temperature=body.temperature,
        max_tokens=body.max_tokens,
        enabled_tool_ids=body.enabled_tool_ids,
        knowledge_collection_ids=body.knowledge_collection_ids,
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    logger.info("agent_created", agent_id=agent.id, tenant_id=tenant_id)
    return _agent_to_response(agent)


@router.get("/{agent_id}")
async def get_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_tenant_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> dict[str, Any]:
    """Get a single agent by ID."""
    result = await db.execute(
        select(AgentModel).where(
            AgentModel.id == agent_id,
            AgentModel.tenant_id == tenant["tenant_id"],
        )
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return _agent_to_response(agent)


@router.patch("/{agent_id}")
async def update_agent(
    agent_id: str,
    body: AgentUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> dict[str, Any]:
    """Update an existing agent."""
    result = await db.execute(
        select(AgentModel).where(
            AgentModel.id == agent_id,
            AgentModel.tenant_id == tenant["tenant_id"],
        )
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)

    await db.commit()
    await db.refresh(agent)
    logger.info("agent_updated", agent_id=agent_id)
    return _agent_to_response(agent)


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_tenant_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> dict[str, bool]:
    """Delete an agent (hard delete)."""
    result = await db.execute(
        select(AgentModel).where(
            AgentModel.id == agent_id,
            AgentModel.tenant_id == tenant["tenant_id"],
        )
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    await db.delete(agent)
    await db.commit()
    logger.info("agent_deleted", agent_id=agent_id)
    return {"deleted": True}
