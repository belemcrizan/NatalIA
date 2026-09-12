"""One disposable process per run; hard wall-clock deadline includes startup."""

import multiprocessing as mp
from time import monotonic

from natalia.engine import base_result, verify


def _child(send, payload):
    try:
        send.send(verify(payload))
    except Exception:
        # Solver/internal exceptions must never become acceptance or leak submitted source.
        send.send({"worker_error": True})
    finally:
        send.close()


def execute(payload, *, target=None):
    start = monotonic()
    ctx = mp.get_context("spawn")
    receive, send = ctx.Pipe(duplex=False)
    process = ctx.Process(target=target or _child, args=(send, payload), daemon=True)
    result = None
    try:
        process.start()
        send.close()
        if receive.poll(payload["budget_ms"] / 1000):
            try:
                result = receive.recv()
            except EOFError:
                pass
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
    if result is None or "worker_error" in result:
        reason = "worker_failure" if result else "budget_exhausted_or_worker_exit"
        result = base_result(payload)
        result.update(
            reason=reason,
            proof_holes=[c["id"] for c in payload["claims"]],
            obligations=[
                {"id": c["id"], "oracle": "worker", "status": "unknown", "reason": reason}
                for c in payload["claims"]
            ],
        )
    result["duration_ms"] = round((monotonic() - start) * 1000, 3)
    return result
