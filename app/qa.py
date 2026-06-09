from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.indexer import load_index


DEFAULT_INDEX_PATH = Path("data/index.json")


def compact_text(value: str) -> str:
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def trim_text(value: str, max_chars: int = 800) -> str:
    value = compact_text(value)

    if len(value) <= max_chars:
        return value

    return value[: max_chars - 3].rstrip() + "..."


class WebQASystem:
    def __init__(self, index: dict[str, Any]) -> None:
        self.metadata: dict[str, Any] = index["metadata"]
        self.chunks: list[dict[str, Any]] = index["chunks"]

        if not self.chunks:
            raise ValueError("The QA index does not contain chunks.")

        self.texts = [chunk["text"] for chunk in self.chunks]
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            strip_accents="unicode",
            ngram_range=(1, 2),
            min_df=1,
        )
        self.matrix = self.vectorizer.fit_transform(self.texts)

    def ask(self, question: str, top_k: int = 3) -> dict[str, Any]:
        question = compact_text(question)

        if not question:
            raise ValueError("Question cannot be empty.")

        query_vector = self.vectorizer.transform([question])
        scores = cosine_similarity(query_vector, self.matrix).ravel()
        top_indices = scores.argsort()[::-1][:top_k]

        sources: list[dict[str, Any]] = []

        for index_position in top_indices:
            score = float(scores[index_position])

            if score <= 0:
                continue

            chunk = self.chunks[int(index_position)]
            sources.append(
                {
                    "chunk_id": chunk["chunk_id"],
                    "page_url": chunk["page_url"],
                    "page_title": chunk["page_title"],
                    "score": round(score, 4),
                    "text": trim_text(chunk["text"]),
                }
            )

        if not sources or sources[0]["score"] < 0.03:
            return {
                "answer": (
                    "No encontré información suficiente en la documentación "
                    "indexada de COES para responder esa pregunta."
                ),
                "confidence": "low",
                "sources": sources,
            }

        return {
            "answer": self._compose_answer(sources),
            "confidence": self._confidence_label(sources[0]["score"]),
            "sources": sources,
        }

    def _compose_answer(self, sources: list[dict[str, Any]]) -> str:
        best_source = sources[0]

        return (
            "Según la documentación indexada de COES, la información más "
            f"relevante encontrada es: {best_source['text']}"
        )

    def _confidence_label(self, score: float) -> str:
        if score >= 0.35:
            return "high"

        if score >= 0.15:
            return "medium"

        return "low"


def load_qa_system(index_path: Path = DEFAULT_INDEX_PATH) -> WebQASystem:
    index = load_index(index_path)
    return WebQASystem(index)