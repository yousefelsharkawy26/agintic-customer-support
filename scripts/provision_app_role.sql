-- =============================================================================
-- Provision Application Database Roles
-- =============================================================================
-- Run this script as the database owner (neondb_owner / postgres superuser).
-- Execute once per environment before starting the application.
--
-- Usage:
--   psql $ALEMBIC_DATABASE_URL -f scripts/provision_app_role.sql
--
-- Two roles are created:
--
--   app_worker       — used by the FastAPI runtime for all HTTP traffic.
--                      NOBYPASSRLS: RLS is fully enforced.
--                      DML on tenant-data tables only.
--                      SELECT-only on bootstrap tables (tenants, tenant_api_keys).
--
--   app_provisioner  — used exclusively by the out-of-band provisioning CLI.
--                      NOBYPASSRLS: RLS is still enforced (role-scoped policy
--                      grants full access to bootstrap tables).
--                      No HTTP exposure whatsoever.
--
-- neondb_owner is NEVER used by the application at runtime.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 1. app_worker — FastAPI runtime role
-- ---------------------------------------------------------------------------
DROP ROLE IF EXISTS app_worker;
CREATE ROLE app_worker WITH
    LOGIN
    NOBYPASSRLS
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE
    PASSWORD 'CHANGE_ME_WORKER';

-- Schema access
GRANT CONNECT ON DATABASE neondb TO app_worker;
GRANT USAGE ON SCHEMA public TO app_worker;

-- DML on all current tables (bootstrap tables intentionally included for SELECT;
-- INSERT/UPDATE/DELETE on tenants & tenant_api_keys is blocked by RLS policy).
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_worker;
GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO app_worker;

-- Apply automatically to future tables created by Alembic (owner = neondb_owner)
ALTER DEFAULT PRIVILEGES FOR ROLE neondb_owner IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_worker;
ALTER DEFAULT PRIVILEGES FOR ROLE neondb_owner IN SCHEMA public
    GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO app_worker;

-- ---------------------------------------------------------------------------
-- 2. app_provisioner — out-of-band tenant lifecycle CLI role
-- ---------------------------------------------------------------------------
DROP ROLE IF EXISTS app_provisioner;
CREATE ROLE app_provisioner WITH
    LOGIN
    NOBYPASSRLS
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE
    PASSWORD 'CHANGE_ME_PROVISIONER';

-- Schema access
GRANT CONNECT ON DATABASE neondb TO app_provisioner;
GRANT USAGE ON SCHEMA public TO app_provisioner;

-- Bootstrap tables: full DML (INSERT/UPDATE/DELETE on tenants, tenant_api_keys).
-- Allowed by the tenant_provision / api_key_provision RLS policies (USING true).
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE tenants TO app_provisioner;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE tenant_api_keys TO app_provisioner;
GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO app_provisioner;

-- Explicitly NO grants on tenant-data tables — provisioner only touches bootstrap.

-- ---------------------------------------------------------------------------
-- 3. Verification
-- ---------------------------------------------------------------------------
SELECT
    rolname,
    rolbypassrls,
    rolsuper,
    rolcreatedb,
    rolcreaterole
FROM pg_roles
WHERE rolname IN ('app_worker', 'app_provisioner', 'neondb_owner')
ORDER BY rolname;
