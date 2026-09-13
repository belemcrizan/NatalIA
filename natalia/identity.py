"""Principals come from credentials, never from a client-supplied tenant_id field."""

import hashlib
import hmac
import json
import os
import secrets
from dataclasses import dataclass

LOCAL_TENANT = "local"


def hash_key(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def generate_key() -> str:
    return "nla_" + secrets.token_hex(24)


@dataclass(frozen=True)
class Principal:
    tenant_id: str
    subject: str
    role: str
    key_id: str | None = None
    scopes: tuple[str, ...] = ("jobs:write", "jobs:read", "artifacts:read")


def local_principal() -> Principal:
    return Principal(tenant_id=LOCAL_TENANT, subject="loopback", role="admin", scopes=("*",))


def parse_bootstrap(raw=None):
    text = raw if raw is not None else os.getenv("NATALIA_BOOTSTRAP_KEYS", "")
    if not text.strip():
        return []
    if text.lstrip().startswith("["):
        return json.loads(text)
    entries = []
    for item in text.split(","):
        tenant, _, key = item.partition(":")
        if tenant and key:
            entries.append({"tenant": tenant.strip(), "key": key.strip(), "role": "researcher"})
    return entries


def constant_time_digest(raw: str, expected_hash: str) -> bool:
    digest = hash_key(raw)
    return hmac.compare_digest(digest, expected_hash)
