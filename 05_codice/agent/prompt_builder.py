import json

from models import ApiEndpoint


BASE_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "method": {
            "type": "string",
        },
        "endpoint": {
            "type": "string",
        },
        "pathParameters": {
            "type": "object",
        },
        "queryParameters": {
            "type": "object",
        },
        "body": {
            "type": ["object", "array", "null"],
        },
        "missingInformation": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
    },
    "required": [
        "method",
        "endpoint",
        "pathParameters",
        "queryParameters",
        "body",
        "missingInformation",
    ],
}


class PromptBuilder:
    """Costruisce un prompt compatto usando gli endpoint selezionati."""

    def build_output_schema(
        self,
        endpoints: list[ApiEndpoint],
    ) -> dict:
        """Vincola metodo ed endpoint ai soli candidati selezionati."""

        schema = json.loads(json.dumps(BASE_OUTPUT_SCHEMA))

        schema["properties"]["method"]["enum"] = sorted(
            {endpoint.method for endpoint in endpoints}
        )
        schema["properties"]["endpoint"]["enum"] = [
            endpoint.endpoint for endpoint in endpoints
        ]

        return schema

    def build(
        self,
        endpoints: list[ApiEndpoint],
        request: str,
    ) -> tuple[str, dict]:
        if not endpoints:
            raise ValueError("Nessun endpoint candidato disponibile.")

        endpoint_blocks = [
            (
                f"{endpoint.method} {endpoint.endpoint}\n"
                f"Descrizione: {endpoint.description}\n"
                f"Struttura richiesta: {endpoint.request_hint}"
            )
            for endpoint in endpoints
        ]

        available_apis = "\n\n".join(endpoint_blocks)
        output_schema = self.build_output_schema(endpoints)
        schema_text = json.dumps(
            output_schema,
            ensure_ascii=False,
            indent=2,
        )

        prompt = (
            "Sei un componente che traduce richieste in linguaggio naturale "
            "in chiamate REST WLDT.\n\n"
            "API candidate:\n\n"
            f"{available_apis}\n\n"
            "Regole obbligatorie:\n"
            "- utilizza esclusivamente una delle API candidate;\n"
            "- copia il valore di endpoint esattamente come riportato, "
            "mantenendo eventuali placeholder tra parentesi graffe;\n"
            "- inserisci i valori concreti dei placeholder esclusivamente "
            "in pathParameters;\n"
            "- non inventare endpoint, metodi, campi o valori;\n"
            "- per richieste prive di body usa null, non un oggetto vuoto;\n"
            "- inserisci in missingInformation tutti i dati necessari "
            "ma assenti nella richiesta;\n"
            "- restituisci esclusivamente un oggetto JSON conforme "
            "allo schema.\n\n"
            "Schema JSON dell'output:\n"
            f"{schema_text}\n\n"
            "Richiesta dell'utente:\n"
            f"{request}"
        )

        return prompt, output_schema