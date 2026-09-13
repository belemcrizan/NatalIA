"""Release gates that an external reviewer can replay without a score claim."""

import json
from pathlib import Path

from natalia.cli import classify_port
from natalia.engine import verify
from natalia.lean_cert import match_fragment
from natalia.models import Submission
from natalia.sources import SOURCES, list_sources

ROOT = Path(__file__).resolve().parents[1]


def test_root_smoke_example_is_a_submission_not_a_wrapper():
    payload = json.loads((ROOT / "examples" / "01-energy.json").read_text(encoding="utf-8"))
    assert "submission" not in payload
    result = verify(payload)
    assert result["verdict"] == "ACCEPTED"


def test_runtime_versions_policy_is_shared():
    policy = json.loads((ROOT / "runtime_versions.json").read_text(encoding="utf-8"))
    assert policy["python"]["requires"] == ">=3.12"
    assert "3.12" in policy["python"]["supported"]


def test_lean_mode_does_not_reuse_smt_acceptance():
    payload = json.loads((ROOT / "natalia" / "examples" / "01-energy.json").read_text(encoding="utf-8"))
    submission = payload["submission"]
    submission["verification_mode"] = "lean"
    result = verify(submission)
    assert result["verdict"] == "ABSTAIN"
    assert result["guarantee_level"] == "UNAVAILABLE"
    assert result["verification_mode"] == "lean"


def test_integer_square_maps_to_lean_fragment():
    model = Submission.model_validate(
        {
            "title": "int square",
            "variables": {"n": {"dimension": ["0"] * 7}},
            "claims": [{"id": "int-square", "kind": "relation", "lhs": "n*n", "op": ">=", "rhs": "0"}],
        }
    )
    matched = match_fragment(model)
    assert matched is not None
    assert matched["template"] == "int_sq_nonneg"
    fast = verify(model.model_dump())
    assert fast["verdict"] == "ACCEPTED"
    lean = verify({**model.model_dump(), "verification_mode": "lean"})
    if lean["guarantee_level"] == "KERNEL_CHECKED":
        assert lean["verdict"] == "ACCEPTED"
        assert any(item.get("adapter_id") == "lean" for item in lean["obligations"])
    else:
        assert lean["verdict"] == "ABSTAIN"
        assert lean["guarantee_level"] == "UNAVAILABLE"


def test_source_registry_has_no_fabricated_doi_fields():
    listed = list_sources()
    assert listed["count"] == len(SOURCES)
    for item in SOURCES:
        assert item["id"].startswith("src-")
        assert item["accessed"]
        assert "doi" not in item or item["doi"]


def test_classify_port_distinguishes_invalid_host():
    assert classify_port("127.0.0.1", 0) == "free"
    assert classify_port("this.host.is.not.valid.example", 8000) == "invalid_host"


def test_dockerfile_is_multistage():
    text = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "AS frontend" in text
    assert "COPY --from=frontend" in text
    assert "npm run build" in text


def test_formal_project_has_no_sorry():
    for path in (ROOT / "formal").rglob("*.lean"):
        text = path.read_text(encoding="utf-8")
        assert "sorry" not in text
        assert "admit" not in text
