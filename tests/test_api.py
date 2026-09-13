import threading
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient
from test_engine import submission

from natalia.api import create_app
from natalia.engine import verify
from natalia.storage import RunStore


@pytest.fixture
def app(tmp_path):
    return create_app(tmp_path / "test.db", runner=verify)


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        yield c


def test_complete_flow_and_persistence(client, app):
    response = client.post("/api/runs", json=submission())
    assert response.status_code == 201
    run = response.json()
    assert run["verdict"] == "ACCEPTED"
    assert run["request_id"] == response.headers["x-request-id"]
    assert run["spans"][0]["trace_id"] == run["trace_id"]
    assert all(s["parent_span_id"] == run["spans"][0]["span_id"] for s in run["spans"][1:])
    assert client.get(f"/api/runs/{run['id']}").json() == run
    assert RunStore(app.state.store.path).get(run["id"]) == run
    assert client.get("/api/runs").json()["total"] == 1
    stats = client.get("/api/stats").json()
    assert stats["verdicts"] == {"ACCEPTED": 1}
    assert stats["false_accept_rate"] is None
    metrics = client.get("/metrics").text
    assert 'natalia_runs_total{verdict="ACCEPTED"} 1.0' in metrics
    assert 'natalia_obligations_total{oracle="z3",status="certified"} 1.0' in metrics
    assert run["id"] not in metrics  # No high-cardinality labels.


def test_health_assets_and_examples(client):
    assert client.get("/health/ready").json()["status"] == "ready"
    assert client.get("/health/live").status_code == 200
    home = client.get("/")
    assert 'id="root"' in home.text
    assert "/assets/" in home.text
    assert "script-src 'self'" in home.headers["content-security-policy"]
    assert "font-src 'self'" in home.headers["content-security-policy"]
    library = client.get("/library")
    assert library.status_code == 200
    assert "text/html" in library.headers["content-type"]
    missing_api = client.get("/api/does-not-exist")
    assert missing_api.status_code == 404
    assert "application/json" in missing_api.headers["content-type"]
    assert client.get("/missing.js").status_code == 404
    assert len(client.get("/api/examples").json()) == 9
    assert client.get("/api/capabilities").json()["calibration"] is None
    assert client.get("/api/capabilities").json()["frontend"] == "react-vite"
    assert client.get("/openapi.json").status_code == 200


def test_errors_and_pagination(client):
    assert client.post("/api/runs", json={}).status_code == 422
    assert (
        client.post(
            "/api/runs", content="{", headers={"Content-Type": "application/json"}
        ).status_code
        == 422
    )
    assert client.get("/api/runs?limit=101").status_code == 422
    assert client.get("/api/runs?offset=-1").status_code == 422
    assert client.get("/api/runs/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa").status_code == 404
    assert client.get("/api/runs/not-a-uuid").status_code == 422


def test_oversized_streamed_request(client):
    assert client.post("/api/runs", content=iter([b"x" * 40000, b"y" * 40000])).status_code == 413


def test_local_origin_and_host_protection(client):
    assert (
        client.post(
            "/api/runs", json=submission(), headers={"Origin": "https://evil.example"}
        ).status_code
        == 403
    )
    assert client.get("/", headers={"Host": "evil.example"}).status_code == 400
    assert (
        client.post(
            "/api/runs", json=submission(), headers={"Origin": "http://testserver"}
        ).status_code
        == 201
    )


def test_internal_failure_is_generic_and_slot_released(tmp_path):
    def bad_runner(payload):
        raise RuntimeError("sensitive details")

    with TestClient(create_app(tmp_path / "bad.db", runner=bad_runner)) as c:
        response = c.post("/api/runs", json=submission())
        assert response.status_code == 201
        body = response.json()
        assert body["job_status"] == "failed"
        assert body["verdict"] == "ABSTAIN"
        assert "sensitive" not in response.text
        assert body["reason"] == "worker_failure"
        assert c.get("/api/stats").json()["active_runs"] == 0


def test_saturation_rejects_while_health_stays_responsive(tmp_path, monkeypatch):
    monkeypatch.setenv("NATALIA_MAX_WORKERS", "1")
    started, release = threading.Event(), threading.Event()

    def slow_runner(payload):
        started.set()
        assert release.wait(5)
        return verify(payload)

    with TestClient(create_app(tmp_path / "concurrent.db", runner=slow_runner)) as c:
        with ThreadPoolExecutor() as pool:
            first = pool.submit(c.post, "/api/runs", json=submission())
            assert started.wait(3)
            try:
                assert c.get("/health/live").status_code == 200
                rejected = c.post("/api/runs", json=submission())
                assert rejected.status_code == 429
                assert rejected.headers["retry-after"] == "2"
            finally:
                release.set()
            assert first.result(timeout=5).status_code == 201
        assert c.get("/api/stats").json()["active_runs"] == 0


def test_log_correlation_without_source(client, caplog):
    p = submission()
    p["source_latex"] = "private research content"
    with caplog.at_level("INFO", logger="natalia"):
        run = client.post("/api/runs", json=p).json()
    assert run["trace_id"] in caplog.text
    assert "private research content" not in caplog.text


def test_readiness_reports_storage_failure(client, app, monkeypatch):
    monkeypatch.setattr(app.state.store, "ready", lambda: False)
    assert client.get("/health/ready").status_code == 503
