import re
from abc import ABC, abstractmethod

from apps.api.core.interfaces import Document


class Chunker(ABC):
    @abstractmethod
    def chunk(self, document: Document) -> list[Document]: ...


class RecursiveChunker(Chunker):
    def __init__(
        self, chunk_size: int = 1000, chunk_overlap: int = 200, separators: list[str] | None = None
    ) -> None:
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self._separators = separators or ["\n\n", "\n", ".", " ", ""]

    def chunk(self, document: Document) -> list[Document]:
        chunks: list[Document] = []
        text = document.content
        for i, segment in enumerate(self._split_text(text)):
            chunks.append(
                Document(
                    id=f"{document.id}:chunk:{i}",
                    content=segment,
                    metadata={**document.metadata, "chunk_index": i, "source_id": document.id},
                )
            )
        return chunks

    def _split_text(self, text: str) -> list[str]:
        segments: list[str] = []
        start = 0
        while start < len(text):
            end = min(start + self._chunk_size, len(text))
            if end < len(text):
                best_sep = -1
                for sep in self._separators:
                    idx = text.rfind(sep, start, end)
                    if idx > best_sep and sep != "":
                        best_sep = idx
                    elif sep == "":
                        break
                if best_sep > start:
                    end = best_sep + len(self._find_sep(text, start, end))
            segment = text[start:end].strip()
            if segment:
                segments.append(segment)
            new_start = end - self._chunk_overlap if end - self._chunk_overlap > start else end
            if new_start <= start:
                break
            start = new_start
        return segments or [text.strip()]

    def _find_sep(self, text: str, start: int, end: int) -> str:
        for sep in self._separators:
            if sep and text[start:end].rfind(sep) >= 0:
                return sep
        return ""


class MarkdownChunker(Chunker):
    def __init__(self, max_chunk_size: int = 1500) -> None:
        self._max_chunk_size = max_chunk_size

    def chunk(self, document: Document) -> list[Document]:
        chunks: list[Document] = []
        text = document.content
        sections = re.split(r"(?=^#{1,6}\s)", text, flags=re.MULTILINE)
        current = ""
        current_heading = ""
        for section in sections:
            if not section.strip():
                continue
            heading_match = re.match(r"^(#{1,6})\s+(.+)$", section, re.MULTILINE)
            heading = heading_match.group(0) if heading_match else ""

            if len(current) + len(section) > self._max_chunk_size and current:
                chunks.append(
                    Document(
                        id=f"{document.id}:chunk:{len(chunks)}",
                        content=current.strip(),
                        metadata={
                            **document.metadata,
                            "heading": current_heading,
                            "chunk_index": len(chunks),
                            "source_id": document.id,
                        },
                    )
                )
                current = heading
                current_heading = heading_match.group(2) if heading_match else ""
            current += "\n" + section if current else section
            if heading_match:
                current_heading = heading_match.group(2)
        if current.strip():
            chunks.append(
                Document(
                    id=f"{document.id}:chunk:{len(chunks)}",
                    content=current.strip(),
                    metadata={
                        **document.metadata,
                        "heading": current_heading,
                        "chunk_index": len(chunks),
                        "source_id": document.id,
                    },
                )
            )
        return chunks


class SemanticChunker(Chunker):
    def __init__(self, min_chunk_size: int = 200, max_chunk_size: int = 1500) -> None:
        self._min_chunk_size = min_chunk_size
        self._max_chunk_size = max_chunk_size

    def chunk(self, document: Document) -> list[Document]:
        paragraphs = re.split(r"\n\n+", document.content)
        chunks: list[Document] = []
        current = ""
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            if len(current) + len(para) > self._max_chunk_size and current:
                chunks.append(
                    Document(
                        id=f"{document.id}:chunk:{len(chunks)}",
                        content=current.strip(),
                        metadata={
                            **document.metadata,
                            "chunk_index": len(chunks),
                            "source_id": document.id,
                        },
                    )
                )
                current = para if len(para) < self._max_chunk_size else para[: self._max_chunk_size]
            else:
                current += "\n\n" + para if current else para
        if current.strip():
            chunks.append(
                Document(
                    id=f"{document.id}:chunk:{len(chunks)}",
                    content=current.strip(),
                    metadata={
                        **document.metadata,
                        "chunk_index": len(chunks),
                        "source_id": document.id,
                    },
                )
            )
        return chunks
