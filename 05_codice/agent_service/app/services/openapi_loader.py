from typing import Any

import httpx
import yaml
from fastapi import Depends

from ..config import Settings, get_settings


class OpenApiLoadError(RuntimeError):
    """Errore durante il caricamento o la validazione della specifica."""


class OpenApiLoader:
    """Carica la specifica OpenAPI esposta dal Persistence Service."""

    def __init__(
        self,
        spec_url: str,
        timeout_seconds: float,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.spec_url = spec_url
        self.timeout_seconds = timeout_seconds
        self._transport = transport

    async def load(self) -> dict[str, Any]:
        """Scarica e valida la struttura minima della specifica OpenAPI."""

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout_seconds,
                transport=self._transport,
            ) as client:
                response = await client.get(self.spec_url)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise OpenApiLoadError(
                f"Impossibile caricare la specifica OpenAPI da {self.spec_url}."
            ) from exc

        try:
            document = yaml.safe_load(response.text)
        except yaml.YAMLError as exc:
            raise OpenApiLoadError(
                "La specifica ricevuta non contiene un documento YAML valido."
            ) from exc

        if not isinstance(document, dict):
            raise OpenApiLoadError(
                "La specifica OpenAPI deve essere rappresentata da un oggetto."
            )

        openapi_version = document.get("openapi")
        paths = document.get("paths")

        if not isinstance(openapi_version, str):
            raise OpenApiLoadError(
                "La specifica non contiene una versione OpenAPI valida."
            )

        if not isinstance(paths, dict):
            raise OpenApiLoadError(
                "La specifica non contiene la sezione paths."
            )

        return document


def get_openapi_loader(
    settings: Settings = Depends(get_settings),
) -> OpenApiLoader:
    """Costruisce il loader usando la configurazione del servizio."""

    return OpenApiLoader(
        spec_url=settings.openapi_spec_url,
        timeout_seconds=settings.request_timeout_seconds,
    )