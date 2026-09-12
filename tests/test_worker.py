import multiprocessing
import time

from test_engine import submission

from natalia.worker import execute


def hangs(send, payload):
    time.sleep(20)


def crashes(send, payload):
    send.send({"worker_error": True})
    send.close()


def test_real_isolated_solver():
    result = execute(submission())
    assert result["verdict"] == "ACCEPTED"
    assert result["duration_ms"] > 0


def test_hard_deadline_kills_worker():
    p = submission()
    p["budget_ms"] = 250
    tick = time.monotonic()
    result = execute(p, target=hangs)
    assert time.monotonic() - tick < 3
    assert result["verdict"] == "ABSTAIN"
    assert result["proof_holes"] == ["claim"]
    assert not multiprocessing.active_children()


def test_worker_failure_never_accepts():
    assert execute(submission(), target=crashes)["verdict"] == "ABSTAIN"
