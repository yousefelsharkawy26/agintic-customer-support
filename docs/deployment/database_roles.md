# Database Roles & Deployment

This application heavily relies on PostgreSQL Row-Level Security (RLS) for tenant isolation.

## The BYPASSRLS Constraint

In managed PostgreSQL environments (such as Neon or Supabase) and local superuser accounts (`postgres`), the default connection role is often granted the `BYPASSRLS` privilege.

If the FastAPI application connects using a role that has `BYPASSRLS`, **all Row-Level Security policies are silently ignored**, completely bypassing tenant isolation.

## Required Roles

To safely run this application in production, you must separate database responsibilities into two distinct roles:

1. **Owner Role (e.g., `neondb_owner`)**

   - **Purpose:** Database administration, table creation, migrations.
   - **Environment Variable:** `ALEMBIC_DATABASE_URL`
   - **Privileges:** `BYPASSRLS`, DDL, schema creation.

2. **Application Worker Role (e.g., `app_worker`)**
   - **Purpose:** FastAPI application runtime execution.
   - **Environment Variable:** `DATABASE_URL`
   - **Privileges:** `NOBYPASSRLS`, `CONNECT`, `USAGE`, and strictly DML (`SELECT, INSERT, UPDATE, DELETE`) on the application tables.

## Provisioning the `app_worker` Role

Before deploying the application, an administrator must execute the provisioning script against the database using the Owner role.

1. Connect to your database using the owner role (e.g., `neondb_owner`).
2. Run the SQL script located at `scripts/provision_app_role.sql`.
   ```bash
   psql $ALEMBIC_DATABASE_URL -f scripts/provision_app_role.sql
   ```
3. Update your `.env` or production environment variables:

   ```env
   # Used by FastAPI runtime
   DATABASE_URL=postgresql+asyncpg://app_worker:YOUR_SECURE_PASSWORD@your-db-host/customer_support

   # Used strictly by Alembic migrations
   ALEMBIC_DATABASE_URL=postgresql+asyncpg://neondb_owner:OWNER_PASSWORD@your-db-host/customer_support
   ```
