# AginticCustomerSupport — Task Ledger

Last updated: 2026-07-05

## Completed
- [x] Audit outstanding issues and unfinished features
- [x] Produce `docs/ISSUES_AND_UNFINISHED_FEATURES.md`
- [x] Fix `tests/test_api_integration.py` route assertions under new tenant-router shape (`/api/v1/tenants/config`, `/quota`)
- [x] Add tenant-isolation coverage in `tests/test_api_integration.py`
- [x] Auth test DB-mocking path updated; successful standalone compile/build checks

## In Progress
- [ ] Repair `tests/test_auth.py` so auth middleware/tenancy isolation tests are deterministic:
  - Unauthenticated requests must hit real auth deps, returning 401
  - Authenticated success paths require explicit `override_db(db_module=...)`
  - Quota/monitoring/RLS tests must use mocked DB sessions, not external Postgres

## Pending — Priority Order

### P0 — Release blockers
1. **Resolve all remaining test failures** (`tests/test_auth.py`):
   - `patch` vs `AsyncClient.app` mistake
   - Missing `FakeResult.scalar()` in quota mock
   - Misconfigured dependency overrides for `get_current_tenant`
2. **Fix production auth regression on tenant config/quota routes**:
   - `/api/v1/tenants/config` must reject unauthenticated requests
   - `/api/v1/tenants/quota` must reject unauthenticated requests
3. **Run fresh, passing verification** for:
   - `tests/test_api_integration.py`
   - `tests/test_auth.py`
   - `tests/core/`, `tests/rag/`, `tests/events/`
   - Dashboard `tsc --noEmit` and build

### P1 — High-severity risks (from `docs/ISSUES_AND_UNFINISHED_FEATURES.md`)
4. **Cross-tenant data leakage**:
   - Verify RLS `set_config('app.tenant_id', ...)` is applied in every DB session
   - Ensure no path bypasses tenant filter (webhook ingestion, background jobs, migrations)
5. **Auth regressions**:
   - JWT and API-key validation paths in `apps/api/auth/deps.py` must both enforce `tenant_id`
   - Verify token expiration, rotation, and revocation flows
6. **Dashboard navigation breakage**:
   - Confirm legacy route deletions in `apps/dashboard/src/app/(dashboard)/` do not leave 404s
   - Fix any broken links from dashboard home/sidebar

### P2 — Integration reliability
7. **Webhook delivery retries/backoff** in `apps/api/webhooks/`
8. **RAG pipeline fault tolerance**:
   - Confirm fallback when Qdrant/OpenAI is unavailable
   - Validate semantic cache expiry/hit-miss logic (`tests/rag/test_semantic_cache.py`)
9. **Event bus startup noise**:
   - Fix Redis/asyncio-eventlet startup warning/deprecation
   - Add graceful shutdown for background consumers

### P3 — DX/ops debt
10. **Frontend lint/format consistency** across dashboard (`pnpm run lint`, `pnpm run typecheck`)
11. **Backend type safety** (`mypy --strict`, `pyright`)
12. **Structured logging audit** — ensure no PII leaks in `structlog` outputs
13. **Terraform AWS infra alignment** — reconcile infra state with app env vars

## Verification Checklist
- [ ] `pnpm run lint`
- [ ] `pnpm run typecheck`
- [ ] `pnpm run format`
- [ ] `tests/test_api_integration.py` — green
- [ ] `tests/test_auth.py` — green
- [ ] `tests/core/` — green
- [ ] `tests/rag/` — green
- [ ] `tests/events/` — green
- [ ] Dashboard build — green

## Notes
- Credentials/API keys must remain redacted; no secrets in committed tests.
- Backend uses Python 3.12/3.13; frontend uses TypeScript + Next.js.
- Local services: Postgres, Redis, Qdrant via `docker-compose`.
- Branch `main` is currently ahead of `origin/main` with uncommitted fixes.
