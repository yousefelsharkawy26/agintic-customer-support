import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

OWNER_URL = "postgresql+asyncpg://neondb_owner:npg_fY4hxdcyVBv1@ep-autumn-tree-athm4sjs-pooler.c-9.us-east-1.aws.neon.tech/neondb?ssl=require"


async def provision():
    engine = create_async_engine(OWNER_URL, isolation_level="AUTOCOMMIT")
    async with engine.connect() as conn:
        # Create app_provisioner
        await conn.execute(text("DROP ROLE IF EXISTS app_provisioner;"))
        await conn.execute(
            text(
                "CREATE ROLE app_provisioner WITH LOGIN NOBYPASSRLS NOSUPERUSER NOCREATEDB NOCREATEROLE "
                "PASSWORD 'Pr0v1s10n_S3cr3t_XyZ!';"
            )
        )
        await conn.execute(text("GRANT CONNECT ON DATABASE neondb TO app_provisioner;"))
        await conn.execute(text("GRANT USAGE ON SCHEMA public TO app_provisioner;"))
        await conn.execute(
            text("GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE tenants TO app_provisioner;")
        )
        await conn.execute(
            text(
                "GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE tenant_api_keys TO app_provisioner;"
            )
        )
        await conn.execute(
            text(
                "GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO app_provisioner;"
            )
        )

        # Verify both roles
        res = await conn.execute(
            text(
                "SELECT rolname, rolbypassrls, rolsuper FROM pg_roles "
                "WHERE rolname IN ('app_worker', 'app_provisioner', 'neondb_owner') ORDER BY rolname;"
            )
        )
        print("\nRole Verification:")
        print(f"{'ROLE':<20} {'BYPASSRLS':<12} {'SUPERUSER'}")
        print("-" * 45)
        for row in res.fetchall():
            print(f"{row[0]:<20} {str(row[1]):<12} {row[2]}")

    await engine.dispose()
    print("\n✅  app_provisioner provisioned on Neon.")


if __name__ == "__main__":
    asyncio.run(provision())
