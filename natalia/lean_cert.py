"""Controlled Lean 4 certification for a declared integer positivity fragment.

The FastAPI process never executes uploaded Lean. It may only invoke `lake`
against the pinned project under formal/, with a timeout and no extra flags.
Absence of Lean fails closed. SMT acceptance is never reused.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

from natalia.evidence import record as evidence_record

FRAGMENT = "lean4_int_poly_pos_v1"
POLICY = "natalia-lean-axiom-policy-v1"
FORMAL_ROOT = Path(__file__).resolve().parents[1] / "formal"
ALLOWED_THEOREMS = {
    "int_sq_nonneg": "NatalIA.int_sq_nonneg",
    "dissipative_term_nonneg": "NatalIA.dissipative_term_nonneg",
}
# Lean 4 kernel / prelude axioms that a sorry-free Int lemma may depend on.
ALLOWED_AXIOMS = frozenset(
    {
        "propext",
        "Quot.sound",
        "Quot.sound.{0}",
        "Classical.choice",
        "funext",
        "Eq.rec",
    }
)
FORBIDDEN_SOURCE = re.compile(r"\b(sorry|admit|axiom|run_cmd|macro|elab|extern)\b")


def _normalize(expr: str) -> str:
    return "".join(expr.split())


def match_fragment(submission) -> dict | None:
    """Return a template id if the obligation maps faithfully onto the Int fragment."""
    claims = submission.claims
    if len(claims) != 1 or claims[0].kind != "relation":
        return None
    claim = claims[0]
    if claim.op != ">=" or _normalize(claim.rhs) != "0":
        return None
    dims = {name: tuple(var.dimension) for name, var in submission.variables.items()}
    zero = ("0",) * 7
    if any(dim != zero for dim in dims.values()):
        return None
    lhs = _normalize(claim.lhs)
    names = list(submission.variables)
    if len(names) == 1:
        x = names[0]
        if lhs in {f"{x}**2", f"{x}*{x}"} and not submission.assumptions:
            return {"template": "int_sq_nonneg", "theorem": ALLOWED_THEOREMS["int_sq_nonneg"], "vars": [x]}
    if len(names) == 2:
        assumptions = [(_normalize(a.lhs), a.op, _normalize(a.rhs)) for a in submission.assumptions]
        for c, v in (names, list(reversed(names))):
            if lhs in {f"{c}*({v}*{v})", f"{c}*{v}*{v}", f"{c}*{v}**2"}:
                if assumptions == [(c, ">=", "0")]:
                    return {
                        "template": "dissipative_term_nonneg",
                        "theorem": ALLOWED_THEOREMS["dissipative_term_nonneg"],
                        "vars": [c, v],
                    }
    return None


def probe_toolchain():
    lake = shutil.which("lake")
    lean = shutil.which("lean")
    toolchain = FORMAL_ROOT / "lean-toolchain"
    lakefile = FORMAL_ROOT / "lakefile.lean"
    version = None
    if lean:
        try:
            completed = subprocess.run(
                [lean, "--version"], capture_output=True, text=True, timeout=5, check=False
            )
            version = (completed.stdout or completed.stderr or "").strip()[:200]
        except (OSError, subprocess.TimeoutExpired):
            version = "lean --version failed"
    available = bool(lake and lean and toolchain.is_file() and lakefile.is_file())
    reason = (
        "Pinned Lean/Lake project is present."
        if available
        else (
            "Lean 4 toolchain is not available in this environment. "
            "Requested Lean certification fails closed and does not reuse SMT."
        )
    )
    return {
        "available": available,
        "reason": reason,
        "lake": lake,
        "lean": lean,
        "version": version,
        "lakefile": str(lakefile) if lakefile.is_file() else None,
        "toolchain": toolchain.read_text(encoding="utf-8").strip() if toolchain.is_file() else None,
        "fragment": FRAGMENT,
        "policy": POLICY,
    }


def _axiom_audit(output: str) -> dict:
    names = set()
    for line in output.splitlines():
        stripped = line.strip()
        if stripped.startswith("'") and "'" in stripped[1:]:
            names.add(stripped.strip("[] '"))
        for token in stripped.replace(",", " ").split():
            if token in ALLOWED_AXIOMS or token.endswith(".choice"):
                names.add(token)
    extra = [name for name in names if name not in ALLOWED_AXIOMS and "sorry" not in name.lower()]
    sorry = [name for name in names if "sorry" in name.lower()]
    unapproved = [name for name in extra if name not in ALLOWED_AXIOMS and not name.startswith("NatalIA")]
    return {
        "ok": len(sorry) == 0 and len(unapproved) == 0,
        "printed": sorted(names),
        "unapproved": unapproved,
        "sorry": sorry,
    }


def check_library(*, timeout_s=60):
    """Build the pinned library and print axioms of the approved theorems."""
    info = probe_toolchain()
    if not info["available"]:
        return {"checked": False, "classification": "toolchain_absent", "reason": info["reason"], "info": info}
    try:
        build = subprocess.run(
            [info["lake"], "build"],
            cwd=FORMAL_ROOT,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "checked": False,
            "classification": "timeout",
            "reason": f"lake build timed out: {exc}",
            "info": info,
        }
    if build.returncode != 0:
        return {
            "checked": False,
            "classification": "dependency",
            "reason": (build.stderr or build.stdout or "lake build failed")[:800],
            "info": info,
        }
    audits = {}
    for key, theorem in ALLOWED_THEOREMS.items():
        printer = (
            f"import NatalIA\n#print axioms {theorem}\n"
        )
        try:
            printed = subprocess.run(
                [info["lake"], "env", "lean", "--stdin"],
                cwd=FORMAL_ROOT,
                input=printer,
                capture_output=True,
                text=True,
                timeout=timeout_s,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return {
                "checked": False,
                "classification": "timeout",
                "reason": f"axiom audit timed out for {theorem}",
                "info": info,
            }
        text = f"{printed.stdout}\n{printed.stderr}"
        if printed.returncode != 0:
            return {
                "checked": False,
                "classification": "type",
                "reason": text[:800],
                "info": info,
            }
        audits[key] = _axiom_audit(text)
        if not audits[key]["ok"]:
            return {
                "checked": False,
                "classification": "unapproved_axioms",
                "reason": f"Axiom policy {POLICY} rejected {theorem}: {audits[key]}",
                "info": info,
                "audits": audits,
            }
    return {
        "checked": True,
        "classification": "accepted",
        "reason": "Pinned library built; approved theorems are sorry-free under the axiom policy",
        "info": info,
        "audits": audits,
    }


def certify(submission, *, timeout_s=60):
    mapping = match_fragment(submission)
    payload = submission.model_dump(exclude_none=True)
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if mapping is None:
        return evidence_record(
            adapter_id="lean",
            fragment=FRAGMENT,
            obligation_id=submission.claims[0].id,
            payload={"stage": "lean", "input_sha256": digest},
            status="unknown",
            reason=(
                "Obligation is outside lean4_int_poly_pos_v1 "
                "(dimensionless integer square or c*v*v with c ≥ 0). "
                "No SMT fallback."
            ),
            trust="unavailable",
            validation="not_run",
            extra={"provider": "lean4", "policy": POLICY, "mapping": None},
        )
    library = check_library(timeout_s=timeout_s)
    if not library.get("checked"):
        return evidence_record(
            adapter_id="lean",
            fragment=FRAGMENT,
            obligation_id=submission.claims[0].id,
            payload={"stage": "lean", "input_sha256": digest, "theorem": mapping["theorem"]},
            status="unknown",
            reason=library.get("reason") or "Lean toolchain unavailable",
            trust="unavailable",
            validation="not_run",
            extra={
                "provider": "lean4",
                "policy": POLICY,
                "mapping": mapping,
                "classification": library.get("classification"),
            },
        )
    sources = [
        (FORMAL_ROOT / "NatalIA" / "Polynomial.lean").read_text(encoding="utf-8"),
        (FORMAL_ROOT / "NatalIA" / "Dissipation.lean").read_text(encoding="utf-8"),
    ]
    if any(FORBIDDEN_SOURCE.search(src) for src in sources):
        return evidence_record(
            adapter_id="lean",
            fragment=FRAGMENT,
            obligation_id=submission.claims[0].id,
            payload={"stage": "lean", "input_sha256": digest},
            status="unknown",
            reason="Pinned Lean sources contain a forbidden construct",
            trust="unavailable",
            extra={"provider": "lean4"},
        )
    return evidence_record(
        adapter_id="lean",
        fragment=FRAGMENT,
        obligation_id=submission.claims[0].id,
        payload={
            "stage": "lean",
            "input_sha256": digest,
            "theorem": mapping["theorem"],
            "interpretation": "integers",
            "not_reals": True,
        },
        status="certified",
        reason=(
            f"Lean kernel checked {mapping['theorem']} in fragment {FRAGMENT}. "
            "The DSL claim is accepted only as the integer image of this template."
        ),
        trust="kernel_certificate",
        validation="independent_pass",
        extra={
            "provider": "lean4",
            "policy": POLICY,
            "mapping": mapping,
            "audits": library.get("audits"),
            "toolchain": library.get("info", {}).get("toolchain"),
        },
    )
