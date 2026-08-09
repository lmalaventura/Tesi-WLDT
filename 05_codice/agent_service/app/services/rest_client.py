from dataclasses import dataclass
from typing import Any

from fastapi import Depends
import httpx

from ..config import Settings, get_settings
from .api_request_preparer import PreparedApiRequest


class PersistenceUnavailableError(RuntimeError):
    """Errore di comunicazione con il Persistence Service."""


@dataclass(frozen=True, slots=True)
class RestExecution:
    """Risposta ottenuta dall'esecuzione della richiesta HTTP."""

    status_code: int
    content_type: str | None
    body: Any | None


class RestClient:
    """Client HTTP dedicato al Persistence Service."""

    def __init__(
        self,
        timeout_seconds: float,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self._transport = transport

    async def execute(
        self,
        request: PreparedApiRequest,
    ) -> RestExecution:
        """Esegue una richiesta precedentemente preparata e validata."""

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout_seconds,
                transport=self._transport,
            ) as client:
                if request.body is None:
                    response = await client.request(
                        method=request.method,
                        url=request.url,
                        params=request.query_parameters,
                    )
                else:
                    response = await client.request(
                        method=request.method,
                        url=request.url,
                        params=request.query_parameters,
                        json=request.body,
                    )
        except httpx.RequestError as exc:
            raise PersistenceUnavailableError(
                "Impossibile comunicare con il "
                "Persistence Service."
            ) from exc

        content_type = response.headers.get(
            "content-type"
        )

        response_body = _decode_response_body(
            response=response,
            content_type=content_type,
        )

        return RestExecution(
            status_code=response.status_code,
            content_type=content_type,
            body=response_body,
        )


def get_rest_client(
    settings: Settings = Depends(get_settings),
) -> RestClient:
    """Costruisce il client per il Persistence Service."""

    return RestClient(
        timeout_seconds=settings.request_timeout_seconds,
    )


def _decode_response_body(
    response: httpx.Response,
    content_type: str | None,
) -> Any | None:
    if not response.content:
        return None

    normalized_content_type = (
        content_type.lower()
        if isinstance(content_type, str)
        else ""
    )

    if (
        "application/json" in normalized_content_type
        or "+json" in normalized_content_type
    ):
        try:
            return response.json()
        except ValueError:
            return response.text

    return response.text