from collections.abc import AsyncIterator

from openai import AsyncOpenAI

from apps.api.core.interfaces import LLMConfig, LLMMessage, LLMProvider, LLMResponse


class OpenAILLMProvider(LLMProvider):
    def __init__(self, api_key: str, base_url: str | None = None) -> None:
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def generate(
        self, messages: list[LLMMessage], config: LLMConfig | None = None
    ) -> LLMResponse:
        cfg = config or LLMConfig()
        api_messages = self._to_openai_messages(messages)
        response = await self._client.chat.completions.create(
            model=cfg.model,
            messages=api_messages,  # type: ignore[arg-type]
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens,
            top_p=cfg.top_p,
            stop=cfg.stop,
        )
        choice = response.choices[0]
        raw_usage = response.usage
        usage = raw_usage.model_dump() if raw_usage else None
        return LLMResponse(
            content=choice.message.content or "",
            model=response.model,
            usage=usage,
            finish_reason=choice.finish_reason,
        )

    def generate_stream(
        self, messages: list[LLMMessage], config: LLMConfig | None = None
    ) -> AsyncIterator[str]:
        return self._stream(messages, config)

    async def _stream(
        self, messages: list[LLMMessage], config: LLMConfig | None = None
    ) -> AsyncIterator[str]:
        cfg = config or LLMConfig()
        api_messages = self._to_openai_messages(messages)
        stream = await self._client.chat.completions.create(
            model=cfg.model,
            messages=api_messages,  # type: ignore[arg-type]
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens,
            top_p=cfg.top_p,
            stop=cfg.stop,
            stream=True,
        )
        async for chunk in stream:  # type: ignore[union-attr]
            content = chunk.choices[0].delta.content or ""
            if content:
                yield content

    async def count_tokens(self, messages: list[LLMMessage]) -> int:
        api_messages = self._to_openai_messages(messages)
        response = await self._client.chat.completions.create(
            model="gpt-4o-mini",
            messages=api_messages,  # type: ignore[arg-type]
            max_tokens=1,
        )
        raw_usage = response.usage
        return raw_usage.prompt_tokens if raw_usage else 0  # type: ignore[no-any-return]

    def _to_openai_messages(self, messages: list[LLMMessage]) -> list[dict[str, str]]:
        return [{"role": m.role.value, "content": m.content} for m in messages]
