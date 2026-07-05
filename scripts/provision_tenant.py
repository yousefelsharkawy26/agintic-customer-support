#!/usr/bin/env python
"""
Tenant Provisioning CLI
=======================
Creates, deactivates, and rotates API keys for tenants.

This script runs OUT OF BAND — it is never called by the FastAPI application.
It connects using PROVISIONER_DATABASE_URL (the app_provisioner role), which
has NOBYPASSRLS but is granted INSERT/UPDATE/DELETE on the bootstrap tables
(tenants, tenant_api_keys) via a dedicated RLS policy.

The FastAPI app_worker role has NO write access to these tables.

Usage
-----
    # Create a new tenant
    uv run python scripts/provision_tenant.py create \\
        --name "Acme Corp" \\
        --slug "acme" \\
        --plan "pro"

    # Deactivate a tenant (does not delete data)
    uv run python scripts/provision_tenant.py deactivate --tenant-id <uuid>

    # Rotate the primary API key for a tenant
    uv run python scripts/provision_tenant.py rotate-key --tenant-id <uuid>

    # List all tenants
    uv run python scripts/provision_tenant.py list

Environment
-----------
Requires PROVISIONER_DATABASE_URL to be set (app_provisioner role).
Never uses DATABASE_URL (app_worker) or ALEMBIC_DATABASE_URL (neondb_owner).
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib

# ── Config ────────────────────────────────────────────────────────────────────
# Import provisioner URL from settings; fail loudly if missing.
import os
import secrets
import sys
import uuid
from datetime import UTC, datetime

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

load_dotenv()

PROVISIONER_URL = os.environ.get("PROVISIONER_DATABASE_URL")
if not PROVISIONER_URL:
    sys.exit(
        "PROVISIONER_DATABASE_URL is not set.\n"
        "This must point to the app_provisioner role, not neondb_owner or app_worker.\n"
        "Example: postgresql+asyncpg://app_provisioner:PASSWORD@host/db?ssl=require"
    )


# ── Database setup ─────────────────────────────────────────────────────────────
def _make_engine():
    return create_async_engine(PROVISIONER_URL, echo=False)


# ── Helpers ────────────────────────────────────────────────────────────────────
def _generate_api_key() -> tuple[str, str]:
    """Return (raw_key, sha256_hash). Only the hash is stored."""
    raw = "sk_live_" + secrets.token_urlsafe(32)
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    return raw, hashed


# ── Commands ───────────────────────────────────────────────────────────────────
async def cmd_create(name: str, slug: str, plan: str) -> None:
    engine = _make_engine()
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        # Verify we are running as app_provisioner (safety check)
        row = await session.execute(
            text("SELECT current_user, rolbypassrls FROM pg_roles WHERE rolname = current_user")
        )
        current_user, bypassrls = row.fetchone()
        if bypassrls:
            await engine.dispose()
            sys.exit(
                f"ABORT: Connected as '{current_user}' which has BYPASSRLS=true.\n"
                "PROVISIONER_DATABASE_URL must use the app_provisioner role (NOBYPASSRLS)."
            )

        # Check slug uniqueness
        existing = await session.execute(
            text("SELECT id FROM tenants WHERE slug = :slug"), {"slug": slug}
        )
        if existing.scalar_one_or_none():
            await engine.dispose()
            sys.exit(f"Tenant with slug '{slug}' already exists.")

        tenant_id = str(uuid.uuid4())
        raw_key, key_hash = _generate_api_key()

        now = datetime.now(UTC)
        await session.execute(
            text(
                "INSERT INTO tenants (id, name, slug, api_key, plan, is_active, created_at, updated_at) "
                "VALUES (:id, :name, :slug, :api_key, :plan, true, :now, :now)"
            ),
            {
                "id": tenant_id,
                "name": name,
                "slug": slug,
                "api_key": key_hash,  # store hash, not raw key
                "plan": plan,
                "now": now,
            },
        )
        await session.execute(
            text(
                "INSERT INTO tenant_api_keys (id, tenant_id, key_hash, label, is_active, created_at) "
                "VALUES (:id, :tenant_id, :key_hash, 'primary', true, :now)"
            ),
            {"id": str(uuid.uuid4()), "tenant_id": tenant_id, "key_hash": key_hash, "now": now},
        )
        await session.commit()

    await engine.dispose()

    print("\n✅  Tenant created successfully")
    print(f"   Tenant ID : {tenant_id}")
    print(f"   Name      : {name}")
    print(f"   Slug      : {slug}")
    print(f"   Plan      : {plan}")
    print("\n   API Key (store this — it will NOT be shown again):")
    print(f"   {raw_key}\n")


async def cmd_deactivate(tenant_id: str) -> None:
    engine = _make_engine()
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        result = await session.execute(
            text(
                "UPDATE tenants SET is_active = false, updated_at = now() WHERE id = :id RETURNING id"
            ),
            {"id": tenant_id},
        )
        if not result.scalar_one_or_none():
            await engine.dispose()
            sys.exit(f"Tenant {tenant_id!r} not found.")
        # Also revoke all active API keys
        await session.execute(
            text("UPDATE tenant_api_keys SET is_active = false WHERE tenant_id = :id"),
            {"id": tenant_id},
        )
        await session.commit()

    await engine.dispose()
    print(f"✅  Tenant {tenant_id} deactivated (data retained).")


async def cmd_rotate_key(tenant_id: str) -> None:
    engine = _make_engine()
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        # Verify tenant exists
        exists = await session.execute(
            text("SELECT id FROM tenants WHERE id = :id"), {"id": tenant_id}
        )
        if not exists.scalar_one_or_none():
            await engine.dispose()
            sys.exit(f"Tenant {tenant_id!r} not found.")

        raw_key, key_hash = _generate_api_key()
        now = datetime.now(UTC)

        # Revoke old keys
        await session.execute(
            text("UPDATE tenant_api_keys SET is_active = false WHERE tenant_id = :id"),
            {"id": tenant_id},
        )
        # Update primary api_key hash on tenant row
        await session.execute(
            text("UPDATE tenants SET api_key = :key_hash, updated_at = :now WHERE id = :id"),
            {"key_hash": key_hash, "now": now, "id": tenant_id},
        )
        # Insert new key record
        await session.execute(
            text(
                "INSERT INTO tenant_api_keys (id, tenant_id, key_hash, label, is_active, created_at) "
                "VALUES (:id, :tenant_id, :key_hash, 'rotated', true, :now)"
            ),
            {"id": str(uuid.uuid4()), "tenant_id": tenant_id, "key_hash": key_hash, "now": now},
        )
        await session.commit()

    await engine.dispose()
    print(f"\n✅  API key rotated for tenant {tenant_id}")
    print("   New API Key (store this — it will NOT be shown again):")
    print(f"   {raw_key}\n")


async def cmd_list() -> None:
    engine = _make_engine()
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        result = await session.execute(
            text(
                "SELECT id, name, slug, plan, is_active, created_at FROM tenants ORDER BY created_at DESC"
            )
        )
        rows = result.fetchall()

    await engine.dispose()

    if not rows:
        print("No tenants found.")
        return

    print(f"\n{'ID':<38} {'NAME':<25} {'SLUG':<20} {'PLAN':<10} {'ACTIVE':<8} CREATED")
    print("-" * 115)
    for r in rows:
        print(
            f"{r.id:<38} {r.name:<25} {r.slug:<20} {r.plan:<10} {str(r.is_active):<8} {r.created_at}"
        )
    print()


# ── Entry point ────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Tenant Provisioning CLI (app_provisioner role only)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # create
    p_create = subparsers.add_parser("create", help="Create a new tenant")
    p_create.add_argument("--name", required=True, help="Display name")
    p_create.add_argument("--slug", required=True, help="URL-safe unique identifier")
    p_create.add_argument("--plan", default="free", choices=["free", "pro", "enterprise"])

    # deactivate
    p_deactivate = subparsers.add_parser("deactivate", help="Deactivate a tenant")
    p_deactivate.add_argument("--tenant-id", required=True)

    # rotate-key
    p_rotate = subparsers.add_parser("rotate-key", help="Rotate the API key for a tenant")
    p_rotate.add_argument("--tenant-id", required=True)

    # list
    subparsers.add_parser("list", help="List all tenants")

    args = parser.parse_args()

    if args.command == "create":
        asyncio.run(cmd_create(args.name, args.slug, args.plan))
    elif args.command == "deactivate":
        asyncio.run(cmd_deactivate(args.tenant_id))
    elif args.command == "rotate-key":
        asyncio.run(cmd_rotate_key(args.tenant_id))
    elif args.command == "list":
        asyncio.run(cmd_list())


if __name__ == "__main__":
    main()
