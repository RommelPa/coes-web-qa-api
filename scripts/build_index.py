from __future__ import annotations

from pathlib import Path

from app.crawler import DEFAULT_SOURCE_URL, crawl_website
from app.indexer import build_index, save_index


def main() -> None:
    pages = crawl_website(DEFAULT_SOURCE_URL, max_pages=80)

    if not pages:
        raise RuntimeError("No pages were crawled from the COES documentation site.")

    index = build_index(pages, source_url=DEFAULT_SOURCE_URL)
    output_path = Path("data/index.json")
    save_index(index, output_path)

    metadata = index["metadata"]
    print(f"Index written to: {output_path}")
    print(f"Pages indexed: {metadata['page_count']}")
    print(f"Chunks created: {metadata['chunk_count']}")


if __name__ == "__main__":
    main()