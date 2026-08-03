import pytest

from app.services.openapi_catalog import (
    OpenApiCatalog,
    OpenApiCatalogError,
)


def test_catalog_extracts_operations_and_parameters() -> None:
    document = {
        "openapi": "3.0.3",
        "paths": {
            "/hdts": {
                "get": {
                    "operationId": "getHdts",
                    "summary": "Restituisce i Digital Twin.",
                    "tags": ["HDT"],
                },
            },
            "/hdts/{id}/snapshot": {
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                    }
                ],
                "get": {
                    "operationId": "getHdtSnapshot",
                    "summary": "Restituisce lo snapshot.",
                    "parameters": [
                        {
                            "name": "includeMetadata",
                            "in": "query",
                            "required": True,
                        }
                    ],
                },
            },
            "/query/event/comparison": {
                "post": {
                    "operationId": "compareProperties",
                    "requestBody": {
                        "required": True,
                    },
                },
            },
        },
    }

    catalog = OpenApiCatalog.from_document(document)

    assert len(catalog.operations) == 3

    get_hdts = catalog.operations[0]

    assert get_hdts.method == "GET"
    assert get_hdts.path == "/hdts"
    assert get_hdts.operation_id == "getHdts"
    assert get_hdts.tags == ("HDT",)

    snapshot = catalog.operations[1]

    assert snapshot.required_path_parameters == ("id",)
    assert snapshot.required_query_parameters == (
        "includeMetadata",
    )

    comparison = catalog.operations[2]

    assert comparison.method == "POST"
    assert comparison.request_body_required is True


def test_catalog_rejects_document_without_paths() -> None:
    with pytest.raises(
        OpenApiCatalogError,
        match="sezione paths valida",
    ):
        OpenApiCatalog.from_document(
            {
                "openapi": "3.0.3",
            }
        )