from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncSession

_BOUND_KEY = "rls.tenant_id"  # key in session.sync_session.info


def bind_session_to_tenant(session: AsyncSession, tenant_id: str) -> None:
    """
    Installs an after_begin listener on this session that executes
    set_config('app.tenant_id', tenant_id, true) inside every new transaction.

    The listener is scoped to this session instance via instance-level event
    dispatch. It cannot leak to other sessions. No explicit cleanup is needed
    (listener is garbage-collected with the session instance).

    Raises RuntimeError if called twice on the same session (double-bind guard).
    """
    sync_sess = session.sync_session

    # Public SQLAlchemy API — session.info is a per-instance dict
    if _BOUND_KEY in sync_sess.info:
        already = sync_sess.info[_BOUND_KEY]
        raise RuntimeError(
            f"Session is already bound to tenant {already!r}. "
            f"Cannot rebind to {tenant_id!r}. "
            "Create a new session for a different tenant."
        )
    sync_sess.info[_BOUND_KEY] = tenant_id

    # app.tenant_id is transaction-local because
    # set_config(..., true) is cleared after COMMIT/ROLLBACK.
    # Therefore it must be reapplied on every transaction.
    @event.listens_for(sync_sess, "after_begin")
    def _set_rls_tenant(ss, transaction, connection):  # noqa: ARG001
        connection.execute(
            text("SELECT set_config('app.tenant_id', :tid, true)"),
            {"tid": tenant_id},
        )
