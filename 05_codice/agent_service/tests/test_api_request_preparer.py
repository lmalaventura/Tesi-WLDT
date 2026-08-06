import pytest

from app.models import GeneratedApiCall
from app.services.api_request_preparer import (
    ApiRequestPreparer,
    RequestPreparationError,
)


def _generated_call(
    *,
    method: str = "GET",
    endpoint: str = "/hdts",
    path_parameters: dict | None = None,
    query_parameters: dict | None = None,
    body: object | None = None,
) -> GeneratedApiCall:
    return GeneratedApiCall(
        method=method,
        endpoint=endpoint,
        pathParameters=path_parameters or {},
        queryParameters=query_parameters or {},
        body=body,
        missingInformation=[],
    )


def test_preparer_builds_simple_url() -> None:
    result = ApiRequestPreparer().prepare(
        generated_call=_generated_call(),
        base_url="http://localhost:8081",
    )

    assert result.method == "GET"
    assert result.url == "http://localhost:8081/hdts"
    assert result.query_parameters == {}
    assert result.body is None


def test_preparer_replaces_and_encodes_path_parameter() -> None:
    result = ApiRequestPreparer().prepare(
        generated_call=_generated_call(
            endpoint="/hdts/{id}/snapshot",
            path_parameters={
                "id": "HDT 001/A",
            },
        ),
        base_url="http://localhost:8081/",
    )

    assert result.url == (
        "http://localhost:8081/"
        "hdts/HDT%20001%2FA/snapshot"
    )


def test_preparer_preserves_query_parameters_and_body() -> None:
    body = {
        "propertyName": "heartRate",
    }

    result = ApiRequestPreparer().prepare(
        generated_call=_generated_call(
            method="POST",
            endpoint="/query/event/stats",
            query_parameters={
                "limit": 10,
            },
            body=body,
        ),
        base_url="http://localhost:8081",
    )

    assert result.method == "POST"
    assert result.query_parameters == {
        "limit": 10,
    }
    assert result.body == body


def test_preparer_rejects_missing_path_parameter() -> None:
    with pytest.raises(
        RequestPreparationError,
        match="Path parameter mancanti: id",
    ):
        ApiRequestPreparer().prepare(
            generated_call=_generated_call(
                endpoint="/hdts/{id}/snapshot",
            ),
            base_url="http://localhost:8081",
        )


def test_preparer_rejects_unexpected_path_parameter() -> None:
    with pytest.raises(
        RequestPreparationError,
        match="Path parameter non previsti: id",
    ):
        ApiRequestPreparer().prepare(
            generated_call=_generated_call(
                endpoint="/hdts",
                path_parameters={
                    "id": "HDT-001",
                },
            ),
            base_url="http://localhost:8081",
        )