import asyncio

from sqlalchemy import text

from apps.api.core.database import async_session_factory


async def setup_test_user():
    async with async_session_factory() as s:
        await s.execute(text("DROP ROLE IF EXISTS app_test_user;"))
        await s.execute(text("CREATE ROLE app_test_user WITH LOGIN PASSWORD 'testpassword';"))
        await s.execute(text("GRANT ALL ON SCHEMA public TO app_test_user;"))
        await s.execute(text("GRANT ALL ON ALL TABLES IN SCHEMA public TO app_test_user;"))
        await s.execute(text("GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO app_test_user;"))
        await s.execute(
            text("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO app_test_user;")
        )
        await s.commit()


if __name__ == "__main__":
    asyncio.run(setup_test_user())
