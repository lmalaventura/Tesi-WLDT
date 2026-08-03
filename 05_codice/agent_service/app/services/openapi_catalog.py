from dataclasses import dataclass
from typing import Any, Final


HTTP_METHODS: Final[tuple[str, ...]] = (
    "get",
    "post",
    "put",
    "patch",
    "delete",
    "options",
    "head",
    "trace",
)


class OpenApiCatalogError(ValueError):
    """Errore nella costruzione del catalogo delle operazioni."""


@dataclass(frozen=True, slots=True)
class ApiOperation:
    """Rappresentazione sintetica di un'operazione REST."""

    method: str
    path: str
    operation_id: str | None
    summary: str
    description: str
    tags: tuple[str, ...]
    required_path_parameters: tuple[str, ...]
    required_query_parameters: tuple[str, ...]
    request_body_required: bool


class OpenApiCatalog:
    """Catalogo normalizzato delle operazioni presenti nell'OpenAPI."""

    def __init__(self, operations: tuple[ApiOperation, ...]) -> None:
        self._operations = operations

    @property
    def operations(self) -> tuple[ApiOperation, ...]:
        """Restituisce tutte le operazioni del catalogo."""

        return self._operations

    @classmethod
    def from_document(
        cls,
        document: dict[str, Any],
    ) -> "OpenApiCatalog":
        """Costruisce il catalogo partendo da un documento OpenAPI."""

        paths = document.get("paths")

        if not isinstance(paths, dict):
            raise OpenApiCatalogError(
                "Il documento OpenAPI non contiene una sezione paths valida."
            )

        operations: list[ApiOperation] = []

        for path, path_item in paths.items():
            if not isinstance(path, str) or not isinstance(path_item, dict):
                continue

            inherited_parameters = _read_parameters(
                path_item.get("parameters")
            )

            for method in HTTP_METHODS:
                operation_document = path_item.get(method)

                if not isinstance(operation_document, dict):
                    continue

                operation_parameters = _read_parameters(
                    operation_document.get("parameters")
                )

                parameters = _merge_parameters(
                    inherited_parameters,
                    operation_parameters,
                )

                required_path_parameters = tuple(
                    parameter["name"]
                    for parameter in parameters
                    if (
                        parameter["location"] == "path"
                        and parameter["required"]
                    )
                )

                required_query_parameters = tuple(
                    parameter["name"]
                    for parameter in parameters
                    if (
                        parameter["location"] == "query"
                        and parameter["required"]
                    )
                )

                request_body = operation_document.get("requestBody")
                request_body_required = (
                    isinstance(request_body, dict)
                    and request_body.get("required") is True
                )

                operations.append(
                    ApiOperation(
                        method=method.upper(),
                        path=path,
                        operation_id=_optional_text(
                            operation_document.get("operationId")
                        ),
                        summary=_text(
                            operation_document.get("summary")
                        ),
                        description=_text(
                            operation_document.get("description")
                        ),
                        tags=_read_tags(
                            operation_document.get("tags")
                        ),
                        required_path_parameters=(
                            required_path_parameters
                        ),
                        required_query_parameters=(
                            required_query_parameters
                        ),
                        request_body_required=request_body_required,
                    )
                )

        operations.sort(
            key=lambda operation: (
                operation.path,
                operation.method,
            )
        )

        return cls(tuple(operations))


def _read_parameters(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []

    parameters: list[dict[str, Any]] = []

    for item in value:
        if not isinstance(item, dict):
            continue

        name = item.get("name")
        location = item.get("in")

        if not isinstance(name, str) or not isinstance(location, str):
            continue

        parameters.append(
            {
                "name": name,
                "location": location,
                "required": item.get("required") is True,
            }
        )

    return parameters


def _merge_parameters(
    inherited: list[dict[str, Any]],
    operation_parameters: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    merged: dict[tuple[str, str], dict[str, Any]] = {}

    for parameter in inherited:
        key = (
            parameter["name"],
            parameter["location"],
        )
        merged[key] = parameter

    for parameter in operation_parameters:
        key = (
            parameter["name"],
            parameter["location"],
        )
        merged[key] = parameter

    return list(merged.values())


def _read_tags(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()

    return tuple(
        tag
        for tag in value
        if isinstance(tag, str)
    )


def _text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _optional_text(value: Any) -> str | None:
    return value if isinstance(value, str) else None