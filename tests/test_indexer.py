from app.crawler import CrawledPage
from app.indexer import build_index, split_text_into_chunks


def test_split_text_into_chunks_returns_content() -> None:
    text = " ".join(["mediciones"] * 250)

    chunks = split_text_into_chunks(text, max_words=100, overlap_words=20)

    assert len(chunks) >= 2
    assert all("mediciones" in chunk for chunk in chunks)


def test_build_index_creates_metadata_and_chunks() -> None:
    pages = [
        CrawledPage(
            url="https://example.com/help",
            title="Example Help",
            text="Esta página describe endpoints de mediciones y generación. " * 20,
        )
    ]

    index = build_index(pages, source_url="https://example.com/help")

    assert index["metadata"]["page_count"] == 1
    assert index["metadata"]["chunk_count"] >= 1
    assert index["chunks"][0]["page_url"] == "https://example.com/help"