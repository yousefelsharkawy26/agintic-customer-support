import pytest
from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import async_sessionmaker

from apps.api.core.database import engine

pytestmark = pytest.mark.asyncio


async def test_session_scoped_after_begin_hook():
    """
    Verifies that an after_begin hook attached to a specific session's sync_session
    fires exactly once per transaction, even if the user manually calls commit()
    multiple times, and that parameter binding in set_config works.
    """
    factory = async_sessionmaker(engine, expire_on_commit=False)
    tenant_id = "test-tenant-123"

    invocations = 0

    async with factory() as session:
        # Register the session-specific listener
        @event.listens_for(session.sync_session, "after_begin")
        def set_tenant(sync_session, transaction, connection):
            nonlocal invocations
            invocations += 1
            connection.execute(
                text("SELECT set_config('app.tenant_id', :tenant_id, true)"),
                {"tenant_id": tenant_id},
            )

        # Transaction 1: Implicitly started by first execute
        await session.execute(text("SELECT 1"))

        # Verify app.tenant_id is set
        result = await session.execute(text("SELECT current_setting('app.tenant_id', true)"))
        assert result.scalar_one() == tenant_id

        # Commit ends Transaction 1
        await session.commit()
        assert invocations == 1

        # Transaction 2: Implicitly started by next execute
        await session.execute(text("SELECT 1"))
        result = await session.execute(text("SELECT current_setting('app.tenant_id', true)"))
        assert result.scalar_one() == tenant_id

        # Commit ends Transaction 2
        await session.commit()
        assert invocations == 2

        # Transaction 3: Implicitly started by next execute
        await session.execute(text("SELECT 1"))
        result = await session.execute(text("SELECT current_setting('app.tenant_id', true)"))
        assert result.scalar_one() == tenant_id

        # Don't commit, just let context manager roll it back
        assert invocations == 3

    # Ensure the event listener does not leak to other sessions
    async with factory() as other_session:
        # Execute query to trigger a transaction
        await other_session.execute(text("SELECT 1"))

        # It should be empty (or raise an error if not set)
        result = await other_session.execute(text("SELECT current_setting('app.tenant_id', true)"))
        val = result.scalar_one()
        assert val is None or val == ""

        # Invocations should still be 3
        assert invocations == 3
