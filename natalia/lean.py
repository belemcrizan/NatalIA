"""Lean 4 adapter. Absent toolchain is reported, never mocked. Generated files are exports."""

import hashlib
import shutil
import subprocess
import tempfile
from pathlib import Path

from natalia.evidence import record as evidence_record

FRAGMENT = "lean4_export_sq_nonneg_v1"


def probe():
    executable = shutil.which("lean")
    lakefile = Path(__file__).resolve().parents[1] / "formal" / "lakefile.lean"
    if executable and lakefile.exists():
        return {
            "available": True,
            "reason": "Lean executable found. Kernel checking still requires a matching lakefile and approved imports.",
            "lean": executable,
        }
    return {
        "available": False,
        "reason": "Lean 4 is an optional extra. The default local install does not require it. Certificates use natalia.kernel when Lean is absent.",
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


def export_square_nonneg(obligation_hash, variables, proposition):
    """Lean 4 sketch bound to the obligation hash. Not a kernel certificate by itself."""
    binders = " ".join(f"({name} : ℝ)" for name in variables) or "(x : ℝ)"
    prop = f"({proposition['lhs']}) {proposition['op']} ({proposition['rhs']})"
    return f"""-- NatalIA Lean export (not checked unless Lean 4 + approved imports run this file).
-- obligation_hash: {obligation_hash}
-- Independent certificate in this profile: natalia.kernel, fragment poly_sos_identity_q_v1.
-- Do not weaken this proposition. A different statement is a different obligation.

/-
  Candidate proposition (DSL transcript, not a completed Lean proof):
  theorem natalia_obligation {binders} : {prop}
  Imports and tactics are intentionally omitted so an absent Mathlib cannot be
  reported as a successful kernel check.
-/
"""


def check_export(source: str, timeout_s=20):
    info = probe()
    if not info["available"]:
        return {
            "checked": False,
            "reason": info["reason"],
            "trust": "unavailable",
            "rejected_sorry": "sorry" in source,
        }
    if "sorry" in source or "admit" in source:
        return {
            "checked": False,
            "reason": "Export contains sorry/admit; rejected as a certificate",
            "trust": "unavailable",
            "rejected_sorry": True,
        }
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "Obligation.lean"
        path.write_text(source, encoding="utf-8")
        try:
            completed = subprocess.run(
                [info["lean"], str(path)],
                capture_output=True,
                text=True,
                timeout=timeout_s,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return {
                "checked": False,
                "reason": f"Lean execution failed: {exc}",
                "trust": "unavailable",
                "source_sha256": digest,
            }
        if completed.returncode != 0:
            return {
                "checked": False,
                "reason": "Lean rejected the export (missing imports or proof)",
                "trust": "unavailable",
                "source_sha256": digest,
                "stderr": (completed.stderr or "")[:500],
            }
        return {
            "checked": True,
            "reason": "Lean kernel accepted the export",
            "trust": "kernel_certificate",
            "source_sha256": digest,
        }
