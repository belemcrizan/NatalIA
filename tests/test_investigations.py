from fastapi.testclient import TestClient

from natalia.api import create_app
from natalia.engine import verify
from natalia.investigations import INVESTIGATIONS, list_investigations


def test_investigations_are_honest_and_match_engine():
    catalog = list_investigations()
    assert catalog["count"] >= 12
    assert catalog["schema"] == "natalia-investigations-1.1"
    ids = [item["id"] for item in INVESTIGATIONS]
    assert len(set(ids)) == len(ids)
    capabilities = {item["capability"] for item in INVESTIGATIONS}
    assert "runnable" in capabilities
    assert "negative_boundary" in capabilities
    assert "educational_unverified" in capabilities
    for item in INVESTIGATIONS:
        assert item["educational_model"] is True
        assert item["real_world_validated"] is False
        assert item["question"]
        assert item["equations"]
        assert item["obligation_english"]
        assert item["source_ids"]
        assert item["expected_by_mode"]
        result = verify(item["submission"])
        assert result["verdict"] == item["expected_verdict"], item["id"]
    damped = next(item for item in INVESTIGATIONS if item["id"] == "inv-10-damped")
    assert damped["expected_verdict"] == "ABSTAIN"
    assert damped["difficulty"] == "Research Boundary"


def test_investigations_endpoint(tmp_path):
    with TestClient(create_app(tmp_path / "inv.db", runner=verify)) as client:
        data = client.get("/api/investigations").json()
        assert data["count"] >= 12
        item = client.get("/api/investigations/inv-01-kinetic").json()
        assert item["domain"] == "Classical Mechanics"
        assert client.get("/api/investigations/missing").status_code == 404
