from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from apps.api.core.config import settings
from apps.api.core.rls import bind_session_to_tenant

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_pre_ping=settings.db_pool_pre_ping,
)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncIterator[AsyncSession]:
    async with async_session_factory() as session:
        try:
            yield session
            if session.in_transaction():
                await session.commit()
        except Exception:
            if session.in_transaction():
                await session.rollback()
            raise


async def get_system_db() -> AsyncIterator[AsyncSession]:
    """
    Cross-tenant session via the system nil UUID.
    Provides a bound session that cannot read tenant rows.
    """
    async with async_session_factory() as session:
        bind_session_to_tenant(session, "00000000-0000-0000-0000-000000000000")
        try:
            yield session
            if session.in_transaction():
                await session.commit()
        except Exception:
            if session.in_transaction():
                await session.rollback()
            raise
