from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_metadata_returns_index_information() -> None:
    response = client.get("/metadata")

    assert response.status_code == 200
    assert response.json()["chunk_count"] > 0


def test_ask_returns_answer_and_sources() -> None:
    response = client.post(
        "/ask",
        json={
            "question": "¿Cómo consulto demanda por fecha?",
            "top_k": 2,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["answer"]
    assert len(body["sources"]) >= 1


def test_metrics_returns_prometheus_text() -> None:
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "coes_web_qa_chunks_indexed" in response.text