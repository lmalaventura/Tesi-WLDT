from dataclasses import dataclass

from fastapi import Depends
import httpx
from pydantic import ValidationError

from ..config import Settings, get_settings
from ..models import GeneratedApiCall
from .prompt_builder import BuiltPrompt


class OllamaUnavailableError(RuntimeError):
    """Errore di comunicazione con Ollama."""


class OllamaResponseError(RuntimeError):
    """Risposta di Ollama assente o non conforme allo schema."""


@dataclass(frozen=True, slots=True)
class OllamaGeneration:
    """Risultato strutturato e metriche della generazione."""

    generated_call: GeneratedApiCall
    model: str
    total_duration_ns: int | None
    prompt_eval_count: int | None
    eval_count: int | None


class OllamaClient:
    """Client HTTP per la Chat API locale di Ollama."""

    def __init__(
        self,
        base_url: str,
        model: str,
        timeout_seconds: float,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self._transport = transport

    async def generate(
        self,
        prompt: BuiltPrompt,
    ) -> OllamaGeneration:
        """Genera e valida una chiamata REST strutturata."""

        request_body = {
            "model": self.model,
            "messages": list(prompt.messages),
            "stream": False,
            "think": False,
            "format": prompt.output_schema,
        }

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout_seconds,
                transport=self._transport,
            ) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=request_body,
                )
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise OllamaUnavailableError(
                f"Impossibile comunicare con Ollama su "
                f"{self.base_url}."
            ) from exc

        try:
            response_document = response.json()
        except ValueError as exc:
            raise OllamaResponseError(
                "Ollama non ha restituito una risposta JSON valida."
            ) from exc

        message = response_document.get("message")

        if not isinstance(message, dict):
            raise OllamaResponseError(
                "La risposta di Ollama non contiene il messaggio."
            )

        content = message.get("content")

        if not isinstance(content, str) or not content.strip():
            raise OllamaResponseError(
                "La risposta di Ollama non contiene un output utile."
            )

        try:
            generated_call = GeneratedApiCall.model_validate_json(
                content
            )
        except (ValidationError, ValueError) as exc:
            raise OllamaResponseError(
                "L'output di Ollama non rispetta lo schema richiesto."
            ) from exc

        returned_model = response_document.get("model")

        return OllamaGeneration(
            generated_call=generated_call,
            model=(
                returned_model
                if isinstance(returned_model, str)
                else self.model
            ),
            total_duration_ns=_optional_int(
                response_document.get("total_duration")
            ),
            prompt_eval_count=_optional_int(
                response_document.get("prompt_eval_count")
            ),
            eval_count=_optional_int(
                response_document.get("eval_count")
            ),
        )


def get_ollama_client(
    settings: Settings = Depends(get_settings),
) -> OllamaClient:
    """Costruisce il client utilizzando la configurazione."""

    return OllamaClient(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        timeout_seconds=settings.ollama_timeout_seconds,
    )


def _optional_int(value: object) -> int | None:
    return value if isinstance(value, int) else None