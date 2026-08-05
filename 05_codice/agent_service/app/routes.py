from fastapi import APIRouter, Depends, HTTPException

from .config import Settings, get_settings
from .models import (
    ApiOperationResponse,
    CandidateOperationResponse,
    HealthResponse,
    OpenApiOperationsResponse,
    OpenApiStatusResponse,
    QueryRequest,
    QueryResponse,
    GenerationMetricsResponse,
)
from .services.api_selector import ApiSelector, get_api_selector
from .services.openapi_catalog import (
    OpenApiCatalog,
    OpenApiCatalogError,
)
from .services.openapi_loader import (
    OpenApiLoader,
    OpenApiLoadError,
    get_openapi_loader,
)

from .services.ollama_client import (
    OllamaClient,
    OllamaResponseError,
    OllamaUnavailableError,
    get_ollama_client,
)
from .services.prompt_builder import (
    PromptBuildError,
    PromptBuilder,
    get_prompt_builder,
)


router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["system"],
)
def health(
    settings: Settings = Depends(get_settings),
) -> HealthResponse:
    """Verifica che l'Agent Service sia avviato."""

    return HealthResponse(
        service=settings.service_name,
        version=settings.service_version,
    )


@router.get(
    "/openapi/status",
    response_model=OpenApiStatusResponse,
    tags=["openapi"],
    responses={
        503: {
            "description": "Persistence Service non disponibile.",
        },
    },
)
async def openapi_status(
    loader: OpenApiLoader = Depends(get_openapi_loader),
) -> OpenApiStatusResponse:
    """Verifica il caricamento della specifica del Persistence Service."""

    try:
        document = await loader.load()
    except OpenApiLoadError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    return OpenApiStatusResponse(
        source=loader.spec_url,
        openapi_version=document["openapi"],
        path_count=len(document["paths"]),
    )


@router.get(
    "/openapi/operations",
    response_model=OpenApiOperationsResponse,
    tags=["openapi"],
    responses={
        500: {
            "description": "Catalogo OpenAPI non valido.",
        },
        503: {
            "description": "Persistence Service non disponibile.",
        },
    },
)
async def openapi_operations(
    loader: OpenApiLoader = Depends(get_openapi_loader),
) -> OpenApiOperationsResponse:
    """Restituisce il catalogo delle operazioni disponibili."""

    try:
        document = await loader.load()
        catalog = OpenApiCatalog.from_document(document)
    except OpenApiLoadError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc
    except OpenApiCatalogError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    operations = [
        ApiOperationResponse(
            method=operation.method,
            path=operation.path,
            operation_id=operation.operation_id,
            summary=operation.summary,
            description=operation.description,
            tags=list(operation.tags),
            required_path_parameters=list(
                operation.required_path_parameters
            ),
            required_query_parameters=list(
                operation.required_query_parameters
            ),
            request_body_required=operation.request_body_required,
        )
        for operation in catalog.operations
    ]

    return OpenApiOperationsResponse(
        source=loader.spec_url,
        count=len(operations),
        operations=operations,
    )


@router.post(
    "/query",
    response_model=QueryResponse,
    tags=["agent"],
    responses={
        500: {
            "description": "Catalogo o prompt non valido.",
        },
        502: {
            "description": "Output del modello non valido.",
        },
        503: {
            "description": (
                "Persistence Service oppure Ollama non disponibile."
            ),
        },
    },
)
async def process_query(
    payload: QueryRequest,
    loader: OpenApiLoader = Depends(get_openapi_loader),
    selector: ApiSelector = Depends(get_api_selector),
    prompt_builder: PromptBuilder = Depends(get_prompt_builder),
    ollama_client: OllamaClient = Depends(get_ollama_client),
) -> QueryResponse:
    """Genera una chiamata REST strutturata tramite il modello locale."""

    try:
        document = await loader.load()
        catalog = OpenApiCatalog.from_document(document)
    except OpenApiLoadError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc
    except OpenApiCatalogError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    ranked_operations = selector.select(
        query=payload.query,
        catalog=catalog,
        limit=3,
    )

    if not ranked_operations:
        raise HTTPException(
            status_code=422,
            detail=(
                "Nessuna operazione OpenAPI candidata "
                "per la richiesta ricevuta."
            ),
        )

    try:
        prompt = prompt_builder.build(
            query=payload.query,
            candidates=ranked_operations,
            openapi_document=document,
        )
    except PromptBuildError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    try:
        generation = await ollama_client.generate(prompt)
    except OllamaUnavailableError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc
    except OllamaResponseError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    candidates = [
        CandidateOperationResponse(
            method=candidate.operation.method,
            path=candidate.operation.path,
            operation_id=candidate.operation.operation_id,
            summary=candidate.operation.summary,
            score=candidate.score,
            matched_terms=list(candidate.matched_terms),
            required_path_parameters=list(
                candidate.operation.required_path_parameters
            ),
            required_query_parameters=list(
                candidate.operation.required_query_parameters
            ),
            request_body_required=(
                candidate.operation.request_body_required
            ),
        )
        for candidate in ranked_operations
    ]

    return QueryResponse(
        received_query=payload.query,
        model=generation.model,
        candidate_count=len(candidates),
        candidates=candidates,
        generated_call=generation.generated_call,
        metrics=GenerationMetricsResponse(
            total_duration_ns=generation.total_duration_ns,
            prompt_eval_count=generation.prompt_eval_count,
            eval_count=generation.eval_count,
        ),
        message=(
            "Chiamata REST generata. "
            "La validazione e l'esecuzione non sono ancora collegate."
        ),
    )