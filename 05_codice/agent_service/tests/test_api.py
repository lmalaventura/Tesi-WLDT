from fastapi.testclient import TestClient

from app.main import app
from app.services.openapi_loader import get_openapi_loader
from app.models import GeneratedApiCall
from app.services.ollama_client import (
    OllamaGeneration,
    get_ollama_client,
)
from app.services.api_request_preparer import (
    PreparedApiRequest,
)
from app.services.rest_client import (
    PersistenceUnavailableError,
    RestExecution,
    get_rest_client,
)


client = TestClient(app)


class FakeOpenApiLoader:
    """Loader controllato utilizzato nei test dell'API."""

    spec_url = "http://persistence-service/openapi.yaml"

    async def load(self) -> dict:
        return {
            "openapi": "3.0.3",
            "paths": {
                "/hdts": {
                    "get": {
                        "operationId": "getHdts",
                        "summary": (
                            "List all available Human Digital Twins."
                        ),
                    }
                },
                "/hdts/{id}/snapshot": {
                    "get": {
                        "operationId": "getHdtSnapshot",
                        "summary": (
                            "Get the current property values "
                            "of a Human Digital Twin."
                        ),
                        "parameters": [
                            {
                                "name": "id",
                                "in": "path",
                                "required": True,
                            }
                        ],
                    }
                },
            },
        }

class FakeOllamaClient:
    """Client Ollama controllato per i test HTTP."""

    async def generate(self, prompt: object) -> OllamaGeneration:
        return OllamaGeneration(
            generated_call=GeneratedApiCall(
                method="GET",
                endpoint="/hdts",
                pathParameters={},
                queryParameters={},
                body=None,
                missingInformation=[],
            ),
            model="qwen3:8b",
            total_duration_ns=1200,
            prompt_eval_count=300,
            eval_count=40,
        )

class FakeRestClient:
    """Persistence Service simulato per i test HTTP."""

    async def execute(
        self,
        request: PreparedApiRequest,
    ) -> RestExecution:
        assert request.method == "GET"
        assert request.url == (
            "http://localhost:8081/hdts"
        )

        return RestExecution(
            status_code=200,
            content_type="application/json",
            body=[
                {
                    "id": "HDT-001",
                }
            ],
        )

class FakeUnavailableRestClient:
    """Simula l'indisponibilità del Persistence Service."""

    async def execute(
        self,
        request: PreparedApiRequest,
    ) -> RestExecution:
        raise PersistenceUnavailableError(
            "Impossibile comunicare con il "
            "Persistence Service."
        )

class FakeNotFoundRestClient:
    """Simula una risposta HTTP 404 del backend."""

    async def execute(
        self,
        request: PreparedApiRequest,
    ) -> RestExecution:
        return RestExecution(
            status_code=404,
            content_type="application/json",
            body={
                "message": "HDT not found",
            },
        )    
    
class FakeInvalidOllamaClient:
    """Produce intenzionalmente una chiamata non candidata."""

    async def generate(self, prompt: object) -> OllamaGeneration:
        return OllamaGeneration(
            generated_call=GeneratedApiCall(
                method="POST",
                endpoint="/hdts",
                pathParameters={},
                queryParameters={},
                body={},
                missingInformation=[],
            ),
            model="qwen3:8b",
            total_duration_ns=1200,
            prompt_eval_count=300,
            eval_count=40,
        )

def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "WLDT LLM Agent Service",
        "version": "0.1.0",
    }


def test_query_executes_validated_call() -> None:
    app.dependency_overrides[get_openapi_loader] = (
        lambda: FakeOpenApiLoader()
    )
    app.dependency_overrides[get_ollama_client] = (
        lambda: FakeOllamaClient()
    )
    app.dependency_overrides[get_rest_client] = (
    lambda: FakeRestClient()
    )

    try:
        response = client.post(
            "/query",
            json={
                "query": (
                    "Mostrami tutti i Digital Twin disponibili."
                ),
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "executed"
    assert data["model"] == "qwen3:8b"
    assert data["candidate_count"] >= 1
    assert data["candidates"][0]["path"] == "/hdts"
    assert data["generated_call"] == {
        "method": "GET",
        "endpoint": "/hdts",
        "pathParameters": {},
        "queryParameters": {},
        "body": None,
        "missingInformation": [],
    }
    assert data["validation"] == {
    "valid": True,
    "method": "GET",
    "endpoint": "/hdts",
    "issues": [],
    }
    assert data["metrics"] == {
        "total_duration_ns": 1200,
        "prompt_eval_count": 300,
        "eval_count": 40,
    }
    assert data["prepared_request"] == {
        "method": "GET",
        "url": "http://localhost:8081/hdts",
        "query_parameters": {},
        "body": None,
    }

    assert data["persistence_response"] == {
        "status_code": 200,
        "content_type": "application/json",
        "body": [
            {
                "id": "HDT-001",
            }
        ],
    }

def test_query_rejects_semantically_invalid_call() -> None:
    app.dependency_overrides[get_openapi_loader] = (
        lambda: FakeOpenApiLoader()
    )
    app.dependency_overrides[get_ollama_client] = (
        lambda: FakeInvalidOllamaClient()
    )

    try:
        response = client.post(
            "/query",
            json={
                "query": (
                    "Mostrami tutti i Digital Twin disponibili."
                ),
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 502

    detail = response.json()["detail"]

    assert detail["message"] == (
        "La chiamata generata non rispetta "
        "la specifica OpenAPI."
    )
    assert detail["issues"][0]["code"] == (
        "operation_not_candidate"
    )

def test_query_rejects_empty_text() -> None:
    response = client.post(
        "/query",
        json={"query": ""},
    )

    assert response.status_code == 422


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
    assert data["operations"][0]["path"] == "/hdts"
    assert data["operations"][1]["path"] == (
        "/hdts/{id}/snapshot"
    )

def test_query_reports_persistence_unavailable() -> None:
    app.dependency_overrides[get_openapi_loader] = (
        lambda: FakeOpenApiLoader()
    )
    app.dependency_overrides[get_ollama_client] = (
        lambda: FakeOllamaClient()
    )
    app.dependency_overrides[get_rest_client] = (
        lambda: FakeUnavailableRestClient()
    )

    try:
        response = client.post(
            "/query",
            json={
                "query": (
                    "Mostrami tutti i Digital Twin disponibili."
                ),
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Impossibile comunicare con il "
        "Persistence Service."
    )

def test_query_preserves_persistence_error_response() -> None:
    app.dependency_overrides[get_openapi_loader] = (
        lambda: FakeOpenApiLoader()
    )
    app.dependency_overrides[get_ollama_client] = (
        lambda: FakeOllamaClient()
    )
    app.dependency_overrides[get_rest_client] = (
        lambda: FakeNotFoundRestClient()
    )

    try:
        response = client.post(
            "/query",
            json={
                "query": (
                    "Mostrami tutti i Digital Twin disponibili."
                ),
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "executed"
    assert data["persistence_response"] == {
        "status_code": 404,
        "content_type": "application/json",
        "body": {
            "message": "HDT not found",
        },
    }