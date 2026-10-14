from __future__ import annotations

import json

import pytest

from agent_sdk_lab.cases import CaseNotFound, get_case, load_cases


def test_dataset_records_are_fictional_and_fact_ids_are_unique() -> None:
    cases = load_cases()
    assert set(cases) == {"SYN-001", "SYN-002", "SYN-003"}
    for record in cases.values():
        assert record["synthetic"] is True
        fact_ids = [fact["fact_id"] for fact in record["facts"]]
        assert len(fact_ids) == len(set(fact_ids))


def test_get_case_returns_exact_match() -> None:
    record = get_case("SYN-001")
    assert record["case_id"] == "SYN-001"
    assert record["facts"][0]["fact_id"] == "F1"


def test_unknown_case_raises_and_does_not_accept_path_input() -> None:
    with pytest.raises(CaseNotFound):
        get_case("../../.env")


def test_loader_rejects_duplicate_case_ids(tmp_path) -> None:
    row = {"case_id": "SYN-001", "synthetic": True, "facts": []}
    data = tmp_path / "duplicate.jsonl"
    data.write_text(json.dumps(row) + "\n" + json.dumps(row) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="duplicado"):
        load_cases(data)
