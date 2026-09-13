"""SQLite persistence with versioned migrations. Replace this repository at the cloud milestone."""

import json
import sqlite3
from pathlib import Path

SCHEMA_VERSION = 3
TERMINAL = frozenset({"succeeded", "failed", "cancelled", "timed_out", "rejected"})


class PersistenceError(RuntimeError):
    pass


class IdempotencyConflict(ValueError):
    pass


class RunStore:
    def __init__(self, path):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("PRAGMA foreign_keys=ON")
            self._migrate(db)

    def connect(self):
        db = sqlite3.connect(self.path, timeout=5)
        db.row_factory = sqlite3.Row
        return db

    def _migrate(self, db):
        db.execute("CREATE TABLE IF NOT EXISTS schema_version (version INTEGER PRIMARY KEY)")
        row = db.execute("SELECT version FROM schema_version").fetchone()
        version = row["version"] if row else 0
        if version == 0:
            db.execute("INSERT INTO schema_version VALUES (1)")
            version = 1
            db.execute(
                """CREATE TABLE IF NOT EXISTS runs (
                id TEXT PRIMARY KEY, created_at TEXT NOT NULL, title TEXT NOT NULL,
                verdict TEXT NOT NULL, duration_ms REAL NOT NULL, document TEXT NOT NULL)"""
            )
            db.execute("CREATE INDEX IF NOT EXISTS runs_created ON runs(created_at DESC)")
        if version == 1:
            db.execute(
                """CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                title TEXT NOT NULL,
                job_status TEXT NOT NULL,
                verdict TEXT,
                duration_ms REAL,
                payload TEXT NOT NULL,
                document TEXT,
                content_hash TEXT NOT NULL,
                idempotency_key TEXT,
                request_id TEXT,
                trace_id TEXT NOT NULL,
                lease_token TEXT,
                cancel_requested INTEGER NOT NULL DEFAULT 0,
                operational_reason TEXT
                )"""
            )
            db.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS jobs_idempotency ON jobs(idempotency_key) WHERE idempotency_key IS NOT NULL"
            )
            db.execute("CREATE INDEX IF NOT EXISTS jobs_created ON jobs(created_at DESC)")
            db.execute("CREATE INDEX IF NOT EXISTS jobs_status ON jobs(job_status)")
            db.execute("CREATE INDEX IF NOT EXISTS jobs_title ON jobs(title)")
            for run in db.execute("SELECT id, created_at, title, verdict, duration_ms, document FROM runs"):
                document = json.loads(run["document"])
                payload = json.dumps(document.get("submission", {}), ensure_ascii=False)
                db.execute(
                    """INSERT OR IGNORE INTO jobs (
                    id, created_at, updated_at, title, job_status, verdict, duration_ms,
                    payload, document, content_hash, idempotency_key, request_id, trace_id,
                    lease_token, cancel_requested, operational_reason)
                    VALUES (?, ?, ?, ?, 'succeeded', ?, ?, ?, ?, ?, NULL, ?, ?, NULL, 0, NULL)""",
                    (
                        run["id"],
                        run["created_at"],
                        run["created_at"],
                        run["title"],
                        run["verdict"],
                        run["duration_ms"],
                        payload,
                        run["document"],
                        document.get("input_sha256", ""),
                        document.get("request_id"),
                        document.get("trace_id") or run["id"].replace("-", ""),
                    ),
                )
            db.execute("UPDATE schema_version SET version=2")
            version = 2
        if version == 2:
            db.execute("ALTER TABLE jobs ADD COLUMN lease_until TEXT")
            db.execute("ALTER TABLE jobs ADD COLUMN parent_id TEXT")
            db.execute("ALTER TABLE jobs ADD COLUMN version INTEGER NOT NULL DEFAULT 1")
            db.execute("ALTER TABLE jobs ADD COLUMN origin TEXT")
            db.execute(
                """CREATE TABLE IF NOT EXISTS imports (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                document TEXT NOT NULL
                )"""
            )
            db.execute("UPDATE schema_version SET version=3")
            version = 3
        if version != SCHEMA_VERSION:
            raise PersistenceError(f"Unsupported schema version {version}")

    def ready(self):
        with self.connect() as db:
            return db.execute("SELECT version FROM schema_version").fetchone()[0] == SCHEMA_VERSION

    def recover_interrupted(self, now_iso, reason="interrupted_by_restart"):
        with self.connect() as db:
            rows = db.execute("SELECT id FROM jobs WHERE job_status='running'").fetchall()
            db.execute(
                """UPDATE jobs SET job_status='failed', operational_reason=?, updated_at=?,
                verdict=NULL, lease_token=NULL, lease_until=NULL WHERE job_status='running'""",
                (reason, now_iso),
            )
        return [row["id"] for row in rows]

    def count_dispatchable(self):
        with self.connect() as db:
            return db.execute(
                """SELECT COUNT(*) AS n FROM jobs
                WHERE job_status='queued' AND IFNULL(origin,'queue')='queue'"""
            ).fetchone()["n"]

    def count_status(self, status):
        with self.connect() as db:
            return db.execute(
                "SELECT COUNT(*) AS n FROM jobs WHERE job_status=?", (status,)
            ).fetchone()["n"]

    def claim_queued(self, now_iso, lease_token, lease_until):
        with self.connect() as db:
            row = db.execute(
                """SELECT id FROM jobs WHERE job_status='queued' AND IFNULL(origin,'queue')='queue'
                ORDER BY created_at ASC LIMIT 1"""
            ).fetchone()
            if row is None:
                return None
            cur = db.execute(
                """UPDATE jobs SET job_status='running', updated_at=?, lease_token=?, lease_until=?
                WHERE id=? AND job_status='queued'""",
                (now_iso, lease_token, lease_until, row["id"]),
            )
            if cur.rowcount != 1:
                return None
        return self.get_job(row["id"])

    def heartbeat(self, job_id, lease_token, lease_until, updated_at):
        with self.connect() as db:
            cur = db.execute(
                """UPDATE jobs SET lease_until=?, updated_at=?
                WHERE id=? AND lease_token=? AND job_status='running'""",
                (lease_until, updated_at, job_id, lease_token),
            )
            return cur.rowcount == 1

    def hashes(self):
        with self.connect() as db:
            return {row["content_hash"] for row in db.execute("SELECT content_hash FROM jobs")}

    def save_import(self, record_id, created_at, document):
        with self.connect() as db:
            db.execute(
                "INSERT INTO imports VALUES (?, ?, ?)",
                (record_id, created_at, json.dumps(document, ensure_ascii=False)),
            )

    def create_job(self, job):
        try:
            with self.connect() as db:
                if job.get("idempotency_key"):
                    existing = db.execute(
                        "SELECT id, content_hash, job_status, document FROM jobs WHERE idempotency_key=?",
                        (job["idempotency_key"],),
                    ).fetchone()
                    if existing:
                        if existing["content_hash"] != job["content_hash"]:
                            raise IdempotencyConflict(
                                "Idempotency-Key reused with a different submission"
                            )
                        return dict(existing), True
                db.execute(
                    """INSERT INTO jobs (
                    id, created_at, updated_at, title, job_status, verdict, duration_ms,
                    payload, document, content_hash, idempotency_key, request_id, trace_id,
                    lease_token, cancel_requested, operational_reason, origin)
                    VALUES (?, ?, ?, ?, ?, NULL, NULL, ?, NULL, ?, ?, ?, ?, NULL, 0, NULL, ?)""",
                    (
                        job["id"],
                        job["created_at"],
                        job["updated_at"],
                        job["title"],
                        job["job_status"],
                        job["payload"],
                        job["content_hash"],
                        job.get("idempotency_key"),
                        job.get("request_id"),
                        job["trace_id"],
                        job.get("origin"),
                    ),
                )
        except sqlite3.IntegrityError as exc:
            raise PersistenceError("Could not persist job") from exc
        return job, False

    def transition(self, job_id, from_status, to_status, *, updated_at, **fields):
        assignments = ["job_status=?", "updated_at=?"]
        values = [to_status, updated_at]
        for key in (
            "verdict",
            "duration_ms",
            "document",
            "lease_token",
            "operational_reason",
            "cancel_requested",
            "lease_until",
            "parent_id",
            "version",
        ):
            if key in fields:
                assignments.append(f"{key}=?")
                values.append(fields[key])
        values.extend([job_id, from_status])
        lease = fields.get("require_lease")
        lease_clause = " AND lease_token=?" if lease else ""
        if lease:
            values.append(lease)
        with self.connect() as db:
            cur = db.execute(
                f"UPDATE jobs SET {', '.join(assignments)} WHERE id=? AND job_status=?{lease_clause}",
                values,
            )
            if cur.rowcount != 1:
                return False
            if to_status == "succeeded" and fields.get("document"):
                document = json.loads(fields["document"])
                db.execute(
                    "INSERT OR REPLACE INTO runs VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        document["id"],
                        document["created_at"],
                        document["submission"]["title"],
                        document["verdict"],
                        document["duration_ms"],
                        fields["document"],
                    ),
                )
        return True

    def request_cancel(self, job_id, updated_at):
        with self.connect() as db:
            row = db.execute("SELECT job_status FROM jobs WHERE id=?", (job_id,)).fetchone()
            if row is None:
                return None
            if row["job_status"] in TERMINAL:
                return self.get_job(job_id)
            db.execute(
                "UPDATE jobs SET cancel_requested=1, updated_at=? WHERE id=?",
                (updated_at, job_id),
            )
        return self.get_job(job_id)

    def cancel_requested(self, job_id):
        with self.connect() as db:
            row = db.execute("SELECT cancel_requested FROM jobs WHERE id=?", (job_id,)).fetchone()
        return bool(row and row["cancel_requested"])

    def get_job(self, job_id):
        with self.connect() as db:
            row = db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        if row is None:
            return None
        data = dict(row)
        data["payload"] = json.loads(data["payload"])
        if data["document"]:
            data["document"] = json.loads(data["document"])
        return data

    def save(self, run):
        """Compatibility writer used by older tests: persist a completed verification."""
        document = json.dumps(run, ensure_ascii=False)
        created = run["created_at"]
        payload = json.dumps(run["submission"], ensure_ascii=False)
        with self.connect() as db:
            db.execute(
                "INSERT OR REPLACE INTO runs VALUES (?, ?, ?, ?, ?, ?)",
                (
                    run["id"],
                    created,
                    run["submission"]["title"],
                    run["verdict"],
                    run["duration_ms"],
                    document,
                ),
            )
            db.execute(
                """INSERT INTO jobs (
                id, created_at, updated_at, title, job_status, verdict, duration_ms,
                payload, document, content_hash, idempotency_key, request_id, trace_id,
                lease_token, cancel_requested, operational_reason)
                VALUES (?, ?, ?, ?, 'succeeded', ?, ?, ?, ?, ?, NULL, ?, ?, NULL, 0, NULL)
                ON CONFLICT(id) DO UPDATE SET
                job_status='succeeded', verdict=excluded.verdict, duration_ms=excluded.duration_ms,
                document=excluded.document, updated_at=excluded.updated_at, lease_token=NULL""",
                (
                    run["id"],
                    created,
                    created,
                    run["submission"]["title"],
                    run["verdict"],
                    run["duration_ms"],
                    payload,
                    document,
                    run.get("input_sha256", ""),
                    run.get("request_id"),
                    run.get("trace_id", run["id"].replace("-", "")),
                ),
            )

    def get(self, run_id):
        with self.connect() as db:
            row = db.execute("SELECT document FROM jobs WHERE id=?", (run_id,)).fetchone()
            if row and row["document"]:
                return json.loads(row["document"])
            legacy = db.execute("SELECT document FROM runs WHERE id=?", (run_id,)).fetchone()
        return json.loads(legacy["document"]) if legacy else None

    def list(self, limit, offset, *, query="", verdict=None, job_status=None):
        clauses = ["1=1"]
        values = []
        if query:
            clauses.append("title LIKE ?")
            values.append(f"%{query}%")
        if verdict:
            clauses.append("verdict=?")
            values.append(verdict)
        if job_status:
            clauses.append("job_status=?")
            values.append(job_status)
        where = " AND ".join(clauses)
        with self.connect() as db:
            rows = db.execute(
                f"""SELECT id, created_at, title, verdict, duration_ms, job_status, content_hash
                FROM jobs WHERE {where} ORDER BY created_at DESC LIMIT ? OFFSET ?""",
                [*values, limit, offset],
            ).fetchall()
            total = db.execute(f"SELECT COUNT(*) AS n FROM jobs WHERE {where}", values).fetchone()["n"]
        return {
            "items": [dict(r) for r in rows],
            "total": total,
        }

    def list_jobs(self, limit, offset):
        with self.connect() as db:
            rows = db.execute(
                """SELECT id, created_at, updated_at, title, job_status, verdict, duration_ms,
                operational_reason FROM jobs ORDER BY created_at DESC LIMIT ? OFFSET ?""",
                (limit, offset),
            ).fetchall()
            total = db.execute("SELECT COUNT(*) AS n FROM jobs").fetchone()["n"]
        return {"items": [dict(r) for r in rows], "total": total}

    def stats(self):
        with self.connect() as db:
            counts = dict(
                db.execute(
                    "SELECT verdict, COUNT(*) FROM jobs WHERE verdict IS NOT NULL GROUP BY verdict"
                ).fetchall()
            )
            jobs = dict(db.execute("SELECT job_status, COUNT(*) FROM jobs GROUP BY job_status").fetchall())
            average = db.execute(
                "SELECT AVG(duration_ms) FROM jobs WHERE duration_ms IS NOT NULL"
            ).fetchone()[0]
        return {
            "total": sum(counts.values()),
            "verdicts": counts,
            "job_statuses": jobs,
            "average_duration_ms": round(average or 0, 2),
            "calibration": None,
            "false_accept_rate": None,
            "note": "Operational counts, not an accuracy benchmark; ground truth is unavailable",
        }
