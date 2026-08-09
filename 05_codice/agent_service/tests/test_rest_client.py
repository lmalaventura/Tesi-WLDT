import asyncio
import json

import httpx
import pytest

from app.services.api_request_preparer import (
    PreparedApiRequest,
)
from app.services.rest_client import (
    PersistenceUnavailableError,
    RestClient,
)


def test_rest_client_executes_get_request() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/hdts"
        assert request.url.params["limit"] == "10"

        return httpx.Response(
            status_code=200,
            headers={
                "content-type": "application/json",
            },
            json=[
                {
                    "id": "HDT-001",
                }
            ],
        )

    client = RestClient(
        timeout_seconds=5.0,
        transport=httpx.MockTransport(handler),
    )

    result = asyncio.run(
        client.execute(
            PreparedApiRequest(
                method="GET",
                url="http://persistence:8081/hdts",
                query_parameters={
                    "limit": 10,
                },
                body=None,
            )
        )
    )

    assert result.status_code == 200
    assert result.content_type == "application/json"
    assert result.body == [
        {
            "id": "HDT-001",
        }
    ]


def test_rest_client_sends_json_body() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/query/event/stats"

        assert json.loads(request.content) == {
            "propertyName": "heartRate",
        }

        return httpx.Response(
            status_code=200,
            headers={
                "content-type": "application/json",
            },
            json={
                "count": 10,
            },
        )

    client = RestClient(
        timeout_seconds=5.0,
        transport=httpx.MockTransport(handler),
    )

    result = asyncio.run(
        client.execute(
            PreparedApiRequest(
                method="POST",
                url=(
                    "http://persistence:8081/"
                    "query/event/stats"
                ),
                query_parameters={},
                body={
                    "propertyName": "heartRate",
                },
            )
        )
    )

    assert result.status_code == 200
    assert result.body == {
        "count": 10,
    }


def test_rest_client_preserves_backend_error_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=404,
            headers={
                "content-type": "application/json",
            },
            json={
                "message": "HDT not found",
            },
        )

    client = RestClient(
        timeout_seconds=5.0,
        transport=httpx.MockTransport(handler),
    )

    result = asyncio.run(
        client.execute(
            PreparedApiRequest(
                method="GET",
                url=(
                    "http://persistence:8081/"
                    "hdts/HDT-999/snapshot"
                ),
                query_parameters={},
                body=None,
            )
        )
    )

    assert result.status_code == 404
    assert result.body == {
        "message": "HDT not found",
    }


def test_rest_client_reports_transport_failure() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError(
            "Connection refused",
            request=request,
        )

    client = RestClient(
        timeout_seconds=5.0,
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(
        PersistenceUnavailableError,
        match="Impossibile comunicare",
    ):
        asyncio.run(
            client.execute(
                PreparedApiRequest(
                    method="GET",
                    url="http://persistence:8081/hdts",
                    query_parameters={},
                    body=None,
                )
            )
        )