import pytest

from apps.api.rag.loaders import HTMLLoader, MarkdownLoader


class TestMarkdownLoader:
    @pytest.mark.asyncio
    async def test_loads_markdown(self) -> None:
        loader = MarkdownLoader()
        docs = await loader.load("# Hello\n\nWorld")
        assert len(docs) == 1
        assert docs[0].content == "# Hello\n\nWorld"
        assert docs[0].metadata["source_type"] == "markdown"


class TestHTMLLoader:
    @pytest.mark.asyncio
    async def test_strips_html_tags(self) -> None:
        loader = HTMLLoader()
        docs = await loader.load("<html><body><h1>Title</h1><p>Content</p></body></html>")
        assert len(docs) == 1
        assert "Title" in docs[0].content
        assert "Content" in docs[0].content
        assert "<html>" not in docs[0].content

    @pytest.mark.asyncio
    async def test_removes_script_and_style(self) -> None:
        loader = HTMLLoader()
        html = "<html><script>bad</script><style>.css{}</style><body>Good</body></html>"
        docs = await loader.load(html)
        assert "bad" not in docs[0].content
        assert ".css" not in docs[0].content
        assert "Good" in docs[0].content
