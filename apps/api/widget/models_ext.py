from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from apps.api.tenants.models import Base


class WidgetSettings(Base):
    __tablename__ = "widget_settings"

    id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    tenant_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False), unique=True, nullable=False, index=True
    )
    primary_color: Mapped[str] = mapped_column(String(7), default="#2563eb")
    position: Mapped[str] = mapped_column(String(20), default="bottom-right")
    title: Mapped[str] = mapped_column(String(100), default="Support")
    greeting: Mapped[str] = mapped_column(String(500), default="Hi! How can I help you today?")
    locale: Mapped[str] = mapped_column(String(10), default="en")
    brand_logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    custom_css: Mapped[str | None] = mapped_column(Text, nullable=True)
    show_branding: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class WidgetEvent(Base):
    __tablename__ = "widget_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), nullable=False, index=True)
    visitor_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    metadata_: Mapped[dict[str, object] | None] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
