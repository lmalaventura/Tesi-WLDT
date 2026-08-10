import argparse
from collections import defaultdict
from datetime import datetime
import json
from pathlib import Path
import time
from typing import Any

import httpx


SCRIPT_DIR = Path(__file__).resolve().parent
CASES_PATH = SCRIPT_DIR / "cases.json"

DEFAULT_AGENT_URL = "http://127.0.0.1:8000"
DEFAULT_RUNS = 3


def load_cases() -> list[dict[str, Any]]:
    """Carica e valida i casi del benchmark."""

    with CASES_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("cases.json deve contenere un array.")

    required_expected_fields = {
        "method",
        "endpoint",
        "pathParameters",
        "queryParameters",
        "body",
        "missingInformation",
    }

    for case in data:
        if not isinstance(case, dict):
            raise ValueError("Ogni caso del benchmark deve essere un oggetto.")

        for field in ("id", "name", "query", "expected"):
            if field not in case:
                raise ValueError(
                    f"Campo mancante nel caso benchmark: {field}."
                )

        expected = case["expected"]

        if not isinstance(expected, dict):
            raise ValueError(
                f"{case['id']}: expected deve essere un oggetto."
            )

        missing_fields = required_expected_fields - expected.keys()

        if missing_fields:
            raise ValueError(
                f"{case['id']}: campi expected mancanti: "
                f"{sorted(missing_fields)}."
            )

    return data


def _extract_generated_call(
    response_body: Any,
) -> dict[str, Any] | None:
    """Estrae la chiamata generata anche dalle risposte di errore."""

    if not isinstance(response_body, dict):
        return None

    generated_call = response_body.get("generated_call")

    if isinstance(generated_call, dict):
        return generated_call

    detail = response_body.get("detail")

    if isinstance(detail, dict):
        generated_call = detail.get("generated_call")

        if isinstance(generated_call, dict):
            return generated_call

    return None


def _extract_candidates(
    response_body: Any,
) -> list[dict[str, Any]]:
    """Estrae le candidate quando l'Agent Service le restituisce."""

    if not isinstance(response_body, dict):
        return []

    candidates = response_body.get("candidates")

    if not isinstance(candidates, list):
        return []

    return [
        candidate
        for candidate in candidates
        if isinstance(candidate, dict)
    ]


def _expected_candidate_rank(
    candidates: list[dict[str, Any]],
    expected: dict[str, Any],
) -> int | None:
    """Trova il rank della chiamata attesa tra le candidate osservabili."""

    for index, candidate in enumerate(candidates, start=1):
        if (
            candidate.get("method") == expected["method"]
            and candidate.get("path") == expected["endpoint"]
        ):
            return index

    return None


def _compare_arguments(
    generated_call: dict[str, Any],
    expected: dict[str, Any],
) -> tuple[bool, list[str]]:
    """Confronta parametri, body e missingInformation col ground truth."""

    issues: list[str] = []

    comparisons = (
        (
            "pathParameters",
            generated_call.get("pathParameters", {}),
            expected["pathParameters"],
        ),
        (
            "queryParameters",
            generated_call.get("queryParameters", {}),
            expected["queryParameters"],
        ),
        (
            "body",
            generated_call.get("body"),
            expected["body"],
        ),
        (
            "missingInformation",
            generated_call.get("missingInformation", []),
            expected["missingInformation"],
        ),
    )

    for field, actual_value, expected_value in comparisons:
        if actual_value != expected_value:
            issues.append(
                f"{field}: atteso "
                f"{json.dumps(expected_value, ensure_ascii=False)}; "
                f"ottenuto "
                f"{json.dumps(actual_value, ensure_ascii=False)}"
            )

    return not issues, issues


def _extract_validation_valid(
    response_body: Any,
    status_code: int,
) -> bool | None:
    """Determina se il validatore OpenAPI è stato raggiunto e superato."""

    if not isinstance(response_body, dict):
        return None

    validation = response_body.get("validation")

    if isinstance(validation, dict):
        value = validation.get("valid")

        if isinstance(value, bool):
            return value

    detail = response_body.get("detail")

    if (
        status_code == 502
        and isinstance(detail, dict)
        and isinstance(detail.get("issues"), list)
        and isinstance(detail.get("generated_call"), dict)
    ):
        return False

    return None


def _extract_persistence_response(
    response_body: Any,
) -> dict[str, Any] | None:
    """Estrae la risposta del Persistence Service se presente."""

    if not isinstance(response_body, dict):
        return None

    persistence_response = response_body.get("persistence_response")

    if isinstance(persistence_response, dict):
        return persistence_response

    return None


def _execution_success(
    persistence_response: dict[str, Any] | None,
) -> bool:
    """Richiede che il Persistence Service simulato abbia risposto 2xx."""

    if persistence_response is None:
        return False

    status_code = persistence_response.get("status_code")

    return (
        isinstance(status_code, int)
        and 200 <= status_code < 300
    )


def _classify_error_stage(
    status_code: int | None,
    response_body: Any,
    transport_error: str | None = None,
) -> str | None:
    """Classifica lo stadio in cui la pipeline si è interrotta."""

    if transport_error is not None:
        return "transport"

    if status_code == 200:
        return None

    if not isinstance(response_body, dict):
        return "agent"

    detail = response_body.get("detail")

    if status_code == 422:
        return "missing_information"

    if status_code == 502:
        if (
            isinstance(detail, dict)
            and isinstance(detail.get("generated_call"), dict)
            and isinstance(detail.get("issues"), list)
        ):
            return "validation"

        return "llm_or_generation"

    if status_code == 503:
        detail_text = (
            detail
            if isinstance(detail, str)
            else json.dumps(detail, ensure_ascii=False)
        )

        if "Ollama" in detail_text:
            return "ollama_unavailable"

        if "Persistence" in detail_text:
            return "persistence_unavailable"

        return "dependency_unavailable"

    return "agent"


def _empty_failure_result(
    case: dict[str, Any],
    run_number: int,
    elapsed_seconds: float,
    transport_error: str,
) -> dict[str, Any]:
    """Costruisce il risultato di un errore di trasporto verso l'Agent."""

    return {
        "case_id": case["id"],
        "case_name": case["name"],
        "run": run_number,
        "query": case["query"],
        "expected": case["expected"],
        "agent_status_code": None,
        "wall_time_seconds": round(elapsed_seconds, 3),
        "transport_error": transport_error,
        "generated_call_observed": False,
        "actual_method": None,
        "actual_endpoint": None,
        "operation_correct": False,
        "arguments_correct": False,
        "semantic_correct": False,
        "semantic_issues": [
            "Nessuna chiamata generata osservabile."
        ],
        "expected_candidate_rank": None,
        "validation_valid": None,
        "execution_reached": False,
        "execution_success": False,
        "end_to_end_success": False,
        "success": False,
        "error_stage": "transport",
    }


def run_case(
    client: httpx.Client,
    agent_url: str,
    case: dict[str, Any],
    run_number: int,
) -> dict[str, Any]:
    """Esegue e valuta un singolo caso contro POST /query."""

    expected = case["expected"]
    started_at = time.perf_counter()

    try:
        response = client.post(
            f"{agent_url.rstrip('/')}/query",
            json={"query": case["query"]},
        )
    except httpx.RequestError as exc:
        return _empty_failure_result(
            case=case,
            run_number=run_number,
            elapsed_seconds=time.perf_counter() - started_at,
            transport_error=str(exc),
        )

    elapsed_seconds = time.perf_counter() - started_at

    try:
        response_body: Any = response.json()
    except ValueError:
        response_body = {"raw": response.text}

    generated_call = _extract_generated_call(response_body)
    generated_call_observed = generated_call is not None

    actual_method = (
        generated_call.get("method")
        if generated_call
        else None
    )
    actual_endpoint = (
        generated_call.get("endpoint")
        if generated_call
        else None
    )

    operation_correct = (
        generated_call is not None
        and actual_method == expected["method"]
        and actual_endpoint == expected["endpoint"]
    )

    if generated_call is not None:
        arguments_correct, semantic_issues = _compare_arguments(
            generated_call=generated_call,
            expected=expected,
        )
    else:
        arguments_correct = False
        semantic_issues = [
            "Nessuna chiamata generata osservabile."
        ]

    semantic_correct = (
        operation_correct
        and arguments_correct
    )

    candidates = _extract_candidates(response_body)

    expected_rank = (
        _expected_candidate_rank(candidates, expected)
        if candidates
        else None
    )

    validation_valid = _extract_validation_valid(
        response_body=response_body,
        status_code=response.status_code,
    )

    persistence_response = _extract_persistence_response(
        response_body
    )
    execution_reached = persistence_response is not None
    execution_success = _execution_success(
        persistence_response
    )

    end_to_end_success = (
        semantic_correct
        and validation_valid is True
        and execution_success
    )

    metrics = (
        response_body.get("metrics", {})
        if isinstance(response_body, dict)
        else {}
    )

    if not isinstance(metrics, dict):
        metrics = {}

    return {
        "case_id": case["id"],
        "case_name": case["name"],
        "run": run_number,
        "query": case["query"],
        "expected": expected,
        "agent_status_code": response.status_code,
        "wall_time_seconds": round(elapsed_seconds, 3),
        "response": response_body,
        "generated_call_observed": generated_call_observed,
        "actual_method": actual_method,
        "actual_endpoint": actual_endpoint,
        "operation_correct": operation_correct,
        "arguments_correct": arguments_correct,
        "semantic_correct": semantic_correct,
        "semantic_issues": semantic_issues,
        "expected_candidate_rank": expected_rank,
        "validation_valid": validation_valid,
        "execution_reached": execution_reached,
        "execution_success": execution_success,
        "generated_call": generated_call,
        "prepared_request": (
            response_body.get("prepared_request")
            if isinstance(response_body, dict)
            else None
        ),
        "persistence_response": persistence_response,
        "model": (
            response_body.get("model")
            if isinstance(response_body, dict)
            else None
        ),
        "total_duration_ns": metrics.get("total_duration_ns"),
        "prompt_eval_count": metrics.get("prompt_eval_count"),
        "eval_count": metrics.get("eval_count"),
        "error_stage": _classify_error_stage(
            status_code=response.status_code,
            response_body=response_body,
        ),
        "end_to_end_success": end_to_end_success,
        "success": end_to_end_success,
    }


def _rate(
    numerator: int,
    denominator: int,
) -> float:
    return numerator / denominator if denominator else 0.0


def _average(
    values: list[float],
) -> float | None:
    if not values:
        return None

    return round(sum(values) / len(values), 3)


def _build_metrics(
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    """Calcola le metriche per un insieme di esecuzioni."""

    total = len(results)

    generated = sum(
        result.get("generated_call_observed") is True
        for result in results
    )
    correct_operations = sum(
        result.get("operation_correct") is True
        for result in results
    )
    correct_arguments = sum(
        result.get("arguments_correct") is True
        for result in results
    )
    semantic_correct = sum(
        result.get("semantic_correct") is True
        for result in results
    )
    validation_pass = sum(
        result.get("validation_valid") is True
        for result in results
    )
    validation_reached = sum(
        isinstance(result.get("validation_valid"), bool)
        for result in results
    )
    execution_reached = sum(
        result.get("execution_reached") is True
        for result in results
    )
    execution_success = sum(
        result.get("execution_success") is True
        for result in results
    )
    end_to_end = sum(
        result.get("end_to_end_success") is True
        for result in results
    )
    http_200 = sum(
        result.get("agent_status_code") == 200
        for result in results
    )

    wall_times = [
        float(result["wall_time_seconds"])
        for result in results
        if isinstance(
            result.get("wall_time_seconds"),
            (int, float),
        )
    ]

    return {
        "total_runs": total,
        "generated_call_runs": generated,
        "generation_observation_rate": _rate(
            generated,
            total,
        ),
        "correct_operations": correct_operations,
        "operation_accuracy": _rate(
            correct_operations,
            total,
        ),
        "correct_arguments": correct_arguments,
        "arguments_accuracy": _rate(
            correct_arguments,
            total,
        ),
        "semantically_correct_runs": semantic_correct,
        "semantic_accuracy": _rate(
            semantic_correct,
            total,
        ),
        "validation_reached_runs": validation_reached,
        "validation_pass_runs": validation_pass,
        "validation_pass_rate_total": _rate(
            validation_pass,
            total,
        ),
        "validation_pass_rate_when_reached": _rate(
            validation_pass,
            validation_reached,
        ),
        "execution_reached_runs": execution_reached,
        "execution_success_runs": execution_success,
        "execution_success_rate": _rate(
            execution_success,
            total,
        ),
        "end_to_end_successful_runs": end_to_end,
        "end_to_end_success_rate": _rate(
            end_to_end,
            total,
        ),
        "http_200_runs": http_200,
        "average_wall_time_seconds": _average(
            wall_times
        ),
    }


def build_summary(
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    """Calcola metriche aggregate e per singolo caso."""

    by_case: dict[str, list[dict[str, Any]]] = defaultdict(
        list
    )

    for result in results:
        by_case[result["case_id"]].append(result)

    per_case = {
        case_id: _build_metrics(case_results)
        for case_id, case_results in by_case.items()
    }

    return {
        **_build_metrics(results),
        "per_case": per_case,
    }


def _status_label(
    value: bool | None,
) -> str:
    if value is True:
        return "OK"

    if value is False:
        return "FAIL"

    return "N/A"


def _print_case_result(
    result: dict[str, Any],
) -> None:
    status = (
        "OK"
        if result.get("end_to_end_success")
        else "FAIL"
    )

    print(
        f"{status} "
        f"[HTTP {result.get('agent_status_code')} | "
        f"op={_status_label(result.get('operation_correct'))} | "
        f"args={_status_label(result.get('arguments_correct'))} | "
        f"sem={_status_label(result.get('semantic_correct'))} | "
        f"val={_status_label(result.get('validation_valid'))} | "
        f"exec={_status_label(result.get('execution_success'))}]"
    )

    if (
        result.get("semantic_correct") is False
        and result.get("semantic_issues")
    ):
        for issue in result["semantic_issues"]:
            print(f"    semantic: {issue}")

    if result.get("error_stage") is not None:
        print(f"    stage: {result['error_stage']}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Esegue il benchmark semantico "
            "della pipeline finale dell'Agent Service."
        )
    )
    parser.add_argument(
        "--agent-url",
        default=DEFAULT_AGENT_URL,
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=DEFAULT_RUNS,
    )

    args = parser.parse_args()

    if args.runs <= 0:
        raise ValueError(
            "--runs deve essere maggiore di zero."
        )

    cases = load_cases()
    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )
    output_path = (
        SCRIPT_DIR
        / f"results_{timestamp}.json"
    )

    results: list[dict[str, Any]] = []

    with httpx.Client(timeout=360.0) as client:
        for run_number in range(
            1,
            args.runs + 1,
        ):
            print(
                f"\n=== RUN {run_number}/"
                f"{args.runs} ==="
            )

            for case in cases:
                print(
                    f"{case['id']} - "
                    f"{case['name']}...",
                    end=" ",
                    flush=True,
                )

                result = run_case(
                    client=client,
                    agent_url=args.agent_url,
                    case=case,
                    run_number=run_number,
                )

                results.append(result)
                _print_case_result(result)

    summary = build_summary(results)

    document = {
        "benchmark": (
            "WLDT Agent Service - pipeline finale"
        ),
        "created_at": (
            datetime.now().astimezone().isoformat()
        ),
        "runs_per_case": args.runs,
        "case_count": len(cases),
        "scoring": {
            "operation_correct": (
                "Metodo HTTP ed endpoint coincidono "
                "con il ground truth."
            ),
            "arguments_correct": (
                "pathParameters, queryParameters, body "
                "e missingInformation coincidono "
                "esattamente con il ground truth."
            ),
            "semantic_correct": (
                "operation_correct AND arguments_correct."
            ),
            "validation_valid": (
                "Il validatore OpenAPI è stato raggiunto "
                "e ha accettato la chiamata."
            ),
            "execution_success": (
                "La chiamata ha raggiunto il Persistence "
                "Service simulato e questo ha restituito 2xx."
            ),
            "end_to_end_success": (
                "semantic_correct AND validation_valid "
                "AND execution_success."
            ),
        },
        "summary": summary,
        "results": results,
    }

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            document,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print("\n=== RISULTATO ===")
    print(f"Esecuzioni: {summary['total_runs']}")
    print(
        "Accuratezza operazione: "
        f"{summary['operation_accuracy']:.1%}"
    )
    print(
        "Accuratezza semantica: "
        f"{summary['semantic_accuracy']:.1%}"
    )
    print(
        "Validazioni superate: "
        f"{summary['validation_pass_runs']}/"
        f"{summary['total_runs']}"
    )
    print(
        "Esecuzioni Persistence riuscite: "
        f"{summary['execution_success_runs']}/"
        f"{summary['total_runs']}"
    )
    print(
        "Successi end-to-end: "
        f"{summary['end_to_end_successful_runs']}/"
        f"{summary['total_runs']} "
        f"({summary['end_to_end_success_rate']:.1%})"
    )
    print(
        "Tempo medio complessivo: "
        f"{summary['average_wall_time_seconds']} s"
    )
    print(
        f"Risultati salvati in:\n{output_path}"
    )


if __name__ == "__main__":
    main()