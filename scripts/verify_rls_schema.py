"""
Live database schema verification for SEC-04 RLS review.
Verifies:
  1. messages.tenant_id column existence and type
  2. All 4 Phase-1 tables have BOTH ENABLE + FORCE ROW LEVEL SECURITY
  3. All 4 Phase-1 policies exist with correct USING expressions
  4. The cs_app_bypassrls role existence (expected: NOT yet exist)
  5. Current database user and BYPASSRLS privilege status
  6. Column definitions for all Phase-1 RLS-protected tables
"""

import asyncio
import os

import asyncpg

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://neondb_owner:npg_fY4hxdcyVBv1@ep-autumn-tree-athm4sjs-pooler.c-9.us-east-1.aws.neon.tech/neondb?ssl=require",
)

# Convert SQLAlchemy URL to asyncpg DSN
dsn = (
    DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    if DATABASE_URL.startswith("postgresql+asyncpg://")
    else DATABASE_URL
)

PHASE1_TABLES = ["conversations", "messages", "mcp_servers", "webhook_configs"]

SECTION = "\n" + "=" * 70 + "\n"


async def run():
    print(f"Connecting to: {dsn.split('@')[1] if '@' in dsn else dsn}")
    conn = await asyncpg.connect(dsn)
    try:
        # ── 1. Current session identity ───────────────────────────────────
        print(SECTION + "1. SESSION IDENTITY")
        row = await conn.fetchrow(
            """
            SELECT current_user, session_user,
                   (SELECT rolbypassrls FROM pg_roles WHERE rolname = current_user)
                     AS has_bypassrls,
                   (SELECT rolsuper FROM pg_roles WHERE rolname = current_user)
                     AS is_superuser
            """
        )
        print(f"  current_user  : {row['current_user']}")
        print(f"  session_user  : {row['session_user']}")
        print(f"  has BYPASSRLS : {row['has_bypassrls']}")
        print(f"  is superuser  : {row['is_superuser']}")

        # ── 2. messages.tenant_id column ─────────────────────────────────
        print(SECTION + "2. messages.tenant_id COLUMN VERIFICATION")
        col = await conn.fetchrow(
            """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name   = 'messages'
              AND column_name  = 'tenant_id'
            """
        )
        if col:
            print("  FOUND   messages.tenant_id")
            print(f"    data_type   : {col['data_type']}")
            print(f"    is_nullable : {col['is_nullable']}")
            print(f"    default     : {col['column_default']}")
        else:
            print("  NOT FOUND — messages.tenant_id does NOT exist in the live DB!")

        # ── 3. All columns for Phase-1 tables ────────────────────────────
        print(SECTION + "3. COLUMN INVENTORY — PHASE 1 TABLES")
        for table in PHASE1_TABLES:
            cols = await conn.fetch(
                """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = $1
                ORDER BY ordinal_position
                """,
                table,
            )
            print(f"\n  [{table}]")
            for c in cols:
                print(
                    f"    {c['column_name']:<30} {c['data_type']:<20} nullable={c['is_nullable']}"
                )

        # ── 4. RLS ENABLE + FORCE status ─────────────────────────────────
        print(SECTION + "4. RLS ENABLE / FORCE STATUS — PHASE 1 TABLES")
        rls_status = await conn.fetch(
            """
            SELECT relname            AS table_name,
                   relrowsecurity     AS rls_enabled,
                   relforcerowsecurity AS rls_forced
            FROM   pg_class
            WHERE  relkind = 'r'
              AND  relname = ANY($1::text[])
            ORDER  BY relname
            """,
            PHASE1_TABLES,
        )
        all_correct = True
        for r in rls_status:
            status_enable = "✓ ENABLED " if r["rls_enabled"] else "✗ DISABLED"
            status_force = "✓ FORCED  " if r["rls_forced"] else "✗ NOT FORCED"
            ok = r["rls_enabled"] and r["rls_forced"]
            if not ok:
                all_correct = False
            flag = "OK" if ok else "PROBLEM"
            print(f"  [{flag}] {r['table_name']:<20} ENABLE={status_enable}  FORCE={status_force}")
        if all_correct:
            print("\n  All Phase 1 tables: ENABLE + FORCE confirmed ✓")

        # ── 5. RLS policy definitions ─────────────────────────────────────
        print(SECTION + "5. RLS POLICY DEFINITIONS")
        policies = await conn.fetch(
            """
            SELECT p.polname            AS policy_name,
                   c.relname            AS table_name,
                   p.polcmd             AS command,
                   pg_get_expr(p.polqual, p.polrelid) AS using_expr
            FROM   pg_policy  p
            JOIN   pg_class   c ON c.oid = p.polrelid
            WHERE  c.relname = ANY($1::text[])
            ORDER  BY c.relname, p.polname
            """,
            PHASE1_TABLES,
        )
        for p in policies:
            cmd_map = {"*": "ALL", "r": "SELECT", "a": "INSERT", "w": "UPDATE", "d": "DELETE"}
            cmd = cmd_map.get(p["command"], p["command"])
            print(f"\n  Policy: {p['policy_name']}")
            print(f"    Table  : {p['table_name']}")
            print(f"    Command: {cmd}")
            print(f"    USING  : {p['using_expr']}")
        if not policies:
            print("  WARNING: No policies found for Phase 1 tables!")

        # ── 6. cs_app_bypassrls role existence ───────────────────────────
        print(SECTION + "6. cs_app_bypassrls ROLE STATUS")
        role = await conn.fetchrow(
            "SELECT rolname, rolbypassrls FROM pg_roles WHERE rolname = 'cs_app_bypassrls'"
        )
        if role:
            print(f"  FOUND   cs_app_bypassrls  bypassrls={role['rolbypassrls']}")
        else:
            print(
                "  NOT FOUND — cs_app_bypassrls role does not yet exist (expected for pre-implementation)"
            )

        # ── 7. All roles with BYPASSRLS ───────────────────────────────────
        print(SECTION + "7. ALL ROLES WITH BYPASSRLS PRIVILEGE")
        bypass_roles = await conn.fetch(
            "SELECT rolname, rolsuper FROM pg_roles WHERE rolbypassrls = TRUE ORDER BY rolname"
        )
        if bypass_roles:
            for r in bypass_roles:
                print(f"  {r['rolname']:<30} superuser={r['rolsuper']}")
        else:
            print("  No non-superuser roles have BYPASSRLS (expected)")

        # ── 8. Deployment path: init.sql vs create_all discrepancy ───────
        print(SECTION + "8. ORM vs LIVE SCHEMA DISCREPANCY CHECK")
        # Check if messages.tenant_id has an index (would indicate it was
        # created by init.sql, not by SQLAlchemy create_all from the ORM model)
        idx = await conn.fetch(
            """
            SELECT i.relname AS index_name, ix.indisunique, ix.indisprimary
            FROM   pg_index    ix
            JOIN   pg_class    t  ON t.oid  = ix.indrelid
            JOIN   pg_class    i  ON i.oid  = ix.indexrelid
            JOIN   pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
            WHERE  t.relname = 'messages'
              AND  a.attname = 'tenant_id'
            """,
        )
        if idx:
            for i in idx:
                print(f"  Index on messages.tenant_id: {i['index_name']} unique={i['indisunique']}")
        else:
            print("  No index on messages.tenant_id (column may exist but not indexed)")

        print(SECTION + "VERIFICATION COMPLETE")

    finally:
        await conn.close()


asyncio.run(run())
