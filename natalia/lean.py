"""Lean 4 adapter.

Availability of a `lean` executable is not a certificate. Comment-only exports,
`sorry`, `admit`, and extra axioms never produce KERNEL_CHECKED. A Lean kernel
failure is classified (syntax, type, dependency, timeout, incomplete proof);
it is not a refutation of the scientific claim.

The original checklist mentions `lean --check`. Lean 4 does not guarantee that
flag. This adapter invokes `lean <file>` and records the argv actually used.
"""

from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from natalia.evidence import record as evidence_record

FRAGMENT = "lean4_export_sq_nonneg_v1"
CHECK_ARGV_TEMPLATE = ["lean", "<file>"]


def probe():
    executable = shutil.which("lean")
    lakefile = Path(__file__).resolve().parents[1] / "formal" / "lakefile.lean"
    version = None
    if executable:
        try:
            completed = subprocess.run(
                [executable, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            version = (completed.stdout or completed.stderr or "").strip()[:200]
        except (OSError, subprocess.TimeoutExpired):
            version = "lean --version failed"
    if executable and lakefile.exists():
        return {
            "available": True,
            "reason": (
                "Lean executable found. Kernel checking still requires a matching lakefile, "
                "approved imports, and a sorry-free theorem matching the obligation."
            ),
            "lean": executable,
            "version": version,
            "check_command": CHECK_ARGV_TEMPLATE,
            "lakefile": str(lakefile),
        }
    return {
        "available": False,
        "reason": (
            "Lean 4 is an optional extra. The default local install does not require it. "
            "Certificates use natalia.kernel when Lean is absent. Presence of Lean without "
            "a checked theorem is not KERNEL_CHECKED."
        ),
        "lean": executable,
        "version": version,
        "check_command": CHECK_ARGV_TEMPLATE,
        "lakefile_present": lakefile.exists(),
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
    """Lean 4 export bound to the obligation hash.

    The theorem is stated, not proved. The file must fail to be a certificate
    until a human-approved, sorry-free proof of this exact statement exists.
    The statement is not weakened from ℝ-style DSL to ℕ to obtain a green kernel.
    """
    binders = " ".join(f"({name} : ℝ)" for name in variables) or "(x : ℝ)"
    prop = f"({proposition['lhs']}) {proposition['op']} ({proposition['rhs']})"
    return f"""-- NatalIA Lean export. Not a certificate.
-- obligation_hash: {obligation_hash}
-- Independent certificate in this profile: natalia.kernel, fragment poly_sos_identity_q_v1.
-- Do not weaken this proposition. A different statement is a different obligation.
-- Check command (Lean 4): lean Obligation.lean
-- The flag `lean --check` from the original checklist is treated as mandatory
-- checking intent, not as a guaranteed CLI option of the pinned Lean version.

theorem natalia_obligation {binders} : {prop} := by
  -- Proof omitted: ℝ and the relation require approved imports (e.g. Mathlib).
  -- This hole is intentional. Completing it with a different proposition is forbidden.
  sorry
"""


def classify_lean_output(*, returncode, stdout, stderr, source, timed_out=False):
    if timed_out:
        return "timeout"
    if _is_comment_or_empty(source):
        return "export_not_a_proof"
    text = f"{stdout}\n{stderr}".lower()
    if "sorry" in source or "admit" in source:
        return "incomplete_proof"
    if re.search(r"(?m)^axiom\s", source):
        return "incomplete_proof"
    if returncode == 0:
        if _is_comment_or_empty(source):
            return "export_not_a_proof"
        if "sorry" in source or "admit" in source:
            return "incomplete_proof"
        return "accepted"
    if "unknown identifier" in text or "unknown constant" in text or "unknown namespace" in text:
        return "dependency"
    if "unexpected token" in text or "expected token" in text:
        return "syntax"
    if "type mismatch" in text or "type error" in text:
        return "type"
    if "timeout" in text:
        return "timeout"
    if "sorry" in text or "declaration uses 'sorry'" in text:
        return "incomplete_proof"
    return "incomplete_proof"


def _is_comment_or_empty(source: str) -> bool:
    stripped = re.sub(r"--[^\n]*", "", source)
    stripped = re.sub(r"/-.*?-/", "", stripped, flags=re.S)
    return not stripped.strip()


def _forbids_certificate(source: str) -> str | None:
    if _is_comment_or_empty(source):
        return "Export contains no checkable declaration"
    if "sorry" in source or "admit" in source:
        return "Export contains sorry/admit; rejected as a certificate"
    if re.search(r"(?m)^axiom\s", source):
        return "Export introduces axioms; rejected as a certificate"
    if "theorem natalia_obligation" not in source:
        return "Export does not contain theorem natalia_obligation bound to the obligation"
    return None


def inspect_export(source: str):
    """Classify an export without executing Lean. Used when the toolchain is absent."""
    reason = _forbids_certificate(source)
    classification = classify_lean_output(
        returncode=1,
        stdout="",
        stderr=reason or "",
        source=source,
    )
    return {
        "checked": False,
        "reason": reason or "Export was not submitted to a Lean kernel",
        "trust": "unavailable",
        "classification": classification,
        "refutation": False,
        "check_command": CHECK_ARGV_TEMPLATE,
        "rejected_sorry": "sorry" in source or "admit" in source,
    }


def check_export(source: str, timeout_s=20):
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
    forbidden = _forbids_certificate(source)
    info = probe()
    if forbidden:
        result = inspect_export(source)
        result["source_sha256"] = digest
        if not info["available"]:
            result["reason"] = f"{forbidden}. {info['reason']}"
        return result
    if not info["available"]:
        return {
            "checked": False,
            "reason": info["reason"],
            "trust": "unavailable",
            "classification": "toolchain_absent",
            "refutation": False,
            "source_sha256": digest,
            "check_command": CHECK_ARGV_TEMPLATE,
            "rejected_sorry": False,
        }
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "Obligation.lean"
        path.write_text(source, encoding="utf-8")
        argv = [info["lean"], str(path)]
        try:
            completed = subprocess.run(
                argv,
                capture_output=True,
                text=True,
                timeout=timeout_s,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return {
                "checked": False,
                "reason": f"Lean execution timed out: {exc}",
                "trust": "unavailable",
                "classification": "timeout",
                "refutation": False,
                "source_sha256": digest,
                "check_command": ["lean", "Obligation.lean"],
            }
        except OSError as exc:
            return {
                "checked": False,
                "reason": f"Lean execution failed: {exc}",
                "trust": "unavailable",
                "classification": "dependency",
                "refutation": False,
                "source_sha256": digest,
                "check_command": ["lean", "Obligation.lean"],
            }
        classification = classify_lean_output(
            returncode=completed.returncode,
            stdout=completed.stdout or "",
            stderr=completed.stderr or "",
            source=source,
        )
        if completed.returncode != 0 or classification != "accepted":
            return {
                "checked": False,
                "reason": (
                    "Lean did not accept a complete proof of the exported obligation. "
                    f"Classification: {classification}. This is not a scientific REFUTED."
                ),
                "trust": "unavailable",
                "classification": classification,
                "refutation": False,
                "source_sha256": digest,
                "check_command": ["lean", "Obligation.lean"],
                "stderr": (completed.stderr or "")[:500],
            }
        return {
            "checked": True,
            "reason": "Lean kernel accepted a sorry-free theorem natalia_obligation",
            "trust": "kernel_certificate",
            "classification": "accepted",
            "refutation": False,
            "source_sha256": digest,
            "check_command": ["lean", "Obligation.lean"],
        }
