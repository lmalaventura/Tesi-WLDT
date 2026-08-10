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

def test_output_schema_constrains_snapshot_endpoint() -> None:
    operation = ApiOperation(
        method="GET",
        path="/hdts/{id}/snapshot",
        operation_id="hdts/{id}/snapshot",
        summary="Get HDT snapshot",
        description="",
        tags=("hdt",),
        required_path_parameters=("id",),
        required_query_parameters=(),
        request_body_required=False,
    )

    candidate = RankedApiOperation(
        operation=operation,
        score=30,
        matched_terms=("snapshot",),
    )

    document = {
        "openapi": "3.1.1",
        "paths": {
            "/hdts/{id}/snapshot": {
                "get": {
                    "operationId": (
                        "hdts/{id}/snapshot"
                    ),
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
            }
        },
    }

    prompt = PromptBuilder().build(
        query=(
            "Mostrami lo snapshot del Digital Twin "
            "HDT-001."
        ),
        candidates=(candidate,),
        openapi_document=document,
    )

    properties = prompt.output_schema[
        "properties"
    ]

    assert properties["method"] == {
        "type": "string",
        "enum": [
            "GET",
        ],
    }

    assert properties["endpoint"] == {
        "type": "string",
        "enum": [
            "/hdts/{id}/snapshot",
        ],
    }

    assert properties["body"] == {
        "type": "null",
    }

def test_output_schema_constrains_array_body() -> None:
    operation = ApiOperation(
        method="POST",
        path="/query/event/values/valuesByName",
        operation_id="query/event/values/byName",
        summary="Query Observations by Name",
        description="",
        tags=("query",),
        required_path_parameters=(),
        required_query_parameters=(),
        request_body_required=True,
    )

    candidate = RankedApiOperation(
        operation=operation,
        score=30,
        matched_terms=("history",),
    )

    document = {
        "openapi": "3.1.1",
        "paths": {
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
                                            "#/components/"
                                            "schemas/"
                                            "PropertyValuesRequest"
                                        )
                                    },
                                }
                            }
                        },
                    },
                }
            }
        },
        "components": {
            "schemas": {
                "PropertyValuesRequest": {
                    "type": "object",
                    "properties": {
                        "propertyName": {
                            "type": "string",
                        }
                    },
                }
            }
        },
    }

    prompt = PromptBuilder().build(
        query=(
            "Mostrami lo storico di heartRate."
        ),
        candidates=(candidate,),
        openapi_document=document,
    )

    properties = prompt.output_schema[
        "properties"
    ]

    assert properties["endpoint"] == {
        "type": "string",
        "enum": [
            "/query/event/values/valuesByName",
        ],
    }

    assert properties["body"] == {
        "type": "array",
        
    }

    candidate_constraint = (
        prompt.output_schema[
            "allOf"
        ][0]["oneOf"][0]
    )

    assert candidate_constraint[
        "properties"
    ]["method"] == {
        "type": "string",
        "enum": [
            "POST",
        ],
    }

    assert candidate_constraint[
        "properties"
    ]["endpoint"] == {
        "type": "string",
        "enum": [
            "/query/event/values/valuesByName",
        ],
    }

    assert candidate_constraint[
        "properties"
    ]["body"] == {
        "type": "array",
        "items": {
            "type": "object",
            "required": [
                "propertyName",
            ],
        },
    }

def test_output_schema_preserves_stats_required_fields() -> None:
    operation = ApiOperation(
        method="POST",
        path="/query/event/stats",
        operation_id="query/event/stats",
        summary="Query Aggregate Stats",
        description="",
        tags=("query",),
        required_path_parameters=(),
        required_query_parameters=(),
        request_body_required=True,
    )

    candidate = RankedApiOperation(
        operation=operation,
        score=30,
        matched_terms=("stats",),
    )

    document = {
        "openapi": "3.1.1",
        "paths": {
            "/query/event/stats": {
                "post": {
                    "operationId": "query/event/stats",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": (
                                        "#/components/schemas/"
                                        "PropertyStatsRequest"
                                    )
                                }
                            }
                        },
                    },
                }
            }
        },
        "components": {
            "schemas": {
                "PropertyStatsRequest": {
                    "type": "object",
                    "required": [
                        "hdtIds",
                        "modelIds",
                        "modelNames",
                        "propertyName",
                    ],
                    "properties": {
                        "hdtIds": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                        },
                        "modelIds": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                        },
                        "modelNames": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
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

    prompt = PromptBuilder().build(
        query=(
            "Calcola le statistiche di heartRate "
            "per tutti i Digital Twin."
        ),
        candidates=(candidate,),
        openapi_document=document,
    )

    candidate_constraint = (
        prompt.output_schema[
            "allOf"
        ][0]["oneOf"][0]
    )

    body_schema = candidate_constraint[
        "properties"
    ]["body"]

    assert body_schema["type"] == "object"

    assert body_schema["required"] == [
        "hdtIds",
        "modelIds",
        "modelNames",
        "propertyName",
    ]

    assert body_schema["properties"]["hdtIds"] == {
        "type": "array",
        "items": {
            "type": "string",
        },
    }

    assert body_schema[
        "properties"
    ]["propertyName"] == {
        "type": "string",
    }

def test_output_schema_does_not_expose_openapi_refs() -> None:
    operation = ApiOperation(
        method="POST",
        path="/query/event/comparison",
        operation_id="query/event/comparison",
        summary="Query Observations by comparisons",
        description="",
        tags=("query",),
        required_path_parameters=(),
        required_query_parameters=(),
        request_body_required=True,
    )

    candidate = RankedApiOperation(
        operation=operation,
        score=30,
        matched_terms=("comparison",),
    )

    document = {
        "openapi": "3.1.1",
        "paths": {
            "/query/event/comparison": {
                "post": {
                    "operationId": (
                        "query/event/comparison"
                    ),
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
            }
        },
        "components": {
            "schemas": {
                "ComparisonRequest": {
                    "type": "object",
                    "required": [
                        "comparisons",
                    ],
                    "properties": {
                        "comparisons": {
                            "type": "array",
                            "items": {
                                "$ref": (
                                    "#/components/schemas/"
                                    "PropertyComparisonDto"
                                )
                            },
                        }
                    },
                },
                "PropertyComparisonDto": {
                    "type": "object",
                    "required": [
                        "propertyName",
                        "comparison",
                        "value",
                    ],
                    "properties": {
                        "propertyName": {
                            "type": "string",
                        },
                        "comparison": {
                            "type": "string",
                        },
                        "value": {
                            "type": "number",
                        },
                    },
                },
            }
        },
    }

    prompt = PromptBuilder().build(
        query=(
            "Trova i Digital Twin con una "
            "proprietà maggiore di 150."
        ),
        candidates=(candidate,),
        openapi_document=document,
    )

    serialized_schema = json.dumps(
        prompt.output_schema
    )

    assert "#/components/schemas/" not in (
        serialized_schema
    )

    body_schema = (
        prompt.output_schema[
            "allOf"
        ][0]["oneOf"][0][
            "properties"
        ]["body"]
    )

    assert body_schema[
        "properties"
    ]["comparisons"] == {
        "type": "array",
        "items": {
            "type": "object",
        },
    }