from fastapi import APIRouter, Depends

from .config import Settings, get_settings
from .models import HealthResponse, QueryRequest, QueryResponse


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