import json

import pytest

from app.services.api_selector import RankedApiOperation
from app.services.openapi_catalog import ApiOperation
from app.services.prompt_builder import (
    PromptBuilder,
    PromptBuildError,
)


def _candidate() -> RankedApiOperation:
    operation = ApiOperation(
        method="POST",
        path="/query/event/comparison",
        operation_id="compareProperties",
        summary="Filter Digital Twins using comparisons.",
        description="",
        tags=("query",),
        required_path_parameters=(),
        required_query_parameters=(),
        request_body_required=True,
    )

    return RankedApiOperation(
        operation=operation,
        score=30,
        matched_terms=("comparison",),
    )


def test_prompt_contains_only_candidates_and_referenced_schemas() -> None:
    document = {
        "openapi": "3.0.3",
        "paths": {
            "/query/event/comparison": {
                "post": {
                    "operationId": "compareProperties",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": (
                                        "#/components/schemas/"
                                        "ComparisonRequest"
                                    )
                                }
                            }
                        },
                    },
                }
            },
            "/hdts": {
                "get": {
                    "operationId": "getHdts",
                }
            },
        },
        "components": {
            "schemas": {
                "ComparisonRequest": {
                    "type": "object",
                    "properties": {
                        "comparisons": {
                            "type": "array",
                            "items": {
                                "$ref": (
                                    "#/components/schemas/"
                                    "PropertyComparison"
                                )
                            },
                        }
                    },
                },
                "PropertyComparison": {
                    "type": "object",
                    "properties": {
                        "propertyName": {
                            "type": "string",
                        }
                    },
                },
                "UnusedSchema": {
                    "type": "object",
                },
            }
        },
    }

    prompt = PromptBuilder().build(
        query="Trova i Digital Twin con pressione maggiore di 150.",
        candidates=(_candidate(),),
        openapi_document=document,
    )

    payload = json.loads(prompt.messages[1]["content"])

    assert len(payload["candidateOperations"]) == 1
    assert payload["candidateOperations"][0]["rank"] == 1
    assert payload["candidateOperations"][0]["path"] == (
        "/query/event/comparison"
    )
    assert "ComparisonRequest" in payload["referencedSchemas"]
    assert "PropertyComparison" in payload["referencedSchemas"]
    assert "UnusedSchema" not in payload["referencedSchemas"]
    assert "/hdts" not in prompt.messages[1]["content"]
    assert prompt.output_schema["type"] == "object"

    system_message = prompt.messages[0]["content"]

    assert "rank 1" in system_message
    assert "deve essere un array JSON" in system_message
    assert "propertyName" in system_message
    assert "propertyId" in system_message


def test_prompt_rejects_empty_candidates() -> None:
    with pytest.raises(
        PromptBuildError,
        match="senza candidati",
    ):
        PromptBuilder().build(
            query="Richiesta",
            candidates=(),
            openapi_document={
                "openapi": "3.0.3",
                "paths": {},
            },
        )