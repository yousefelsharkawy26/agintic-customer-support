from __future__ import annotations

from typing import Any

import structlog
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.auth.deps import get_current_tenant, verify_tenant_access
from apps.api.core.database import get_db
from apps.api.tools.models import MCPServer

logger = structlog.get_logger()

router = APIRouter(
    prefix="/api/v1/tools/servers", tags=["mcp"], dependencies=[Depends(get_current_tenant)]
)


class MCPServerCreate(BaseModel):
    tenant_id: str
    name: str
    server_url: str
    api_key: str | None = None
    transport: str = "http"
    timeout_ms: int = 30000


class MCPServerResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    server_url: str
    transport: str
    is_active: bool
    health_status: str
    timeout_ms: int


@router.post("")
async def register_server(
    body: MCPServerCreate,
    db: AsyncSession = Depends(get_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> dict[str, str]:
    verify_tenant_access(body.tenant_id, tenant)
    server = MCPServer(
        tenant_id=body.tenant_id,
        name=body.name,
        server_url=body.server_url,
        api_key=body.api_key,
        transport=body.transport,
        timeout_ms=body.timeout_ms,
    )
    db.add(server)
    logger.info("mcp_server_registered", name=body.name, tenant_id=body.tenant_id)
    return {"id": server.id}


@router.get("")
async def list_servers(
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> list[MCPServerResponse]:
    verify_tenant_access(tenant_id, tenant)
    result = await db.execute(
        select(MCPServer).where(MCPServer.tenant_id == tenant_id, MCPServer.is_active.is_(True))
    )
    return [
        MCPServerResponse(
            id=s.id,
            tenant_id=s.tenant_id,
            name=s.name,
            server_url=s.server_url,
            transport=s.transport,
            is_active=s.is_active,
            health_status=s.health_status,
            timeout_ms=s.timeout_ms,
        )
        for s in result.scalars().all()
    ]


@router.delete("/{server_id}")
async def delete_server(server_id: str, db: AsyncSession = Depends(get_db)) -> dict[str, bool]:
    result = await db.execute(select(MCPServer).where(MCPServer.id == server_id))
    server = result.scalar_one_or_none()
    if server:
        server.is_active = False
        logger.info("mcp_server_deactivated", server_id=server_id)
    return {"deleted": server is not None}
