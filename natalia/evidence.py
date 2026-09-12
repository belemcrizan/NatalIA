"""Typed evidence records. Strings alone are not the inter-component contract."""

import hashlib
import json
from typing import Any, Literal

from natalia.models import StrictModel

ObligationStatus = Literal["certified", "refuted", "unknown", "invalid"]
TrustLevel = Literal[
    "smt_relative",
    "exact_rational_witness",
    "cas_advisory",
    "static_compile",
    "operational",
    "unavailable",
]
ValidationState = Literal["independent_pass", "independent_fail", "not_applicable", "not_run"]


class EvidenceRecord(StrictModel):
    adapter_id: str
    adapter_version: str
    fragment: str
    obligation_hash: str
    status: ObligationStatus
    reason: str
    trust: TrustLevel
    validation: ValidationState
    artifacts: dict[str, Any] | None = None
    duration_ms: float | None = None


def obligation_hash(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def record(
    *,
    adapter_id: str,
    fragment: str,
    obligation_id: str,
    payload: dict,
    status: ObligationStatus,
    reason: str,
    trust: TrustLevel,
    validation: ValidationState = "not_applicable",
    adapter_version: str = "1.0",
    extra: dict | None = None,
) -> dict:
    hashed = obligation_hash({"id": obligation_id, **payload})
    body = {
        "id": obligation_id,
        "oracle": adapter_id,
        "adapter_id": adapter_id,
        "adapter_version": adapter_version,
        "fragment": fragment,
        "obligation_hash": hashed,
        "status": status,
        "reason": reason,
        "trust": trust,
        "validation": validation,
    }
    if extra:
        body.update(extra)
    return body
