from __future__ import annotations

import json

from agent_sdk_lab.evaluation import (
    DEMO_RESPONSES_PATH,
    EXPECTATIONS_PATH,
    evaluate_files,
    read_jsonl,
    score_response,
)


def test_demo_fixtures_pass_all_four_eval_types() -> None:
    results = evaluate_files()
    assert len(results) == 4
    assert all(result["passed"] for result in results)
    assert {result["case_id"] for result in results} == {"SYN-001", "SYN-002", "SYN-003", "SYN-404"}


def test_score_response_rejects_unseen_evidence_id() -> None:
    expectation = next(row for row in read_jsonl(EXPECTATIONS_PATH) if row["case_id"] == "SYN-001")
    response = next(row["response"] for row in read_jsonl(DEMO_RESPONSES_PATH) if row["case_id"] == "SYN-001")
    response["evidence"] = ["F1", "FABRICATED-99"]
    issues = score_response(expectation, response)
    assert any("Evidencia no presente" in issue for issue in issues)


def test_score_response_rejects_failure_to_escalate_boundary_case() -> None:
    expectation = next(row for row in read_jsonl(EXPECTATIONS_PATH) if row["case_id"] == "SYN-002")
    response = next(row["response"] for row in read_jsonl(DEMO_RESPONSES_PATH) if row["case_id"] == "SYN-002")
    response["needs_human_review"] = False
    issues = score_response(expectation, response)
    assert any("needs_human_review" in issue for issue in issues)
