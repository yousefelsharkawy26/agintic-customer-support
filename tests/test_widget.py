from apps.api.widget.models import OfflineMessage, WidgetSession


class TestWidgetSession:
    def test_session_creation(self) -> None:
        session = WidgetSession(
            tenant_id="tenant-1",
            visitor_id="visitor-1",
            locale="en",
            is_active=True,
        )
        assert session.locale == "en"

    def test_session_end(self) -> None:
        session = WidgetSession(
            tenant_id="t1",
            visitor_id="v1",
            is_active=True,
        )
        session.is_active = False
        assert session.is_active is False


class TestOfflineMessage:
    def test_offline_message_creation(self) -> None:
        msg = OfflineMessage(
            tenant_id="tenant-1",
            session_id="session-1",
            visitor_id="visitor-1",
            content="Help me please",
            message_type="text",
            delivered=False,
        )
        assert msg.content == "Help me please"
        assert msg.delivered is False

    def test_mark_delivered(self) -> None:
        msg = OfflineMessage(
            tenant_id="t1",
            session_id="s1",
            visitor_id="v1",
            content="Test",
            delivered=False,
        )
        msg.delivered = True
        assert msg.delivered is True

    def test_client_timestamp(self) -> None:
        msg = OfflineMessage(
            tenant_id="t1",
            session_id="s1",
            visitor_id="v1",
            content="Timed",
            client_ts="2026-07-01T12:00:00Z",
        )
        assert msg.client_ts == "2026-07-01T12:00:00Z"
