import asyncio
import json
import logging
import os
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from time import monotonic
from urllib.parse import urlsplit

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.middleware.trustedhost import TrustedHostMiddleware

from natalia import __version__
from natalia.artifacts import ArtifactStore
from natalia.certificates import recheck as recheck_certificate
from natalia.compile import preview as compile_preview
from natalia.identity import Principal, hash_key, local_principal, parse_bootstrap
from natalia.importers import inspect_records
from natalia.investigations import get_investigation, list_investigations
from natalia.jobs import JobManager, utcnow
from natalia.lean import probe as lean_probe
from natalia.library import CASES, featured
from natalia.models import Submission
from natalia.replay import replay
from natalia.storage import SCHEMA_VERSION, IdempotencyConflict, PersistenceError, RunStore
from natalia.telemetry import Metrics, event
from natalia.textio import read_json
from natalia.trust import TRUST_CONTRACT
from natalia.worker import execute

PACKAGE = Path(__file__).parent
FRONTEND_MISSING = (
    "Frontend build missing at natalia/web/index.html. "
    "Run scripts/setup.ps1 or scripts/setup.sh, which build the React app. "
    "Development: npm --prefix frontend ci && npm --prefix frontend run build."
)


def _frontend_root() -> Path:
    dist = PACKAGE / "web"
    if not (dist / "index.html").is_file():
        raise RuntimeError(FRONTEND_MISSING)
    return dist


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


def create_app(db_path=None, runner=execute, profile=None, artifact_dir=None):
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    metrics = Metrics()
    store = RunStore(db_path or os.getenv("NATALIA_DB_PATH", "data/natalia.db"))
    profile = profile or os.getenv("NATALIA_PROFILE", "local")
    if profile not in {"local", "distributed"}:
        raise ValueError("NATALIA_PROFILE must be local or distributed")
    artifacts = ArtifactStore(artifact_dir or os.getenv("NATALIA_ARTIFACT_DIR", "data/artifacts"))
    max_workers = int(os.getenv("NATALIA_MAX_WORKERS", "2"))
    max_queue = int(os.getenv("NATALIA_MAX_QUEUE", "32"))
    tenant_queue = int(os.getenv("NATALIA_TENANT_QUEUE", str(max_queue)))
    if not 1 <= max_workers <= 8:
        raise ValueError("NATALIA_MAX_WORKERS must be between 1 and 8")
    if not 1 <= max_queue <= 200:
        raise ValueError("NATALIA_MAX_QUEUE must be between 1 and 200")
    jobs = JobManager(
        store,
        runner,
        metrics,
        max_workers,
        max_queue=max_queue,
        artifacts=artifacts,
        max_queue_per_tenant=tenant_queue,
    )
    stamp = utcnow()
    store.ensure_tenant("local", "Local loopback", stamp)
    for entry in parse_bootstrap():
        store.ensure_tenant(entry["tenant"], entry.get("name") or entry["tenant"], stamp)
        try:
            store.add_api_key(
                entry.get("id") or uuid.uuid4().hex,
                entry["tenant"],
                hash_key(entry["key"]),
                entry.get("role") or "researcher",
                entry.get("scopes") or ["jobs:write", "jobs:read", "artifacts:read"],
                stamp,
            )
        except Exception:
            pass

    @asynccontextmanager
    async def lifespan(app):
        interrupted = jobs.recover()
        metrics.recovered.inc(len(interrupted))
        await jobs.start_dispatcher()
        event(
            "startup",
            version=__version__,
            workers=max_workers,
            queue=max_queue,
            recovered=len(interrupted),
            semantics="at-least-once persistence; queued jobs resume after restart; running jobs fail operationally",
        )
        try:
            yield
        finally:
            await jobs.stop_dispatcher()

    app = FastAPI(title="NatalIA local verifier", version=__version__, lifespan=lifespan)
    app.state.store, app.state.metrics, app.state.jobs = store, metrics, jobs
    app.state.profile, app.state.artifacts = profile, artifacts

    def current_principal(
        authorization: str | None = Header(default=None),
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ) -> Principal:
        if profile == "local":
            return local_principal()
        raw = x_api_key
        if not raw and authorization and authorization.lower().startswith("bearer "):
            raw = authorization.split(" ", 1)[1].strip()
        if not raw:
            raise HTTPException(401, "Authentication required in the distributed profile")
        row = store.lookup_api_key(hash_key(raw))
        if row is None:
            raise HTTPException(401, "Invalid or revoked API key")
        scopes = tuple(json.loads(row["scopes"])) if isinstance(row["scopes"], str) else tuple(row["scopes"])
        return Principal(
            tenant_id=row["tenant_id"],
            subject=row["id"],
            role=row["role"],
            key_id=row["id"],
            scopes=scopes,
        )
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
            if origin:
                origin_host = urlsplit(origin).hostname
                request_host = urlsplit("//" + (request.headers.get("host") or "")).hostname
                if origin_host != request_host:
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
        if request.url.path.startswith("/api"):
            response.headers["Cache-Control"] = "no-store"
        if request.url.path.startswith("/assets/"):
            response.headers.setdefault("Cache-Control", "public, max-age=31536000, immutable")
        if response.headers.get("content-type", "").startswith("text/html"):
            response.headers["Cache-Control"] = "no-store"
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
                "font-src 'self'; img-src 'self' data:; connect-src 'self'; "
                "frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
            )
        return response

    @app.get("/health/live")
    def live():
        return {"status": "ok", "version": __version__}

    @app.get("/health/ready")
    def ready():
        try:
            if store.ready():
                return {"status": "ready", "schema_version": SCHEMA_VERSION}
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
            "mode": profile,
            "schema_version": "1.0",
            "trust_contract": TRUST_CONTRACT,
            "replay_schema": "natalia-replay-1.0",
            "translation": "manual DSL",
            "dimensions": "exact Q^7",
            "z3": "real arithmetic, validated rational counterexamples",
            "sympy": "advisory limits only",
            "lean": lean_probe(),
            "kernel": "polynomial identity and sum-of-squares fragment over Q",
            "interval": "exact rational box enclosure when domain_min and domain_max are set",
            "fast": "SMT-relative acceptance is not a certificate",
            "certified": "Acceptance requires KERNEL_CHECKED; SMT is not silently reused",
            "auth": "none on loopback local profile; API keys required in distributed profile",
            "policy": "deterministic",
            "calibration": None,
            "jobs": "at-least-once persistence; queued jobs are claimed atomically; interrupted running jobs fail operationally after restart; stale lease results are rejected",
            "max_workers": max_workers,
            "max_queue": max_queue,
            "max_queue_per_tenant": tenant_queue,
            "max_body_bytes": 65536,
            "max_budget_ms": 15000,
            "python_tested": ["3.12", "3.13"],
            "frontend": "react-vite",
            "version": __version__,
        }

    @app.get("/api/examples")
    def examples():
        return [read_json(path) for path in sorted((PACKAGE / "examples").glob("*.json"))]

    @app.get("/api/stats")
    def stats():
        return {**store.stats(), "active_runs": jobs.active, "queued": store.count_status("queued")}

    @app.get("/api/runs")
    def runs(
        principal: Principal = Depends(current_principal),
        limit: int = Query(20, ge=1, le=100),
        offset: int = Query(0, ge=0, le=1000000),
        q: str = Query("", max_length=160),
        verdict: str | None = Query(None),
        job_status: str | None = Query(None),
    ):
        return store.list(
            limit,
            offset,
            query=q,
            verdict=verdict,
            job_status=job_status,
            tenant_id=principal.tenant_id,
        )

    @app.get("/api/jobs")
    def list_jobs(
        principal: Principal = Depends(current_principal),
        limit: int = Query(20, ge=1, le=100),
        offset: int = Query(0, ge=0, le=1000000),
    ):
        return store.list_jobs(limit, offset, tenant_id=principal.tenant_id)

    @app.get("/api/jobs/{job_id}")
    def get_job(job_id: uuid.UUID, principal: Principal = Depends(current_principal)):
        job = store.get_job(str(job_id), tenant_id=principal.tenant_id)
        if job is None:
            raise HTTPException(404, "Job not found")
        return _public_job(job)

    @app.post("/api/jobs/{job_id}/cancel")
    def cancel_job(job_id: uuid.UUID, principal: Principal = Depends(current_principal)):
        existing = store.get_job(str(job_id), tenant_id=principal.tenant_id)
        if existing is None:
            raise HTTPException(404, "Job not found")
        job = jobs.request_cancel(str(job_id))
        if job is None:
            raise HTTPException(404, "Job not found")
        return _public_job(job)

    @app.get("/api/jobs/{job_id}/events")
    async def job_events(job_id: uuid.UUID, principal: Principal = Depends(current_principal)):
        if store.get_job(str(job_id), tenant_id=principal.tenant_id) is None:
            raise HTTPException(404, "Job not found")

        async def stream():
            last = None
            for _ in range(400):
                job = store.get_job(str(job_id), tenant_id=principal.tenant_id)
                if job is None:
                    yield "event: error\ndata: {\"detail\":\"gone\"}\n\n"
                    return
                payload = json.dumps(
                    {
                        "id": job["id"],
                        "job_status": job["job_status"],
                        "verdict": job.get("verdict"),
                        "conclusion": job.get("conclusion"),
                        "guarantee_level": job.get("guarantee_level"),
                    }
                )
                if payload != last:
                    yield f"event: job\ndata: {payload}\n\n"
                    last = payload
                if job["job_status"] in {"succeeded", "failed", "cancelled", "timed_out", "rejected"}:
                    return
                await asyncio.sleep(0.2)

        return StreamingResponse(stream(), media_type="text/event-stream")

    @app.post("/api/jobs", status_code=202)
    async def submit_job(
        submission: Submission,
        request: Request,
        principal: Principal = Depends(current_principal),
        idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    ):
        payload = submission.model_dump(exclude_none=True)
        try:
            job, replayed, reason = jobs.enqueue(
                payload, request.state.request_id, idempotency_key, tenant_id=principal.tenant_id
            )
        except IdempotencyConflict as exc:
            raise HTTPException(409, str(exc)) from None
        if reason == "queue_full":
            metrics.jobs.labels("rejected").inc()
            raise HTTPException(
                429, "Local verification queue is full; retry shortly", headers={"Retry-After": "2"}
            )
        if reason == "tenant_quota":
            metrics.jobs.labels("rejected").inc()
            raise HTTPException(
                429, "Tenant job quota exhausted; retry shortly", headers={"Retry-After": "2"}
            )
        metrics.queued.set(store.count_status("queued"))
        return _public_job(job)

    @app.post("/api/compile")
    def compile_submission(submission: dict):
        return compile_preview(submission)

    @app.get("/api/catalog")
    def catalog(theme: str | None = None):
        items = CASES if not theme else [item for item in CASES if item["theme"] == theme]
        return {"count": len(items), "themes": sorted({item["theme"] for item in CASES}), "items": items}

    @app.get("/api/catalog/featured")
    def catalog_featured():
        return featured()

    @app.get("/api/investigations")
    def investigations():
        return list_investigations()

    @app.get("/api/investigations/{ident}")
    def investigation(ident: str):
        item = get_investigation(ident)
        if item is None:
            raise HTTPException(404, "Investigation not found")
        return item

    @app.post("/api/import")
    def import_cases(payload: dict):
        inspection = inspect_records(payload)
        if payload.get("dry_run", True) or not payload.get("confirm"):
            inspection["applied"] = False
            inspection["note"] = (
                "Preview only. Send confirm=true and dry_run=false to record the batch. "
                "Imported expressions are not executed."
            )
            return inspection
        if inspection["errors"]:
            raise HTTPException(status_code=422, detail=inspection)
        known = store.hashes()
        duplicates = [item for item in inspection["accepted"] if item["content_hash"] in known]
        inspection["duplicates"] = duplicates
        if duplicates and payload.get("policy") != "skip_duplicates":
            inspection["applied"] = False
            raise HTTPException(status_code=409, detail=inspection)
        kept = [
            item
            for item in inspection["accepted"]
            if item["content_hash"] not in known or payload.get("policy") == "skip_duplicates"
        ]
        store.save_import(uuid.uuid4().hex, utcnow(), {"accepted": kept})
        inspection["applied"] = True
        inspection["stored"] = len(kept)
        return inspection

    @app.get("/api/system")
    def system(principal: Principal = Depends(current_principal)):
        stats = store.stats()
        return {
            "version": __version__,
            "schema_version": SCHEMA_VERSION,
            "profile": profile,
            "trust_contract": TRUST_CONTRACT,
            "tenant_id": principal.tenant_id,
            "api": "ready" if store.ready() else "unavailable",
            "executor": {
                "active": jobs.active,
                "max_workers": max_workers,
                "queued": store.count_status("queued"),
                "max_queue": max_queue,
                "semantics": "at-least-once",
            },
            "adapters": {
                "z3": "real arithmetic with independent rational witnesses",
                "sympy": "advisory limits only",
                "interval": "exact rational box enclosure when a finite domain is declared",
                "kernel": "polynomial identity / sum-of-squares over Q",
                "lean": lean_probe(),
                "translation": {
                    "available": False,
                    "reason": "No model provider is configured. Text/LaTeX is stored, not interpreted.",
                },
            },
            "stats": stats,
            "usage": store.usage_for_tenant(principal.tenant_id),
            "effective_config": {
                "max_workers": max_workers,
                "max_queue": max_queue,
                "max_queue_per_tenant": tenant_queue,
                "max_body_bytes": 65536,
                "max_budget_ms": 15000,
                "auth": profile,
            },
        }

    @app.get("/api/benchmark/manifest")
    def benchmark_manifest():
        from natalia.bench import load

        try:
            manifest, instances = load()
        except FileNotFoundError:
            return {
                "available": False,
                "reason": "Run python scripts/eval_bench.py --build to materialize the local corpus.",
            }
        return {"available": True, "manifest": manifest, "count": len(instances)}

    @app.post("/api/runs", status_code=201)
    async def submit(
        submission: Submission,
        request: Request,
        principal: Principal = Depends(current_principal),
        idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    ):
        payload = submission.model_dump(exclude_none=True)
        try:
            result, status = await jobs.submit_wait(
                payload,
                request.state.request_id,
                idempotency_key,
                tenant_id=principal.tenant_id,
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
    def get_run(run_id: uuid.UUID, principal: Principal = Depends(current_principal)):
        job = store.get_job(str(run_id), tenant_id=principal.tenant_id)
        if job is None:
            raise HTTPException(404, "Run not found")
        if not job.get("document"):
            raise HTTPException(
                409,
                {
                    "detail": "Execution has no scientific result yet",
                    "job_status": job["job_status"],
                    "operational_reason": job.get("operational_reason"),
                },
            )
        return job["document"]

    @app.post("/api/replay")
    def replay_evidence(payload: dict, principal: Principal = Depends(current_principal)):
        try:
            return replay(payload)
        except Exception as exc:
            raise HTTPException(422, str(exc)) from None

    @app.post("/api/certificates/recheck")
    def recheck(payload: dict, principal: Principal = Depends(current_principal)):
        try:
            return recheck_certificate(payload)
        except Exception as exc:
            raise HTTPException(422, str(exc)) from None

    @app.get("/api/artifacts/{digest}")
    def get_artifact(digest: str, principal: Principal = Depends(current_principal)):
        meta = store.get_artifact_meta(principal.tenant_id, digest)
        if meta is None:
            raise HTTPException(404, "Artifact not found")
        data, path = artifacts.get(principal.tenant_id, digest)
        if data is None:
            raise HTTPException(404, "Artifact not found")
        return Response(data, media_type="application/octet-stream")

    frontend = _frontend_root()

    @app.get("/")
    def index():
        return FileResponse(frontend / "index.html")

    app.mount("/assets", StaticFiles(directory=frontend / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def spa(full_path: str):
        if full_path == "metrics" or full_path.startswith(
            ("api/", "health/", "docs", "redoc", "openapi.json", "assets/")
        ):
            raise HTTPException(404, "Not found")
        suffix = Path(full_path).suffix.lower()
        if suffix in {
            ".js",
            ".css",
            ".map",
            ".json",
            ".woff",
            ".woff2",
            ".ttf",
            ".png",
            ".svg",
            ".ico",
            ".txt",
        }:
            raise HTTPException(404, "Not found")
        return FileResponse(frontend / "index.html")

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
        "tenant_id": job.get("tenant_id"),
        "verification_mode": job.get("verification_mode"),
        "guarantee_level": job.get("guarantee_level"),
        "conclusion": job.get("conclusion"),
        "document": job.get("document"),
    }
