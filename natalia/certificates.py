"""Independent rechecking of stored certificates. Does not execute imported files as code."""

from natalia.dsl import relation_nodes
from natalia.kernel import check_certificate, obligation_payload
from natalia.models import Submission


def recheck(payload: dict):
    """Reconstruct the obligation and verify the certificate in-process.

    This is a clean-checker path for the polynomial fragment. It does not invoke Z3.
    """
    submission = Submission.model_validate(payload["submission"])
    certificate = payload.get("certificate") or {}
    claim_id = certificate.get("proposition", {}).get("id")
    claim = next((c for c in submission.claims if c.id == claim_id), None)
    if claim is None or claim.kind != "relation":
        return {
            "accepted": False,
            "reason": "Certificate is not bound to a relation claim in this submission",
            "guarantee_level": "UNAVAILABLE",
        }
    compiled = relation_nodes(claim, submission.variables)
    ok, reason = check_certificate(certificate, claim, compiled, submission)
    return {
        "accepted": ok,
        "reason": reason,
        "guarantee_level": "KERNEL_CHECKED" if ok else "UNAVAILABLE",
        "obligation_hash": certificate.get("obligation_hash"),
        "expected_payload": obligation_payload(claim, submission.assumptions, submission.variables),
        "lean_used": False,
        "smt_used": False,
        "note": "Recheck validates the polynomial certificate only. It does not prove fidelity to a paper.",
    }
