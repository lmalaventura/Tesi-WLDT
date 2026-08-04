from dataclasses import dataclass
import re
import unicodedata
from typing import Final

from .openapi_catalog import ApiOperation, OpenApiCatalog


WORD_PATTERN: Final[re.Pattern[str]] = re.compile(r"[a-z0-9]+")
CAMEL_CASE_BOUNDARY: Final[re.Pattern[str]] = re.compile(
    r"(?<=[a-z0-9])(?=[A-Z])"
)
YEAR_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\b(?:19|20)\d{2}\b"
)

STOPWORDS: Final[frozenset[str]] = frozenset(
    {
        "a",
        "al",
        "alla",
        "alle",
        "con",
        "da",
        "dei",
        "del",
        "della",
        "delle",
        "di",
        "e",
        "gli",
        "i",
        "il",
        "in",
        "la",
        "le",
        "lo",
        "mi",
        "mostrami",
        "per",
        "the",
        "un",
        "una",
    }
)

TOKEN_ALIASES: Final[dict[str, tuple[str, ...]]] = {
    "attuale": ("current", "snapshot"),
    "calcola": ("calculate",),
    "corrente": ("current", "snapshot"),
    "digital": ("hdt", "hdts"),
    "disponibili": ("all", "list"),
    "gemelli": ("hdt", "hdts"),
    "gemello": ("hdt", "hdts"),
    "maggiore": ("comparison", "greater", "gt"),
    "media": ("average", "mean", "populationstats", "stats"),
    "minore": ("comparison", "less", "lt"),
    "proprieta": ("properties", "property"),
    "selezionati": ("filter", "filtered"),
    "statistica": (
        "aggregate",
        "populationstats",
        "statistics",
        "stats",
    ),
    "statistiche": (
        "aggregate",
        "populationstats",
        "statistics",
        "stats",
    ),
    "storico": ("event", "historical", "history"),
    "storia": ("event", "historical", "history"),
    "superiore": ("comparison", "greater", "gt"),
    "tutti": ("all", "gethdts", "hdts", "list"),
    "twin": ("hdt", "hdts"),
    "valore": ("value", "values"),
    "valori": ("value", "values"),
}


@dataclass(frozen=True, slots=True)
class RankedApiOperation:
    """Operazione candidata associata al relativo punteggio."""

    operation: ApiOperation
    score: int
    matched_terms: tuple[str, ...]


class ApiSelector:
    """Ordina le operazioni OpenAPI rispetto alla richiesta dell'utente."""

    def select(
        self,
        query: str,
        catalog: OpenApiCatalog,
        limit: int = 5,
    ) -> tuple[RankedApiOperation, ...]:
        """Restituisce le operazioni candidate con punteggio positivo."""

        if limit <= 0:
            raise ValueError("Il limite deve essere maggiore di zero.")

        query_terms = _query_terms(query)
        ranked_operations: list[RankedApiOperation] = []

        for operation in catalog.operations:
            weighted_terms = _operation_terms(operation)

            matched_terms = tuple(
                sorted(
                    term
                    for term in query_terms
                    if term in weighted_terms
                )
            )

            score = sum(
                weighted_terms[term]
                for term in matched_terms
            )

            candidate_terms = set(weighted_terms)

            score += _intent_bonus(
                query_terms=query_terms,
                candidate_terms=candidate_terms,
                operation=operation,
            )

            if score <= 0:
                continue

            ranked_operations.append(
                RankedApiOperation(
                    operation=operation,
                    score=score,
                    matched_terms=matched_terms,
                )
            )

        ranked_operations.sort(
            key=lambda candidate: (
                -candidate.score,
                candidate.operation.path,
                candidate.operation.method,
            )
        )

        return tuple(ranked_operations[:limit])


def get_api_selector() -> ApiSelector:
    """Restituisce il componente di selezione delle API."""

    return ApiSelector()


def _query_terms(query: str) -> set[str]:
    raw_terms = _tokenize(query)

    terms = {
        term
        for term in raw_terms
        if term not in STOPWORDS
    }

    for term in raw_terms:
        terms.update(TOKEN_ALIASES.get(term, ()))

    if _contains_time_range(query, raw_terms):
        terms.update(
            {
                "from",
                "range",
                "to",
                "valuesbyname",
            }
        )

    return terms


def _operation_terms(
    operation: ApiOperation,
) -> dict[str, int]:
    weighted_terms: dict[str, int] = {}

    _add_weighted_terms(
        weighted_terms,
        operation.path,
        weight=6,
    )
    _add_weighted_terms(
        weighted_terms,
        operation.operation_id or "",
        weight=6,
    )
    _add_weighted_terms(
        weighted_terms,
        operation.summary,
        weight=3,
    )
    _add_weighted_terms(
        weighted_terms,
        operation.description,
        weight=1,
    )

    for tag in operation.tags:
        _add_weighted_terms(
            weighted_terms,
            tag,
            weight=3,
        )

    for parameter in operation.required_path_parameters:
        _add_weighted_terms(
            weighted_terms,
            parameter,
            weight=2,
        )

    for parameter in operation.required_query_parameters:
        _add_weighted_terms(
            weighted_terms,
            parameter,
            weight=2,
        )

    return weighted_terms


def _add_weighted_terms(
    destination: dict[str, int],
    value: str,
    weight: int,
) -> None:
    for term in _tokenize(value):
        destination[term] = max(
            destination.get(term, 0),
            weight,
        )


def _intent_bonus(
    query_terms: set[str],
    candidate_terms: set[str],
    operation: ApiOperation,
) -> int:
    bonus = 0

    if (
        "list" in query_terms
        and operation.method == "GET"
        and not operation.required_path_parameters
        and candidate_terms.intersection({"gethdts", "hdts"})
    ):
        bonus += 8

    if (
        "snapshot" in query_terms
        and "snapshot" in candidate_terms
    ):
        bonus += 12

    if "comparison" in query_terms:
        if candidate_terms.intersection(
            {
                "compare",
                "comparison",
                "comparisons",
            }
        ):
            bonus += 24
    elif "snapshot" in candidate_terms:
        bonus -= 8

    if (
        "stats" in query_terms
        and candidate_terms.intersection(
            {
                "populationstats",
                "statistics",
                "stats",
            }
        )
    ):
        bonus += 12

    if "range" in query_terms:
        if (
            "valuesbyname" in candidate_terms
            or {"from", "to"}.issubset(candidate_terms)
        ):
            bonus += 12
        elif "history" in candidate_terms:
            bonus -= 3
    elif (
        "history" in query_terms
        and "history" in candidate_terms
    ):
        bonus += 10

    return bonus


def _contains_time_range(
    query: str,
    terms: set[str],
) -> bool:
    normalized_query = _normalize(query)

    has_range_expression = (
        "intervallo" in terms
        or "tra" in terms
        or (
            "dal" in terms
            and "al" in terms
        )
    )

    has_year = YEAR_PATTERN.search(normalized_query) is not None

    return has_range_expression and has_year


def _tokenize(value: str) -> set[str]:
    terms: set[str] = set()

    raw_segments = re.split(r"[^A-Za-zÀ-ÿ0-9]+", value)

    for raw_segment in raw_segments:
        if not raw_segment:
            continue

        normalized_segment = _normalize(raw_segment)

        if normalized_segment:
            terms.add(normalized_segment)

        split_segment = CAMEL_CASE_BOUNDARY.sub(
            " ",
            raw_segment,
        )

        normalized_split = _normalize(split_segment)
        terms.update(WORD_PATTERN.findall(normalized_split))

    return terms


def _normalize(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)

    without_accents = "".join(
        character
        for character in decomposed
        if not unicodedata.combining(character)
    )

    return without_accents.lower()