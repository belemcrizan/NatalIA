import asyncio
import json
import logging
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic, time_ns
from urllib.parse import urlsplit

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.middleware.trustedhost import TrustedHostMiddleware

from natalia import __version__
from natalia.models import Submission
from natalia.storage import RunStore
from natalia.telemetry import Metrics, event
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
    active = 0

    @asynccontextmanager
    async def lifespan(app):
        event("startup", version=__version__, workers=max_workers)
        yield

    app = FastAPI(title="NatalIA local verifier", version=__version__, lifespan=lifespan)
    app.state.store, app.state.metrics = store, metrics
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
                return {"status": "ready"}
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
            "translation": "manual DSL",
            "dimensions": "exact Q^7",
            "z3": "real arithmetic, validated rational counterexamples",
            "sympy": "advisory limits only",
            "lean": "not implemented",
            "interval": "not implemented",
            "policy": "deterministic",
            "calibration": None,
            "max_workers": max_workers,
            "max_body_bytes": 65536,
            "max_budget_ms": 15000,
        }

    @app.get("/api/examples")
    def examples():
        return [
            json.loads(path.read_text()) for path in sorted((PACKAGE / "examples").glob("*.json"))
        ]

    @app.get("/api/stats")
    def stats():
        return {**store.stats(), "active_runs": active}

    @app.get("/api/runs")
    def runs(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0, le=1000000)):
        return store.list(limit, offset)

    @app.post("/api/runs", status_code=201)
    async def submit(submission: Submission, request: Request):
        nonlocal active
        if active >= max_workers:
            raise HTTPException(
                429, "All local workers are busy; retry shortly", headers={"Retry-After": "2"}
            )
        active += 1
        metrics.active.inc()
        payload = submission.model_dump()
        run_id, trace_id = str(uuid.uuid4()), uuid.uuid4().hex
        wall, tick = time_ns(), monotonic()
        # Shield keeps the slot until the disposable child has actually finished, even on cancellation.
        task = asyncio.create_task(asyncio.to_thread(runner, payload))
        try:
            try:
                result = await asyncio.shield(task)
            except asyncio.CancelledError:
                result = await task
            result.update(
                id=run_id,
                trace_id=trace_id,
                request_id=request.state.request_id,
                created_at=datetime.now(timezone.utc).isoformat(),
                submission=payload,
            )
            root_span = uuid.uuid4().hex[:16]
            for span in result["spans"]:
                span.update(trace_id=trace_id, parent_span_id=root_span)
            result["spans"].insert(
                0,
                {
                    "span_id": root_span,
                    "parent_span_id": None,
                    "trace_id": trace_id,
                    "name": "verification",
                    "oracle": "orchestrator",
                    "start_time_unix_ns": wall,
                    "duration_ms": round((monotonic() - tick) * 1000, 3),
                    "status": result["verdict"],
                },
            )
            await asyncio.to_thread(store.save, result)
            metrics.runs.labels(result["verdict"]).inc()
            metrics.duration.observe(result["duration_ms"] / 1000)
            for obligation in result["obligations"]:
                metrics.oracles.labels(obligation["oracle"], obligation["status"]).inc()
            event(
                "verification_completed",
                run_id=run_id,
                trace_id=trace_id,
                request_id=request.state.request_id,
                verdict=result["verdict"],
                duration_ms=result["duration_ms"],
            )
            return result
        except Exception:
            event("verification_failed", run_id=run_id, trace_id=trace_id)
            raise HTTPException(500, "Run could not be completed or persisted") from None
        finally:
            active -= 1
            metrics.active.dec()

    @app.get("/api/runs/{run_id}")
    def get_run(run_id: uuid.UUID):
        run = store.get(str(run_id))
        if run is None:
            raise HTTPException(404, "Run not found")
        return run

    @app.get("/")
    def index():
        return FileResponse(PACKAGE / "static" / "index.html")

    app.mount("/assets", StaticFiles(directory=PACKAGE / "static"), name="assets")
    return app
