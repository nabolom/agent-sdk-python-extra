"""Contrato de salida y validación local independiente del SDK."""

from __future__ import annotations

from typing import Any

CATEGORIES = {"access", "data_quality", "security", "unknown"}
PRIORITIES = {"P0", "P1", "P2", "P3", "unknown"}
NEXT_STEPS = {"request_information", "escalate_to_human", "monitor"}

OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "case_id": {"type": "string"},
        "category": {"type": "string", "enum": sorted(CATEGORIES)},
        "priority": {"type": "string", "enum": sorted(PRIORITIES)},
        "summary": {"type": "string"},
        "evidence": {"type": "array", "items": {"type": "string"}, "uniqueItems": True},
        "next_step": {"type": "string", "enum": sorted(NEXT_STEPS)},
        "needs_human_review": {"type": "boolean"},
        "prompt_injection_detected": {"type": "boolean"},
    },
    "required": [
        "case_id",
        "category",
        "priority",
        "summary",
        "evidence",
        "next_step",
        "needs_human_review",
        "prompt_injection_detected",
    ],
    "additionalProperties": False,
}


def validate_response(response: Any, expected_case_id: str) -> dict[str, Any]:
    """Valida la salida estructurada también en modo offline."""
    if not isinstance(response, dict):
        raise ValueError("La respuesta debe ser un objeto JSON.")

    required = set(OUTPUT_SCHEMA["required"])
    missing = required - response.keys()
    extra = response.keys() - required
    if missing:
        raise ValueError(f"Faltan campos obligatorios: {', '.join(sorted(missing))}.")
    if extra:
        raise ValueError(f"Campos no permitidos: {', '.join(sorted(extra))}.")

    if response["case_id"] != expected_case_id:
        raise ValueError("case_id de la respuesta no coincide con el caso solicitado.")
    if response["category"] not in CATEGORIES:
        raise ValueError("category no pertenece al contrato del laboratorio.")
    if response["priority"] not in PRIORITIES:
        raise ValueError("priority no pertenece al contrato del laboratorio.")
    if response["next_step"] not in NEXT_STEPS:
        raise ValueError("next_step no pertenece al contrato del laboratorio.")
    if not isinstance(response["summary"], str) or not response["summary"].strip():
        raise ValueError("summary debe ser texto no vacío.")
    if not isinstance(response["evidence"], list) or any(
        not isinstance(item, str) or not item.strip() for item in response["evidence"]
    ):
        raise ValueError("evidence debe ser una lista de identificadores de evidencia.")
    if len(set(response["evidence"])) != len(response["evidence"]):
        raise ValueError("evidence no debe contener identificadores duplicados.")
    if type(response["needs_human_review"]) is not bool:
        raise ValueError("needs_human_review debe ser booleano.")
    if type(response["prompt_injection_detected"]) is not bool:
        raise ValueError("prompt_injection_detected debe ser booleano.")

    return dict(response)
