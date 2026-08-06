from app.models import GeneratedApiCall
from app.services.api_call_validator import ApiCallValidator
from app.services.api_selector import RankedApiOperation
from app.services.openapi_catalog import ApiOperation


def _document() -> dict:
    return {
        "openapi": "3.0.3",
        "paths": {
            "/hdts": {
                "get": {
                    "operationId": "hdts/get",
                }
            },
            "/hdts/{id}/snapshot": {
                "get": {
                    "operationId": "hdts/{id}/snapshot",
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "string",
                            },
                        }
                    ],
                }
            },
            "/query/event/values/valuesByName": {
                "post": {
                    "operationId": (
                        "query/event/values/byName"
                    ),
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {
                                        "$ref": (
                                            "#/components/schemas/"
                                            "PropertyValuesRequest"
                                        )
                                    },
                                }
                            }
                        },
                    },
                }
            },
        },
        "components": {
            "schemas": {
                "PropertyValuesRequest": {
                    "type": "object",
                    "properties": {
                        "hdtId": {
                            "type": "string",
                        },
                        "propertyId": {
                            "type": "string",
                        },
                        "propertyName": {
                            "type": "string",
                        },
                        "from": {
                            "type": [
                                "string",
                                "null",
                            ],
                            "format": "date-time",
                        },
                        "to": {
                            "type": [
                                "string",
                                "null",
                            ],
                            "format": "date-time",
                        },
                    },
                }
            }
        },
    }


def _candidate(
    method: str,
    path: str,
    operation_id: str,
) -> RankedApiOperation:
    return RankedApiOperation(
        operation=ApiOperation(
            method=method,
            path=path,
            operation_id=operation_id,
            summary="",
            description="",
            tags=(),
            required_path_parameters=(
                ("id",)
                if "{id}" in path
                else ()
            ),
            required_query_parameters=(),
            request_body_required=(
                method == "POST"
            ),
        ),
        score=10,
        matched_terms=(),
    )


def test_validator_accepts_simple_get() -> None:
    result = ApiCallValidator().validate(
        generated_call=GeneratedApiCall(
            method="GET",
            endpoint="/hdts",
            pathParameters={},
            queryParameters={},
            body=None,
            missingInformation=[],
        ),
        candidates=(
            _candidate(
                method="GET",
                path="/hdts",
                operation_id="hdts/get",
            ),
        ),
        openapi_document=_document(),
    )

    assert result.valid
    assert result.issues == ()


def test_validator_rejects_operation_not_in_candidates() -> None:
    result = ApiCallValidator().validate(
        generated_call=GeneratedApiCall(
            method="POST",
            endpoint="/hdts",
            pathParameters={},
            queryParameters={},
            body={},
            missingInformation=[],
        ),
        candidates=(
            _candidate(
                method="GET",
                path="/hdts",
                operation_id="hdts/get",
            ),
        ),
        openapi_document=_document(),
    )

    assert not result.valid
    assert result.issues[0].code == (
        "operation_not_candidate"
    )


def test_validator_rejects_missing_path_parameter() -> None:
    result = ApiCallValidator().validate(
        generated_call=GeneratedApiCall(
            method="GET",
            endpoint="/hdts/{id}/snapshot",
            pathParameters={},
            queryParameters={},
            body=None,
            missingInformation=[],
        ),
        candidates=(
            _candidate(
                method="GET",
                path="/hdts/{id}/snapshot",
                operation_id="hdts/{id}/snapshot",
            ),
        ),
        openapi_document=_document(),
    )

    issue_codes = {
        issue.code
        for issue in result.issues
    }

    assert not result.valid
    assert "missing_path_parameter" in issue_codes


def test_validator_rejects_unexpected_query_parameter() -> None:
    result = ApiCallValidator().validate(
        generated_call=GeneratedApiCall(
            method="GET",
            endpoint="/hdts",
            pathParameters={},
            queryParameters={
                "invented": "value",
            },
            body=None,
            missingInformation=[],
        ),
        candidates=(
            _candidate(
                method="GET",
                path="/hdts",
                operation_id="hdts/get",
            ),
        ),
        openapi_document=_document(),
    )

    issue_codes = {
        issue.code
        for issue in result.issues
    }

    assert not result.valid
    assert "unexpected_query_parameter" in issue_codes


def test_validator_rejects_object_when_array_is_required() -> None:
    result = ApiCallValidator().validate(
        generated_call=GeneratedApiCall(
            method="POST",
            endpoint=(
                "/query/event/values/valuesByName"
            ),
            pathParameters={},
            queryParameters={},
            body={
                "hdtId": "HDT-001",
                "propertyName": "heartRate",
            },
            missingInformation=[],
        ),
        candidates=(
            _candidate(
                method="POST",
                path=(
                    "/query/event/values/valuesByName"
                ),
                operation_id=(
                    "query/event/values/byName"
                ),
            ),
        ),
        openapi_document=_document(),
    )

    issue_codes = {
        issue.code
        for issue in result.issues
    }

    assert not result.valid
    assert "type_mismatch" in issue_codes


def test_validator_requires_property_name_for_by_name() -> None:
    result = ApiCallValidator().validate(
        generated_call=GeneratedApiCall(
            method="POST",
            endpoint=(
                "/query/event/values/valuesByName"
            ),
            pathParameters={},
            queryParameters={},
            body=[
                {
                    "hdtId": "HDT-001",
                    "propertyId": "heartRate",
                    "from": "2026-07-01T00:00:00Z",
                    "to": "2026-07-07T23:59:59Z",
                }
            ],
            missingInformation=[],
        ),
        candidates=(
            _candidate(
                method="POST",
                path=(
                    "/query/event/values/valuesByName"
                ),
                operation_id=(
                    "query/event/values/byName"
                ),
            ),
        ),
        openapi_document=_document(),
    )

    issue_codes = {
        issue.code
        for issue in result.issues
    }

    assert not result.valid
    assert "property_name_required" in issue_codes


def test_validator_accepts_values_by_name_body() -> None:
    result = ApiCallValidator().validate(
        generated_call=GeneratedApiCall(
            method="POST",
            endpoint=(
                "/query/event/values/valuesByName"
            ),
            pathParameters={},
            queryParameters={},
            body=[
                {
                    "hdtId": "HDT-001",
                    "propertyName": "heartRate",
                    "from": "2026-07-01T00:00:00Z",
                    "to": "2026-07-07T23:59:59Z",
                }
            ],
            missingInformation=[],
        ),
        candidates=(
            _candidate(
                method="POST",
                path=(
                    "/query/event/values/valuesByName"
                ),
                operation_id=(
                    "query/event/values/byName"
                ),
            ),
        ),
        openapi_document=_document(),
    )

    assert result.valid
    assert result.issues == ()