"""Refine RLS policies for bootstrap tables (tenants, tenant_api_keys)

Revision ID: a1b2c3d4e5f6
Revises: 2739e75eea89
Create Date: 2026-07-04

Rationale
---------
The initial migration applied a single FOR ALL policy on `tenants` and left
`tenant_api_keys` with no policy at all.  Both decisions were incorrect:

1. `tenants` FOR ALL with a USING clause blocks INSERT by app_worker entirely —
   a new tenant row has no pre-existing id to match.  The application role must
   be able to SELECT its own tenant row (for JWT validation) but must never
   INSERT / UPDATE / DELETE a tenant — that belongs to the provisioning plane.

2. `tenant_api_keys` had RLS enabled (FORCE ROW LEVEL SECURITY was implied by
   the table owner) but no policy was written, meaning app_worker would see 0
   rows even when authenticated — silent starvation rather than an error.

Fix
---
We introduce a second limited database role: app_provisioner.
  - app_worker      : NOBYPASSRLS  — runtime FastAPI connections
  - app_provisioner : NOBYPASSRLS  — out-of-band CLI tenant provisioning

Policy split for bootstrap tables:
  tenants
    SELECT  → app_worker   :  id = current_setting('app.tenant_id')::uuid
    ALL     → app_provisioner : unrestricted (provisioning plane)

  tenant_api_keys
    SELECT  → app_worker   :  tenant_id = current_setting('app.tenant_id')::uuid
    ALL     → app_provisioner : unrestricted

All other tenant-data tables keep their existing FOR ALL policies because
app_worker is always session-bound before touching them.
"""

from collections.abc import Sequence

from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: str | Sequence[str] | None = "2739e75eea89"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Replace bootstrap-table RLS policies with role-scoped variants."""

    # ── tenants ──────────────────────────────────────────────────────────────
    # Drop the original blanket policy (blocks INSERT for app_worker entirely).
    op.execute("DROP POLICY IF EXISTS tenant_isolation ON tenants;")

    # app_worker: may only SELECT its own tenant row (needed for JWT auth lookup).
    # INSERT / UPDATE / DELETE are categorically forbidden to the application role.
    op.execute(
        """
        CREATE POLICY tenant_read_own ON tenants
            FOR SELECT
            TO app_worker
            USING (id = current_setting('app.tenant_id', true)::uuid);
        """
    )

    # app_provisioner: unrestricted on the bootstrap table.
    # This role is used exclusively by the out-of-band provisioning CLI —
    # it never serves HTTP traffic and has NOBYPASSRLS itself, so RLS still
    # fires; the permissive USING (true) simply grants full access to this role.
    op.execute(
        """
        CREATE POLICY tenant_provision ON tenants
            FOR ALL
            TO app_provisioner
            USING (true)
            WITH CHECK (true);
        """
    )

    # ── tenant_api_keys ──────────────────────────────────────────────────────
    # Enable RLS — was missing from the initial migration.
    op.execute("ALTER TABLE tenant_api_keys ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE tenant_api_keys FORCE ROW LEVEL SECURITY;")

    # app_worker: read own tenant's keys (needed for API key validation).
    op.execute(
        """
        CREATE POLICY api_key_read_own ON tenant_api_keys
            FOR SELECT
            TO app_worker
            USING (tenant_id = current_setting('app.tenant_id', true)::uuid);
        """
    )

    # app_provisioner: full control (rotate keys, revoke, create initial key).
    op.execute(
        """
        CREATE POLICY api_key_provision ON tenant_api_keys
            FOR ALL
            TO app_provisioner
            USING (true)
            WITH CHECK (true);
        """
    )


def downgrade() -> None:
    """Restore the original single-policy state."""

    # ── tenant_api_keys ──────────────────────────────────────────────────────
    op.execute("DROP POLICY IF EXISTS api_key_provision ON tenant_api_keys;")
    op.execute("DROP POLICY IF EXISTS api_key_read_own ON tenant_api_keys;")
    op.execute("ALTER TABLE tenant_api_keys DISABLE ROW LEVEL SECURITY;")

    # ── tenants ──────────────────────────────────────────────────────────────
    op.execute("DROP POLICY IF EXISTS tenant_provision ON tenants;")
    op.execute("DROP POLICY IF EXISTS tenant_read_own ON tenants;")

    # Restore the original (flawed) blanket policy so downgrade is idempotent.
    op.execute(
        """
        CREATE POLICY tenant_isolation ON tenants
            FOR ALL
            USING (id = current_setting('app.tenant_id', true)::uuid)
            WITH CHECK (id = current_setting('app.tenant_id', true)::uuid);
        """
    )
