import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


async def check():
    url = "postgresql+asyncpg://app_worker:s3Cur3_N30N_p4ssW0rD_XyZ!@ep-autumn-tree-athm4sjs-pooler.c-9.us-east-1.aws.neon.tech/neondb?ssl=require"
    engine = create_async_engine(url)
    async with engine.connect() as conn:
        res = await conn.execute(
            text("SELECT current_user, rolbypassrls FROM pg_roles WHERE rolname = current_user;")
        )
        row = res.fetchone()
        print(f"DATABASE_URL Connection -> User: {row[0]}, BYPASSRLS: {row[1]}")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(check())
