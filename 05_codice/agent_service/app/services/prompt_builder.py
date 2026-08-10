from dataclasses import dataclass
import json
from typing import Any

from ..models import GeneratedApiCall
from .api_selector import RankedApiOperation


class PromptBuildError(ValueError):
    """Errore durante la costruzione del prompt."""


@dataclass(frozen=True, slots=True)
class BuiltPrompt:
    """Messaggi e schema inviati al modello."""

    messages: tuple[dict[str, str], ...]
    output_schema: dict[str, Any]


class PromptBuilder:
    """Costruisce un prompt ristretto alle operazioni candidate."""

    def build(
        self,
        query: str,
        candidates: tuple[RankedApiOperation, ...],
        openapi_document: dict[str, Any],
    ) -> BuiltPrompt:
        """Costruisce messaggi e JSON Schema per Ollama."""

        if not candidates:
            raise PromptBuildError(
                "Non è possibile costruire il prompt senza candidati."
            )

        paths = openapi_document.get("paths")

        if not isinstance(paths, dict):
            raise PromptBuildError(
                "Il documento OpenAPI non contiene una sezione paths valida."
            )

        candidate_documents: list[dict[str, Any]] = []
        referenced_schema_names: set[str] = set()

        for rank, candidate in enumerate(candidates, start=1):
            operation = candidate.operation
            path_item = paths.get(operation.path)

            if not isinstance(path_item, dict):
                raise PromptBuildError(
                    f"Path non trovato nella specifica: {operation.path}."
                )

            operation_document = path_item.get(
                operation.method.lower()
            )

            if not isinstance(operation_document, dict):
                raise PromptBuildError(
                    "Operazione non trovata nella specifica: "
                    f"{operation.method} {operation.path}."
                )

            relevant_operation_data = {
                key: operation_document[key]
                for key in (
                    "operationId",
                    "summary",
                    "description",
                    "tags",
                    "parameters",
                    "requestBody",
                )
                if key in operation_document
            }

            candidate_document = {
                "rank": rank,
                "method": operation.method,
                "path": operation.path,
                "score": candidate.score,
                "matchedTerms": list(candidate.matched_terms),
                "pathLevelParameters": path_item.get(
                    "parameters",
                    [],
                ),
                "operation": relevant_operation_data,
            }

            candidate_documents.append(candidate_document)
            referenced_schema_names.update(
                _find_schema_references(candidate_document)
            )

        referenced_schemas = _collect_referenced_schemas(
            document=openapi_document,
            initial_names=referenced_schema_names,
        )

        output_schema = _build_output_schema(
            candidates=candidates,
            openapi_document=openapi_document,
        )

        system_message = (
            "Sei un componente di traduzione da linguaggio naturale "
            "a chiamate REST. Usa esclusivamente una delle operazioni "
            "candidate fornite. Le operazioni sono ordinate per "
            "rilevanza: la candidata con rank 1 è quella considerata "
            "più coerente con la richiesta. Seleziona la candidata con "
            "rank 1 quando il suo significato, il metodo HTTP e lo schema "
            "sono compatibili con la richiesta. Utilizza una candidata "
            "di rango inferiore soltanto quando quella di rank 1 è "
            "chiaramente incompatibile. "
            "Il metodo e l'endpoint devono appartenere alla stessa "
            "operazione candidata. Non inventare endpoint, parametri, "
            "campi o valori. Il campo endpoint deve contenere il path "
            "OpenAPI esatto, senza sostituire i placeholder. Inserisci "
            "i valori dei placeholder in pathParameters e i parametri "
            "della query in queryParameters. "
            "Il body deve rispettare esattamente il requestBody e gli "
            "schemi OpenAPI referenziati dall'operazione selezionata. "
            "Se lo schema radice del requestBody è un array, il campo "
            "body deve essere un array JSON, anche quando contiene un "
            "solo elemento. "
            "Quando l'utente indica il nome di una proprietà, utilizza "
            "propertyName. Utilizza propertyId soltanto quando viene "
            "fornito esplicitamente un identificatore della proprietà. "
            "Per /query/event/stats, hdtIds, modelIds e modelNames sono "
            "array di filtro obbligatori. Quando l'utente non restringe "
            "una di queste dimensioni, utilizza un array vuoto invece "
            "di omettere il campo, inventare identificatori o segnalarlo "
            "come informazione mancante. "
            "Usa null come body quando l'operazione non richiede un "
            "corpo. Quando manca un'informazione necessaria, non "
            "inventarla e inseriscila in missingInformation. "
            "Restituisci soltanto un oggetto conforme al JSON Schema "
            "richiesto."
        )

        user_content = json.dumps(
            {
                "userRequest": query,
                "candidateOperations": candidate_documents,
                "referencedSchemas": referenced_schemas,
                "outputSchema": output_schema,
            },
            ensure_ascii=False,
            indent=2,
        )

        return BuiltPrompt(
            messages=(
                {
                    "role": "system",
                    "content": system_message,
                },
                {
                    "role": "user",
                    "content": user_content,
                },
            ),
            output_schema=output_schema,
        )


def get_prompt_builder() -> PromptBuilder:
    """Restituisce il costruttore del prompt."""

    return PromptBuilder()


def _find_schema_references(value: Any) -> set[str]:
    names: set[str] = set()

    if isinstance(value, dict):
        reference = value.get("$ref")

        if isinstance(reference, str):
            prefix = "#/components/schemas/"

            if reference.startswith(prefix):
                names.add(reference.removeprefix(prefix))

        for nested_value in value.values():
            names.update(_find_schema_references(nested_value))

    elif isinstance(value, list):
        for item in value:
            names.update(_find_schema_references(item))

    return names


def _collect_referenced_schemas(
    document: dict[str, Any],
    initial_names: set[str],
) -> dict[str, Any]:
    components = document.get("components")

    if not isinstance(components, dict):
        return {}

    available_schemas = components.get("schemas")

    if not isinstance(available_schemas, dict):
        return {}

    collected: dict[str, Any] = {}
    pending = set(initial_names)

    while pending:
        schema_name = pending.pop()

        if schema_name in collected:
            continue

        schema = available_schemas.get(schema_name)

        if not isinstance(schema, dict):
            continue

        collected[schema_name] = schema

        nested_names = _find_schema_references(schema)

        pending.update(
            name
            for name in nested_names
            if name not in collected
        )

    return collected

def _build_output_schema(
    candidates: tuple[RankedApiOperation, ...],
    openapi_document: dict[str, Any],
) -> dict[str, Any]:
    """Adatta lo schema di output alle operazioni candidate."""

    output_schema = GeneratedApiCall.model_json_schema(
        by_alias=True
    )

    properties = output_schema.get("properties")

    if not isinstance(properties, dict):
        raise PromptBuildError(
            "Il JSON Schema di output non contiene "
            "proprietà valide."
        )

    methods = list(
        dict.fromkeys(
            candidate.operation.method
            for candidate in candidates
        )
    )

    endpoints = list(
        dict.fromkeys(
            candidate.operation.path
            for candidate in candidates
        )
    )

    properties["method"] = {
        "type": "string",
        "enum": methods,
    }

    properties["endpoint"] = {
        "type": "string",
        "enum": endpoints,
    }

    body_types = _collect_candidate_body_types(
        candidates=candidates,
        openapi_document=openapi_document,
    )

    if body_types:
        properties["body"] = {
            "type": (
                body_types[0]
                if len(body_types) == 1
                else list(body_types)
            ),
        }

    candidate_constraints = [
        _build_candidate_output_constraint(
            candidate=candidate,
            openapi_document=openapi_document,
        )
        for candidate in candidates
    ]

    output_schema["allOf"] = [
        {
            "oneOf": candidate_constraints,
        }
    ]

    return output_schema

def _build_candidate_output_constraint(
    candidate: RankedApiOperation,
    openapi_document: dict[str, Any],
) -> dict[str, Any]:
    """Collega metodo, endpoint e body della stessa candidata."""

    operation = candidate.operation

    constraint_properties: dict[str, Any] = {
        "method": {
            "type": "string",
            "enum": [
                operation.method,
            ],
        },
        "endpoint": {
            "type": "string",
            "enum": [
                operation.path,
            ],
        },
    }

    body_constraint = _build_candidate_body_constraint(
        candidate=candidate,
        openapi_document=openapi_document,
    )

    if body_constraint is not None:
        constraint_properties["body"] = body_constraint

    return {
        "type": "object",
        "properties": constraint_properties,
    }


def _build_candidate_body_constraint(
    candidate: RankedApiOperation,
    openapi_document: dict[str, Any],
) -> dict[str, Any] | None:
    """Costruisce i vincoli del body per una singola operazione."""

    operation = candidate.operation

    paths = openapi_document.get("paths")

    if not isinstance(paths, dict):
        return None

    path_item = paths.get(operation.path)

    if not isinstance(path_item, dict):
        return None

    operation_document = path_item.get(
        operation.method.lower()
    )

    if not isinstance(operation_document, dict):
        return None

    request_body = operation_document.get(
        "requestBody"
    )

    if not isinstance(request_body, dict):
        return {
            "type": "null",
        }

    body_schema = _extract_json_body_schema(
        request_body
    )

    if body_schema is None:
        return None

    resolved_schema = _resolve_root_schema(
        schema=body_schema,
        openapi_document=openapi_document,
    )

    body_types = _infer_schema_types(
        schema=resolved_schema,
        openapi_document=openapi_document,
    )

    if not body_types:
        return None

    if request_body.get("required") is not True:
        body_types.add("null")

    type_order = (
        "null",
        "object",
        "array",
        "string",
        "integer",
        "number",
        "boolean",
    )

    ordered_types = [
        schema_type
        for schema_type in type_order
        if schema_type in body_types
    ]

    body_constraint: dict[str, Any] = {
        "type": (
            ordered_types[0]
            if len(ordered_types) == 1
            else ordered_types
        ),
    }

    required_properties = resolved_schema.get(
        "required"
    )

    if (
        "object" in body_types
        and isinstance(required_properties, list)
    ):
        body_constraint["required"] = [
            property_name
            for property_name in required_properties
            if isinstance(property_name, str)
        ]

        schema_properties = resolved_schema.get(
            "properties"
        )

        if isinstance(schema_properties, dict):
            body_constraint["properties"] = (
                _build_output_properties(
                    properties=schema_properties,
                    openapi_document=openapi_document,
                )
            )

    descriptor = (
        f"{operation.path} "
        f"{operation.operation_id or ''}"
    ).lower()

    required_property: str | None = None

    if "byname" in descriptor:
        required_property = "propertyName"
    elif "byid" in descriptor:
        required_property = "propertyId"

    if required_property is None:
        return body_constraint

    if "array" in body_types:
        body_constraint["items"] = {
            "type": "object",
            "required": [
                required_property,
            ],
        }

    elif "object" in body_types:
        current_required = body_constraint.setdefault(
            "required",
            [],
        )

        if required_property not in current_required:
            current_required.append(
                required_property
            )

    return body_constraint

def _resolve_root_schema(
    schema: dict[str, Any],
    openapi_document: dict[str, Any],
) -> dict[str, Any]:
    """Risolve un eventuale $ref posto alla radice dello schema."""

    reference = schema.get("$ref")

    if not isinstance(reference, str):
        return schema

    prefix = "#/components/schemas/"

    if not reference.startswith(prefix):
        return schema

    schema_name = reference.removeprefix(prefix)

    components = openapi_document.get(
        "components"
    )

    if not isinstance(components, dict):
        return schema

    schemas = components.get("schemas")

    if not isinstance(schemas, dict):
        return schema

    referenced_schema = schemas.get(
        schema_name
    )

    if not isinstance(referenced_schema, dict):
        return schema

    return referenced_schema

def _build_output_properties(
    properties: dict[str, Any],
    openapi_document: dict[str, Any],
) -> dict[str, Any]:
    """Mantiene vincoli semplici senza propagare $ref OpenAPI."""

    output_properties: dict[str, Any] = {}

    for property_name, property_schema in properties.items():
        if not isinstance(property_schema, dict):
            continue

        resolved_schema = _resolve_root_schema(
            schema=property_schema,
            openapi_document=openapi_document,
        )

        output_property: dict[str, Any] = {}

        for keyword in (
            "type",
            "enum",
            "format",
        ):
            if keyword in resolved_schema:
                output_property[keyword] = (
                    resolved_schema[keyword]
                )

        items = resolved_schema.get("items")

        if isinstance(items, dict):
            item_types = _infer_schema_types(
                schema=items,
                openapi_document=openapi_document,
            )

            if item_types:
                ordered_item_types = [
                    schema_type
                    for schema_type in (
                        "null",
                        "object",
                        "array",
                        "string",
                        "integer",
                        "number",
                        "boolean",
                    )
                    if schema_type in item_types
                ]

                output_property["items"] = {
                    "type": (
                        ordered_item_types[0]
                        if len(ordered_item_types) == 1
                        else ordered_item_types
                    )
                }

        if output_property:
            output_properties[property_name] = (
                output_property
            )

    return output_properties

def _collect_candidate_body_types(
    candidates: tuple[RankedApiOperation, ...],
    openapi_document: dict[str, Any],
) -> tuple[str, ...] | None:
    """Ricava i tipi radice ammessi per i body dei candidati."""

    paths = openapi_document.get("paths")

    if not isinstance(paths, dict):
        return None

    collected_types: set[str] = set()
    unknown_schema = False

    for candidate in candidates:
        operation = candidate.operation

        path_item = paths.get(operation.path)

        if not isinstance(path_item, dict):
            unknown_schema = True
            continue

        operation_document = path_item.get(
            operation.method.lower()
        )

        if not isinstance(operation_document, dict):
            unknown_schema = True
            continue

        request_body = operation_document.get(
            "requestBody"
        )

        if not isinstance(request_body, dict):
            collected_types.add("null")
            continue

        if request_body.get("required") is not True:
            collected_types.add("null")

        body_schema = _extract_json_body_schema(
            request_body
        )

        if body_schema is None:
            unknown_schema = True
            continue

        inferred_types = _infer_schema_types(
            schema=body_schema,
            openapi_document=openapi_document,
        )

        if not inferred_types:
            unknown_schema = True
            continue

        collected_types.update(inferred_types)

    if unknown_schema:
        return None

    type_order = (
        "null",
        "object",
        "array",
        "string",
        "integer",
        "number",
        "boolean",
    )

    return tuple(
        schema_type
        for schema_type in type_order
        if schema_type in collected_types
    )


def _extract_json_body_schema(
    request_body: dict[str, Any],
) -> dict[str, Any] | None:
    """Estrae lo schema del request body JSON."""

    content = request_body.get("content")

    if not isinstance(content, dict):
        return None

    for media_type, media_definition in content.items():
        if not (
            media_type == "application/json"
            or media_type.endswith("+json")
        ):
            continue

        if not isinstance(media_definition, dict):
            continue

        schema = media_definition.get("schema")

        if isinstance(schema, dict):
            return schema

    return None


def _infer_schema_types(
    schema: dict[str, Any],
    openapi_document: dict[str, Any],
) -> set[str]:
    """Determina i tipi JSON radice di uno schema OpenAPI."""

    reference = schema.get("$ref")

    if isinstance(reference, str):
        prefix = "#/components/schemas/"

        if reference.startswith(prefix):
            schema_name = reference.removeprefix(prefix)

            components = openapi_document.get(
                "components"
            )

            if isinstance(components, dict):
                schemas = components.get("schemas")

                if isinstance(schemas, dict):
                    referenced_schema = schemas.get(
                        schema_name
                    )

                    if isinstance(
                        referenced_schema,
                        dict,
                    ):
                        return _infer_schema_types(
                            schema=referenced_schema,
                            openapi_document=(
                                openapi_document
                            ),
                        )

    declared_type = schema.get("type")

    if isinstance(declared_type, str):
        return {
            declared_type,
        }

    if isinstance(declared_type, list):
        return {
            schema_type
            for schema_type in declared_type
            if isinstance(schema_type, str)
        }

    for keyword in ("oneOf", "anyOf"):
        alternatives = schema.get(keyword)

        if not isinstance(alternatives, list):
            continue

        inferred: set[str] = set()

        for alternative in alternatives:
            if isinstance(alternative, dict):
                inferred.update(
                    _infer_schema_types(
                        schema=alternative,
                        openapi_document=(
                            openapi_document
                        ),
                    )
                )

        if inferred:
            return inferred

    if "properties" in schema:
        return {
            "object",
        }

    if "items" in schema:
        return {
            "array",
        }

    return set()