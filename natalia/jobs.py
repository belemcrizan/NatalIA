"""Durable job lifecycle. Succeeded means the execution finished, not that a claim was accepted."""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from time import monotonic, time_ns

from natalia.telemetry import event

KIND_TO_JOB = {
    "timed_out": "timed_out",
    "cancelled": "cancelled",
    "worker_crash": "failed",
    "worker_exception": "failed",
    "transport_timeout": "failed",
    "transport_error": "failed",
    "transport_empty": "failed",
    "evidence_too_large": "failed",
}


def utcnow():
    return datetime.now(timezone.utc).isoformat()


class JobManager:
    def __init__(self, store, runner, metrics, max_workers):
        self.store = store
        self.runner = runner
        self.metrics = metrics
        self.max_workers = max_workers
        self.active = 0
        self._cancels = {}
        self._lock = asyncio.Lock()

    def recover(self):
        interrupted = self.store.recover_interrupted(utcnow())
        for job_id in interrupted:
            self.metrics.jobs.labels("failed").inc()
            event("job_recovered_interrupted", run_id=job_id)
        return interrupted

    def _content_hash(self, payload):
        from natalia.engine import base_result

        return base_result(payload)["input_sha256"]

    def create(self, payload, request_id, idempotency_key=None):
        job_id, trace_id = str(uuid.uuid4()), uuid.uuid4().hex
        stamp = utcnow()
        record = {
            "id": job_id,
            "created_at": stamp,
            "updated_at": stamp,
            "title": payload["title"],
            "job_status": "queued",
            "payload": json.dumps(payload, ensure_ascii=False),
            "content_hash": self._content_hash(payload),
            "idempotency_key": idempotency_key,
            "request_id": request_id,
            "trace_id": trace_id,
        }
        stored, replayed = self.store.create_job(record)
        if replayed:
            existing = self.store.get_job(stored["id"])
            return existing, True
        return self.store.get_job(job_id), False

    async def acquire(self):
        async with self._lock:
            if self.active >= self.max_workers:
                return False
            self.active += 1
            self.metrics.active.inc()
            return True

    def release(self):
        self.active -= 1
        self.metrics.active.dec()

    def request_cancel(self, job_id):
        event("job_cancel_requested", run_id=job_id)
        self._cancels[job_id] = True
        return self.store.request_cancel(job_id, utcnow())

    def _cancel_check(self, job_id):
        return self._cancels.get(job_id) or self.store.cancel_requested(job_id)

    def _attach_metadata(self, job, result, tick, wall):
        result.update(
            id=job["id"],
            trace_id=job["trace_id"],
            request_id=job["request_id"],
            created_at=job["created_at"],
            submission=job["payload"] if isinstance(job["payload"], dict) else json.loads(job["payload"]),
            job_status=None,
        )
        root_span = uuid.uuid4().hex[:16]
        for span in result.get("spans", []):
            span.update(trace_id=job["trace_id"], parent_span_id=root_span)
        result.setdefault("spans", [])
        result["spans"].insert(
            0,
            {
                "span_id": root_span,
                "parent_span_id": None,
                "trace_id": job["trace_id"],
                "name": "verification",
                "oracle": "orchestrator",
                "start_time_unix_ns": wall,
                "duration_ms": round((monotonic() - tick) * 1000, 3),
                "status": result.get("operational_kind") or result.get("verdict"),
            },
        )
        return result

    def _finalize_status(self, result):
        kind = result.get("operational_kind")
        if kind in KIND_TO_JOB:
            return KIND_TO_JOB[kind]
        return "succeeded"

    async def execute_job(self, job):
        if not self.store.transition(
            job["id"],
            "queued",
            "running",
            updated_at=utcnow(),
            lease_token=uuid.uuid4().hex,
        ):
            current = self.store.get_job(job["id"])
            return current.get("document") if current else None
        wall, tick = time_ns(), monotonic()
        payload = job["payload"] if isinstance(job["payload"], dict) else json.loads(job["payload"])
        try:
            result = await asyncio.to_thread(
                self.runner, payload, **self._runner_kwargs(job["id"])
            )
        except TypeError:
            result = await asyncio.to_thread(self.runner, payload)
        except Exception:
            result = {
                "verdict": "ABSTAIN",
                "reason": "worker_failure",
                "operational_kind": "worker_exception",
                "obligations": [],
                "spans": [],
                "duration_ms": round((monotonic() - tick) * 1000, 3),
            }
            from natalia.engine import base_result

            result = {**base_result(payload), **result}
        result = self._attach_metadata(job, result, tick, wall)
        status = self._finalize_status(result)
        if self._cancel_check(job["id"]) and status != "cancelled":
            result["operational_kind"] = "cancelled"
            result["reason"] = "cancelled"
            result["verdict"] = "ABSTAIN"
            status = "cancelled"
        result["job_status"] = status
        document = json.dumps(result, ensure_ascii=False)
        persisted = self.store.transition(
            job["id"],
            "running",
            status,
            updated_at=utcnow(),
            verdict=None if status != "succeeded" else result.get("verdict"),
            duration_ms=result["duration_ms"],
            document=document,
            lease_token=None,
            operational_reason=None if status == "succeeded" else result.get("reason"),
        )
        if not persisted:
            current = self.store.get_job(job["id"])
            event("job_stale_lease", run_id=job["id"], job_status=current and current["job_status"])
            return current.get("document") if current else result
        if status == "succeeded":
            self.metrics.runs.labels(result["verdict"]).inc()
            self.metrics.duration.observe(result["duration_ms"] / 1000)
            for obligation in result.get("obligations", []):
                self.metrics.oracles.labels(obligation.get("oracle", "unknown"), obligation["status"]).inc()
        self.metrics.jobs.labels(status).inc()
        event(
            "verification_completed" if status == "succeeded" else "verification_operational",
            run_id=job["id"],
            trace_id=job["trace_id"],
            request_id=job["request_id"],
            verdict=result.get("verdict"),
            job_status=status,
            duration_ms=result["duration_ms"],
        )
        return result

    def _runner_kwargs(self, job_id):
        import inspect

        try:
            parameters = inspect.signature(self.runner).parameters
        except (TypeError, ValueError):
            return {}
        kwargs = {}
        if "cancel_check" in parameters:
            kwargs["cancel_check"] = lambda: self._cancel_check(job_id)
        return kwargs

    async def run_reserved(self, job):
        try:
            return await self.execute_job(job)
        finally:
            self.release()
            self._cancels.pop(job["id"], None)

    async def submit_wait(self, payload, request_id, idempotency_key=None):
        job, replayed = self.create(payload, request_id, idempotency_key)
        if replayed and job.get("document"):
            return job["document"], 200
        if replayed and job["job_status"] in {"queued", "running"}:
            raise RuntimeError("idempotent_in_flight")
        if not await self.acquire():
            self.store.transition(
                job["id"],
                "queued",
                "rejected",
                updated_at=utcnow(),
                operational_reason="capacity_exhausted",
            )
            self.metrics.jobs.labels("rejected").inc()
            return None, 429
        result = await self.run_reserved(job)
        return result, 201
