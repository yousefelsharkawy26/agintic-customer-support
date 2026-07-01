from collections.abc import AsyncIterator

from apps.api.core.interfaces import Document, DocumentLoader


class PDFDocumentLoader(DocumentLoader):
    async def load(self, source: str) -> list[Document]:
        content = await self._extract_text(source)
        return [
            Document(
                id=source,
                content=content,
                metadata={"source": source, "type": "pdf"},
            )
        ]

    async def load_stream(self, source: str) -> AsyncIterator[Document]:
        doc = await self.load(source)
        for d in doc:
            yield d

    async def _extract_text(self, path: str) -> str:
        try:
            import pypdf

            async with pypdf.PdfReader(path) as reader:
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                return text
        except ImportError:
            return f"[PDF content placeholder: {path}]"
        except Exception as e:
            return f"[PDF extraction error: {e}]"
