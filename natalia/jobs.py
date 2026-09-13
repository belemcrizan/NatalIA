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
    def __init__(self, store, runner, metrics, max_workers, max_queue=32, artifacts=None, max_queue_per_tenant=None):
        self.store = store
        self.runner = runner
        self.metrics = metrics
        self.max_workers = max_workers
        self.max_queue = max_queue
        self.max_queue_per_tenant = max_queue_per_tenant or max_queue
        self.artifacts = artifacts
        self.active = 0
        self._cancels = {}
        self._lock = asyncio.Lock()
        self._stop = asyncio.Event()
        self._wake = asyncio.Event()
        self._dispatcher = None

    def recover(self):
        interrupted = self.store.recover_interrupted(utcnow())
        for job_id in interrupted:
            self.metrics.jobs.labels("failed").inc()
            event("job_recovered_interrupted", run_id=job_id)
        return interrupted

    async def start_dispatcher(self):
        self._dispatcher = asyncio.create_task(self._dispatch_loop())

    async def stop_dispatcher(self):
        self._stop.set()
        self._wake.set()
        if self._dispatcher is not None:
            self._dispatcher.cancel()
            try:
                await self._dispatcher
            except asyncio.CancelledError:
                pass

    async def _dispatch_loop(self):
        while not self._stop.is_set():
            if self.store.count_dispatchable() == 0:
                self._wake.clear()
                try:
                    await asyncio.wait_for(self._wake.wait(), 0.2)
                except TimeoutError:
                    continue
                continue
            if not await self.acquire():
                try:
                    await asyncio.wait_for(self._stop.wait(), 0.05)
                except TimeoutError:
                    continue
                break
            token = uuid.uuid4().hex
            job = self.store.claim_queued(utcnow(), token, utcnow())
            if job is None:
                self.release()
                continue
            asyncio.create_task(self.run_reserved(job))

    def enqueue(self, payload, request_id, idempotency_key=None, tenant_id="local"):
        if self.store.count_status("queued") >= self.max_queue:
            return None, False, "queue_full"
        tenant_queue = int(getattr(self, "max_queue_per_tenant", self.max_queue))
        if self.store.count_inflight_for_tenant(tenant_id) >= tenant_queue:
            return None, False, "tenant_quota"
        job, replayed = self.create(payload, request_id, idempotency_key, tenant_id=tenant_id)
        self._wake.set()
        return job, replayed, None

    def _content_hash(self, payload):
        from natalia.engine import base_result

        return base_result(payload)["input_sha256"]

    def create(self, payload, request_id, idempotency_key=None, origin="queue", tenant_id="local"):
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
            "origin": origin,
            "tenant_id": tenant_id,
            "verification_mode": payload.get("verification_mode") or "fast",
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
            tenant_id=job.get("tenant_id") or "local",
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
        lease = job.get("lease_token")
        if job["job_status"] == "queued":
            lease = uuid.uuid4().hex
            if not self.store.transition(
                job["id"],
                "queued",
                "running",
                updated_at=utcnow(),
                lease_token=lease,
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
            require_lease=lease,
            operational_reason=None if status == "succeeded" else result.get("reason"),
            guarantee_level=result.get("guarantee_level"),
            conclusion=result.get("conclusion") or result.get("verdict"),
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
            tenant = job.get("tenant_id") or "local"
            self.store.add_usage(tenant, "jobs", 1, utcnow())
            self.store.add_usage(tenant, "duration_ms", result["duration_ms"], utcnow())
            if self.artifacts:
                for obligation in result.get("obligations", []):
                    cert = (obligation.get("artifacts") or {}).get("certificate")
                    if cert:
                        meta = self.artifacts.put(tenant, job["id"], f"{obligation['id']}-certificate.json", cert)
                        self.store.record_artifact(meta, utcnow())
                    lean_src = (obligation.get("artifacts") or {}).get("lean_export")
                    if lean_src:
                        meta = self.artifacts.put(
                            tenant, job["id"], f"{obligation['id']}.lean", lean_src, "text/plain"
                        )
                        self.store.record_artifact(meta, utcnow())
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

    async def submit_wait(self, payload, request_id, idempotency_key=None, tenant_id="local"):
        job, replayed = self.create(
            payload, request_id, idempotency_key, origin="http-wait", tenant_id=tenant_id
        )
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
