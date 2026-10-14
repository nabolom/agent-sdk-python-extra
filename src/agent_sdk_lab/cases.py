"""Carga acotada del dataset local sintético; el modelo no decide rutas."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# La ruta de datos se calcula desde este paquete; nunca viene del prompt/modelo.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "casos_sinteticos.jsonl"


class CaseNotFound(LookupError):
    """El identificador solicitado no existe en el dataset local."""


def load_cases(path: Path = DATA_PATH) -> dict[str, dict[str, Any]]:
    """Carga registros JSONL y rechaza IDs o evidencias duplicados."""
    cases: dict[str, dict[str, Any]] = {}
    with path.open(encoding="utf-8") as file:
        # JSONL guarda un objeto por línea; el número permite señalar errores
        # directamente sin que el alumno tenga que adivinar qué registro falló.
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"JSON inválido en {path}:{line_number}: {exc.msg}") from exc

            # Aceptamos solo IDs sintéticos con prefijo explícito.
            case_id = record.get("case_id")
            if not isinstance(case_id, str) or not case_id.startswith("SYN-"):
                raise ValueError(f"case_id inválido en {path}:{line_number}; solo se admiten IDs SYN-.")
            if case_id in cases:
                # Un ID duplicado haría ambiguo qué registro devolvemos.
                raise ValueError(f"case_id duplicado: {case_id}")
            if record.get("synthetic") is not True:
                raise ValueError(f"El registro {case_id} no está marcado como sintético.")

            # Las pruebas esperan una lista de hechos con IDs únicos para que
            # la evaluación pueda comprobar evidencia sin llamar a un modelo.
            facts = record.get("facts")
            if not isinstance(facts, list):
                raise ValueError(f"facts debe ser una lista para {case_id}.")
            fact_ids = [fact.get("fact_id") for fact in facts]
            if any(not isinstance(fact_id, str) for fact_id in fact_ids):
                raise ValueError(f"fact_id inválido para {case_id}.")
            if len(set(fact_ids)) != len(fact_ids):
                raise ValueError(f"fact_id duplicado para {case_id}.")
            cases[case_id] = record
    return cases


def get_case(case_id: str, path: Path = DATA_PATH) -> dict[str, Any]:
    """Devuelve solo el registro cuyo identificador exacto coincide."""
    if not isinstance(case_id, str) or not case_id.strip():
        raise CaseNotFound("El case_id está vacío.")

    # Se hace lookup de una clave en el dataset; no se concatena el input a una
    # ruta de archivo, por lo que valores tipo '../../.env' no abren archivos.
    record = load_cases(path).get(case_id.strip())
    if record is None:
        raise CaseNotFound(f"No existe el caso sintético {case_id!r}.")
    return record
