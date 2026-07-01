from apps.api.core.adapters.anthropic_llm import AnthropicLLMProvider
from apps.api.core.adapters.google_llm import GoogleLLMProvider
from apps.api.core.adapters.openai_llm import OpenAILLMProvider
from apps.api.core.config import settings
from apps.api.core.interfaces import LLMProvider


class ModelRouter:
    def __init__(self) -> None:
        self._providers: dict[str, LLMProvider] = {}
        self._fallback_order: list[str] = ["openai", "anthropic", "google"]
        self._init_providers()

    def _init_providers(self) -> None:
        if settings.openai_api_key:
            self._providers["openai"] = OpenAILLMProvider(api_key=settings.openai_api_key)
        if settings.anthropic_api_key:
            self._providers["anthropic"] = AnthropicLLMProvider(api_key=settings.anthropic_api_key)
        if settings.google_api_key:
            self._providers["google"] = GoogleLLMProvider(api_key=settings.google_api_key)

    def select(
        self,
        _conversation_id: str | None = None,
        _model_tier: str = "standard",
        _tenant_id: str | None = None,
    ) -> LLMProvider:
        errors: list[str] = []
        for name in self._fallback_order:
            provider = self._providers.get(name)
            if provider is None:
                continue

            try:
                return provider
            except Exception as e:
                errors.append(f"{name}: {e}")
                continue

        msg = f"No LLM provider available. Tried: {', '.join(self._fallback_order)}"
        raise RuntimeError(msg)
