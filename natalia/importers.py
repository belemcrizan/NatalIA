"""Validated import of structured cases. Never executes expressions as Python."""

from pydantic import ValidationError

from natalia.engine import base_result
from natalia.models import Submission

MAX_RECORDS = 50
MAX_BYTES = 256_000


def inspect_records(payload):
    if isinstance(payload, dict) and "records" in payload:
        records = payload["records"]
        policy = payload.get("policy", "reject_duplicates")
        confirm = bool(payload.get("confirm"))
    elif isinstance(payload, list):
        records, policy, confirm = payload, "reject_duplicates", False
    else:
        return {
            "ok": False,
            "errors": [{"index": None, "message": "Expected a list or {records, policy, confirm}"}],
            "accepted": [],
            "duplicates": [],
        }
    if policy not in {"reject_duplicates", "skip_duplicates"}:
        return {
            "ok": False,
            "errors": [{"index": None, "message": "policy must be reject_duplicates or skip_duplicates"}],
            "accepted": [],
            "duplicates": [],
        }
    if len(records) > MAX_RECORDS:
        return {
            "ok": False,
            "errors": [{"index": None, "message": f"At most {MAX_RECORDS} records per import"}],
            "accepted": [],
            "duplicates": [],
        }
    errors, accepted = [], []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append({"index": index, "message": "Record must be an object"})
            continue
        submission = record.get("submission", record)
        try:
            model = Submission.model_validate(submission)
        except ValidationError as exc:
            errors.append({"index": index, "message": exc.errors()[0]["msg"]})
            continue
        dumped = model.model_dump(exclude_none=True)
        digest = base_result(dumped)["input_sha256"]
        accepted.append(
            {
                "index": index,
                "id": record.get("id"),
                "title": dumped["title"],
                "content_hash": digest,
                "submission": dumped,
            }
        )
    return {
        "ok": not errors,
        "policy": policy,
        "confirm": confirm,
        "errors": errors,
        "accepted": accepted,
        "count": len(accepted),
        "note": "Import never executes solver code or imported artifacts.",
    }
