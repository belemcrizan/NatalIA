from fastapi.testclient import TestClient

from natalia.api import create_app
from natalia.engine import verify
from natalia.investigations import INVESTIGATIONS, list_investigations


def test_investigations_are_honest_and_match_engine():
    catalog = list_investigations()
    assert catalog["count"] == 11
    assert catalog["schema"] == "natalia-investigations-1.0"
    ids = [item["id"] for item in INVESTIGATIONS]
    assert len(set(ids)) == 11
    for item in INVESTIGATIONS:
        assert item["educational_model"] is True
        assert item["real_world_validated"] is False
        assert item["question"]
        assert item["equations"]
        assert item["obligation_english"]
        result = verify(item["submission"])
        assert result["verdict"] == item["expected_verdict"], item["id"]
    damped = next(item for item in INVESTIGATIONS if item["id"] == "inv-10-damped")
    assert damped["expected_verdict"] == "ABSTAIN"
    assert damped["difficulty"] == "Research Boundary"


def test_investigations_endpoint(tmp_path):
    with TestClient(create_app(tmp_path / "inv.db", runner=verify)) as client:
        data = client.get("/api/investigations").json()
        assert data["count"] == 11
        item = client.get("/api/investigations/inv-01-kinetic").json()
        assert item["domain"] == "Classical Mechanics"
        assert client.get("/api/investigations/missing").status_code == 404
