"""
SEC-04 Integration Tests — requires live PostgreSQL with RLS enabled.
Run with: pytest -m integration tests/test_rls_integration.py

These tests do NOT mock the database. They prove:
  1. Phase 1 tables have both ENABLE and FORCE ROW LEVEL SECURITY.
  2. Phase 1 tables have the correct isolation policies.
  3. Tenant A cannot read rows belonging to Tenant B (app_worker role).
  4. app_worker CANNOT write to bootstrap tables (tenants, tenant_api_keys).
  5. app_provisioner CAN write to bootstrap tables.
  6. The tenant binding survives COMMIT → BEGIN and ROLLBACK → BEGIN.
"""

import asyncio
import os
import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from apps.api.core.database import async_session_factory
from apps.api.core.rls import bind_session_to_tenant

pytestmark = pytest.mark.integration  # skip unless -m integration

TENANT_A = str(uuid.uuid4())
TENANT_B = str(uuid.uuid4())

PHASE1_TABLES = ["conversations", "messages", "mcp_servers", "webhook_configs"]

# ── Session factories for tests ─────────────────────────────────────────────


def _load_env():
    from dotenv import load_dotenv

    load_dotenv()


def _provisioner_factory():
    """app_provisioner role — bootstrap tables (tenants, tenant_api_keys) only."""
    _load_env()
    url = os.environ.get("PROVISIONER_DATABASE_URL")
    if not url:
        pytest.skip("PROVISIONER_DATABASE_URL not set — skipping bootstrap tests")
    engine = create_async_engine(url, poolclass=NullPool)
    return async_sessionmaker(engine, expire_on_commit=False), engine


def _owner_factory():
    """neondb_owner role — full access for test seed/teardown infrastructure only."""
    _load_env()
    url = os.environ.get("ALEMBIC_DATABASE_URL")
    if not url:
        pytest.skip("ALEMBIC_DATABASE_URL not set — cannot seed test data")
    engine = create_async_engine(url, poolclass=NullPool)
    return async_sessionmaker(engine, expire_on_commit=False), engine


def _current_user_has_bypassrls() -> bool:
    """Return True if DATABASE_URL role has rolbypassrls=True."""
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    from sqlalchemy.pool import NullPool

    from apps.api.core.config import settings

    async def _check():
        engine = create_async_engine(settings.database_url, poolclass=NullPool)
        factory = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with factory() as s:
                r = await s.execute(
                    text("SELECT rolbypassrls FROM pg_roles WHERE rolname = current_user")
                )
                row = r.fetchone()
                return bool(row and row[0])
        finally:
            await engine.dispose()

    return (
        asyncio.get_event_loop().run_until_complete(_check())
        if asyncio.get_event_loop().is_running()
        else asyncio.run(_check())
    )


# Isolation tests require a DB role without BYPASSRLS.
skip_if_bypassrls = pytest.mark.skipif(
    _current_user_has_bypassrls(),
    reason=("DB role has rolbypassrls=True. " "RLS enforcement requires a non-BYPASSRLS app role."),
)


# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture(scope="function")
async def db_with_seed():
    """
    Seeds two tenants + conversations + messages for isolation tests.

    Seeding strategy (test infrastructure only — NOT application code):
      - ALEMBIC_DATABASE_URL (neondb_owner) is used to INSERT all rows.
        The owner has BYPASSRLS and DML on all tables.
      - app_provisioner is tested separately in TestBootstrapRLS.
      - app_worker (DATABASE_URL) is used only in the actual isolation assertions.

    Teardown also uses the owner URL to DELETE without RLS constraints.
    """
    owner_factory, owner_engine = _owner_factory()

    conv_a_id = str(uuid.uuid4())
    conv_b_id = str(uuid.uuid4())

    async with owner_factory() as seed_session:
        await seed_session.execute(
            text(
                "INSERT INTO tenants (id, name, slug, api_key, plan, is_active) VALUES "
                "(:a, 'Tenant A', :slug_a, :ak, 'free', true), "
                "(:b, 'Tenant B', :slug_b, :bk, 'free', true)"
            ),
            {
                "a": TENANT_A,
                "slug_a": f"tenant-a-{TENANT_A[:8]}",
                "ak": f"key-a-{TENANT_A[:8]}",
                "b": TENANT_B,
                "slug_b": f"tenant-b-{TENANT_B[:8]}",
                "bk": f"key-b-{TENANT_B[:8]}",
            },
        )
        await seed_session.execute(
            text(
                "INSERT INTO conversations (id, tenant_id, status) VALUES "
                "(:ca, :a, 'active'), (:cb, :b, 'active')"
            ),
            {"ca": conv_a_id, "a": TENANT_A, "cb": conv_b_id, "b": TENANT_B},
        )
        await seed_session.execute(
            text(
                "INSERT INTO messages (id, conversation_id, tenant_id, role, content) VALUES "
                "(:ma, :ca, :a, 'user', 'Message from A'), "
                "(:mb, :cb, :b, 'user', 'Message from B')"
            ),
            {
                "ma": str(uuid.uuid4()),
                "ca": conv_a_id,
                "a": TENANT_A,
                "mb": str(uuid.uuid4()),
                "cb": conv_b_id,
                "b": TENANT_B,
            },
        )
        await seed_session.commit()

    yield {"conv_a": conv_a_id, "conv_b": conv_b_id}

    # Teardown via owner (bypasses RLS)
    async with owner_factory() as cleanup:
        await cleanup.execute(
            text("DELETE FROM messages WHERE tenant_id IN (:a, :b)"), {"a": TENANT_A, "b": TENANT_B}
        )
        await cleanup.execute(
            text("DELETE FROM conversations WHERE tenant_id IN (:a, :b)"),
            {"a": TENANT_A, "b": TENANT_B},
        )
        await cleanup.execute(
            text("DELETE FROM tenants WHERE id IN (:a, :b)"), {"a": TENANT_A, "b": TENANT_B}
        )
        await cleanup.commit()

    await owner_engine.dispose()


# ── Test 0: Bootstrap table RLS enforcement ────────────────────────────────────


class TestBootstrapRLS:
    """
    Proves the three-tier role model is correctly enforced at the database level:
      - app_worker  : cannot INSERT/DELETE on tenants (RLS blocks it)
      - app_provisioner : can INSERT/DELETE on tenants (permitted by policy)
    """

    @skip_if_bypassrls
    async def test_app_worker_cannot_insert_tenant(self):
        """
        app_worker must be blocked from inserting a new tenant row.
        The tenant_read_own policy only grants SELECT, so INSERT must raise.
        """
        import pytest
        from sqlalchemy.exc import ProgrammingError

        new_id = str(uuid.uuid4())
        async with async_session_factory() as session:
            with pytest.raises(ProgrammingError, match="row-level security"):
                await session.execute(
                    text(
                        "INSERT INTO tenants (id, name, slug, api_key, plan, is_active) "
                        "VALUES (:id, 'Blocked', 'blocked', 'blocked-key', 'free', true)"
                    ),
                    {"id": new_id},
                )
                await session.commit()

    async def test_app_provisioner_can_insert_and_delete_tenant(self):
        """
        app_provisioner must successfully INSERT and DELETE a tenant row.
        This proves the tenant_provision policy (USING true) is active.
        """
        prov_factory, prov_engine = _provisioner_factory()
        new_id = str(uuid.uuid4())
        try:
            async with prov_factory() as session:
                await session.execute(
                    text(
                        "INSERT INTO tenants (id, name, slug, api_key, plan, is_active) "
                        "VALUES (:id, 'Test Provisioner Tenant', :slug, 'prov-test-key', 'free', true)"
                    ),
                    {"id": new_id, "slug": f"prov-{new_id[:8]}"},
                )
                await session.commit()

            # Verify it exists
            async with prov_factory() as session:
                row = await session.execute(
                    text("SELECT id FROM tenants WHERE id = :id"), {"id": new_id}
                )
                assert str(row.scalar_one_or_none()) == new_id, "Insert did not persist"

        finally:
            # Always clean up
            async with prov_factory() as session:
                await session.execute(text("DELETE FROM tenants WHERE id = :id"), {"id": new_id})
                await session.commit()
            await prov_engine.dispose()


# ── Test 1: Schema verification ───────────────────────────────────────────────


class TestRLSSchema:
    async def test_phase1_tables_have_enable_and_force_rls(self):
        """Every Phase 1 table must have BOTH rls_enabled AND rls_forced = TRUE."""
        async with async_session_factory() as session:
            result = await session.execute(
                text("""
                SELECT relname,
                       relrowsecurity      AS rls_enabled,
                       relforcerowsecurity AS rls_forced
                FROM   pg_class
                WHERE  relname = ANY(:tables)
                ORDER  BY relname
            """),
                {"tables": PHASE1_TABLES},
            )
            rows = result.fetchall()

        found = {r.relname for r in rows}
        missing = set(PHASE1_TABLES) - found
        assert not missing, f"Tables not found in pg_class: {missing}"

        for row in rows:
            assert row.rls_enabled, f"{row.relname}: ENABLE ROW LEVEL SECURITY is not set"
            assert row.rls_forced, f"{row.relname}: FORCE ROW LEVEL SECURITY is not set"

    async def test_phase1_policies_exist_with_correct_using_clause(self):
        """Each Phase 1 table must have an isolation policy using set_config."""
        async with async_session_factory() as session:
            result = await session.execute(
                text("""
                SELECT c.relname AS table_name,
                       p.polname AS policy_name,
                       pg_get_expr(p.polqual, p.polrelid) AS using_expr
                FROM   pg_policy p
                JOIN   pg_class  c ON c.oid = p.polrelid
                WHERE  c.relname = ANY(:tables)
                ORDER  BY c.relname
            """),
                {"tables": PHASE1_TABLES},
            )
            policies = {row.table_name: row.using_expr for row in result}

        for table in PHASE1_TABLES:
            assert table in policies, f"No RLS policy found for {table}"
            expr = policies[table]
            assert (
                "current_setting" in expr
            ), f"{table} policy does not use current_setting(): {expr!r}"
            assert (
                "app.tenant_id" in expr
            ), f"{table} policy does not reference app.tenant_id: {expr!r}"


# ── Test 2: Cross-tenant isolation ───────────────────────────────────────────


class TestCrossTenantIsolation:
    @skip_if_bypassrls
    async def test_tenant_a_cannot_read_tenant_b_conversations(self, db_with_seed):
        """Session bound to Tenant A must see zero rows owned by Tenant B.

        Requires a DB role without BYPASSRLS — see module-level note.
        """
        async with async_session_factory() as session:
            bind_session_to_tenant(session, TENANT_A)

            # Tenant A's own conversation — must be visible
            own = await session.execute(
                text("SELECT id FROM conversations WHERE tenant_id = :tid"),
                {"tid": TENANT_A},
            )
            assert own.fetchone() is not None, "Tenant A cannot see its own conversations"

            # Tenant B's conversation — must NOT be visible
            other = await session.execute(
                text("SELECT id FROM conversations WHERE id = :conv_b"),
                {"conv_b": db_with_seed["conv_b"]},
            )
            assert (
                other.fetchone() is None
            ), "ISOLATION FAILURE: Tenant A can see Tenant B's conversation!"

    @skip_if_bypassrls
    async def test_tenant_a_cannot_read_tenant_b_messages(self, db_with_seed):
        """Session bound to Tenant A must see zero messages owned by Tenant B.

        Requires a DB role without BYPASSRLS — see module-level note.
        """
        async with async_session_factory() as session:
            bind_session_to_tenant(session, TENANT_A)

            result = await session.execute(
                text("SELECT id FROM messages WHERE tenant_id = :tid"),
                {"tid": TENANT_B},
            )
            rows = result.fetchall()
            assert (
                len(rows) == 0
            ), f"ISOLATION FAILURE: Tenant A sees {len(rows)} Tenant B messages!"

    @skip_if_bypassrls
    async def test_unbound_session_is_rejected(self, db_with_seed):
        """
        An app_worker session with NO tenant binding must be denied access.

        Why does this raise an error instead of returning 0 rows?
        1. Custom PostgreSQL variables (like 'app.tenant_id') return NULL initially.
        2. However, once set in a connection (e.g., by a previous transaction in
           the connection pool) and subsequently cleared at the end of the
           transaction (via ROLLBACK or is_local=true), PostgreSQL resets
           the custom variable to an empty string `''`, not NULL.
        3. The RLS policy evaluates `current_setting('app.tenant_id', true)::uuid`.
        4. Casting `''` to UUID raises `InvalidTextRepresentationError`.

        This is standard PostgreSQL behavior for custom GUCs, providing an
        even stricter safe-by-default outcome: unbound sessions crash rather
        than silently returning empty result sets.
        """
        from sqlalchemy.exc import DBAPIError

        async with async_session_factory() as session:
            with pytest.raises(DBAPIError):
                await session.execute(
                    text("SELECT tenant_id FROM conversations WHERE tenant_id IN (:a, :b)"),
                    {"a": TENANT_A, "b": TENANT_B},
                )

    async def test_switching_tenant_mid_session_is_prevented(self):
        """
        Verify that bind_session_to_tenant raises on double-binding.
        A session cannot switch tenant identity mid-lifecycle.
        """
        from apps.api.core.rls import bind_session_to_tenant

        async with async_session_factory() as session:
            bind_session_to_tenant(session, TENANT_A)
            with pytest.raises(RuntimeError, match="already bound"):
                bind_session_to_tenant(session, TENANT_B)


# ── Test 3: Transaction lifecycle ─────────────────────────────────────────────


class TestTransactionLifecycle:
    async def test_tenant_binding_survives_commit_and_rollback(self):
        """
        Proves app.tenant_id is reapplied on every new transaction:
          BEGIN → verify → COMMIT → BEGIN → verify → ROLLBACK → BEGIN → verify

        NOTE: Nested transactions (SAVEPOINT) are explicitly out of scope.
        set_config(..., true) is transaction-local, not savepoint-local.
        Rolling back to a savepoint does NOT revert set_config.
        app.tenant_id remains set throughout all savepoints within a transaction.
        This is correct by construction and does not require explicit testing.
        """
        async with async_session_factory() as session:
            bind_session_to_tenant(session, TENANT_A)

            # Phase 1: implicit BEGIN on first execute
            val1 = (
                await session.execute(text("SELECT current_setting('app.tenant_id', TRUE)"))
            ).scalar_one()
            assert val1 == TENANT_A, f"Phase 1 failed: got {val1!r}"

            # Phase 2: after COMMIT, implicit BEGIN on next execute
            await session.commit()
            val2 = (
                await session.execute(text("SELECT current_setting('app.tenant_id', TRUE)"))
            ).scalar_one()
            assert val2 == TENANT_A, f"Phase 2 (post-commit) failed: got {val2!r}"

            # Phase 3: after ROLLBACK, implicit BEGIN on next execute
            await session.rollback()
            val3 = (
                await session.execute(text("SELECT current_setting('app.tenant_id', TRUE)"))
            ).scalar_one()
            assert val3 == TENANT_A, f"Phase 3 (post-rollback) failed: got {val3!r}"
