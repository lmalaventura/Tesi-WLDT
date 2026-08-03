import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class OllamaClientError(RuntimeError):
    """Errore durante la comunicazione con Ollama."""


class OllamaClient:
    def __init__(
        self,
        model: str = "qwen3:8b",
        base_url: str = "http://localhost:11434/api",
        timeout_seconds: int = 180,
    ) -> None:
        self.model = model
        self.generate_url = f"{base_url.rstrip('/')}/generate"
        self.timeout_seconds = timeout_seconds

    def generate_api_call(
        self,
        prompt: str,
        output_schema: dict[str, Any],
    ) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "think": False,
            "format": output_schema,
            "options": {
                "temperature": 0,
            },
        }

        request = Request(
            self.generate_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urlopen(
                request,
                timeout=self.timeout_seconds,
            ) as response:
                response_data = json.loads(
                    response.read().decode("utf-8")
                )
        except HTTPError as exc:
            error_body = exc.read().decode(
                "utf-8",
                errors="replace",
            )
            raise OllamaClientError(
                f"Ollama ha restituito HTTP {exc.code}: {error_body}"
            ) from exc
        except URLError as exc:
            raise OllamaClientError(
                "Impossibile contattare Ollama. "
                "Verifica che sia in esecuzione."
            ) from exc
        except TimeoutError as exc:
            raise OllamaClientError(
                "Ollama non ha risposto entro il tempo previsto."
            ) from exc

        generated_text = response_data.get("response")

        if not isinstance(generated_text, str) or not generated_text.strip():
            raise OllamaClientError(
                "La risposta di Ollama non contiene il campo 'response'."
            )

        try:
            parsed_output = json.loads(generated_text)
        except json.JSONDecodeError as exc:
            raise OllamaClientError(
                "Il modello non ha restituito un JSON valido."
            ) from exc

        if not isinstance(parsed_output, dict):
            raise OllamaClientError(
                "Il modello ha restituito un JSON che non è un oggetto."
            )

        return parsed_output