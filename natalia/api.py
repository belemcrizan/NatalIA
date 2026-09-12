import asyncio
import logging
import os
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from time import monotonic
from urllib.parse import urlsplit

from fastapi import FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.middleware.trustedhost import TrustedHostMiddleware

from natalia import __version__
from natalia.jobs import JobManager, utcnow
from natalia.models import Submission
from natalia.replay import replay
from natalia.storage import IdempotencyConflict, PersistenceError, RunStore
from natalia.telemetry import Metrics, event
from natalia.textio import read_json
from natalia.worker import execute

PACKAGE = Path(__file__).parent


class BodyLimit:
    """Bound streamed bodies too, before JSON decoding."""

    def __init__(self, app, maximum=65536):
        self.app, self.maximum = app, maximum

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] not in {"POST", "PUT", "PATCH"}:
            return await self.app(scope, receive, send)
        chunks, size = [], 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            chunk = message.get("body", b"")
            size += len(chunk)
            if size > self.maximum:
                return await JSONResponse({"detail": "Request exceeds 64 KiB"}, status_code=413)(
                    scope, receive, send
                )
            chunks.append(chunk)
            if not message.get("more_body", False):
                break
        pending = True

        async def bounded_receive():
            nonlocal pending
            if pending:
                pending = False
                return {"type": "http.request", "body": b"".join(chunks), "more_body": False}
            return await receive()

        await self.app(scope, bounded_receive, send)


def create_app(db_path=None, runner=execute):
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    metrics = Metrics()
    store = RunStore(db_path or os.getenv("NATALIA_DB_PATH", "data/natalia.db"))
    max_workers = int(os.getenv("NATALIA_MAX_WORKERS", "2"))
    if not 1 <= max_workers <= 8:
        raise ValueError("NATALIA_MAX_WORKERS must be between 1 and 8")
    jobs = JobManager(store, runner, metrics, max_workers)

    @asynccontextmanager
    async def lifespan(app):
        interrupted = jobs.recover()
        metrics.recovered.inc(len(interrupted))
        event("startup", version=__version__, workers=max_workers, recovered=len(interrupted))
        yield

    app = FastAPI(title="NatalIA local verifier", version=__version__, lifespan=lifespan)
    app.state.store, app.state.metrics, app.state.jobs = store, metrics, jobs
    app.add_middleware(BodyLimit)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "[::1]", "natalia", "testserver"],
    )

    @app.middleware("http")
    async def observe(request: Request, call_next):
        tick = monotonic()
        request.state.request_id = uuid.uuid4().hex
        if request.method == "POST":
            origin = request.headers.get("origin")
            if origin and urlsplit(origin).netloc != request.headers.get("host"):
                return JSONResponse(
                    {"detail": "Cross-origin submission is disabled"}, status_code=403
                )
        response = await call_next(request)
        route = getattr(request.scope.get("route"), "path", "unmatched")
        if route.startswith("/assets"):
            route = "/assets"
        seconds = monotonic() - tick
        metrics.requests.labels(route, request.method, str(response.status_code)).inc()
        metrics.latency.labels(route).observe(seconds)
        event(
            "http_request",
            request_id=request.state.request_id,
            route=route,
            method=request.method,
            status=response.status_code,
            duration_ms=round(seconds * 1000, 2),
        )
        response.headers["X-Request-ID"] = request.state.request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        if request.url.path == "/" or request.url.path.startswith("/assets"):
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
            )
        if request.url.path.startswith("/api"):
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/health/live")
    def live():
        return {"status": "ok", "version": __version__}

    @app.get("/health/ready")
    def ready():
        try:
            if store.ready():
                return {"status": "ready", "schema_version": 2}
        except Exception:
            pass
        raise HTTPException(503, "Persistence unavailable")

    @app.get("/metrics", include_in_schema=False)
    def prometheus():
        return Response(
            generate_latest(metrics.registry), headers={"Content-Type": CONTENT_TYPE_LATEST}
        )

    @app.get("/api/capabilities")
    def capabilities():
        return {
            "mode": "local",
            "schema_version": "1.0",
            "replay_schema": "natalia-replay-1.0",
            "translation": "manual DSL",
            "dimensions": "exact Q^7",
            "z3": "real arithmetic, validated rational counterexamples",
            "sympy": "advisory limits only",
            "lean": "not implemented",
            "interval": "not implemented",
            "policy": "deterministic",
            "calibration": None,
            "jobs": "at-least-once persistence; interrupted jobs fail operationally after restart",
            "max_workers": max_workers,
            "max_body_bytes": 65536,
            "max_budget_ms": 15000,
            "python_tested": ["3.12", "3.13"],
            "version": __version__,
        }

    @app.get("/api/examples")
    def examples():
        return [read_json(path) for path in sorted((PACKAGE / "examples").glob("*.json"))]

    @app.get("/api/stats")
    def stats():
        return {**store.stats(), "active_runs": jobs.active}

    @app.get("/api/runs")
    def runs(
        limit: int = Query(20, ge=1, le=100),
        offset: int = Query(0, ge=0, le=1000000),
        q: str = Query("", max_length=160),
        verdict: str | None = Query(None),
        job_status: str | None = Query(None),
    ):
        return store.list(limit, offset, query=q, verdict=verdict, job_status=job_status)

    @app.get("/api/jobs")
    def list_jobs(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0, le=1000000)):
        return store.list_jobs(limit, offset)

    @app.get("/api/jobs/{job_id}")
    def get_job(job_id: uuid.UUID):
        job = store.get_job(str(job_id))
        if job is None:
            raise HTTPException(404, "Job not found")
        return _public_job(job)

    @app.post("/api/jobs/{job_id}/cancel")
    def cancel_job(job_id: uuid.UUID):
        job = jobs.request_cancel(str(job_id))
        if job is None:
            raise HTTPException(404, "Job not found")
        return _public_job(job)

    @app.post("/api/jobs", status_code=202)
    async def submit_job(
        submission: Submission,
        request: Request,
        idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    ):
        payload = submission.model_dump()
        try:
            job, replayed = jobs.create(payload, request.state.request_id, idempotency_key)
        except IdempotencyConflict as exc:
            raise HTTPException(409, str(exc)) from None
        if replayed:
            return _public_job(job)
        if not await jobs.acquire():
            store.transition(
                job["id"],
                "queued",
                "rejected",
                updated_at=utcnow(),
                operational_reason="capacity_exhausted",
            )
            metrics.jobs.labels("rejected").inc()
            raise HTTPException(
                429, "All local workers are busy; retry shortly", headers={"Retry-After": "2"}
            )

        async def _run():
            try:
                await jobs.run_reserved(job)
            except Exception:
                event("job_background_failure", run_id=job["id"])

        asyncio.create_task(_run())
        return _public_job(store.get_job(job["id"]))

    @app.post("/api/runs", status_code=201)
    async def submit(
        submission: Submission,
        request: Request,
        idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    ):
        payload = submission.model_dump()
        try:
            result, status = await jobs.submit_wait(
                payload, request.state.request_id, idempotency_key
            )
        except IdempotencyConflict as exc:
            raise HTTPException(409, str(exc)) from None
        except PersistenceError:
            event("verification_failed", error_kind="persistence")
            raise HTTPException(500, "Run could not be persisted") from None
        except RuntimeError as exc:
            if str(exc) == "idempotent_in_flight":
                raise HTTPException(
                    409, "An execution with this Idempotency-Key is still running"
                ) from None
            event("verification_failed", error_kind="internal")
            raise HTTPException(500, "Run could not be completed") from None
        if status == 429:
            raise HTTPException(
                429, "All local workers are busy; retry shortly", headers={"Retry-After": "2"}
            )
        if status == 200:
            return JSONResponse(result, status_code=200)
        return result

    @app.get("/api/runs/{run_id}")
    def get_run(run_id: uuid.UUID):
        run = store.get(str(run_id))
        if run is None:
            job = store.get_job(str(run_id))
            if job is None:
                raise HTTPException(404, "Run not found")
            raise HTTPException(
                409,
                {
                    "detail": "Execution has no scientific result yet",
                    "job_status": job["job_status"],
                    "operational_reason": job.get("operational_reason"),
                },
            )
        return run

    @app.post("/api/replay")
    def replay_evidence(payload: dict):
        try:
            return replay(payload)
        except Exception as exc:
            raise HTTPException(422, str(exc)) from None

    @app.get("/")
    def index():
        return FileResponse(PACKAGE / "static" / "index.html")

    app.mount("/assets", StaticFiles(directory=PACKAGE / "static"), name="assets")
    return app


def _public_job(job):
    return {
        "id": job["id"],
        "created_at": job["created_at"],
        "updated_at": job["updated_at"],
        "title": job["title"],
        "job_status": job["job_status"],
        "verdict": job.get("verdict"),
        "duration_ms": job.get("duration_ms"),
        "operational_reason": job.get("operational_reason"),
        "content_hash": job.get("content_hash"),
        "trace_id": job.get("trace_id"),
        "document": job.get("document"),
    }
