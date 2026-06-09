from app.qa import WebQASystem


def test_qa_returns_relevant_source() -> None:
    index = {
        "metadata": {
            "source_url": "https://example.com/help",
            "built_at_utc": "2026-06-09T00:00:00+00:00",
            "page_count": 1,
            "chunk_count": 2,
        },
        "chunks": [
            {
                "chunk_id": "c1",
                "page_url": "https://example.com/help/demanda",
                "page_title": "Demanda",
                "text": (
                    "GET api/Demanda?fecha={fecha}. "
                    "Obtener demanda programada diaria COES."
                ),
            },
            {
                "chunk_id": "c2",
                "page_url": "https://example.com/help/frecuencia",
                "page_title": "Frecuencia",
                "text": (
                    "GET api/Frecuencia?fecha={fecha}. "
                    "Consulta del registro de frecuencia."
                ),
            },
        ],
    }

    qa_system = WebQASystem(index)
    result = qa_system.ask("¿Cómo consulto demanda por fecha?", top_k=1)

    assert result["sources"][0]["chunk_id"] == "c1"
    assert "demanda" in result["answer"].lower()


def test_qa_returns_low_confidence_when_no_match() -> None:
    index = {
        "metadata": {
            "source_url": "https://example.com/help",
            "built_at_utc": "2026-06-09T00:00:00+00:00",
            "page_count": 1,
            "chunk_count": 1,
        },
        "chunks": [
            {
                "chunk_id": "c1",
                "page_url": "https://example.com/help/demanda",
                "page_title": "Demanda",
                "text": "GET api/Demanda?fecha={fecha}. Obtener demanda COES.",
            },
        ],
    }

    qa_system = WebQASystem(index)
    result = qa_system.ask("¿Cuál es el precio del dólar?", top_k=1)

    assert result["confidence"] == "low"