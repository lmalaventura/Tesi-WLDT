from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse


app = FastAPI(
    title="WLDT Mock Persistence Service",
    version="1.0.0",
)


ROOT_DIR = Path(__file__).resolve().parents[2]
OPENAPI_PATH = ROOT_DIR / "00_materiali" / "openapi.yaml"


@app.get("/openapi.yaml", include_in_schema=False)
async def openapi_spec() -> FileResponse:
    """Restituisce la specifica OpenAPI reale usata dal progetto."""

    return FileResponse(
        OPENAPI_PATH,
        media_type="application/yaml",
    )


@app.get("/hdts")
async def list_hdts() -> list[dict[str, str]]:
    """Risposta simulata per l'elenco dei Digital Twin."""

    return [
        {
            "id": "HDT-001",
        },
        {
            "id": "HDT-002",
        },
    ]


@app.get("/hdts/{hdt_id}/snapshot")
async def hdt_snapshot(
    hdt_id: str,
) -> dict[str, Any]:
    """Risposta simulata per lo snapshot corrente."""

    return {
        "id": hdt_id,
        "properties": {
            "heartRate": 72,
            "systolicPressure": 120,
        },
    }


@app.post("/query/event/values/valuesByName")
async def values_by_name(
    request: Request,
) -> dict[str, Any]:
    """Registra la richiesta storica ricevuta."""

    body = await request.json()

    return {
        "mock": True,
        "operation": "valuesByName",
        "receivedBody": body,
    }


@app.post("/query/event/comparison")
async def comparison(
    request: Request,
) -> dict[str, Any]:
    """Registra la richiesta di confronto ricevuta."""

    body = await request.json()

    return {
        "mock": True,
        "operation": "comparison",
        "receivedBody": body,
    }


@app.post("/query/event/stats")
async def stats(
    request: Request,
) -> dict[str, Any]:
    """Registra la richiesta di statistiche ricevuta."""

    body = await request.json()

    return {
        "mock": True,
        "operation": "stats",
        "receivedBody": body,
    }