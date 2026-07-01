from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.auth.deps import get_current_tenant
from apps.api.core.database import get_db

router = APIRouter(
    prefix="/api/v1/webhooks/tools",
    tags=["webhooks"],
    dependencies=[Depends(get_current_tenant)],
)


class WebhookPayload(BaseModel):
    tool_call_id: str
    result: dict[str, Any]
    is_error: bool = False


@router.post("/{server_id}")
async def tool_webhook(
    _server_id: str, _body: WebhookPayload, _request: Request, _db: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    return {"status": "received"}
