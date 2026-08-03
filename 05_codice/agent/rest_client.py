import json
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode


class RestClientError(ValueError):
    """Errore nella preparazione della richiesta REST."""


@dataclass(frozen=True)
class PreparedRequest:
    method: str
    url: str
    headers: dict[str, str]
    body: bytes | None


class RestClient:
    def __init__(
        self,
        base_url: str = "http://localhost:8080",
    ) -> None:
        self.base_url = base_url.rstrip("/")

    def prepare(
        self,
        api_call: dict[str, Any],
    ) -> PreparedRequest:
        method = api_call["method"]
        endpoint = api_call["endpoint"]
        path_parameters = api_call["pathParameters"]
        query_parameters = api_call["queryParameters"]
        body = api_call["body"]

        resolved_endpoint = self._resolve_path_parameters(
            endpoint,
            path_parameters,
        )

        url = f"{self.base_url}{resolved_endpoint}"

        if query_parameters:
            url = f"{url}?{urlencode(query_parameters, doseq=True)}"

        headers = {
            "Accept": "application/json",
        }

        encoded_body: bytes | None = None

        if body is not None:
            headers["Content-Type"] = "application/json"
            encoded_body = json.dumps(
                body,
                ensure_ascii=False,
            ).encode("utf-8")

        return PreparedRequest(
            method=method,
            url=url,
            headers=headers,
            body=encoded_body,
        )

    @staticmethod
    def _resolve_path_parameters(
        endpoint: str,
        path_parameters: dict[str, Any],
    ) -> str:
        resolved = endpoint

        for name, value in path_parameters.items():
            resolved = resolved.replace(
                f"{{{name}}}",
                str(value),
            )

        unresolved = re.findall(r"{([^{}]+)}", resolved)

        if unresolved:
            raise RestClientError(
                "Path parameter non risolti: "
                + ", ".join(sorted(unresolved))
            )

        return resolved