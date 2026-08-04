from app.services.api_selector import ApiSelector
from app.services.openapi_catalog import OpenApiCatalog


def _build_catalog() -> OpenApiCatalog:
    return OpenApiCatalog.from_document(
        {
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
                "/query/event/comparison": {
                    "post": {
                        "operationId": "compareProperties",
                        "summary": (
                            "Filter Digital Twins using "
                            "property comparisons."
                        ),
                        "requestBody": {
                            "required": True,
                        },
                    }
                },
                "/query/event/stats": {
                    "post": {
                        "operationId": "getPropertyStats",
                        "summary": (
                            "Calculate statistics for a property."
                        ),
                        "requestBody": {
                            "required": True,
                        },
                    }
                },
                "/query/event/values/history": {
                    "post": {
                        "operationId": "getPropertyHistory",
                        "summary": (
                            "Get the historical values "
                            "of a property."
                        ),
                        "requestBody": {
                            "required": True,
                        },
                    }
                },
                "/query/event/values/valuesByName": {
                    "post": {
                        "operationId": "getValuesByName",
                        "summary": (
                            "Get property values in a time range "
                            "using from and to."
                        ),
                        "requestBody": {
                            "required": True,
                        },
                    }
                },
            },
        }
    )


def _first_path(query: str) -> str:
    selector = ApiSelector()

    candidates = selector.select(
        query=query,
        catalog=_build_catalog(),
        limit=3,
    )

    assert candidates

    return candidates[0].operation.path


def test_selector_prefers_hdt_list() -> None:
    assert _first_path(
        "Mostrami tutti i Digital Twin disponibili."
    ) == "/hdts"


def test_selector_prefers_snapshot_for_current_values() -> None:
    assert _first_path(
        "Mostrami il valore corrente delle proprietà "
        'del Digital Twin con id "HDT-001".'
    ) == "/hdts/{id}/snapshot"


def test_selector_prefers_values_by_name_for_time_range() -> None:
    assert _first_path(
        "Mostrami lo storico della proprietà heartRate "
        "tra il 1 luglio 2026 e il 7 luglio 2026."
    ) == "/query/event/values/valuesByName"


def test_selector_prefers_comparison() -> None:
    assert _first_path(
        "Trova i Digital Twin per cui systolicPressure "
        "ha un valore maggiore di 150."
    ) == "/query/event/comparison"


def test_selector_prefers_stats() -> None:
    assert _first_path(
        "Calcola le statistiche della proprietà heartRate."
    ) == "/query/event/stats"


def test_selector_respects_limit() -> None:
    selector = ApiSelector()

    candidates = selector.select(
        query="Mostrami i valori delle proprietà.",
        catalog=_build_catalog(),
        limit=2,
    )

    assert len(candidates) == 2
    assert candidates[0].score >= candidates[1].score