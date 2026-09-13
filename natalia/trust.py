"""Versioned trust contract: operational state, conclusion, and evidence guarantee are distinct."""

from typing import Literal

from natalia.models import StrictModel

TRUST_CONTRACT = "natalia-trust-1.0"

JobStatus = Literal[
    "queued",
    "running",
    "succeeded",
    "failed",
    "cancelled",
    "timed_out",
    "rejected",
]
Conclusion = Literal["ACCEPTED", "REFUTED", "INVALID", "ABSTAIN"]
GuaranteeLevel = Literal[
    "SMT_RELATIVE",
    "EXACT_WITNESS_CHECKED",
    "INTERVAL_ENCLOSURE",
    "KERNEL_CHECKED",
    "STATIC_COMPILE",
    "ADVISORY",
    "UNAVAILABLE",
]
VerificationMode = Literal["fast", "certified"]

GUARANTEE_NOTES = {
    "SMT_RELATIVE": "Relative to the Z3 encoding and stated premises. Not an independent kernel certificate.",
    "EXACT_WITNESS_CHECKED": "A rational assignment was re-evaluated with exact arithmetic, independently of the solver's claimed status.",
    "INTERVAL_ENCLOSURE": "Exact rational box enclosure on a declared finite domain. Not a global real-line certificate.",
    "KERNEL_CHECKED": "An independent checker accepted a proof object bound to this exact obligation hash.",
    "STATIC_COMPILE": "Dimensional/AST rejection before solvers. Not a mathematical refutation of a well-typed claim.",
    "ADVISORY": "Informative only. Must not be promoted to a certificate.",
    "UNAVAILABLE": "The requested checker was not run or is not installed.",
}

CERTIFIED_ACCEPT = frozenset({"KERNEL_CHECKED"})
CERTIFIED_REFUTE = frozenset({"EXACT_WITNESS_CHECKED"})


class TrustReport(StrictModel):
    contract: Literal["natalia-trust-1.0"] = TRUST_CONTRACT
    verification_mode: VerificationMode
    job_status: JobStatus | None = None
    conclusion: Conclusion
    guarantee_level: GuaranteeLevel
    critical: bool = False
    policy_block: str | None = None
    tcb: list[str]


def classify_fast(verdict: str, obligations: list[dict]) -> GuaranteeLevel:
    if verdict == "INVALID":
        return "STATIC_COMPILE"
    if verdict == "REFUTED":
        if any(item.get("trust") == "exact_rational_witness" for item in obligations):
            return "EXACT_WITNESS_CHECKED"
        if any(item.get("adapter_id") == "interval" and item.get("status") == "refuted" for item in obligations):
            return "INTERVAL_ENCLOSURE"
        return "ADVISORY"
    if verdict == "ACCEPTED":
        if any(item.get("trust") == "kernel_certificate" for item in obligations):
            return "KERNEL_CHECKED"
        return "SMT_RELATIVE"
    trusts = {item.get("trust") for item in obligations}
    if trusts <= {"cas_advisory", "unavailable", "operational", "smt_relative", "static_compile"}:
        return "ADVISORY"
    return "ADVISORY"


def apply_policy(*, mode: VerificationMode, critical: bool, conclusion: Conclusion, guarantee: GuaranteeLevel):
    """Return (conclusion, guarantee, policy_block). Never silently downgrades Certified to Fast."""
    if mode == "certified":
        if conclusion == "ACCEPTED" and guarantee not in CERTIFIED_ACCEPT:
            return "ABSTAIN", guarantee if guarantee != "SMT_RELATIVE" else "UNAVAILABLE", "certified_rejects_smt_only"
        if conclusion == "REFUTED" and guarantee not in CERTIFIED_REFUTE:
            return "ABSTAIN", guarantee, "certified_refute_requires_independent_witness"
        return conclusion, guarantee, None
    if critical and conclusion == "ACCEPTED" and guarantee not in CERTIFIED_ACCEPT:
        return "ABSTAIN", guarantee, "critical_requires_certificate"
    return conclusion, guarantee, None


def tcb_for(mode: VerificationMode, adapters: list[str]) -> list[str]:
    base = [
        "natalia.dsl parser and elaborator",
        "natalia.compile dimensional checker (Q^7)",
        "Python runtime and standard library arithmetic",
        "host operating system and process isolation of the worker",
    ]
    extra = {
        "z3": "Z3 solver and the QF_NRA encoding in natalia.oracles",
        "sympy": "SymPy limit routine (advisory path only)",
        "interval": "natalia.interval exact rational box arithmetic",
        "kernel": "natalia.kernel polynomial identity/sum-of-squares checker",
        "lean": "Lean 4 executable, lakefile, and any imported libraries/axioms",
    }
    listed = list(base)
    for name in adapters:
        if name in extra and extra[name] not in listed:
            listed.append(extra[name])
    if mode == "fast":
        listed.append("Fast-mode policy: SMT-relative acceptance is not independently certified")
    else:
        listed.append("Certified-mode policy: SMT UNSAT cannot close an acceptance")
    return listed
