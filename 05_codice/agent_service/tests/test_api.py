from fastapi.testclient import TestClient

from app.main import app
from app.services.openapi_loader import get_openapi_loader


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

class FakeOpenApiLoader:
    """Loader controllato utilizzato nei test dell'API."""

    spec_url = "http://persistence-service/openapi.yaml"

    async def load(self) -> dict:
        return {
            "openapi": "3.0.3",
            "paths": {
                "/health": {
                    "get": {
                        "operationId": "health",
                        "summary": "Health check.",
                    }
                },
                "/hdts": {
                    "get": {
                        "operationId": "getHdts",
                        "summary": "Restituisce i Digital Twin.",
                    }
                },
            },
        }


def test_openapi_status() -> None:
    app.dependency_overrides[get_openapi_loader] = (
        lambda: FakeOpenApiLoader()
    )

    try:
        response = client.get("/openapi/status")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "source": "http://persistence-service/openapi.yaml",
        "openapi_version": "3.0.3",
        "path_count": 2,
    }

def test_openapi_operations() -> None:
    app.dependency_overrides[get_openapi_loader] = (
        lambda: FakeOpenApiLoader()
    )

    try:
        response = client.get("/openapi/operations")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["source"] == (
        "http://persistence-service/openapi.yaml"
    )
    assert data["count"] == 2
    assert data["operations"][0]["method"] == "GET"
    assert data["operations"][0]["path"] == "/hdts"
    assert data["operations"][1]["path"] == "/health"