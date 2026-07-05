-- Customer Support Platform - Database Schema
-- Applied automatically on first container start
--
-- DOCKER FAST BOOT vs PRODUCTION SCHEMA (TECHNICAL DEBT)
-- ======================================================
-- This init.sql file is acceptable for local Docker fast boot in this PR,
-- but it represents temporary technical debt. The long-term goal is a SINGLE
-- SOURCE OF TRUTH for the database schema.
--
-- In a future migration, Docker should migrate to using:
--      alembic upgrade head
--
-- Do NOT allow this schema definition and the Alembic migrations to diverge again!

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tenants
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    api_key VARCHAR(255) UNIQUE NOT NULL,
    plan VARCHAR(50) DEFAULT 'free',
    is_active BOOLEAN DEFAULT TRUE,
    settings TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tenants_slug ON tenants(slug);
CREATE INDEX IF NOT EXISTS idx_tenants_api_key ON tenants(api_key);

-- Tenant API Keys
CREATE TABLE IF NOT EXISTS tenant_api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    label VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_tenant_api_keys_tenant ON tenant_api_keys(tenant_id);

-- Row-Level Security
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenants FORCE ROW LEVEL SECURITY;

ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations FORCE ROW LEVEL SECURITY;

ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages FORCE ROW LEVEL SECURITY;

ALTER TABLE mcp_servers ENABLE ROW LEVEL SECURITY;
ALTER TABLE mcp_servers FORCE ROW LEVEL SECURITY;

ALTER TABLE webhook_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE webhook_configs FORCE ROW LEVEL SECURITY;


-- Tenant isolation policies
CREATE POLICY tenant_isolation ON tenants
    FOR ALL
    USING (id = current_setting('app.tenant_id', TRUE)::UUID);

CREATE POLICY conversation_isolation ON conversations
    FOR ALL
    USING (tenant_id = current_setting('app.tenant_id', TRUE)::UUID);

CREATE POLICY message_isolation ON messages
    FOR ALL
    USING (tenant_id = current_setting('app.tenant_id', TRUE)::UUID);

CREATE POLICY mcp_server_isolation ON mcp_servers
    FOR ALL
    USING (tenant_id = current_setting('app.tenant_id', TRUE)::UUID);

CREATE POLICY webhook_config_isolation ON webhook_configs
    FOR ALL
    USING (tenant_id = current_setting('app.tenant_id', TRUE)::UUID);
