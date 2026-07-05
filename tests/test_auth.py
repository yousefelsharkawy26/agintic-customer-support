from collections.abc import AsyncIterator
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import jwt as pyjwt
import pytest
from httpx import ASGITransport, AsyncClient

from apps.api.auth.utils import create_api_key, hash_api_key, verify_jwt
from apps.api.core.config import settings
from apps.api.main import app

TEST_TENANT_ID = "00000000-0000-0000-0000-0000000000a1"
ALT_TENANT_ID = "00000000-0000-0000-0000-0000000000a2"


@pytest.fixture
def mock_db():
    db = AsyncMock()

    class FakeResult:
        def __init__(self, data=None):
            self._data = data or []

        def scalar_one_or_none(self):
            return self._data[0] if self._data else None

        def scalars(self):
            class FakeScalars:
                def __init__(self, data):
                    self._data = data

                def all(self):
                    return self._data

                def first(self):
                    return self._data[0] if self._data else None

                def one_or_none(self):
                    return self._data[0] if self._data else None

            return FakeScalars(self._data)

        def scalar(self):
            return self._data[0][0] if self._data else None

    fake_key = MagicMock()
    fake_key.id = "key-1"
    fake_key.tenant_id = TEST_TENANT_ID
    fake_key.is_active = True

    fake_tenant = MagicMock()
    fake_tenant.id = TEST_TENANT_ID
    fake_tenant.name = "Test Tenant"
    fake_tenant.slug = "test-tenant"
    fake_tenant.plan = "pro"
    fake_tenant.is_active = True

    fake_config = MagicMock()
    fake_config.tenant_id = TEST_TENANT_ID
    fake_config.llm_model = "gpt-4o"
    fake_config.embeddings_model = "text-embedding-3-large"
    fake_config.daily_request_limit = 1000
    fake_config.monthly_token_limit = 1000000

    async def fake_execute(stmt):
        compiled = str(stmt.compile(compile_kwargs={"literal_binds": True}))
        if "tenant_api_keys" in compiled or "api_keys" in compiled:
            return FakeResult([fake_key])
        if "tenants" in compiled:
            return FakeResult([fake_tenant])
        if "tenant_configs" in compiled:
            return FakeResult([fake_config])
        if any(token in compiled for token in ["request_count", "token_count", "coalesce"]):
            return FakeResult([[0]])
        return FakeResult()

    db.execute = fake_execute
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.add = MagicMock()
    return db


@pytest.fixture
async def client(mock_db):
    """Unauthenticated client for 401-assertion tests."""
    from apps.api.core.database import get_db

    async def override_get_db() -> AsyncIterator[Any]:
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
async def authed_client(mock_db):
    """Authed client for success-path tests."""
    from apps.api.auth.deps import get_current_tenant, get_tenant_db
    from apps.api.core.database import get_db

    async def override_get_db() -> AsyncIterator[Any]:
        yield mock_db

    async def override_auth() -> dict[str, Any]:
        return {"tenant_id": TEST_TENANT_ID, "auth_method": "test"}

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_tenant_db] = override_get_db
    app.dependency_overrides[get_current_tenant] = override_auth

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.pop(get_current_tenant, None)
    app.dependency_overrides.pop(get_tenant_db, None)
    app.dependency_overrides.pop(get_db, None)


def _valid_token(tenant_id=TEST_TENANT_ID):
    return pyjwt.encode(
        {"tenant_id": tenant_id},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


class TestAuthUtils:
    def test_create_api_key_format(self):
        key = create_api_key()
        assert key.startswith("cs_")
        assert len(key) > 32

    def test_hash_api_key_hex(self):
        h = hash_api_key("test-key")
        assert len(h) == 64
        assert h.isalnum()

    def test_verify_jwt_valid(self):
        token = _valid_token()
        payload = verify_jwt(token)
        assert payload is not None
        assert payload["tenant_id"] == TEST_TENANT_ID

    def test_verify_jwt_invalid_secret(self):
        token = pyjwt.encode(
            {"tenant_id": TEST_TENANT_ID}, "wrong-secret", algorithm=settings.jwt_algorithm
        )
        assert verify_jwt(token) is None

    def test_verify_jwt_expired(self):
        import time

        token = pyjwt.encode(
            {"tenant_id": TEST_TENANT_ID, "exp": int(time.time()) - 3600},
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
        )
        assert verify_jwt(token) is None


class TestAuthMiddleware:
    async def test_no_auth_returns_401(self, client):
        resp = await client.get("/api/v1/tenants/config")
        assert resp.status_code == 401

    async def test_no_auth_quota_returns_401(self, client):
        resp = await client.get("/api/v1/tenants/quota")
        assert resp.status_code == 401

    async def test_invalid_bearer_returns_401(self, client):
        resp = await client.get(
            "/api/v1/tenants/config",
            headers={"Authorization": "Bearer invalidtoken"},
        )
        assert resp.status_code == 401

    async def test_bearer_auth_success(self, authed_client):
        token = _valid_token(TEST_TENANT_ID)
        resp = await authed_client.get(
            "/api/v1/tenants/config",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200

    async def test_api_key_auth_success(self, authed_client):
        resp = await authed_client.get(
            "/api/v1/tenants/config",
            headers={"x-api-key": "test-api-key"},
        )
        assert resp.status_code == 200


class TestTenantIsolation:
    async def test_different_bearer_tenant_does_not_leak(self):
        local_db = AsyncMock()

        class FakeResult:
            def __init__(self, data=None):
                self._data = data or []

            def scalar_one_or_none(self):
                return self._data[0] if self._data else None

            def scalars(self):
                class FakeScalars:
                    def __init__(self, data):
                        self._data = data

                    def all(self):
                        return self._data

                    def first(self):
                        return self._data[0] if self._data else None

                    def one_or_none(self):
                        return self._data[0] if self._data else None

                return FakeScalars(self._data)

            def scalar(self):
                return self._data[0][0] if self._data else None

        tenant = MagicMock()
        tenant.id = TEST_TENANT_ID

        async def fake_execute(stmt):
            compiled = str(stmt.compile(compile_kwargs={"literal_binds": True}))
            if "tenant_api_keys" in compiled or "api_keys" in compiled:
                return FakeResult([])
            if "tenants" in compiled:
                return FakeResult([tenant])
            if "tenant_configs" in compiled:
                return FakeResult([])
            if any(token in compiled for token in ["request_count", "token_count", "coalesce"]):
                return FakeResult([[0]])
            return FakeResult()

        local_db.execute = fake_execute

        from apps.api.auth.deps import get_current_tenant, get_tenant_db
        from apps.api.core.database import get_db

        app.dependency_overrides[get_db] = lambda: local_db
        app.dependency_overrides[get_tenant_db] = lambda: local_db
        app.dependency_overrides[get_current_tenant] = lambda: {
            "tenant_id": ALT_TENANT_ID,
            "auth_method": "jwt",
        }
        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as auth_ac:
                resp = await auth_ac.get(
                    "/api/v1/tenants/quota",
                    headers={"Authorization": f"Bearer {_valid_token(ALT_TENANT_ID)}"},
                )
            assert resp.status_code == 200
            data = resp.json()
            assert data["within_quota"] is True
            assert data.get("daily_requests", 0) == 0
            assert data.get("monthly_tokens", 0) == 0
        finally:
            app.dependency_overrides.pop(get_current_tenant, None)
            app.dependency_overrides.pop(get_tenant_db, None)
            app.dependency_overrides.pop(get_db, None)
