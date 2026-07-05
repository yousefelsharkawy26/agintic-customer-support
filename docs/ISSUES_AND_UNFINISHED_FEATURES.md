# Issues, Uncompleted Features, and Production Impact

Generated from the active workspace: `AginticCustomerSupport`

## How to read this document

- **Issue / Uncompleted Feature**: what appears incomplete or risky in the current codebase/worktree.
- **Current state**: why it is flagged.
- **Production impact**: likely consequences if shipped without finishing.
- **Suggested next step**: concrete work to resolve or reduce risk.

---

## 1. Unpushed local work is ahead of `origin/main`

- **Current state**:

  - Branch status: `main` is **ahead of `origin/main` by 3 commits**.
  - There are many modified files, including core backend pieces:
    - `apps/api/auth/deps.py`
    - `apps/api/auth/router.py`
    - `apps/api/conversation/manager.py`
    - `apps/api/conversation/models.py`
    - `apps/api/conversation/router.py`
    - `apps/api/core/config.py`
    - `apps/api/core/database.py`
    - `apps/api/core/interfaces.py`
    - `apps/api/main.py`
    - multiple `apps/api/*/router.py` and model files
  - There are also many untracked files, including new modules and dashboard files:
    - `apps/api/core/rls.py`
    - `apps/api/prompts/router.py`
    - new dashboard app structure under `apps/dashboard/src/app/(dashboard)/`
    - `apps/dashboard/src/app/api/...`
    - test migrations and utility scripts

- **Production impact**:

  - High risk if any of these changes touch auth, tenants, conversations, or request handling.
  - Without CI review on this exact diff, production deployment can introduce:
    - auth regressions
    - multi-tenant data-leakage bugs
    - conversation state corruption
    - dashboard breakage for end users

- **Suggested next step**:
  - Review the diff against `origin/main` before treating the branch as deployable.
  - Confirm which of the 3 ahead commits were approved for release.

---

## 2. Large dashboard restructure with deleted legacy pages

- **Current state**:

  - Several dashboard pages were deleted:
    - `apps/dashboard/src/app/page.tsx`
    - `apps/dashboard/src/app/analytics/page.tsx`
    - `apps/dashboard/src/app/conversations/page.tsx`
    - `apps/dashboard/src/app/knowledge-base/page.tsx`
    - `apps/dashboard/src/app/prompts/page.tsx`
    - `apps/dashboard/src/app/settings/page.tsx`
    - `apps/dashboard/src/app/tools/page.tsx`
    - `apps/dashboard/src/app/widget-config/page.tsx`
  - New/newer dashboard structures exist:
    - `apps/dashboard/src/app/(dashboard)/`
    - `apps/dashboard/src/app/login/`
  - New dashboard utilities/routes appear added:
    - `apps/dashboard/src/components/sidebar.tsx`
    - `apps/dashboard/src/components/topbar.tsx`
    - `apps/dashboard/src/lib/api-client.ts`
    - `apps/dashboard/src/lib/session.ts`
    - `apps/dashboard/src/middleware.ts`

- **Production impact**:

  - If the new dashboard routes are incomplete or only partially wired, users may encounter:
    - missing pages / 404s
    - broken navigation/auth flows
    - inconsistent behavior between old and new sections
  - This directly affects admin and operator UX, which is often treated as production-critical.

- **Suggested next step**:
  - Verify all dashboard route groups resolve in the Next.js app router.
  - Run the frontend build/tests if available.
  - Decide whether the old dashboard pages are intentionally retired or unintentionally removed.

---

## 3. Backend RLS and tenant isolation is newly introduced as untracked files

- **Current state**:

  - `apps/api/core/rls.py` is `untracked`.
  - Tenant-related modules show extended/untracked files:
    - `apps/api/tenants/models.py` is modified
    - `apps/api/tenants/models_ext.py` is `untracked`
    - `apps/api/tenants/router.py` is modified
  - Database initialization was changed:
    - `infra/postgres/init.sql` is modified

- **Production impact**:

  - Tenant isolation and RLS are high-impact areas.
  - If RLS binding is incorrect, incomplete, or missing for some code paths, this can cause:
    - cross-tenant data leakage
    - permission bypass
    - silent failures where one tenant sees another tenant’s data
  - Modified `init.sql` can change schema/bootstrap behavior in production databases if migrations are not synchronized.

- **Suggested next step**:
  - Inspect `apps/api/core/rls.py` and every session creation path to confirm binding is enforced everywhere.
  - Audit migration history vs `init.sql` to ensure release matches expected schema.
  - Add/inspect focused tests for tenant boundary enforcement.

---

## 4. Conversation/agent/auth modules modified without obvious paired test updates

- **Current state**:

  - Modified files include:
    - `apps/api/auth/deps.py`
    - `tests/conftest.py`
  - New/unreviewed backend modules include:
    - `apps/api/agent/models.py`
    - `apps/api/agent/router.py`
    - `apps/api/prompts/router.py`

- **Production impact**:

  - Auth and conversation handling affect every user request.
  - Modified `auth/deps.py` without explicit updated tests is risky for:
    - JWT/API key behavior
    - role resolution
    - dependency injection issues
  - New agent and prompt routers may be wired into `apps/api/main.py` without full test coverage, increasing production regression risk.

- **Suggested next step**:
  - Run backend tests after reviewing auth changes.
  - Add missing coverage for new routers and modified dependencies before release.

---

## 5. External service adapters and integrations changed

- **Current state**:

  - Modified files:
    - `apps/api/core/adapters/redis_cache.py`
    - `apps/api/core/adapters/redis_memory.py`
    - `apps/api/tools/router.py`
    - `apps/api/webhooks/engine.py`
    - `apps/api/webhooks/router.py`
    - `apps/api/webhooks/schemas.py`
    - `apps/api/webhooks/subscriber.py`
    - `apps/api/widget/router.py`

- **Production impact**:

  - Redis cache/memory changes can affect durability and hit/miss behavior.
  - Webhook changes affect delivery reliability and subscriber behavior.
  - Widget router changes affect user-facing customer experiences.
  - Any misconfiguration here can reduce availability or break integrations in production.

- **Suggested next step**:
  - Review intent of each change.
  - Verify adapter fallback behavior and webhook retry/hmac logic are unchanged or intentionally updated.

---

## 6. Tests and migration/test utilities present but not fully verified in this scan

- **Current state**:

  - New test files:
    - `tests/core/test_rls_session.py`
    - `tests/rag/test_semantic_cache.py`
    - `tests/test_rls_integration.py`
  - New/diagnostic scripts outside `tests/`:
    - `scripts/verify_rls_schema.py`
    - `scripts/provision_tenant.py`
    - `scripts/provision_app_role.sql`
    - `setup_test_user.py`
    - `verify_roles.py`
    - `create_neon_role.py`
    - `refactor_models.py`

- **Production impact**:

  - If the new RLS tests are incomplete, there is a risk of shipping tenant isolation without adequate regression coverage.
  - Diagnostic/provisioning scripts in tree can be mistaken for supported operational tooling if not clearly labeled.

- **Suggested next step**:
  - Ensure tests are run via the project test runner instead of standalone scripts.
  - Move one-off diagnostic scripts out of the production repository or clearly mark them as internal tooling.

---

## Summary Risk Matrix

| Area                   | Status                                        | Production Risk | Notes                                               |
| ---------------------- | --------------------------------------------- | --------------- | --------------------------------------------------- |
| Git/release state      | Unreviewed ahead commits + untracked changes  | High            | Cannot safely assume deployable without diff review |
| Dashboard refactor     | Deleted legacy pages + new route groups       | High-High       | May break user-facing admin experience              |
| RLS / tenant isolation | New untracked RLS file + tenant model changes | High            | Cross-tenant leakage risk                           |
| Auth/conversation      | Modified core dependency and router files     | High            | Affects most user requests                          |
| Webhooks/widgets       | Changed engines, routers, schemas             | Medium-High     | Affects delivery and embedding UX                   |
| RAG/agents             | New router files added                        | Medium          | Impact depends on whether live in main router       |
| Tests/migrations       | New tests exist but verification is ongoing   | Medium          | Coverage may not match surface area of changes      |

---

## Recommended Remediation Order

1. **Stabilize release state**

   - Identify whether the 3 ahead commits are approved.
   - Review full diff for auth, RLS, dashboard, and conversation changes.

2. **Harden tenant security**

   - Review `apps/api/core/rls.py`.
   - Confirm every `AsyncSession` goes through tenant binding.
   - Verify `init.sql` matches expected schema/migrations.

3. **Complete dashboard migration**

   - Audit deleted dashboard pages.
   - Validate new app router sections and login flow.
   - Fix any broken routes or auth middleware.

4. **Validate auth and conversation paths**

   - Run focused tests on changed auth and conversation modules.
   - Add missing regression tests for JWT, API keys, session assumptions.

5. **Verify external integrations**

   - Review Redis adapter and webhook changes.
   - Validate widget public routes and auth boundaries.

6. **Clean repo state**
   - Move one-off scripts out of the repo or clearly isolate them.
   - Ensure test artifacts and debug output files are not tracked.

---

## Document Owner Notes

If you want, I can extend this document with:

- a per-file change summary derived from `git diff --stat`
- a release checklist based on modified files only
- automated extraction of TODO/FIXME markers from the current worktree
