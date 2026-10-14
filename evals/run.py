"""Ejecuta evals locales sin iniciar Claude Agent SDK ni realizar llamadas."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from agent_sdk_lab.evaluation import DEMO_RESPONSES_PATH, evaluate_files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evalúa respuestas registradas sin llamada live.")
    parser.add_argument(
        "--responses",
        type=Path,
        default=DEMO_RESPONSES_PATH,
        help="JSONL con filas {case_id, response}; por defecto usa fixtures didácticos.",
    )
    args = parser.parse_args(argv)
    results = evaluate_files(args.responses)
    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"{status} {result['case_id']}")
        for issue in result["issues"]:
            print(f"  - {issue}")
    passed = sum(result["passed"] for result in results)
    print(json.dumps({"passed": passed, "total": len(results)}, ensure_ascii=False))
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
