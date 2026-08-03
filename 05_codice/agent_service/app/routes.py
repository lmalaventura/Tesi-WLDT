from fastapi import APIRouter, Depends, HTTPException

from .config import Settings, get_settings
from .models import (
    HealthResponse,
    OpenApiStatusResponse,
    QueryRequest,
    QueryResponse,
)
from .services.openapi_loader import (
    OpenApiLoader,
    OpenApiLoadError,
    get_openapi_loader,
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
    tags=["system"],
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


@router.post(
    "/query",
    response_model=QueryResponse,
    tags=["agent"],
)
def process_query(payload: QueryRequest) -> QueryResponse:
    """Riceve una query; la pipeline verrà collegata nei prossimi step."""

    return QueryResponse(
        received_query=payload.query,
        message=(
            "Richiesta ricevuta correttamente. "
            "La pipeline LLM non è ancora collegata."
        ),
    )