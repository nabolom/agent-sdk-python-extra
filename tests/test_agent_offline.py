from __future__ import annotations

import json

import pytest

from agent_sdk_lab.agent import main


def test_default_mode_is_offline_even_without_sdk_installed(capsys, monkeypatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert main(["--case", "SYN-001"]) == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["mode"] == "offline"
    assert payload["model_call_made"] is False


def test_live_mode_stops_without_api_key(capsys, monkeypatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert main(["--case", "SYN-001", "--live"]) == 2
    captured = capsys.readouterr()
    assert "no se hizo ninguna llamada" in captured.err
    assert captured.out == ""


def test_offline_unknown_case_fails_without_live_call(capsys) -> None:
    assert main(["--case", "SYN-404"]) == 2
    captured = capsys.readouterr()
    assert "No existe" in captured.err
    assert captured.out == ""
