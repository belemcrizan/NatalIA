"""Reproduce entrada → validação → job → execução → resultado → evidência.

Uses an in-process TestClient. Does not start a long-lived server.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

from natalia.api import create_app
from natalia.engine import verify


def main():
    energy = json.loads(Path("natalia/examples/01-energy.json").read_text(encoding="utf-8"))
    counter = json.loads(Path("natalia/examples/02-counterexample.json").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        root = Path(tmp)
        with TestClient(create_app(root / "natalia.db", runner=verify, artifact_dir=root / "art")) as client:
            health = client.get("/health/ready")
            print("health", health.status_code, health.json())
            compiled = client.post("/api/compile", json=energy["submission"])
            print("compile", compiled.status_code, compiled.json().get("ok"))
            run = client.post("/api/runs", json=energy["submission"])
            body = run.json()
            print(
                "run",
                run.status_code,
                "verdict",
                body.get("verdict"),
                "job",
                body.get("job_status"),
                "guarantee",
                body.get("guarantee_level"),
            )
            job = client.post("/api/jobs", json=counter["submission"])
            print("job", job.status_code, job.json().get("id"), job.json().get("job_status"))
            job_id = job.json()["id"]
            events = client.get(f"/api/jobs/{job_id}/events")
            print("sse", events.status_code, "bytes", len(events.text))
            fetched = client.get(f"/api/runs/{body['id']}")
            print("fetch", fetched.status_code, fetched.json().get("input_sha256"))
            replay_payload = {
                "replay_schema": "natalia-replay-1.0",
                "input_sha256": body["input_sha256"],
                "submission": body["submission"],
                "obligations": body["obligations"],
                "verdict": body["verdict"],
            }
            replayed = client.post("/api/replay", json=replay_payload)
            print("replay", replayed.status_code, replayed.json().get("accepted"))
            square = {
                "title": "square",
                "verification_mode": "certified",
                "variables": {"x": {"dimension": ["0"] * 7}},
                "assumptions": [],
                "claims": [{"id": "claim", "kind": "relation", "lhs": "x**2", "op": ">=", "rhs": "0"}],
                "budget_ms": 5000,
            }
            cert_run = client.post("/api/runs", json=square).json()
            kernel = next(o for o in cert_run["obligations"] if o.get("artifacts", {}).get("certificate"))
            recheck = client.post(
                "/api/certificates/recheck",
                json={
                    "submission": cert_run["submission"],
                    "certificate": kernel["artifacts"]["certificate"],
                },
            ).json()
            print(
                "certified",
                cert_run.get("verdict"),
                cert_run.get("guarantee_level"),
                "recheck",
                recheck.get("accepted"),
                "lean_class",
                kernel["artifacts"]["lean_check"].get("classification"),
            )


if __name__ == "__main__":
    main()
