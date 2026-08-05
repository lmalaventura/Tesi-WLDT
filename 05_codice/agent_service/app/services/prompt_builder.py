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

        output_schema = GeneratedApiCall.model_json_schema(
            by_alias=True
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