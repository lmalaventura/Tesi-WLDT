from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "WLDT LLM Agent Service",
        "version": "0.1.0",
    }


def test_query_stub() -> None:
    response = client.post(
        "/query",
        json={
            "query": "Mostrami tutti i Digital Twin disponibili.",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": "stub",
        "received_query": "Mostrami tutti i Digital Twin disponibili.",
        "message": (
            "Richiesta ricevuta correttamente. "
            "La pipeline LLM non è ancora collegata."
        ),
    }


def test_query_rejects_empty_text() -> None:
    response = client.post(
        "/query",
        json={"query": ""},
    )

    assert response.status_code == 422