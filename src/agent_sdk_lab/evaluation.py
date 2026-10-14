"""Scorer determinista para respuestas live o fixtures locales."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .cases import DATA_PATH, CaseNotFound, get_case
from .schema import validate_response

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPECTATIONS_PATH = PROJECT_ROOT / "evals" / "expectativas.jsonl"
DEMO_RESPONSES_PATH = PROJECT_ROOT / "evals" / "respuestas_demo.jsonl"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Lee objetos JSONL e informa la línea si el archivo está mal formado."""
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"JSON inválido en {path}:{line_number}: {exc.msg}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"Cada línea debe ser un objeto JSON: {path}:{line_number}.")
            rows.append(row)
    return rows


def score_response(expectation: dict[str, Any], response: Any, data_path: Path = DATA_PATH) -> list[str]:
    """Devuelve errores explicables; lista vacía significa que el caso pasa.

    Este scorer compara reglas declaradas; no llama a un LLM juez ni determina
    si una respuesta es buena fuera de los criterios que están escritos aquí.
    """
    case_id = expectation.get("case_id")
    if not isinstance(case_id, str):
        return ["La expectativa no tiene case_id válido."]
    try:
        # Primero se valida forma/tipos y consistencia del ID del caso.
        validated = validate_response(response, case_id)
    except (TypeError, ValueError) as exc:
        return [str(exc)]

    # Luego se comparan solo los campos que la expectativa marca como críticos.
    issues: list[str] = []
    expected_fields = expectation.get("expected", {})
    if not isinstance(expected_fields, dict):
        return ["expected debe ser un objeto JSON."]
    for field, expected_value in expected_fields.items():
        if validated.get(field) != expected_value:
            issues.append(f"{field}: esperado {expected_value!r}, recibido {validated.get(field)!r}.")

    # Solo cuenta como evidencia un ID que exista en el registro local asociado.
    try:
        case_record = get_case(case_id, data_path)
        known_fact_ids = {fact["fact_id"] for fact in case_record["facts"]}
    except CaseNotFound:
        # SYN-404 no tiene hechos; por tanto, su respuesta no debe inventarlos.
        known_fact_ids = set()

    evidence = set(validated["evidence"])
    unknown_evidence = evidence - known_fact_ids
    if unknown_evidence:
        issues.append(f"Evidencia no presente en el registro: {', '.join(sorted(unknown_evidence))}.")

    # El expected fija evidencias mínimas; no obliga a citar todos los hechos.
    required_evidence = set(expectation.get("required_evidence", []))
    missing_evidence = required_evidence - evidence
    if missing_evidence:
        issues.append(f"Falta evidencia requerida: {', '.join(sorted(missing_evidence))}.")
    return issues


def evaluate_files(
    responses_path: Path = DEMO_RESPONSES_PATH,
    expectations_path: Path = EXPECTATIONS_PATH,
    data_path: Path = DATA_PATH,
) -> list[dict[str, Any]]:
    """Evalúa cada caso esperado contra una respuesta registrada por case_id."""
    expectations = read_jsonl(expectations_path)
    responses = read_jsonl(responses_path)

    # Construimos un índice para comparar filas por ID, no por orden del archivo.
    # Si un ID aparece duplicado se marca como ambiguo y fallará explícitamente.
    response_by_case: dict[str, Any] = {}
    for row in responses:
        case_id = row.get("case_id")
        if not isinstance(case_id, str):
            continue
        if case_id in response_by_case:
            response_by_case[case_id] = None
        else:
            response_by_case[case_id] = row.get("response")

    # Una expectativa sin respuesta también produce FAIL; no omitimos casos.
    results: list[dict[str, Any]] = []
    for expectation in expectations:
        case_id = expectation.get("case_id")
        response = response_by_case.get(case_id)
        issues = ["No se encontró respuesta para este case_id."] if response is None else score_response(
            expectation, response, data_path
        )
        results.append({"case_id": case_id, "passed": not issues, "issues": issues})
    return results
