import json
import logging

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram

logger = logging.getLogger("natalia")


def event(name, **fields):
    logger.info(json.dumps({"event": name, **fields}, ensure_ascii=False))


class Metrics:
    def __init__(self):
        self.registry = CollectorRegistry()
        self.requests = Counter(
            "natalia_http_requests_total",
            "HTTP responses",
            ["route", "method", "status"],
            registry=self.registry,
        )
        self.latency = Histogram(
            "natalia_http_duration_seconds", "HTTP latency", ["route"], registry=self.registry
        )
        self.runs = Counter(
            "natalia_runs_total", "Completed verifications", ["verdict"], registry=self.registry
        )
        self.duration = Histogram(
            "natalia_run_duration_seconds",
            "Verification wall time",
            buckets=(0.1, 0.25, 0.5, 1, 2, 5, 10, 15, 20),
            registry=self.registry,
        )
        self.oracles = Counter(
            "natalia_obligations_total",
            "Obligation outcomes",
            ["oracle", "status"],
            registry=self.registry,
        )
        self.active = Gauge("natalia_active_runs", "Active local workers", registry=self.registry)
