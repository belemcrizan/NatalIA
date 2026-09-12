"""Replay exported evidence without executing imported artifacts as code."""

import json

from natalia.evidence import EvidenceRecord, obligation_hash
from natalia.models import StrictModel, Submission

REPLAY_SCHEMA = "natalia-replay-1.0"


class ReplayRequest(StrictModel):
    replay_schema: str
    natalia_version: str | None = None
    input_sha256: str
    submission: dict
    obligations: list[dict]
    verdict: str


def replay(payload: dict, *, max_bytes=65536):
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    if len(raw) > max_bytes:
        return {
            "accepted": False,
            "reason": "Replay payload exceeds size limit",
            "trust": "operational",
        }
    request = ReplayRequest.model_validate(payload)
    if request.replay_schema != REPLAY_SCHEMA:
        return {
            "accepted": False,
            "reason": "Incompatible replay schema",
            "trust": "operational",
        }
    submission = Submission.model_validate(request.submission)
    canonical = submission.model_dump()
    expected = obligation_hash({"canonical": canonical})
    from hashlib import sha256

    digest = sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    if digest != request.input_sha256:
        return {
            "accepted": False,
            "reason": "Submission hash does not match the exported evidence",
            "trust": "operational",
            "expected_hash": digest,
        }
    checked = []
    for item in request.obligations:
        EvidenceRecord.model_validate(
            {
                "adapter_id": item.get("adapter_id") or item.get("oracle"),
                "adapter_version": item.get("adapter_version", "1.0"),
                "fragment": item.get("fragment", "unspecified"),
                "obligation_hash": item.get("obligation_hash", ""),
                "status": item["status"],
                "reason": item.get("reason", ""),
                "trust": item.get("trust", "unavailable"),
                "validation": item.get("validation", "not_applicable"),
            }
        )
        checked.append(item["id"])
    return {
        "accepted": True,
        "reason": "Structural replay succeeded; solvers were not re-executed",
        "obligations": checked,
        "verdict_claimed": request.verdict,
        "hash_ok": True,
        "placeholder": expected,
        "guarantee": "Replay validates schema, hashes and evidence records. It is not a new proof.",
    }
