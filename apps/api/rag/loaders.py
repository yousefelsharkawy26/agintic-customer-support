import re
import uuid
from collections.abc import AsyncIterator

from apps.api.core.interfaces import Document, DocumentLoader


class MarkdownLoader(DocumentLoader):
    async def load(self, source: str) -> list[Document]:
        doc_id = str(uuid.uuid4())
        return [
            Document(
                id=doc_id,
                content=source,
                metadata={"source_type": "markdown", "source_id": doc_id},
            )
        ]

    async def load_stream(self, source: str) -> AsyncIterator[Document]:
        doc = (await self.load(source))[0]
        yield doc


class HTMLLoader(DocumentLoader):
    async def load(self, source: str) -> list[Document]:
        doc_id = str(uuid.uuid4())
        text = self._html_to_text(source)
        return [
            Document(
                id=doc_id,
                content=text,
                metadata={"source_type": "html", "source_id": doc_id},
            )
        ]

    async def load_stream(self, source: str) -> AsyncIterator[Document]:
        doc = (await self.load(source))[0]
        yield doc

    def _html_to_text(self, html: str) -> str:
        text = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL)
        text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"&[a-zA-Z]+;", " ", text)
        text = re.sub(r"\n\s*\n", "\n\n", text)
        return text.strip()
