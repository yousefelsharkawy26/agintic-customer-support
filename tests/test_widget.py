from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import jwt as pyjwt
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from apps.api.core.config import settings
from apps.api.main import app
from apps.api.widget.models import OfflineMessage, WidgetSession
from apps.api.widget.models_ext import WidgetEvent, WidgetSettings


class TestWidgetSession:
    def test_session_creation(self) -> None:
        session = WidgetSession(
            tenant_id="tenant-1",
            visitor_id="visitor-1",
            locale="en",
            is_active=True,
        )
        assert session.locale == "en"

    def test_session_end(self) -> None:
        session = WidgetSession(
            tenant_id="t1",
            visitor_id="v1",
            is_active=True,
        )
        session.is_active = False
        assert session.is_active is False


class TestOfflineMessage:
    def test_offline_message_creation(self) -> None:
        msg = OfflineMessage(
            tenant_id="tenant-1",
            session_id="session-1",
            visitor_id="visitor-1",
            content="Help me please",
            message_type="text",
            delivered=False,
        )
        assert msg.content == "Help me please"
        assert msg.delivered is False

    def test_mark_delivered(self) -> None:
        msg = OfflineMessage(
            tenant_id="t1",
            session_id="s1",
            visitor_id="v1",
            content="Test",
            delivered=False,
        )
        msg.delivered = True
        assert msg.delivered is True

    def test_client_timestamp(self) -> None:
        msg = OfflineMessage(
            tenant_id="t1",
            session_id="s1",
            visitor_id="v1",
            content="Timed",
            client_ts="2026-07-01T12:00:00Z",
        )
        assert msg.client_ts == "2026-07-01T12:00:00Z"


class TestWidgetSettings:
    def test_settings_creation(self) -> None:
        s = WidgetSettings(
            tenant_id="t1",
            primary_color="#ff0000",
            position="bottom-left",
            title="Help",
        )
        assert s.primary_color == "#ff0000"
        assert s.position == "bottom-left"
        assert s.title == "Help"

    def test_settings_defaults_python(self) -> None:
        s = WidgetSettings(
            tenant_id="t2", primary_color="#2563eb", position="bottom-right", is_active=True
        )
        assert s.primary_color == "#2563eb"
        assert s.position == "bottom-right"
        assert s.is_active is True

    def test_settings_update(self) -> None:
        s = WidgetSettings(tenant_id="t3")
        s.primary_color = "#00ff00"
        s.show_branding = False
        assert s.primary_color == "#00ff00"
        assert s.show_branding is False


class TestWidgetEvent:
    def test_event_creation(self) -> None:
        e = WidgetEvent(
            tenant_id="t1",
            session_id="s1",
            visitor_id="v1",
            event_type="widget_opened",
            metadata_={"source": "button"},
        )
        assert e.event_type == "widget_opened"
        assert e.metadata_ == {"source": "button"}

    def test_event_without_metadata(self) -> None:
        e = WidgetEvent(
            tenant_id="t1",
            session_id="s1",
            visitor_id="v1",
            event_type="widget_loaded",
        )
        assert e.event_type == "widget_loaded"
        assert e.metadata_ is None


# ── Widget Settings API Tests ──


@pytest.fixture
def mock_db():
    db = AsyncMock()

    fake_settings = MagicMock()
    fake_settings.tenant_id = "t1"
    fake_settings.primary_color = "#ff0000"
    fake_settings.position = "bottom-left"
    fake_settings.title = "Help"
    fake_settings.greeting = "Hi!"
    fake_settings.locale = "en"
    fake_settings.brand_logo_url = None
    fake_settings.custom_css = None
    fake_settings.show_branding = True
    fake_settings.is_active = True
    fake_settings.created_at = MagicMock()
    fake_settings.created_at.isoformat.return_value = "2026-01-01T00:00:00+00:00"
    fake_settings.updated_at = MagicMock()
    fake_settings.updated_at.isoformat.return_value = "2026-01-01T00:00:00+00:00"

    fake_event = MagicMock()
    fake_event.id = 1
    fake_event.session_id = "s1"
    fake_event.visitor_id = "v1"
    fake_event.event_type = "widget_opened"
    fake_event.metadata_ = None
    fake_event.created_at = MagicMock()
    fake_event.created_at.isoformat.return_value = "2026-01-01T00:00:00+00:00"

    class FakeResult:
        def __init__(self, data: list[Any] | None = None):
            self._data = data or []

        def scalar_one_or_none(self) -> Any | None:
            return self._data[0] if self._data else None

        def scalar(self) -> Any | None:
            return len(self._data) if self._data else 0

        def scalars(self) -> MagicMock:
            m = MagicMock()
            m.all.return_value = self._data
            return m

    async def fake_execute(stmt: Any) -> FakeResult:
        compiled = str(stmt.compile(compile_kwargs={"literal_binds": True}))
        s = compiled.lower()
        if "widget_settings" in s:
            if "'t1'" in compiled:
                return FakeResult([fake_settings])
            return FakeResult([])
        if "widget_events" in s:
            return FakeResult([fake_event])
        if "tenant_api_keys" in s:
            fake_key = MagicMock()
            fake_key.id = "key-1"
            fake_key.tenant_id = "t1"
            fake_key.is_active = True
            return FakeResult([fake_key])
        if "tenants" in s:
            fake_tenant = MagicMock()
            fake_tenant.id = "t1"
            fake_tenant.name = "Test"
            fake_tenant.slug = "test"
            fake_tenant.plan = "pro"
            fake_tenant.is_active = True
            return FakeResult([fake_tenant])
        return FakeResult([])

    db.execute = fake_execute
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.add = MagicMock()
    db.delete = AsyncMock()
    return db


@pytest_asyncio.fixture
async def auth_client(mock_db):
    from apps.api.core.database import get_db

    async def override_get_db() -> AsyncIterator[Any]:
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db

    token = pyjwt.encode(
        {"tenant_id": "t1", "tenant_name": "Test"},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        ac.headers.update({"Authorization": f"Bearer {token}"})
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def public_client(mock_db):
    from apps.api.core.database import get_db

    async def override_get_db() -> AsyncIterator[Any]:
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


class TestWidgetSettingsAPI:
    async def test_get_settings_public(self, public_client: AsyncClient):
        resp = await public_client.get("/api/v1/widget/settings/t1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["primary_color"] == "#ff0000"
        assert data["position"] == "bottom-left"

    async def test_get_settings_defaults(self, public_client: AsyncClient):
        resp = await public_client.get("/api/v1/widget/settings/t2")
        assert resp.status_code == 200
        data = resp.json()
        assert data["primary_color"] == "#2563eb"
        assert data["is_active"] is True

    async def test_update_settings(self, auth_client: AsyncClient):
        resp = await auth_client.put(
            "/api/v1/widget/settings/t1",
            json={"primary_color": "#00ff00", "title": "Custom"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["tenant_id"] == "t1"

    async def test_update_settings_unauthorized(self, public_client: AsyncClient):
        resp = await public_client.put(
            "/api/v1/widget/settings/t1",
            json={"primary_color": "#000"},
        )
        assert resp.status_code == 401

    async def test_update_settings_wrong_tenant(self, auth_client: AsyncClient):
        resp = await auth_client.put(
            "/api/v1/widget/settings/t999",
            json={"title": "Nope"},
        )
        assert resp.status_code == 403


class TestWidgetAnalyticsAPI:
    async def test_record_event(self, public_client: AsyncClient):
        resp = await public_client.post(
            "/api/v1/widget/analytics/event",
            json={
                "tenant_id": "t1",
                "session_id": "s1",
                "visitor_id": "v1",
                "event_type": "widget_opened",
                "metadata": {"source": "button"},
            },
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "recorded"

    async def test_get_analytics(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/v1/widget/analytics/t1")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_events" in data
        assert "events" in data
        assert "breakdown" in data

    async def test_get_analytics_unauthorized(self, public_client: AsyncClient):
        resp = await public_client.get("/api/v1/widget/analytics/t1")
        assert resp.status_code == 401

    async def test_get_satisfaction(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/v1/widget/analytics/t1/satisfaction")
        assert resp.status_code == 200
        data = resp.json()
        assert "total" in data
        assert "average" in data
