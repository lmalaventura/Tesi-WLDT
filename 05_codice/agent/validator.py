import re
from dataclasses import dataclass, field
from typing import Any

from models import ApiEndpoint


@dataclass
class ValidationResult:
    valid: bool
    executable: bool
    errors: list[str] = field(default_factory=list)
    missing_required_information: list[str] = field(default_factory=list)


class ApiCallValidator:
    REQUIRED_FIELDS = {
        "method",
        "endpoint",
        "pathParameters",
        "queryParameters",
        "body",
        "missingInformation",
    }

    REQUIRED_BODY_FIELDS = {
        "/query/event/stats": {
            "hdtIds",
            "modelIds",
            "modelNames",
            "propertyName",
        },
        "/query/event/comparison": {
            "comparisons",
        },
    }

    def validate(
        self,
        api_call: dict[str, Any],
        candidates: list[ApiEndpoint],
    ) -> ValidationResult:
        errors: list[str] = []
        missing_required_information: list[str] = []

        missing_fields = self.REQUIRED_FIELDS - api_call.keys()

        if missing_fields:
            errors.append(
                "Campi principali mancanti: "
                + ", ".join(sorted(missing_fields))
            )
            return ValidationResult(
                valid=False,
                executable=False,
                errors=errors,
            )

        matching_candidate = next(
            (
                candidate
                for candidate in candidates
                if candidate.method == api_call["method"]
                and candidate.endpoint == api_call["endpoint"]
            ),
            None,
        )

        if matching_candidate is None:
            errors.append(
                "La combinazione metodo/endpoint non appartiene "
                "alle API candidate."
            )
            return ValidationResult(
                valid=False,
                executable=False,
                errors=errors,
            )

        path_parameters = api_call["pathParameters"]

        if not isinstance(path_parameters, dict):
            errors.append("pathParameters deve essere un oggetto JSON.")
        else:
            required_placeholders = set(
                re.findall(r"{([^{}]+)}", matching_candidate.endpoint)
            )
            supplied_placeholders = set(path_parameters.keys())

            absent = required_placeholders - supplied_placeholders
            unexpected = supplied_placeholders - required_placeholders

            if absent:
                missing_required_information.extend(sorted(absent))

            if unexpected:
                errors.append(
                    "Path parameter non previsti: "
                    + ", ".join(sorted(unexpected))
                )

        if not isinstance(api_call["queryParameters"], dict):
            errors.append("queryParameters deve essere un oggetto JSON.")

        declared_missing = api_call["missingInformation"]

        if not isinstance(declared_missing, list):
            errors.append("missingInformation deve essere un array JSON.")
            declared_missing = []

        if api_call["method"] == "GET" and api_call["body"] == {}:
            api_call["body"] = None

        required_body_fields = self.REQUIRED_BODY_FIELDS.get(
            matching_candidate.endpoint,
            set(),
        )

        if required_body_fields:
            body = api_call["body"]

            if not isinstance(body, dict):
                errors.append(
                    "Il body deve essere un oggetto JSON per "
                    f"{matching_candidate.endpoint}."
                )
            else:
                absent_body_fields = required_body_fields - body.keys()
                missing_required_information.extend(
                    sorted(absent_body_fields)
                )

        actual_missing = set(missing_required_information)
        declared_missing_set = set(declared_missing)

        undeclared_missing = actual_missing - declared_missing_set

        if undeclared_missing:
            errors.append(
                "Informazioni obbligatorie mancanti ma non dichiarate: "
                + ", ".join(sorted(undeclared_missing))
            )

        optional_declared_as_missing = (
            declared_missing_set - actual_missing
        )

        if optional_declared_as_missing:
            errors.append(
                "Informazioni dichiarate mancanti ma non obbligatorie: "
                + ", ".join(sorted(optional_declared_as_missing))
            )

        valid = not errors
        executable = valid and not actual_missing

        return ValidationResult(
            valid=valid,
            executable=executable,
            errors=errors,
            missing_required_information=sorted(actual_missing),
        )