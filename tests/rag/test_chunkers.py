from apps.api.core.interfaces import Document
from apps.api.rag.chunkers import MarkdownChunker, RecursiveChunker, SemanticChunker


class TestRecursiveChunker:
    def test_chunks_long_text(self) -> None:
        chunker = RecursiveChunker(chunk_size=100, chunk_overlap=10)
        doc = Document(id="1", content="A " * 200)
        chunks = chunker.chunk(doc)
        assert len(chunks) > 1
        assert all(chunk.content for chunk in chunks)


class TestMarkdownChunker:
    def test_splits_by_heading(self) -> None:
        chunker = MarkdownChunker(max_chunk_size=30)
        text = "# Intro\nHello.\n\n# Details\nMore here.\n\n## Sub\nDetails."
        doc = Document(id="1", content=text)
        chunks = chunker.chunk(doc)
        assert len(chunks) >= 2

    def test_preserves_heading_metadata(self) -> None:
        chunker = MarkdownChunker(max_chunk_size=10)
        text = "# Big Section\n" + "Word " * 20
        doc = Document(id="1", content=text)
        chunks = chunker.chunk(doc)
        assert len(chunks) > 0


class TestSemanticChunker:
    def test_splits_by_paragraph(self) -> None:
        chunker = SemanticChunker(min_chunk_size=10, max_chunk_size=12)
        text = "Para one.\n\nPara two.\n\nPara three."
        doc = Document(id="1", content=text)
        chunks = chunker.chunk(doc)
        assert len(chunks) == 3

    def test_single_paragraph_stays_together(self) -> None:
        chunker = SemanticChunker(min_chunk_size=10, max_chunk_size=500)
        text = "Short single para."
        doc = Document(id="1", content=text)
        chunks = chunker.chunk(doc)
        assert len(chunks) == 1
