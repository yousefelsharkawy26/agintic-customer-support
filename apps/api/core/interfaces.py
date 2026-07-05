from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class MessageRole(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class LLMMessage:
    role: MessageRole
    content: str
    tool_calls: list[dict[str, Any]] | None = None
    tool_call_id: str | None = None
    name: str | None = None


@dataclass
class LLMConfig:
    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 0.9
    stop: list[str] | None = None


@dataclass
class LLMResponse:
    content: str
    model: str
    usage: dict[str, int] | None = None
    finish_reason: str | None = None


class LLMProvider(ABC):
    @abstractmethod
    async def generate(
        self, messages: list[LLMMessage], config: LLMConfig | None = None
    ) -> LLMResponse: ...

    @abstractmethod
    def generate_stream(
        self, messages: list[LLMMessage], config: LLMConfig | None = None
    ) -> AsyncIterator[str]: ...

    @abstractmethod
    async def count_tokens(self, messages: list[LLMMessage]) -> int: ...


@dataclass
class EmbeddingConfig:
    model: str = "text-embedding-3-large"
    dimensions: int = 1536


class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed(
        self, texts: list[str], config: EmbeddingConfig | None = None
    ) -> list[list[float]]: ...

    @abstractmethod
    async def embed_query(
        self, text: str, config: EmbeddingConfig | None = None
    ) -> list[float]: ...

    @abstractmethod
    async def count_tokens(self, texts: list[str]) -> int: ...


@dataclass
class VectorRecord:
    id: str
    vector: list[float]
    payload: dict[str, Any] = field(default_factory=dict)
    score: float | None = None


@dataclass
class SearchFilter:
    key: str
    value: Any
    operator: str = "eq"


@dataclass
class SearchResult:
    records: list[VectorRecord]


class VectorStore(ABC):
    @abstractmethod
    async def create_collection(self, name: str, vector_size: int) -> None: ...

    @abstractmethod
    async def upsert(self, collection: str, records: list[VectorRecord]) -> None: ...

    @abstractmethod
    async def search(
        self,
        collection: str,
        vector: list[float],
        limit: int = 10,
        filters: list[SearchFilter] | None = None,
    ) -> SearchResult: ...

    @abstractmethod
    async def delete(self, collection: str, ids: list[str]) -> None: ...

    @abstractmethod
    async def delete_collection(self, name: str) -> None: ...


@dataclass
class Document:
    id: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    chunks: list["Document"] | None = None


class DocumentLoader(ABC):
    @abstractmethod
    async def load(self, source: str) -> list[Document]: ...

    @abstractmethod
    def load_stream(self, source: str) -> AsyncIterator[Document]: ...


@dataclass
class ToolCall:
    name: str
    arguments: dict[str, Any]
    id: str | None = None


@dataclass
class ToolResult:
    tool_call_id: str
    output: str
    is_error: bool = False


class ToolProvider(ABC):
    @abstractmethod
    async def list_tools(self) -> list[dict[str, Any]]: ...

    @abstractmethod
    async def execute(self, tool_call: ToolCall) -> ToolResult: ...


@dataclass
class MemoryEntry:
    role: MessageRole
    content: str
    timestamp: float
    metadata: dict[str, Any] = field(default_factory=dict)


class MemoryProvider(ABC):
    """
    Abstract memory interface for conversation history.

    SERIALIZATION CONTRACT
    ----------------------
    Serialization of MemoryEntry (including nested fields such as metadata)
    is exclusively the responsibility of the concrete adapter implementation.
    Callers MUST pass fully-typed MemoryEntry objects with native Python types
    in all fields. Callers MUST NOT pre-serialize any field (e.g. by calling
    json.dumps on metadata) before calling add(). The adapter guarantees that
    get() returns MemoryEntry objects whose fields match the types declared in
    the MemoryEntry dataclass.
    """

    @abstractmethod
    async def add(self, conversation_id: str, entry: MemoryEntry) -> None: ...

    @abstractmethod
    async def get(self, conversation_id: str, limit: int = 50) -> list[MemoryEntry]: ...

    @abstractmethod
    async def clear(self, conversation_id: str) -> None: ...

    @abstractmethod
    async def search(
        self, conversation_id: str, query: str, limit: int = 10
    ) -> list[MemoryEntry]: ...


class CacheProvider(ABC):
    """
    Abstract cache interface.

    SERIALIZATION CONTRACT
    ----------------------
    Serialization is exclusively the responsibility of the concrete adapter
    implementation (e.g. RedisCacheProvider). Callers MUST pass native Python
    objects (dict, list, str, int, float, bool, None). Callers MUST NOT call
    json.dumps() or any other serializer before calling set(). The adapter
    guarantees that get() returns the same Python type that was passed to set().

    Violating this contract (pre-serializing before set, or post-deserializing
    after get) produces double-serialization: a JSON string stored inside a
    JSON string, requiring an extra json.loads() on read and masking bugs.
    """

    @abstractmethod
    async def get(self, key: str) -> Any | None: ...

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int | None = None) -> None: ...

    @abstractmethod
    async def delete(self, key: str) -> None: ...

    @abstractmethod
    async def exists(self, key: str) -> bool: ...


@dataclass
class Event:
    type: str
    data: dict[str, Any]
    tenant_id: str | None = None
    correlation_id: str | None = None


class EventBus(ABC):
    @abstractmethod
    async def publish(self, event: Event) -> None: ...

    @abstractmethod
    async def subscribe(
        self, event_type: str, handler: Callable[[Event], Awaitable[None]]
    ) -> None: ...

    @abstractmethod
    async def unsubscribe(
        self, event_type: str, handler: Callable[[Event], Awaitable[None]]
    ) -> None: ...
