from apps.api.core.interfaces import Document, LLMMessage, MessageRole
from apps.api.rag.pipeline import RAGContext, RAGPipeline


class TestRAGPipeline:
    def test_format_context_respects_max_chars(self) -> None:
        chunks = [
            Document(id="1", content="A" * 5000),
            Document(id="2", content="B" * 5000),
        ]
        ctx = RAGContext(chunks=chunks, query="test")
        formatted = RAGPipeline.format_context_static(ctx, max_chars=100)
        assert len(formatted) <= 200

    def test_build_messages_no_context(self) -> None:
        history = [LLMMessage(role=MessageRole.USER, content="Hi")]
        messages = RAGPipeline.build_messages_static("Hi", history)
        assert len(messages) == 2
        assert messages[0].role == MessageRole.SYSTEM
        assert messages[1].role == MessageRole.USER

    def test_extract_citations(self) -> None:
        text = "Hours are 9-5 [Source 1]. Support is 24/7 [Source 2]."
        citations = RAGPipeline.extract_citations(text)
        assert citations == ["1", "2"]

    def test_extract_citations_empty(self) -> None:
        text = "No citations here."
        citations = RAGPipeline.extract_citations(text)
        assert citations == []
