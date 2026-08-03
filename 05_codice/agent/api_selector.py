from models import ApiEndpoint


class ApiSelector:
    """Seleziona gli endpoint candidati usando espressioni specifiche."""

    def __init__(self) -> None:
        self.endpoints = [
            ApiEndpoint(
                method="GET",
                endpoint="/hdts",
                description="Restituisce tutti gli Human Digital Twin.",
                keywords=[
                    "tutti i digital twin",
                    "elenco dei digital twin",
                    "lista dei digital twin",
                    "digital twin disponibili",
                ],
                request_hint="Nessun parametro richiesto.",
            ),
            ApiEndpoint(
                method="GET",
                endpoint="/hdts/{id}/snapshot",
                description=(
                    "Restituisce il valore corrente di tutte le proprietà "
                    "del Digital Twin indicato."
                ),
                keywords=[
                    "valore corrente",
                    "valori correnti",
                    "snapshot",
                    "stato corrente",
                ],
                request_hint=(
                    'Path parameter obbligatorio: "id", identificativo '
                    "del Digital Twin."
                ),
            ),
            ApiEndpoint(
                method="POST",
                endpoint="/query/event/values/history",
                description=(
                    "Restituisce lo storico dei valori di una proprietà "
                    "in un intervallo temporale."
                ),
                keywords=[
                    "storico",
                    "cronologia",
                    "history",
                    "nel tempo",
                ],
                request_hint=(
                    "Il body è un array di oggetti. Ogni oggetto può contenere: "
                    "hdtId, modelId, propertyId, propertyName, from e to."
                ),
            ),
            ApiEndpoint(
                method="POST",
                endpoint="/query/event/comparison",
                description=(
                    "Trova i Digital Twin che soddisfano uno o più confronti "
                    "sul valore delle proprietà."
                ),
                keywords=[
                    "maggiore di",
                    "minore di",
                    "uguale a",
                    "superiore a",
                    "inferiore a",
                    "confronto",
                ],
                request_hint=(
                    'Il body contiene "comparisons", array di oggetti con '
                    '"propertyName", "comparison" e "value". '
                    "Operatori ammessi: GT, GTE, LT, LTE, EQ."
                ),
            ),
            ApiEndpoint(
                method="POST",
                endpoint="/query/event/stats",
                description=(
                    "Calcola statistiche aggregate sui valori "
                    "di una proprietà."
                ),
                keywords=[
                    "statistiche",
                    "statistica",
                    "media",
                    "minimo",
                    "massimo",
                    "conteggio",
                ],
                request_hint=(
                    'Il body richiede gli array "hdtIds", "modelIds", '
                    '"modelNames" e la stringa "propertyName". '
                    'I campi temporali "from" e "to" sono facoltativi '
                    "e non devono essere segnalati come mancanti."
                ),
            ),
        ]

    def select(self, request: str) -> list[ApiEndpoint]:
        normalized_request = request.casefold()
        selected: list[ApiEndpoint] = []

        for endpoint in self.endpoints:
            if any(
                keyword.casefold() in normalized_request
                for keyword in endpoint.keywords
            ):
                selected.append(endpoint)

        return selected