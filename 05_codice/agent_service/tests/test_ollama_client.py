import asyncio
import json

import httpx
import pytest

from app.services.ollama_client import (
    OllamaClient,
    OllamaResponseError,
    OllamaUnavailableError,
)
from app.services.prompt_builder import BuiltPrompt


def _prompt() -> BuiltPrompt:
    return BuiltPrompt(
        messages=(
            {
                "role": "system",
                "content": "Restituisci una chiamata REST.",
            },
            {
                "role": "user",
                "content": "Mostrami tutti i Digital Twin.",
            },
        ),
        output_schema={
            "type": "object",
        },
    )


def test_ollama_client_returns_structured_call() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/chat"

        payload = json.loads(request.content)

        assert payload["model"] == "qwen3:8b"
        assert payload["stream"] is False
        assert payload["think"] is False
        assert payload["options"] == {
            "temperature": 0,
        }
        assert payload["format"] == {
            "type": "object",
        }

        return httpx.Response(
            status_code=200,
            json={
                "model": "qwen3:8b",
                "message": {
                    "role": "assistant",
                    "content": json.dumps(
                        {
                            "method": "GET",
                            "endpoint": "/hdts",
                            "pathParameters": {},
                            "queryParameters": {},
                            "body": None,
                            "missingInformation": [],
                        }
                    ),
                },
                "done": True,
                "total_duration": 1200,
                "prompt_eval_count": 300,
                "eval_count": 40,
            },
        )

    client = OllamaClient(
        base_url="http://ollama:11434",
        model="qwen3:8b",
        timeout_seconds=5.0,
        transport=httpx.MockTransport(handler),
    )

    generation = asyncio.run(
        client.generate(_prompt())
    )

    assert generation.model == "qwen3:8b"
    assert generation.generated_call.method == "GET"
    assert generation.generated_call.endpoint == "/hdts"
    assert generation.total_duration_ns == 1200
    assert generation.prompt_eval_count == 300
    assert generation.eval_count == 40


def test_ollama_client_rejects_invalid_content() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json={
                "model": "qwen3:8b",
                "message": {
                    "role": "assistant",
                    "content": "questa non è una chiamata valida",
                },
            },
        )

    client = OllamaClient(
        base_url="http://ollama:11434",
        model="qwen3:8b",
        timeout_seconds=5.0,
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(
        OllamaResponseError,
        match="non rispetta lo schema",
    ):
        asyncio.run(client.generate(_prompt()))

def test_ollama_client_reports_http_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=500,
            json={
                "error": (
                    "llama-server reported "
                    "out-of-memory"
                ),
            },
        )

    client = OllamaClient(
        base_url="http://ollama:11434",
        model="qwen3:8b",
        timeout_seconds=5.0,
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(
        OllamaResponseError
    ) as exc_info:
        asyncio.run(
            client.generate(_prompt())
        )

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == (
        "llama-server reported out-of-memory"
    )

    assert str(exc_info.value) == (
        "Ollama ha restituito HTTP 500: "
        "llama-server reported out-of-memory"
    )

def test_ollama_client_reports_connection_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError(
            "Connection refused",
            request=request,
        )

    client = OllamaClient(
        base_url="http://ollama:11434",
        model="qwen3:8b",
        timeout_seconds=5.0,
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(
        OllamaUnavailableError,
        match="Impossibile comunicare con Ollama",
    ):
        asyncio.run(
            client.generate(_prompt())
        )