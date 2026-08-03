import json

from api_selector import ApiSelector
from ollama_client import OllamaClient, OllamaClientError
from prompt_builder import PromptBuilder
from validator import ApiCallValidator


def main() -> None:
    print("=== WLDT Agent Prototype ===\n")

    request = input("Richiesta: ").strip()

    if not request:
        print("\nErrore: la richiesta non può essere vuota.")
        return

    selector = ApiSelector()
    endpoints = selector.select(request)

    print("\nEndpoint selezionati:")

    if not endpoints:
        print("- Nessun endpoint candidato")
        return

    for endpoint in endpoints:
        print(f"- {endpoint.method} {endpoint.endpoint}")

    builder = PromptBuilder()

    try:
        prompt, output_schema = builder.build(
            endpoints,
            request,
        )
    except ValueError as exc:
        print(f"\nErrore nella costruzione del prompt: {exc}")
        return

    client = OllamaClient(model="qwen3:8b")

    print("\nGenerazione della chiamata API tramite Ollama...")

    try:
        api_call = client.generate_api_call(
            prompt,
            output_schema,
        )
    except OllamaClientError as exc:
        print(f"\nErrore Ollama: {exc}")
        return

    validator = ApiCallValidator()
    validation = validator.validate(api_call, endpoints)

    print("\nOutput strutturato:\n")
    print(json.dumps(api_call, ensure_ascii=False, indent=2))

    print("\nValidazione:")

    if validation.valid:
        print("- Output strutturalmente valido")
    else:
        print("- Output non valido")

    for error in validation.errors:
        print(f"  - {error}")

    if validation.executable:
        print("- Richiesta pronta per l'esecuzione")
    else:
        print("- Richiesta non eseguibile")

    if validation.missing_required_information:
        print(
            "  Informazioni obbligatorie mancanti: "
            + ", ".join(validation.missing_required_information)
        )


if __name__ == "__main__":
    main()