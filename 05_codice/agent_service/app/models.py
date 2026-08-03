from typing import Literal

from pydantic import BaseModel, Field


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


class QueryResponse(BaseModel):
    """Risposta provvisoria dell'endpoint agentico."""

    status: Literal["stub"] = "stub"
    received_query: str
    message: str

class OpenApiStatusResponse(BaseModel):
    """Informazioni sulla specifica caricata dal Persistence Service."""

    status: Literal["ok"] = "ok"
    source: str
    openapi_version: str
    path_count: int