"""One disposable process per run; wall-clock deadline includes startup and result transport."""

import multiprocessing as mp
import threading
from time import monotonic

from natalia.engine import base_result, verify

MAX_RESULT_BYTES = 256_000
REASONS = {
    "timed_out": "budget_exhausted_or_worker_exit",
    "cancelled": "cancelled",
    "worker_crash": "worker_failure",
    "worker_exception": "worker_failure",
    "transport_timeout": "result_transport_timeout",
    "transport_error": "result_transport_failure",
    "transport_empty": "result_transport_failure",
    "evidence_too_large": "evidence_exceeds_size_limit",
}


def _child(send, payload):
    try:
        send.send(verify(payload))
    except Exception:
        send.send({"worker_error": True})
    finally:
        send.close()


def _recv_bounded(connection, timeout):
    box = []

    def work():
        try:
            box.append(("ok", connection.recv()))
        except EOFError:
            box.append(("eof", None))
        except Exception:
            box.append(("error", None))

    thread = threading.Thread(target=work, daemon=True)
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        return None, "transport_timeout"
    if not box:
        return None, "transport_empty"
    kind, value = box[0]
    if kind == "ok":
        return value, None
    if kind == "eof":
        return None, "worker_crash"
    return None, "transport_error"


def _operational_result(payload, kind):
    reason = REASONS.get(kind, "worker_failure")
    result = base_result(payload)
    result.update(
        reason=reason,
        operational_kind=kind,
        proof_holes=[c["id"] for c in payload["claims"]],
        obligations=[
            {
                "id": c["id"],
                "oracle": "worker",
                "adapter_id": "worker",
                "adapter_version": "1.0",
                "fragment": "process_isolation",
                "status": "unknown",
                "reason": reason,
                "trust": "operational",
                "validation": "not_applicable",
            }
            for c in payload["claims"]
        ],
    )
    return result


def execute(payload, *, target=None, cancel_check=None):
    start = monotonic()
    deadline = start + payload["budget_ms"] / 1000
    ctx = mp.get_context("spawn")
    receive, send = ctx.Pipe(duplex=False)
    process = ctx.Process(target=target or _child, args=(send, payload), daemon=True)
    result, fail_kind = None, None
    try:
        process.start()
        send.close()
        while True:
            if cancel_check and cancel_check():
                fail_kind = "cancelled"
                break
            remaining = deadline - monotonic()
            if remaining <= 0:
                fail_kind = "timed_out"
                break
            if receive.poll(min(0.05, remaining)):
                result, fail_kind = _recv_bounded(receive, max(0.05, deadline - monotonic()))
                break
    finally:
        if process.pid is not None:
            if process.is_alive():
                process.terminate()
            process.join(timeout=1)
            if process.is_alive():
                process.kill()
                process.join(timeout=1)
        receive.close()
        send.close()
    if result is not None and "worker_error" in result:
        fail_kind = "worker_exception"
        result = None
    if result is not None:
        try:
            if len(repr(result).encode("utf-8")) > MAX_RESULT_BYTES:
                result, fail_kind = None, "evidence_too_large"
        except Exception:
            result, fail_kind = None, "transport_error"
    if result is None:
        result = _operational_result(payload, fail_kind or "worker_crash")
    result["duration_ms"] = round((monotonic() - start) * 1000, 3)
    return result
