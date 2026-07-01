from __future__ import annotations

from datetime import datetime
from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.auth.deps import get_current_tenant
from apps.api.core.database import get_db
from apps.api.widget.models import OfflineMessage, WidgetSession
from apps.api.widget.models_ext import WidgetEvent, WidgetSettings

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/widget", tags=["widget"])


class SessionStartRequest(BaseModel):
    tenant_id: str
    visitor_id: str
    locale: str = "en"

    model_config = {
        "json_schema_extra": {
            "example": {
                "tenant_id": "tenant-abc-123",
                "visitor_id": "visitor-xyz-789",
                "locale": "en",
            }
        }
    }


class OfflineMessageCreate(BaseModel):
    tenant_id: str
    session_id: str
    visitor_id: str
    content: str
    message_type: str = "text"
    client_ts: str | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "tenant_id": "tenant-abc-123",
                "session_id": "session-1",
                "visitor_id": "visitor-xyz-789",
                "content": "Please contact me when you're back online.",
                "message_type": "text",
                "client_ts": "2026-07-01T12:00:00Z",
            }
        }
    }


class WidgetSessionUpdate(BaseModel):
    locale: str | None = None


class WidgetSettingsUpdate(BaseModel):
    primary_color: str | None = None
    position: str | None = None
    title: str | None = None
    greeting: str | None = None
    locale: str | None = None
    brand_logo_url: str | None = None
    custom_css: str | None = None
    show_branding: bool | None = None
    is_active: bool | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "primary_color": "#10b981",
                "position": "bottom-left",
                "title": "Acme Support",
                "greeting": "Welcome to Acme! How can we help?",
                "show_branding": False,
            }
        }
    }


class AnalyticsEventCreate(BaseModel):
    tenant_id: str
    session_id: str
    visitor_id: str
    event_type: str
    metadata: dict[str, object] | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "tenant_id": "tenant-abc-123",
                "session_id": "session-1",
                "visitor_id": "visitor-xyz-789",
                "event_type": "widget_opened",
                "metadata": {"source": "button"},
            }
        }
    }


@router.post(
    "/sessions/start",
    summary="Start or resume a widget session",
    description=(
        "Called by the embeddable widget when a user opens it. "
        "If an active session exists for this visitor, it's resumed. "
        "Otherwise, a new session is created and returned."
    ),
)
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


# ── Widget Customization (public read, admin write) ──


@router.get("/settings/{tenant_id}")
async def get_widget_settings(tenant_id: str, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    result = await db.execute(select(WidgetSettings).where(WidgetSettings.tenant_id == tenant_id))
    settings = result.scalar_one_or_none()
    if not settings:
        return {
            "tenant_id": tenant_id,
            "primary_color": "#2563eb",
            "position": "bottom-right",
            "title": "Support",
            "greeting": "Hi! How can I help you today?",
            "locale": "en",
            "brand_logo_url": None,
            "custom_css": None,
            "show_branding": True,
            "is_active": True,
        }
    return {
        "tenant_id": settings.tenant_id,
        "primary_color": settings.primary_color,
        "position": settings.position,
        "title": settings.title,
        "greeting": settings.greeting,
        "locale": settings.locale,
        "brand_logo_url": settings.brand_logo_url,
        "custom_css": settings.custom_css,
        "show_branding": settings.show_branding,
        "is_active": settings.is_active,
    }


@router.put("/settings/{tenant_id}")
async def update_widget_settings(
    tenant_id: str,
    body: WidgetSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> dict[str, Any]:
    if tenant["tenant_id"] != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant mismatch")
    result = await db.execute(select(WidgetSettings).where(WidgetSettings.tenant_id == tenant_id))
    settings = result.scalar_one_or_none()
    if not settings:
        settings = WidgetSettings(tenant_id=tenant_id)
        db.add(settings)
    update_data = body.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    await db.commit()
    await db.refresh(settings)
    return _settings_to_dict(settings)


def _settings_to_dict(s: WidgetSettings) -> dict[str, Any]:
    return {
        "tenant_id": s.tenant_id,
        "primary_color": s.primary_color,
        "position": s.position,
        "title": s.title,
        "greeting": s.greeting,
        "locale": s.locale,
        "brand_logo_url": s.brand_logo_url,
        "custom_css": s.custom_css,
        "show_branding": s.show_branding,
        "is_active": s.is_active,
        "created_at": s.created_at.isoformat(),
        "updated_at": s.updated_at.isoformat(),
    }


# ── Widget Analytics ──


@router.post("/analytics/event")
async def record_analytics_event(
    body: AnalyticsEventCreate, db: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    event = WidgetEvent(
        tenant_id=body.tenant_id,
        session_id=body.session_id,
        visitor_id=body.visitor_id,
        event_type=body.event_type,
        metadata_=body.metadata,
    )
    db.add(event)
    await db.commit()
    return {"status": "recorded"}


@router.get("/analytics/{tenant_id}")
async def get_widget_analytics(
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
    event_type: str | None = Query(None),
    since: str | None = Query(None),
) -> dict[str, Any]:
    if tenant["tenant_id"] != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant mismatch")
    query = select(WidgetEvent).where(WidgetEvent.tenant_id == tenant_id)
    if event_type:
        query = query.where(WidgetEvent.event_type == event_type)
    if since:
        try:
            since_dt = datetime.fromisoformat(since)
            query = query.where(WidgetEvent.created_at >= since_dt)
        except ValueError:
            pass
    query = query.order_by(WidgetEvent.created_at.desc()).limit(1000)
    result = await db.execute(query)
    events = result.scalars().all()

    total = await db.execute(
        select(func.count(WidgetEvent.id)).where(WidgetEvent.tenant_id == tenant_id)
    )
    total_count = total.scalar() or 0

    counts: dict[str, int] = {}
    for ev in events:
        counts[ev.event_type] = counts.get(ev.event_type, 0) + 1

    return {
        "total_events": total_count,
        "events": [
            {
                "id": e.id,
                "session_id": e.session_id,
                "visitor_id": e.visitor_id,
                "event_type": e.event_type,
                "metadata": e.metadata_,
                "created_at": e.created_at.isoformat(),
            }
            for e in events
        ],
        "breakdown": counts,
    }


@router.get("/analytics/{tenant_id}/satisfaction")
async def get_satisfaction_summary(
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> dict[str, Any]:
    if tenant["tenant_id"] != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant mismatch")
    result = await db.execute(
        select(WidgetEvent)
        .where(
            WidgetEvent.tenant_id == tenant_id,
            WidgetEvent.event_type == "satisfaction_rating",
        )
        .order_by(WidgetEvent.created_at.desc())
        .limit(1000)
    )
    ratings = result.scalars().all()
    if not ratings:
        return {"total": 0, "average": 0.0, "distribution": {}}

    distribution: dict[str, int] = {}
    total_score = 0.0
    for r in ratings:
        raw = 0.0
        if r.metadata_ and "score" in r.metadata_:
            val = r.metadata_["score"]
            if isinstance(val, int | float):
                raw = float(val)
        label = str(raw)
        total_score += raw
        distribution[label] = distribution.get(label, 0) + 1
    return {
        "total": len(ratings),
        "average": round(total_score / len(ratings), 2),
        "distribution": distribution,
    }
