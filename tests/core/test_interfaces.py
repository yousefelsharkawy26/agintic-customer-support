import pytest

from apps.api.core.interfaces import (
    CacheProvider,
    DocumentLoader,
    EmbeddingProvider,
    EventBus,
    LLMProvider,
    MemoryProvider,
    MessageRole,
    ToolProvider,
    VectorStore,
)

INTERFACES = [
    LLMProvider,
    EmbeddingProvider,
    VectorStore,
    DocumentLoader,
    ToolProvider,
    MemoryProvider,
    CacheProvider,
    EventBus,
]


class TestInterfaces:
    def test_abc_cannot_be_instantiated(self) -> None:
        for iface in INTERFACES:
            with pytest.raises(TypeError):
                iface()

    def test_message_role_values(self) -> None:
        assert MessageRole.SYSTEM.value == "system"
        assert MessageRole.USER.value == "user"
        assert MessageRole.ASSISTANT.value == "assistant"
        assert MessageRole.TOOL.value == "tool"

    def test_llm_response_dataclass(self) -> None:
        from apps.api.core.interfaces import LLMResponse

        resp = LLMResponse(
            content="hello", model="gpt-4o", usage={"prompt": 10}, finish_reason="stop"
        )
        assert resp.content == "hello"
        assert resp.model == "gpt-4o"

    def test_event_dataclass(self) -> None:
        from apps.api.core.interfaces import Event

        event = Event(type="test.event", data={"key": "val"}, tenant_id="t1")
        assert event.type == "test.event"
        assert event.data["key"] == "val"
