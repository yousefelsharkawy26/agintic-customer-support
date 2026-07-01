from __future__ import annotations

from typing import Any

import structlog
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.database import get_db
from apps.api.widget.models import OfflineMessage, WidgetSession

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/widget", tags=["widget"])


class SessionStartRequest(BaseModel):
    tenant_id: str
    visitor_id: str
    locale: str = "en"


class OfflineMessageCreate(BaseModel):
    tenant_id: str
    session_id: str
    visitor_id: str
    content: str
    message_type: str = "text"
    client_ts: str | None = None


class WidgetSessionUpdate(BaseModel):
    locale: str | None = None


@router.post("/sessions/start")
async def start_session(
    body: SessionStartRequest, db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    result = await db.execute(
        select(WidgetSession)
        .where(
            WidgetSession.tenant_id == body.tenant_id,
            WidgetSession.visitor_id == body.visitor_id,
            WidgetSession.is_active.is_(True),
        )
        .order_by(WidgetSession.created_at.desc())
        .limit(1)
    )
    existing = result.scalar_one_or_none()
    if existing:
        return {"session_id": existing.id, "visitor_id": existing.visitor_id, "resumed": True}

    session = WidgetSession(
        tenant_id=body.tenant_id,
        visitor_id=body.visitor_id,
        locale=body.locale,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return {"session_id": session.id, "visitor_id": session.visitor_id, "resumed": False}


@router.post("/sessions/{session_id}/heartbeat")
async def heartbeat(session_id: str, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    await db.execute(
        update(WidgetSession)
        .where(WidgetSession.id == session_id)
        .values(updated_at=WidgetSession.updated_at)
    )
    await db.commit()
    return {"status": "ok"}


@router.post("/sessions/{session_id}/end")
async def end_session(session_id: str, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    await db.execute(
        update(WidgetSession).where(WidgetSession.id == session_id).values(is_active=False)
    )
    await db.commit()
    return {"status": "ended"}


@router.post("/messages/offline")
async def queue_offline_message(
    body: OfflineMessageCreate, db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    msg = OfflineMessage(
        tenant_id=body.tenant_id,
        session_id=body.session_id,
        visitor_id=body.visitor_id,
        content=body.content,
        message_type=body.message_type,
        client_ts=body.client_ts,
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return {"message_id": msg.id, "queued": True}


@router.get("/messages/offline/{tenant_id}/{visitor_id}")
async def get_offline_messages(
    tenant_id: str, visitor_id: str, db: AsyncSession = Depends(get_db)
) -> list[dict[str, Any]]:
    result = await db.execute(
        select(OfflineMessage)
        .where(
            OfflineMessage.tenant_id == tenant_id,
            OfflineMessage.visitor_id == visitor_id,
            OfflineMessage.delivered.is_(False),
        )
        .order_by(OfflineMessage.created_at.asc())
    )
    msgs = result.scalars().all()

    if msgs:
        ids = [m.id for m in msgs]
        await db.execute(
            update(OfflineMessage).where(OfflineMessage.id.in_(ids)).values(delivered=True)
        )
        await db.commit()

    return [
        {
            "id": m.id,
            "content": m.content,
            "message_type": m.message_type,
            "client_ts": m.client_ts,
            "created_at": m.created_at.isoformat(),
        }
        for m in msgs
    ]
