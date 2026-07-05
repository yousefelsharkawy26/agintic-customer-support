"""
Global test configuration.

For integration tests with pytest-asyncio (function-scoped event loops) and
asyncpg, the module-level engine connection pool will try to reuse connections
that were created on a prior (now-closed) event loop.  Replacing the pool with
NullPool forces every async_session_factory() call to create a brand-new
connection on the *current* loop, eliminating all cross-loop RuntimeErrors.

We also patch the local name `async_session_factory` inside the test module
itself (not just the source module) because Python's `from X import Y` creates
an independent binding in the importing module's __dict__.
"""

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

pytest_plugins = []


@pytest.fixture(autouse=True)
def _use_nullpool_engine(monkeypatch):
    """
    Replace the shared pooled engine with a NullPool engine for each test.
    NullPool never caches connections, so each session gets a fresh connection
    bound to the current event loop.
    """
    from apps.api.core import database as db_module
    from apps.api.core.config import settings

    test_engine = create_async_engine(settings.database_url, poolclass=NullPool)
    test_factory = async_sessionmaker(test_engine, expire_on_commit=False)

    # Patch the source module attributes
    monkeypatch.setattr(db_module, "engine", test_engine)
    monkeypatch.setattr(db_module, "async_session_factory", test_factory)

    # Also patch the direct import binding inside the integration test module
    try:
        import tests.test_rls_integration as rls_test

        monkeypatch.setattr(rls_test, "async_session_factory", test_factory)
    except (ImportError, AttributeError):
        pass
