"""SQLite persistence boundary. Replace this repository at the cloud milestone."""

import json
import sqlite3
from pathlib import Path


class RunStore:
    def __init__(self, path):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("CREATE TABLE IF NOT EXISTS schema_version (version INTEGER PRIMARY KEY)")
            db.execute("INSERT OR IGNORE INTO schema_version VALUES (1)")
            db.execute("""CREATE TABLE IF NOT EXISTS runs (
                id TEXT PRIMARY KEY, created_at TEXT NOT NULL, title TEXT NOT NULL,
                verdict TEXT NOT NULL, duration_ms REAL NOT NULL, document TEXT NOT NULL)""")
            db.execute("CREATE INDEX IF NOT EXISTS runs_created ON runs(created_at DESC)")

    def connect(self):
        return sqlite3.connect(self.path, timeout=5)

    def ready(self):
        with self.connect() as db:
            return db.execute("SELECT version FROM schema_version").fetchone()[0] == 1

    def save(self, run):
        with self.connect() as db:
            db.execute(
                "INSERT INTO runs VALUES (?, ?, ?, ?, ?, ?)",
                (
                    run["id"],
                    run["created_at"],
                    run["submission"]["title"],
                    run["verdict"],
                    run["duration_ms"],
                    json.dumps(run, ensure_ascii=False),
                ),
            )

    def get(self, run_id):
        with self.connect() as db:
            row = db.execute("SELECT document FROM runs WHERE id=?", (run_id,)).fetchone()
        return json.loads(row[0]) if row else None

    def list(self, limit, offset):
        with self.connect() as db:
            rows = db.execute(
                "SELECT id, created_at, title, verdict, duration_ms FROM runs ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
            total = db.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
        return {
            "items": [
                dict(zip(("id", "created_at", "title", "verdict", "duration_ms"), r)) for r in rows
            ],
            "total": total,
        }

    def stats(self):
        with self.connect() as db:
            counts = dict(
                db.execute("SELECT verdict, COUNT(*) FROM runs GROUP BY verdict").fetchall()
            )
            average = db.execute("SELECT AVG(duration_ms) FROM runs").fetchone()[0]
        return {
            "total": sum(counts.values()),
            "verdicts": counts,
            "average_duration_ms": round(average or 0, 2),
            "calibration": None,
            "false_accept_rate": None,
            "note": "Operational counts, not an accuracy benchmark; ground truth is unavailable",
        }
