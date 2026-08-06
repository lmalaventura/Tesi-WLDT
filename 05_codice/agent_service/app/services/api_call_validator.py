from dataclasses import dataclass
from datetime import datetime
import re
from typing import Any

from ..models import GeneratedApiCall
from .api_selector import RankedApiOperation
from .openapi_catalog import ApiOperation


PATH_PARAMETER_PATTERN = re.compile(r"\{([^{}]+)\}")


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """Problema individuato nella chiamata generata."""

    code: str
    location: str
    message: str


@dataclass(frozen=True, slots=True)
class ApiCallValidation:
    """Risultato della validazione semantica."""

    operation: ApiOperation | None
    issues: tuple[ValidationIssue, ...]

    @property
    def valid(self) -> bool:
        return self.operation is not None and not self.issues


class ApiCallValidator:
    """Valida una chiamata generata rispetto all'OpenAPI corrente."""

    def validate(
        self,
        generated_call: GeneratedApiCall,
        candidates: tuple[RankedApiOperation, ...],
        openapi_document: dict[str, Any],
    ) -> ApiCallValidation:
        """Controlla operazione, parametri e request body."""

        issues: list[ValidationIssue] = []

        selected_operation = next(
            (
                candidate.operation
                for candidate in candidates
                if (
                    candidate.operation.method
                    == generated_call.method
                    and candidate.operation.path
                    == generated_call.endpoint
                )
            ),
            None,
        )

        if selected_operation is None:
            issues.append(
                ValidationIssue(
                    code="operation_not_candidate",
                    location="method, endpoint",
                    message=(
                        "Il metodo e l'endpoint generati non "
                        "corrispondono a una delle operazioni candidate."
                    ),
                )
            )

            return ApiCallValidation(
                operation=None,
                issues=tuple(issues),
            )

        paths = openapi_document.get("paths")

        if not isinstance(paths, dict):
            issues.append(
                ValidationIssue(
                    code="invalid_openapi_paths",
                    location="openapi.paths",
                    message=(
                        "La specifica OpenAPI non contiene "
                        "una sezione paths valida."
                    ),
                )
            )

            return ApiCallValidation(
                operation=selected_operation,
                issues=tuple(issues),
            )

        path_item = paths.get(selected_operation.path)

        if not isinstance(path_item, dict):
            issues.append(
                ValidationIssue(
                    code="operation_path_missing",
                    location="openapi.paths",
                    message=(
                        "Il path dell'operazione selezionata "
                        "non è presente nella specifica."
                    ),
                )
            )

            return ApiCallValidation(
                operation=selected_operation,
                issues=tuple(issues),
            )

        operation_document = path_item.get(
            selected_operation.method.lower()
        )

        if not isinstance(operation_document, dict):
            issues.append(
                ValidationIssue(
                    code="operation_method_missing",
                    location="openapi.paths",
                    message=(
                        "Il metodo dell'operazione selezionata "
                        "non è presente nella specifica."
                    ),
                )
            )

            return ApiCallValidation(
                operation=selected_operation,
                issues=tuple(issues),
            )

        parameters = _collect_parameters(
            document=openapi_document,
            path_item=path_item,
            operation_document=operation_document,
        )

        expected_path_names = set(
            PATH_PARAMETER_PATTERN.findall(
                selected_operation.path
            )
        )

        _validate_parameter_container(
            provided=generated_call.path_parameters,
            parameter_location="path",
            parameter_documents=parameters,
            additional_required_names=expected_path_names,
            issues=issues,
        )

        _validate_parameter_container(
            provided=generated_call.query_parameters,
            parameter_location="query",
            parameter_documents=parameters,
            additional_required_names=set(),
            issues=issues,
        )

        _validate_body(
            body=generated_call.body,
            operation_document=operation_document,
            document=openapi_document,
            issues=issues,
        )

        _validate_selector_semantics(
            body=generated_call.body,
            operation=selected_operation,
            issues=issues,
        )

        return ApiCallValidation(
            operation=selected_operation,
            issues=tuple(issues),
        )


def get_api_call_validator() -> ApiCallValidator:
    """Restituisce il validatore delle chiamate API."""

    return ApiCallValidator()


def _collect_parameters(
    document: dict[str, Any],
    path_item: dict[str, Any],
    operation_document: dict[str, Any],
) -> dict[tuple[str, str], dict[str, Any]]:
    collected: dict[tuple[str, str], dict[str, Any]] = {}

    for source in (
        path_item.get("parameters", []),
        operation_document.get("parameters", []),
    ):
        if not isinstance(source, list):
            continue

        for raw_parameter in source:
            parameter = _resolve_object(
                document=document,
                value=raw_parameter,
            )

            if not isinstance(parameter, dict):
                continue

            name = parameter.get("name")
            location = parameter.get("in")

            if not isinstance(name, str):
                continue

            if location not in {"path", "query"}:
                continue

            collected[(location, name)] = parameter

    return collected


def _validate_parameter_container(
    provided: dict[str, Any],
    parameter_location: str,
    parameter_documents: dict[
        tuple[str, str],
        dict[str, Any],
    ],
    additional_required_names: set[str],
    issues: list[ValidationIssue],
) -> None:
    allowed_names = {
        name
        for location, name in parameter_documents
        if location == parameter_location
    }

    if parameter_location == "path":
        allowed_names.update(additional_required_names)

    required_names = {
        name
        for (location, name), parameter
        in parameter_documents.items()
        if (
            location == parameter_location
            and parameter.get("required") is True
        )
    }

    required_names.update(additional_required_names)

    for required_name in sorted(required_names):
        if (
            required_name not in provided
            or _is_missing_value(provided[required_name])
        ):
            issues.append(
                ValidationIssue(
                    code=f"missing_{parameter_location}_parameter",
                    location=(
                        f"{parameter_location}Parameters."
                        f"{required_name}"
                    ),
                    message=(
                        f"Il parametro obbligatorio "
                        f"'{required_name}' non è stato fornito."
                    ),
                )
            )

    for provided_name in sorted(provided):
        if provided_name not in allowed_names:
            issues.append(
                ValidationIssue(
                    code=(
                        f"unexpected_"
                        f"{parameter_location}_parameter"
                    ),
                    location=(
                        f"{parameter_location}Parameters."
                        f"{provided_name}"
                    ),
                    message=(
                        f"Il parametro '{provided_name}' non è "
                        f"previsto tra i {parameter_location} parameter "
                        "dell'operazione selezionata."
                    ),
                )
            )


def _validate_body(
    body: Any,
    operation_document: dict[str, Any],
    document: dict[str, Any],
    issues: list[ValidationIssue],
) -> None:
    raw_request_body = operation_document.get("requestBody")

    if raw_request_body is None:
        if body is not None:
            issues.append(
                ValidationIssue(
                    code="unexpected_body",
                    location="body",
                    message=(
                        "L'operazione selezionata non prevede "
                        "un request body."
                    ),
                )
            )

        return

    request_body = _resolve_object(
        document=document,
        value=raw_request_body,
    )

    if not isinstance(request_body, dict):
        issues.append(
            ValidationIssue(
                code="invalid_request_body_definition",
                location="openapi.requestBody",
                message=(
                    "La definizione del request body "
                    "non può essere interpretata."
                ),
            )
        )

        return

    if body is None:
        if request_body.get("required") is True:
            issues.append(
                ValidationIssue(
                    code="missing_body",
                    location="body",
                    message=(
                        "L'operazione selezionata richiede "
                        "un request body."
                    ),
                )
            )

        return

    schema = _extract_json_schema(request_body)

    if schema is None:
        issues.append(
            ValidationIssue(
                code="missing_json_body_schema",
                location="openapi.requestBody",
                message=(
                    "Non è disponibile uno schema JSON "
                    "per il request body."
                ),
            )
        )

        return

    _validate_schema(
        value=body,
        schema=schema,
        document=document,
        location="body",
        issues=issues,
        reference_stack=frozenset(),
    )


def _extract_json_schema(
    request_body: dict[str, Any],
) -> dict[str, Any] | None:
    content = request_body.get("content")

    if not isinstance(content, dict):
        return None

    media_type = content.get("application/json")

    if not isinstance(media_type, dict):
        media_type = next(
            (
                value
                for key, value in content.items()
                if (
                    isinstance(key, str)
                    and key.endswith("+json")
                    and isinstance(value, dict)
                )
            ),
            None,
        )

    if not isinstance(media_type, dict):
        return None

    schema = media_type.get("schema")

    return schema if isinstance(schema, dict) else None


def _validate_schema(
    value: Any,
    schema: dict[str, Any],
    document: dict[str, Any],
    location: str,
    issues: list[ValidationIssue],
    reference_stack: frozenset[str],
) -> None:
    reference = schema.get("$ref")

    if isinstance(reference, str):
        if reference in reference_stack:
            return

        resolved = _resolve_reference(
            document=document,
            reference=reference,
        )

        if not isinstance(resolved, dict):
            issues.append(
                ValidationIssue(
                    code="unresolved_schema_reference",
                    location=location,
                    message=(
                        f"Impossibile risolvere il riferimento "
                        f"OpenAPI '{reference}'."
                    ),
                )
            )
            return

        _validate_schema(
            value=value,
            schema=resolved,
            document=document,
            location=location,
            issues=issues,
            reference_stack=(
                reference_stack | {reference}
            ),
        )
        return

    if value is None and (
        schema.get("nullable") is True
        or _schema_allows_null(schema)
    ):
        return

    for composed_key in ("oneOf", "anyOf"):
        composed_schemas = schema.get(composed_key)

        if isinstance(composed_schemas, list):
            if _matches_any_schema(
                value=value,
                schemas=composed_schemas,
                document=document,
                location=location,
                reference_stack=reference_stack,
            ):
                return

            issues.append(
                ValidationIssue(
                    code="schema_alternative_mismatch",
                    location=location,
                    message=(
                        "Il valore non rispetta nessuna "
                        "delle strutture ammesse."
                    ),
                )
            )
            return

    all_of = schema.get("allOf")

    if isinstance(all_of, list):
        for nested_schema in all_of:
            if isinstance(nested_schema, dict):
                _validate_schema(
                    value=value,
                    schema=nested_schema,
                    document=document,
                    location=location,
                    issues=issues,
                    reference_stack=reference_stack,
                )

    if "enum" in schema:
        enum_values = schema.get("enum")

        if (
            isinstance(enum_values, list)
            and value not in enum_values
        ):
            issues.append(
                ValidationIssue(
                    code="enum_mismatch",
                    location=location,
                    message=(
                        f"Il valore non appartiene all'insieme "
                        f"ammesso: {enum_values}."
                    ),
                )
            )
            return

    declared_type = schema.get("type")

    if isinstance(declared_type, list):
        matching_types = [
            item
            for item in declared_type
            if (
                isinstance(item, str)
                and _matches_type(value, item)
            )
        ]

        if not matching_types:
            issues.append(
                ValidationIssue(
                    code="type_mismatch",
                    location=location,
                    message=(
                        "Il valore non rispetta nessuno "
                        "dei tipi previsti dallo schema."
                    ),
                )
            )
            return

        effective_type = matching_types[0]

    elif isinstance(declared_type, str):
        effective_type = declared_type

        if not _matches_type(value, effective_type):
            issues.append(
                ValidationIssue(
                    code="type_mismatch",
                    location=location,
                    message=(
                        f"Era atteso un valore di tipo "
                        f"'{effective_type}'."
                    ),
                )
            )
            return

    elif "properties" in schema:
        effective_type = "object"

        if not isinstance(value, dict):
            issues.append(
                ValidationIssue(
                    code="type_mismatch",
                    location=location,
                    message="Era atteso un oggetto JSON.",
                )
            )
            return

    elif "items" in schema:
        effective_type = "array"

        if not isinstance(value, list):
            issues.append(
                ValidationIssue(
                    code="type_mismatch",
                    location=location,
                    message="Era atteso un array JSON.",
                )
            )
            return

    else:
        effective_type = None

    if effective_type == "object":
        _validate_object(
            value=value,
            schema=schema,
            document=document,
            location=location,
            issues=issues,
            reference_stack=reference_stack,
        )

    elif effective_type == "array":
        _validate_array(
            value=value,
            schema=schema,
            document=document,
            location=location,
            issues=issues,
            reference_stack=reference_stack,
        )

    elif effective_type == "string":
        _validate_string(
            value=value,
            schema=schema,
            location=location,
            issues=issues,
        )


def _validate_object(
    value: Any,
    schema: dict[str, Any],
    document: dict[str, Any],
    location: str,
    issues: list[ValidationIssue],
    reference_stack: frozenset[str],
) -> None:
    if not isinstance(value, dict):
        return

    properties = schema.get("properties")

    if not isinstance(properties, dict):
        properties = {}

    required = schema.get("required")

    if not isinstance(required, list):
        required = []

    for required_name in required:
        if (
            isinstance(required_name, str)
            and (
                required_name not in value
                or _is_missing_value(value[required_name])
            )
        ):
            issues.append(
                ValidationIssue(
                    code="missing_body_property",
                    location=f"{location}.{required_name}",
                    message=(
                        f"Il campo obbligatorio "
                        f"'{required_name}' non è presente."
                    ),
                )
            )

    additional_properties = schema.get(
        "additionalProperties"
    )

    for property_name, property_value in value.items():
        property_schema = properties.get(property_name)

        if isinstance(property_schema, dict):
            _validate_schema(
                value=property_value,
                schema=property_schema,
                document=document,
                location=f"{location}.{property_name}",
                issues=issues,
                reference_stack=reference_stack,
            )
            continue

        if isinstance(additional_properties, dict):
            _validate_schema(
                value=property_value,
                schema=additional_properties,
                document=document,
                location=f"{location}.{property_name}",
                issues=issues,
                reference_stack=reference_stack,
            )
            continue

        if properties and additional_properties is not True:
            issues.append(
                ValidationIssue(
                    code="unexpected_body_property",
                    location=f"{location}.{property_name}",
                    message=(
                        f"Il campo '{property_name}' non è "
                        "definito nello schema OpenAPI."
                    ),
                )
            )


def _validate_array(
    value: Any,
    schema: dict[str, Any],
    document: dict[str, Any],
    location: str,
    issues: list[ValidationIssue],
    reference_stack: frozenset[str],
) -> None:
    if not isinstance(value, list):
        return

    minimum_items = schema.get("minItems")

    if (
        isinstance(minimum_items, int)
        and len(value) < minimum_items
    ):
        issues.append(
            ValidationIssue(
                code="array_too_short",
                location=location,
                message=(
                    f"L'array deve contenere almeno "
                    f"{minimum_items} elementi."
                ),
            )
        )

    items_schema = schema.get("items")

    if not isinstance(items_schema, dict):
        return

    for index, item in enumerate(value):
        _validate_schema(
            value=item,
            schema=items_schema,
            document=document,
            location=f"{location}[{index}]",
            issues=issues,
            reference_stack=reference_stack,
        )


def _validate_string(
    value: Any,
    schema: dict[str, Any],
    location: str,
    issues: list[ValidationIssue],
) -> None:
    if not isinstance(value, str):
        return

    if schema.get("format") != "date-time":
        return

    normalized_value = value.replace("Z", "+00:00")

    try:
        parsed = datetime.fromisoformat(normalized_value)
    except ValueError:
        parsed = None

    if parsed is None or "T" not in value:
        issues.append(
            ValidationIssue(
                code="invalid_date_time",
                location=location,
                message=(
                    "Il valore non rispetta un formato "
                    "date-time ISO valido."
                ),
            )
        )


def _validate_selector_semantics(
    body: Any,
    operation: ApiOperation,
    issues: list[ValidationIssue],
) -> None:
    descriptor = (
        f"{operation.path} "
        f"{operation.operation_id or ''}"
    ).lower()

    if isinstance(body, list):
        body_items = body
    elif isinstance(body, dict):
        body_items = [body]
    else:
        return

    requires_property_name = "byname" in descriptor
    requires_property_id = "byid" in descriptor

    for index, item in enumerate(body_items):
        if not isinstance(item, dict):
            continue

        item_location = (
            f"body[{index}]"
            if isinstance(body, list)
            else "body"
        )

        if (
            requires_property_name
            and _is_missing_value(item.get("propertyName"))
        ):
            issues.append(
                ValidationIssue(
                    code="property_name_required",
                    location=f"{item_location}.propertyName",
                    message=(
                        "L'operazione selezionata interroga "
                        "le proprietà per nome e richiede "
                        "quindi il campo propertyName."
                    ),
                )
            )

        if (
            requires_property_id
            and _is_missing_value(item.get("propertyId"))
        ):
            issues.append(
                ValidationIssue(
                    code="property_id_required",
                    location=f"{item_location}.propertyId",
                    message=(
                        "L'operazione selezionata interroga "
                        "le proprietà per identificativo e richiede "
                        "quindi il campo propertyId."
                    ),
                )
            )


def _matches_any_schema(
    value: Any,
    schemas: list[Any],
    document: dict[str, Any],
    location: str,
    reference_stack: frozenset[str],
) -> bool:
    for nested_schema in schemas:
        if not isinstance(nested_schema, dict):
            continue

        nested_issues: list[ValidationIssue] = []

        _validate_schema(
            value=value,
            schema=nested_schema,
            document=document,
            location=location,
            issues=nested_issues,
            reference_stack=reference_stack,
        )

        if not nested_issues:
            return True

    return False


def _schema_allows_null(
    schema: dict[str, Any],
) -> bool:
    declared_type = schema.get("type")

    return (
        declared_type == "null"
        or (
            isinstance(declared_type, list)
            and "null" in declared_type
        )
    )


def _matches_type(value: Any, declared_type: str) -> bool:
    if declared_type == "null":
        return value is None

    if declared_type == "object":
        return isinstance(value, dict)

    if declared_type == "array":
        return isinstance(value, list)

    if declared_type == "string":
        return isinstance(value, str)

    if declared_type == "integer":
        return (
            isinstance(value, int)
            and not isinstance(value, bool)
        )

    if declared_type == "number":
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
        )

    if declared_type == "boolean":
        return isinstance(value, bool)

    return True


def _resolve_object(
    document: dict[str, Any],
    value: Any,
) -> Any:
    if not isinstance(value, dict):
        return value

    reference = value.get("$ref")

    if not isinstance(reference, str):
        return value

    return _resolve_reference(
        document=document,
        reference=reference,
    )


def _resolve_reference(
    document: dict[str, Any],
    reference: str,
) -> Any:
    prefix = "#/"

    if not reference.startswith(prefix):
        return None

    current: Any = document

    for raw_part in reference.removeprefix(prefix).split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")

        if not isinstance(current, dict):
            return None

        current = current.get(part)

    return current


def _is_missing_value(value: Any) -> bool:
    return (
        value is None
        or (
            isinstance(value, str)
            and not value.strip()
        )
    )