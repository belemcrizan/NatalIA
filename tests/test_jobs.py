import json
import sqlite3
import threading
import time
from pathlib import Path

from fastapi.testclient import TestClient
from test_engine import submission
from test_worker import hangs

from natalia.api import create_app
from natalia.engine import verify
from natalia.storage import RunStore
from natalia.worker import execute


def test_v1_database_remains_readable(tmp_path):
    path = tmp_path / "legacy.db"
    db = sqlite3.connect(path)
    db.execute("CREATE TABLE schema_version (version INTEGER PRIMARY KEY)")
    db.execute("INSERT INTO schema_version VALUES (1)")
    db.execute(
        """CREATE TABLE runs (
        id TEXT PRIMARY KEY, created_at TEXT NOT NULL, title TEXT NOT NULL,
        verdict TEXT NOT NULL, duration_ms REAL NOT NULL, document TEXT NOT NULL)"""
    )
    document = {
        "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "created_at": "2026-01-01T00:00:00+00:00",
        "verdict": "ACCEPTED",
        "duration_ms": 1,
        "input_sha256": "abc",
        "trace_id": "trace",
        "request_id": "req",
        "submission": submission(),
        "obligations": [],
        "spans": [],
    }
    document["submission"]["title"] = "legado"
    db.execute(
        "INSERT INTO runs VALUES (?, ?, ?, ?, ?, ?)",
        (
            document["id"],
            document["created_at"],
            "legado",
            "ACCEPTED",
            1,
            json.dumps(document, ensure_ascii=False),
        ),
    )
    db.commit()
    db.close()
    store = RunStore(path)
    loaded = store.get(document["id"])
    assert loaded["submission"]["title"] == "legado"
    assert store.list(10, 0)["total"] == 1
    assert store.ready()


def test_backup_and_restore(tmp_path):
    import subprocess
    import sys

    db = tmp_path / "live.db"
    store = RunStore(db)
    run = verify(submission())
    run.update(
        id="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        created_at="2026-01-01T00:00:00+00:00",
        submission=submission(),
        request_id="r",
        trace_id="t",
    )
    store.save(run)
    backup_path = tmp_path / "copy.db"
    restore_path = tmp_path / "restored.db"
    root = Path(__file__).resolve().parents[1]
    subprocess.check_call(
        [sys.executable, str(root / "scripts" / "backup.py"), str(backup_path), "--source", str(db)]
    )
    subprocess.check_call(
        [sys.executable, str(root / "scripts" / "restore.py"), str(backup_path), str(restore_path)]
    )
    assert RunStore(restore_path).get(run["id"])["verdict"] == "ACCEPTED"


def test_idempotency_conflict_and_replay(tmp_path):
    with TestClient(create_app(tmp_path / "idemp.db", runner=verify)) as c:
        headers = {"Idempotency-Key": "same-key"}
        first = c.post("/api/runs", json=submission(), headers=headers)
        assert first.status_code == 201
        second = c.post("/api/runs", json=submission(), headers=headers)
        assert second.status_code == 200
        assert second.json()["id"] == first.json()["id"]
        other = submission()
        other["title"] = "different"
        conflict = c.post("/api/runs", json=other, headers=headers)
        assert conflict.status_code == 409


def test_windows_path_with_spaces_and_accents(tmp_path):
    folder = tmp_path / "área de investigação"
    folder.mkdir()
    with TestClient(create_app(folder / "dados.db", runner=verify)) as c:
        run = c.post("/api/runs", json=submission())
        assert run.status_code == 201
        assert c.get(f"/api/runs/{run.json()['id']}").status_code == 200


def test_restart_marks_running_jobs_failed(tmp_path):
    db = tmp_path / "restart.db"
    store = RunStore(db)
    payload = json.dumps(submission(), ensure_ascii=False)
    store.create_job(
        {
            "id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
            "created_at": "2026-01-01T00:00:00+00:00",
            "updated_at": "2026-01-01T00:00:00+00:00",
            "title": "interrompida",
            "job_status": "running",
            "payload": payload,
            "content_hash": "x",
            "trace_id": "t",
            "request_id": "r",
        }
    )
    with TestClient(create_app(db, runner=verify)) as c:
        job = c.get("/api/jobs/cccccccc-cccc-cccc-cccc-cccccccccccc").json()
        assert job["job_status"] == "failed"
        assert job["operational_reason"] == "interrupted_by_restart"
        assert job["verdict"] is None


def test_cancel_stops_worker():
    flag = {"c": False}

    def cancel_check():
        return flag["c"]

    payload = submission()
    payload["budget_ms"] = 5000
    box = {}

    def run():
        box["result"] = execute(payload, target=hangs, cancel_check=cancel_check)

    thread = threading.Thread(target=run)
    thread.start()
    time.sleep(0.4)
    flag["c"] = True
    thread.join(timeout=5)
    assert not thread.is_alive()
    assert box["result"]["operational_kind"] == "cancelled"


def test_replay_rejects_tampered_hash(tmp_path):
    with TestClient(create_app(tmp_path / "replay.db", runner=verify)) as c:
        run = c.post("/api/runs", json=submission()).json()
        payload = {
            "replay_schema": "natalia-replay-1.0",
            "input_sha256": "0" * 64,
            "submission": run["submission"],
            "obligations": run["obligations"],
            "verdict": run["verdict"],
        }
        result = c.post("/api/replay", json=payload).json()
        assert result["accepted"] is False
        payload["input_sha256"] = run["input_sha256"]
        ok = c.post("/api/replay", json=payload).json()
        assert ok["accepted"] is True
        assert "not a new proof" in ok["guarantee"]


def test_compile_error_records_span():
    payload = submission("x+1")
    payload["variables"]["x"]["dimension"][0] = "1"
    result = verify(payload)
    assert result["verdict"] == "INVALID"
    assert any(span["name"] == "compile" for span in result["spans"])


def test_evidence_contract_fields():
    result = verify(submission())
    item = result["obligations"][-1]
    assert item["adapter_id"] == "z3"
    assert item["obligation_hash"]
    assert item["trust"] == "smt_relative"
    assert item["fragment"] == "qf_nra_real_arithmetic"
