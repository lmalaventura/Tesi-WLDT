import asyncio

import httpx
import pytest

from app.services.openapi_loader import (
    OpenApiLoader,
    OpenApiLoadError,
)


def test_loader_accepts_valid_openapi() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == (
            "http://persistence-service/openapi.yaml"
        )

        return httpx.Response(
            status_code=200,
            text=(
                "openapi: 3.0.3\n"
                "paths:\n"
                "  /hdts:\n"
                "    get: {}\n"
            ),
        )

    loader = OpenApiLoader(
        spec_url="http://persistence-service/openapi.yaml",
        timeout_seconds=5.0,
        transport=httpx.MockTransport(handler),
    )

    document = asyncio.run(loader.load())

    assert document["openapi"] == "3.0.3"
    assert "/hdts" in document["paths"]


def test_loader_rejects_document_without_paths() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            text="openapi: 3.0.3\ninfo: {}\n",
        )

    loader = OpenApiLoader(
        spec_url="http://persistence-service/openapi.yaml",
        timeout_seconds=5.0,
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(
        OpenApiLoadError,
        match="sezione paths",
    ):
        asyncio.run(loader.load())