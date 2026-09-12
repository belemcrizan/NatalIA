"""Curated regression corpus, not PhysVerifyBench or a generalization claim."""

import json
import sys
from pathlib import Path

from natalia.worker import execute


def main():
    rows = []
    for path in sorted((Path(__file__).parents[1] / "natalia/examples").glob("*.json")):
        case = json.loads(path.read_text())
        result = execute(case["submission"])
        rows.append(
            {
                "id": case["id"],
                "expected": case["expected_verdict"],
                "actual": result["verdict"],
                "passed": case["expected_verdict"] == result["verdict"],
                "duration_ms": result["duration_ms"],
            }
        )
    report = {
        "corpus": "local-curated-regression-v1",
        "count": len(rows),
        "passed": sum(r["passed"] for r in rows),
        "confidence_calibration": None,
        "scope": "Hand-authored regression cases; not a scientific benchmark or estimate of FPR",
        "cases": rows,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0 if all(r["passed"] for r in rows) else 1)


if __name__ == "__main__":
    main()
