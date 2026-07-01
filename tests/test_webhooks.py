from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import jwt as pyjwt
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from apps.api.core.config import settings
from apps.api.main import app
from apps.api.webhooks.engine import (
    PROVIDER_EVENTS,
    SUPPORTED_EVENTS,
    SUPPORTED_PROVIDERS,
    _format_for_provider,
    sign_payload,
)

# ── Fixtures ──


@pytest.fixture
def mock_db():
    db = AsyncMock()

    class FakeResult:
        def __init__(self, data: list[Any] | None = None):
            self._data = data or []

        def scalar_one_or_none(self) -> Any | None:
            return self._data[0] if self._data else None

        def scalars(self) -> MagicMock:
            m = MagicMock()
            m.all.return_value = self._data
            return m

    fake_config = MagicMock()
    fake_config.id = "wc-1"
    fake_config.tenant_id = "t1"
    fake_config.provider = "slack"
    fake_config.label = "Test Slack"
    fake_config.url = "https://hooks.slack.com/test"
    fake_config.secret = "test-secret"
    fake_config.events = '["conversation.created"]'
    fake_config.is_active = True
    fake_config.retry_count = 3
    fake_config.timeout_ms = 10000
    fake_config.created_at = MagicMock()
    fake_config.updated_at = MagicMock()

    class FakeDelivery:
        id = "d-1"
        config_id = "wc-1"
        tenant_id = "t1"
        event_type = "conversation.created"
        status = "delivered"
        response_code = 200
        response_body = "ok"
        error = None
        attempt = 1
        duration_ms = 150
        created_at = MagicMock()

    fake_delivery = FakeDelivery()

    async def fake_execute(stmt: Any) -> FakeResult:
        compiled = str(stmt.compile(compile_kwargs={"literal_binds": True}))
        s = compiled.lower()
        if "webhook_deliveries" in s:
            return FakeResult([fake_delivery])
        if "webhook_configs" in s:
            if "'wc-1'" in compiled:
                return FakeResult([fake_config])
            return FakeResult([])
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
    added_objects: list[Any] = []

    def track_add(obj: Any) -> None:
        added_objects.append(obj)

    db.add = MagicMock(side_effect=track_add)
    db.delete = AsyncMock()

    async def fake_flush() -> None:
        import uuid
        from datetime import UTC, datetime

        for obj in added_objects:
            if hasattr(obj, "id") and isinstance(obj.id, MagicMock):
                obj.id = None
            if obj.id is None and hasattr(obj, "id"):
                obj.id = str(uuid.uuid4())
            if hasattr(obj, "is_active") and obj.is_active is None:
                obj.is_active = True
            if hasattr(obj, "created_at") and obj.created_at is None:
                obj.created_at = datetime.now(UTC)
            if hasattr(obj, "updated_at") and obj.updated_at is None:
                obj.updated_at = datetime.now(UTC)

    db.flush = AsyncMock(side_effect=fake_flush)
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


# ── Engine Tests ──


class TestSignPayload:
    def test_sign_payload_hmac(self):
        payload = '{"hello": "world"}'
        secret = "my-secret"
        sig = sign_payload(payload, secret)
        assert isinstance(sig, str)
        assert len(sig) == 64

    def test_sign_payload_deterministic(self):
        payload = '{"hello": "world"}'
        secret = "my-secret"
        assert sign_payload(payload, secret) == sign_payload(payload, secret)

    def test_sign_payload_different_secret(self):
        payload = '{"hello": "world"}'
        assert sign_payload(payload, "a") != sign_payload(payload, "b")


class TestFormatForProvider:
    def test_slack_format(self):
        data = {"conversation_id": "c1", "message": "Hello", "user_id": "u1"}
        result = _format_for_provider("slack", "conversation.created", data)
        assert "text" in result
        assert "attachments" in result

    def test_zendesk_format(self):
        data = {"conversation_id": "c1", "message": "Need help"}
        result = _format_for_provider("zendesk", "ticket.created", data)
        assert "ticket" in result
        assert result["ticket"]["description"] == "Need help"

    def test_intercom_format(self):
        data = {"conversation_id": "c1", "user_id": "u1", "message": "Hi"}
        result = _format_for_provider("intercom", "conversation.created", data)
        assert result["event_name"] == "conversation.created"
        assert result["user_id"] == "u1"

    def test_hubspot_format(self):
        data = {"conversation_id": "c1", "message": "Hello", "tier": "premium"}
        result = _format_for_provider("hubspot", "conversation.created", data)
        assert "properties" in result
        props = result["properties"]
        has_tier = any(
            p["property"] == "customer_support_tier" and p["value"] == "premium" for p in props
        )
        assert has_tier

    def test_unknown_provider_passthrough(self):
        data = {"key": "value"}
        result = _format_for_provider("unknown", "event", data)
        assert result == data


class TestSupportedLists:
    def test_all_providers_have_events(self):
        for p in SUPPORTED_PROVIDERS:
            assert p in PROVIDER_EVENTS
            assert len(PROVIDER_EVENTS[p]) > 0

    def test_all_provider_events_are_registered(self):
        for events in PROVIDER_EVENTS.values():
            for ev in events:
                assert ev in SUPPORTED_EVENTS


# ── API Tests ──


class TestWebhookAPI:
    async def test_list_providers(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/v1/webhooks/providers")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        providers = {p["provider"] for p in data}
        assert providers == SUPPORTED_PROVIDERS

    async def test_list_events(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/v1/webhooks/events")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == len(SUPPORTED_EVENTS)

    async def test_create_webhook_config(self, auth_client: AsyncClient):
        body = {
            "provider": "slack",
            "label": "My Slack",
            "url": "https://hooks.slack.com/services/T00/B00/xxx",
            "secret": "whsec_test",
            "events": ["conversation.created"],
        }
        resp = await auth_client.post("/api/v1/webhooks/configs", json=body)
        assert resp.status_code == 201
        data = resp.json()
        assert data["provider"] == "slack"

    async def test_create_webhook_invalid_provider(self, auth_client: AsyncClient):
        body = {
            "provider": "invalid",
            "label": "Bad",
            "url": "https://example.com",
            "events": [],
        }
        resp = await auth_client.post("/api/v1/webhooks/configs", json=body)
        assert resp.status_code == 400

    async def test_create_webhook_invalid_event_for_provider(self, auth_client: AsyncClient):
        body = {
            "provider": "slack",
            "label": "Bad",
            "url": "https://example.com",
            "events": ["ticket.created"],
        }
        resp = await auth_client.post("/api/v1/webhooks/configs", json=body)
        assert resp.status_code == 400

    async def test_create_webhook_unknown_event(self, auth_client: AsyncClient):
        body = {
            "provider": "slack",
            "label": "Bad",
            "url": "https://example.com",
            "events": ["nonexistent.event"],
        }
        resp = await auth_client.post("/api/v1/webhooks/configs", json=body)
        assert resp.status_code == 400

    async def test_list_webhook_configs(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/v1/webhooks/configs")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    async def test_get_webhook_config(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/v1/webhooks/configs/wc-1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "wc-1"

    async def test_get_webhook_config_not_found(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/v1/webhooks/configs/wc-404")
        assert resp.status_code == 404

    async def test_update_webhook_config(self, auth_client: AsyncClient):
        body = {"label": "Updated Slack", "is_active": False}
        resp = await auth_client.put("/api/v1/webhooks/configs/wc-1", json=body)
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "wc-1"

    async def test_delete_webhook_config(self, auth_client: AsyncClient):
        resp = await auth_client.delete("/api/v1/webhooks/configs/wc-1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["deleted"] is True

    async def test_list_deliveries(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/v1/webhooks/deliveries")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    async def test_list_deliveries_filtered(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/v1/webhooks/deliveries?config_id=wc-1")
        assert resp.status_code == 200

    async def test_webhook_test_endpoint(self, auth_client: AsyncClient):
        resp = await auth_client.post("/api/v1/webhooks/test?config_id=wc-1")
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data

    async def test_unauthorized_without_token(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get("/api/v1/webhooks/providers")
            assert resp.status_code == 401


# ── Subscriber Tests ──


class TestWebhookSubscriber:
    async def test_event_map_coverage(self):
        from apps.api.webhooks.subscriber import WEBHOOK_EVENT_MAP

        assert "chat.message_sent" in WEBHOOK_EVENT_MAP
        assert "feedback.submitted" in WEBHOOK_EVENT_MAP
        assert "agent.status" in WEBHOOK_EVENT_MAP
        mapped = set(WEBHOOK_EVENT_MAP.values())
        for ev in mapped:
            assert ev in SUPPORTED_EVENTS


# ── Provider Integration Tests (mocked HTTP) ──


class TestSlackProvider:
    async def test_send_slack_message(self):
        from apps.api.webhooks.providers.slack import SlackConfig, send_slack_message

        config = SlackConfig(webhook_url="https://hooks.slack.com/test")
        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True}

        mock_client = MagicMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await send_slack_message(config, "Hello", [{"text": "world"}])
            assert result["ok"] is True

    async def test_verify_slack_signature(self):
        import hashlib
        import hmac
        import time

        from apps.api.webhooks.providers.slack import verify_slack_signature

        secret = "my-secret"
        body = b"payload=test"
        timestamp = str(int(time.time()))
        base = f"v0:{timestamp}:{body.decode()}"
        sig = "v0=" + hmac.new(secret.encode(), base.encode(), hashlib.sha256).hexdigest()
        headers = {"X-Slack-Request-Timestamp": timestamp, "X-Slack-Signature": sig}
        assert verify_slack_signature(body, headers, secret)


class TestZendeskProvider:
    async def test_create_ticket(self):
        from apps.api.webhooks.providers.zendesk import ZendeskConfig, create_ticket

        config = ZendeskConfig(subdomain="test", email="a@b.com", api_token="tok")
        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 201
        mock_response.json.return_value = {"ticket": {"id": 1}}

        mock_client = MagicMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await create_ticket(config, "Subject", "Description")
            assert result["ticket"]["id"] == 1

    async def test_update_ticket(self):
        from apps.api.webhooks.providers.zendesk import ZendeskConfig, update_ticket

        config = ZendeskConfig(subdomain="test", email="a@b.com", api_token="tok")
        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"ticket": {"id": 1}}

        mock_client = MagicMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.put = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await update_ticket(config, "1", "Updated comment")
            assert result["ticket"]["id"] == 1


class TestIntercomProvider:
    async def test_send_event(self):
        from apps.api.webhooks.providers.intercom import IntercomConfig, send_conversation_event

        config = IntercomConfig(access_token="tok")
        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "evt-1"}

        mock_client = MagicMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await send_conversation_event(config, "test-event", "user-1")
            assert result["id"] == "evt-1"


class TestHubSpotProvider:
    async def test_create_contact(self):
        from apps.api.webhooks.providers.hubspot import HubSpotConfig, create_or_update_contact

        config = HubSpotConfig(access_token="tok")
        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "contact-1"}

        mock_client = MagicMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await create_or_update_contact(config, "test@test.com", {"phone": "555"})
            assert result["id"] == "contact-1"

    async def test_create_ticket(self):
        from apps.api.webhooks.providers.hubspot import HubSpotConfig, create_ticket

        config = HubSpotConfig(access_token="tok")
        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "ticket-1"}

        mock_client = MagicMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await create_ticket(config, "Subject", "Description")
            assert result["id"] == "ticket-1"
