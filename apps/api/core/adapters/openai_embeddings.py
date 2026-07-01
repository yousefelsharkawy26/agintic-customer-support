from openai import AsyncOpenAI

from apps.api.core.interfaces import EmbeddingConfig, EmbeddingProvider


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: str, base_url: str | None = None) -> None:
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def embed(
        self, texts: list[str], config: EmbeddingConfig | None = None
    ) -> list[list[float]]:
        cfg = config or EmbeddingConfig()
        response = await self._client.embeddings.create(
            model=cfg.model,
            input=texts,
            dimensions=cfg.dimensions,
        )
        return [item.embedding for item in response.data]

    async def embed_query(self, text: str, config: EmbeddingConfig | None = None) -> list[float]:
        result = await self.embed([text], config)
        return result[0]

    async def count_tokens(self, texts: list[str]) -> int:
        response = await self._client.embeddings.create(
            model="text-embedding-3-large",
            input=texts,
        )
        raw_usage = response.usage
        return raw_usage.prompt_tokens if raw_usage else 0  # type: ignore[no-any-return]
