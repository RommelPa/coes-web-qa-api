from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.crawler import CrawledPage


def split_text_into_chunks(
    text: str,
    max_words: int = 160,
    overlap_words: int = 30,
    min_chars: int = 80,
) -> list[str]:
    words = text.split()

    if not words:
        return []

    if max_words <= overlap_words:
        raise ValueError("max_words must be greater than overlap_words")

    chunks: list[str] = []
    step = max_words - overlap_words

    for start in range(0, len(words), step):
        end = start + max_words
        chunk = " ".join(words[start:end]).strip()

        if len(chunk) >= min_chars:
            chunks.append(chunk)

        if end >= len(words):
            break

    return chunks


def build_index(
    pages: list[CrawledPage],
    source_url: str,
) -> dict[str, Any]:
    chunks: list[dict[str, Any]] = []

    for page_number, page in enumerate(pages, start=1):
        page_chunks = split_text_into_chunks(page.text)

        for chunk_number, chunk_text in enumerate(page_chunks, start=1):
            chunks.append(
                {
                    "chunk_id": f"p{page_number:03d}-c{chunk_number:03d}",
                    "page_url": page.url,
                    "page_title": page.title,
                    "text": chunk_text,
                }
            )

    return {
        "metadata": {
            "source_url": source_url,
            "built_at_utc": datetime.now(UTC).isoformat(),
            "page_count": len(pages),
            "chunk_count": len(chunks),
        },
        "chunks": chunks,
    }


def save_index(index: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(index, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_index(index_path: Path) -> dict[str, Any]:
    return json.loads(index_path.read_text(encoding="utf-8"))