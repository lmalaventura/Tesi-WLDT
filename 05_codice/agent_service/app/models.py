from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    """Risposta dell'endpoint di controllo del servizio."""

    status: Literal["ok"] = "ok"
    service: str
    version: str


class QueryRequest(BaseModel):
    """Richiesta in linguaggio naturale ricevuta dal client."""

    query: str = Field(
        min_length=1,
        max_length=5000,
        description="Richiesta dell'utente espressa in linguaggio naturale.",
    )


class CandidateOperationResponse(BaseModel):
    """Operazione OpenAPI candidata per la richiesta dell'utente."""

    method: str
    path: str
    operation_id: str | None
    summary: str
    score: int
    matched_terms: list[str]
    required_path_parameters: list[str]
    required_query_parameters: list[str]
    request_body_required: bool

class GeneratedApiCall(BaseModel):
    """Chiamata REST strutturata prodotta dal modello LLM."""

    model_config = ConfigDict(populate_by_name=True)

    method: Literal[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
        "HEAD",
        "TRACE",
    ]
    endpoint: str
    path_parameters: dict[str, Any] = Field(
        default_factory=dict,
        alias="pathParameters",
    )
    query_parameters: dict[str, Any] = Field(
        default_factory=dict,
        alias="queryParameters",
    )
    body: Any | None = None
    missing_information: list[str] = Field(
        default_factory=list,
        alias="missingInformation",
    )


class GenerationMetricsResponse(BaseModel):
    """Metriche restituite da Ollama."""

    total_duration_ns: int | None = None
    prompt_eval_count: int | None = None
    eval_count: int | None = None

class ValidationIssueResponse(BaseModel):
    """Problema individuato durante la validazione della chiamata."""

    code: str
    location: str
    message: str


class ValidationResponse(BaseModel):
    """Esito della validazione rispetto alla specifica OpenAPI."""

    valid: bool
    method: str
    endpoint: str
    issues: list[ValidationIssueResponse]

class QueryResponse(BaseModel):
    """Risposta della generazione e validazione della chiamata REST."""

    status: Literal["validated"] = "validated"
    received_query: str
    model: str
    candidate_count: int
    candidates: list[CandidateOperationResponse]
    generated_call: GeneratedApiCall
    validation: ValidationResponse
    metrics: GenerationMetricsResponse
    message: str

class OpenApiStatusResponse(BaseModel):
    """Informazioni sulla specifica caricata dal Persistence Service."""

    status: Literal["ok"] = "ok"
    source: str
    openapi_version: str
    path_count: int

class ApiOperationResponse(BaseModel):
    """Operazione REST estratta dalla specifica OpenAPI."""

    method: str
    path: str
    operation_id: str | None
    summary: str
    description: str
    tags: list[str]
    required_path_parameters: list[str]
    required_query_parameters: list[str]
    request_body_required: bool


class OpenApiOperationsResponse(BaseModel):
    """Elenco delle operazioni caricate dal Persistence Service."""

    status: Literal["ok"] = "ok"
    source: str
    count: int
    operations: list[ApiOperationResponse]