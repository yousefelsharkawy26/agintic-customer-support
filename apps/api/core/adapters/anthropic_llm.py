from collections.abc import AsyncIterator

from apps.api.core.interfaces import LLMConfig, LLMMessage, LLMProvider, LLMResponse


class AnthropicLLMProvider(LLMProvider):
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    async def generate(
        self, _messages: list[LLMMessage], _config: LLMConfig | None = None
    ) -> LLMResponse:
        return LLMResponse(content="", model="claude-3-5-sonnet")

    def generate_stream(
        self, _messages: list[LLMMessage], _config: LLMConfig | None = None
    ) -> AsyncIterator[str]:
        return self._stream(_messages, _config)

    async def _stream(
        self, _messages: list[LLMMessage], _config: LLMConfig | None = None
    ) -> AsyncIterator[str]:
        yield ""

    async def count_tokens(self, _messages: list[LLMMessage]) -> int:
        return 0
