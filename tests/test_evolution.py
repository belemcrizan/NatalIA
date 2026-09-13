import json

from fastapi.testclient import TestClient
from test_engine import submission

from natalia.api import create_app
from natalia.bench import build_instances
from natalia.compile import preview
from natalia.engine import verify
from natalia.importers import inspect_records
from natalia.interval import Interval
from natalia.library import CASES, THEMES
from natalia.storage import SCHEMA_VERSION, RunStore


def test_library_has_thirty_distinct_cases_and_matches_engine():
    assert len(CASES) >= 30
    assert len({item["id"] for item in CASES}) == len(CASES)
    assert set(THEMES) <= {item["theme"] for item in CASES}
    checked = 0
    for item in CASES:
        result = verify(item["submission"])
        assert result["verdict"] == item["expected_verdict"], item["id"]
        checked += 1
    assert checked >= 30


def test_dimension_error_is_actionable():
    payload = submission("x+1")
    payload["variables"]["x"]["dimension"][0] = "1"
    result = verify(payload)
    assert result["verdict"] == "INVALID"
    assert "mistura" in result["obligations"][0]["reason"]


def test_interval_refutes_on_declared_box():
    payload = submission("x", ">=", "2")
    payload["variables"]["x"]["domain_min"] = "-1"
    payload["variables"]["x"]["domain_max"] = "1"
    result = verify(payload)
    assert result["verdict"] == "REFUTED"
    assert any(item["adapter_id"] == "interval" for item in result["obligations"])
    assert result.get("conflicts") == []


def test_interval_enclosure_is_exact():
    value = Interval(1, 2) * Interval(-1, 3)
    assert value.lo == -2 and value.hi == 6


def test_catalog_and_system_endpoints(tmp_path):
    with TestClient(create_app(tmp_path / "cat.db", runner=verify)) as client:
        catalog = client.get("/api/catalog").json()
        assert catalog["count"] >= 30
        assert client.get("/health/ready").json()["schema_version"] == SCHEMA_VERSION
        system = client.get("/api/system").json()
        assert system["executor"]["semantics"] == "at-least-once"
        assert system["adapters"]["translation"]["available"] is False
        lean = system["adapters"]["lean"]
        assert "available" in lean
        if not lean["available"]:
            assert lean["available"] is False
        compiled = client.post("/api/compile", json=submission()).json()
        assert compiled["ok"] is True


def test_import_preview_does_not_execute(tmp_path):
    inspection = inspect_records({"records": [{"submission": submission()}], "dry_run": True})
    assert inspection["accepted"]
    with TestClient(create_app(tmp_path / "imp.db", runner=verify)) as client:
        previewed = client.post(
            "/api/import", json={"records": [{"submission": submission()}], "dry_run": True}
        ).json()
        assert previewed["applied"] is False
        assert client.get("/api/runs").json()["total"] == 0


def test_queued_jobs_survive_restart(tmp_path):
    db = tmp_path / "queue.db"
    store = RunStore(db)
    store.create_job(
        {
            "id": "dddddddd-dddd-dddd-dddd-dddddddddddd",
            "created_at": "2026-01-01T00:00:00+00:00",
            "updated_at": "2026-01-01T00:00:00+00:00",
            "title": "na fila",
            "job_status": "queued",
            "payload": json.dumps(submission(), ensure_ascii=False),
            "content_hash": "x",
            "trace_id": "t",
            "request_id": "r",
            "origin": "queue",
        }
    )
    with TestClient(create_app(db, runner=verify)) as client:
        job = client.get("/api/jobs/dddddddd-dddd-dddd-dddd-dddddddddddd").json()
        assert job["job_status"] in {"queued", "running", "succeeded"}


def test_async_job_is_claimed(tmp_path):
    with TestClient(create_app(tmp_path / "async.db", runner=verify)) as client:
        job = client.post("/api/jobs", json=submission())
        assert job.status_code == 202
        job_id = job.json()["id"]
        for _ in range(50):
            body = client.get(f"/api/jobs/{job_id}").json()
            if body.get("document"):
                assert body["document"]["verdict"] == "ACCEPTED"
                break
        else:
            raise AssertionError(body)


def test_bench_instances_are_diverse_and_split_by_family():
    instances = build_instances()
    assert len(instances) >= 150
    families = {item["family"] for item in instances}
    assert len(families) >= 12
    splits = {item["split"] for item in instances}
    assert splits == {"dev", "val", "test"}
    hashes = {item["canonical_sha256"] for item in instances}
    assert len(hashes) == len(instances)


def test_compile_preview_keeps_payload_on_error():
    payload = submission("m+v")
    payload["variables"] = {
        "m": {"dimension": ["1", "0", "0", "0", "0", "0", "0"]},
        "v": {"dimension": ["0", "1", "-1", "0", "0", "0", "0"]},
    }
    result = preview(payload)
    assert result["ok"] is False
    assert "mistura" in result["errors"][0]["message"]
