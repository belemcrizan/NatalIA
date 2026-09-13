"""Lean 4 adapter boundary. Absent toolchain is reported, never mocked."""

import shutil
from pathlib import Path

from natalia.evidence import record as evidence_record


def probe():
    executable = shutil.which("lean")
    lakefile = Path(__file__).resolve().parents[1] / "formal" / "lakefile.lean"
    if executable and lakefile.exists():
        return {
            "available": True,
            "reason": "Lean executable found; fragment generation is still limited to CI cases",
            "lean": executable,
        }
    return {
        "available": False,
        "reason": "Lean 4 is an optional extra. The default local install does not require it.",
        "lean": executable,
    }


def unavailable_record(obligation_id="lean"):
    info = probe()
    return evidence_record(
        adapter_id="lean",
        fragment="not_installed",
        obligation_id=obligation_id,
        payload={"stage": "lean"},
        status="unknown",
        reason=info["reason"],
        trust="unavailable",
        validation="not_run",
    )
