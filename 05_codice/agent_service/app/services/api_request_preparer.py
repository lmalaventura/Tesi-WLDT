from dataclasses import dataclass
import re
from typing import Any
from urllib.parse import quote

from ..models import GeneratedApiCall


PATH_PARAMETER_PATTERN = re.compile(r"\{([^{}]+)\}")


class RequestPreparationError(ValueError):
    """Errore durante la preparazione della richiesta HTTP."""


@dataclass(frozen=True, slots=True)
class PreparedApiRequest:
    """Richiesta HTTP pronta per essere inviata dal RestClient."""

    method: str
    url: str
    query_parameters: dict[str, Any]
    body: Any | None


class ApiRequestPreparer:
    """Trasforma una chiamata validata in una richiesta HTTP concreta."""

    def prepare(
        self,
        generated_call: GeneratedApiCall,
        base_url: str,
    ) -> PreparedApiRequest:
        """Costruisce URL, parametri e body della richiesta."""

        normalized_base_url = base_url.strip().rstrip("/")

        if not normalized_base_url:
            raise RequestPreparationError(
                "Il base URL del Persistence Service è vuoto."
            )

        endpoint = generated_call.endpoint.strip()

        if not endpoint.startswith("/"):
            raise RequestPreparationError(
                "L'endpoint deve iniziare con '/'."
            )

        expected_path_parameters = set(
            PATH_PARAMETER_PATTERN.findall(endpoint)
        )
        provided_path_parameters = set(
            generated_call.path_parameters
        )

        missing_parameters = {
            parameter_name
            for parameter_name in expected_path_parameters
            if (
                parameter_name
                not in generated_call.path_parameters
                or _is_missing_value(
                    generated_call.path_parameters[
                        parameter_name
                    ]
                )
            )
        }

        if missing_parameters:
            formatted_names = ", ".join(
                sorted(missing_parameters)
            )

            raise RequestPreparationError(
                "Path parameter mancanti: "
                f"{formatted_names}."
            )

        unexpected_parameters = (
            provided_path_parameters
            - expected_path_parameters
        )

        if unexpected_parameters:
            formatted_names = ", ".join(
                sorted(unexpected_parameters)
            )

            raise RequestPreparationError(
                "Path parameter non previsti: "
                f"{formatted_names}."
            )

        rendered_endpoint = endpoint

        for parameter_name in sorted(
            expected_path_parameters
        ):
            raw_value = generated_call.path_parameters[
                parameter_name
            ]

            encoded_value = quote(
                str(raw_value),
                safe="",
            )

            rendered_endpoint = rendered_endpoint.replace(
                f"{{{parameter_name}}}",
                encoded_value,
            )

        unresolved_parameters = (
            PATH_PARAMETER_PATTERN.findall(
                rendered_endpoint
            )
        )

        if unresolved_parameters:
            formatted_names = ", ".join(
                sorted(unresolved_parameters)
            )

            raise RequestPreparationError(
                "Impossibile risolvere i path parameter: "
                f"{formatted_names}."
            )

        return PreparedApiRequest(
            method=generated_call.method,
            url=(
                f"{normalized_base_url}/"
                f"{rendered_endpoint.lstrip('/')}"
            ),
            query_parameters=dict(
                generated_call.query_parameters
            ),
            body=generated_call.body,
        )


def get_api_request_preparer() -> ApiRequestPreparer:
    """Restituisce il preparatore delle richieste HTTP."""

    return ApiRequestPreparer()


def _is_missing_value(value: Any) -> bool:
    return (
        value is None
        or (
            isinstance(value, str)
            and not value.strip()
        )
    )