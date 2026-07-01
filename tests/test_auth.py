from collections.abc import AsyncIterator
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import jwt as pyjwt
import pytest
from httpx import ASGITransport, AsyncClient

from apps.api.auth.utils import create_api_key, hash_api_key, verify_jwt
from apps.api.core.config import settings
from apps.api.main import app

# ── Fixtures ──


@pytest.fixture
def mock_db():
    db = AsyncMock()

    class FakeResult:
        def __init__(self, data: list[Any] | None = None):
            self._data = data or []

        def scalar_one_or_none(self) -> Any | None:
            return self._data[0] if self._data else None

        def scalar(self) -> Any | None:
            return self._data[0] if self._data else 0

        def scalars(self) -> MagicMock:
            m = MagicMock()
            m.all.return_value = self._data
            return m

    fake_key = MagicMock()
    fake_key.id = "key-1"
    fake_key.tenant_id = "t1"
    fake_key.is_active = True

    fake_tenant = MagicMock()
    fake_tenant.id = "t1"
    fake_tenant.name = "Test Tenant"
    fake_tenant.slug = "test-tenant"
    fake_tenant.plan = "pro"
    fake_tenant.is_active = True

    fake_config = MagicMock()
    fake_config.tenant_id = "t1"
    fake_config.llm_model = "gpt-4o"
    fake_config.embeddings_model = "text-embedding-3-large"
    fake_config.daily_request_limit = 1000
    fake_config.monthly_token_limit = 1000000

    async def fake_execute(stmt: Any) -> FakeResult:
        compiled = str(stmt.compile(compile_kwargs={"literal_binds": True}))
        if "tenant_api_keys" in compiled:
            return FakeResult([fake_key])
        if "tenants" in compiled and "tenant_configs" not in compiled:
            return FakeResult([fake_tenant])
        if "tenant_configs" in compiled:
            return FakeResult([fake_config])
        return FakeResult([0])

    db.execute = fake_execute
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.add = MagicMock()
    return db


@pytest.fixture
async def client(mock_db):
    from apps.api.core.database import get_db

    async def override_get_db() -> AsyncIterator[Any]:
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


def _valid_token(tenant_id: str = "t1") -> str:
    return pyjwt.encode(
        {"tenant_id": tenant_id},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


# ── Auth Utility Tests ──


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
        assert payload["tenant_id"] == "t1"

    def test_verify_jwt_invalid_secret(self):
        token = pyjwt.encode({"tenant_id": "t1"}, "wrong-secret", algorithm=settings.jwt_algorithm)
        assert verify_jwt(token) is None

    def test_verify_jwt_expired(self):
        import time

        token = pyjwt.encode(
            {"tenant_id": "t1", "exp": int(time.time()) - 3600},
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
        )
        assert verify_jwt(token) is None


# ── Auth Middleware Tests ──


class TestAuthMiddleware:
    async def test_health_public(self, client: AsyncClient):
        assert (await client.get("/health")).status_code == 200

    async def test_ready_public(self, client: AsyncClient):
        assert (await client.get("/ready")).status_code == 200

    async def test_protected_route_no_auth(self, client: AsyncClient):
        resp = await client.get("/api/v1/tenants/t1/config")
        assert resp.status_code == 401

    async def test_protected_route_invalid_bearer(self, client: AsyncClient):
        resp = await client.get(
            "/api/v1/tenants/t1/config",
            headers={"Authorization": "Bearer invalidtoken"},
        )
        assert resp.status_code == 401

    async def test_bearer_auth_success(self, client: AsyncClient):
        resp = await client.get(
            "/api/v1/tenants/t1/config",
            headers={"Authorization": f"Bearer {_valid_token()}"},
        )
        assert resp.status_code == 200

    async def test_bearer_wrong_tenant_blocked(self, client: AsyncClient):
        resp = await client.get(
            "/api/v1/tenants/t2/config",
            headers={"Authorization": f"Bearer {_valid_token('tenant-a')}"},
        )
        assert resp.status_code == 403


# ── RLS Guard Tests ──


class TestRLSGuard:
    async def test_get_config_same_tenant(self, client: AsyncClient):
        resp = await client.get(
            "/api/v1/tenants/t1/config",
            headers={"Authorization": f"Bearer {_valid_token()}"},
        )
        assert resp.status_code == 200

    async def test_get_config_different_tenant(self, client: AsyncClient):
        resp = await client.get(
            "/api/v1/tenants/other-tenant/config",
            headers={"Authorization": f"Bearer {_valid_token('t1')}"},
        )
        assert resp.status_code == 403

    async def test_quota_same_tenant(self, client: AsyncClient):
        resp = await client.get(
            "/api/v1/tenants/t1/quota",
            headers={"Authorization": f"Bearer {_valid_token()}"},
        )
        assert resp.status_code == 200

    async def test_quota_different_tenant(self, client: AsyncClient):
        resp = await client.get(
            "/api/v1/tenants/t2/quota",
            headers={"Authorization": f"Bearer {_valid_token('t1')}"},
        )
        assert resp.status_code == 403
