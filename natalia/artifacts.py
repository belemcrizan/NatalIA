"""Local artifact store. Paths are tenant-scoped; IDs are not authorization."""

import hashlib
import json
from pathlib import Path


class ArtifactStore:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def put(self, tenant_id, job_id, name, payload, content_type="application/json"):
        if isinstance(payload, (dict, list)):
            data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
            content_type = "application/json"
        elif isinstance(payload, str):
            data = payload.encode("utf-8")
        else:
            data = payload
        digest = hashlib.sha256(data).hexdigest()
        relative = Path(tenant_id) / job_id / f"{digest[:16]}-{name}"
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return {
            "id": digest,
            "tenant_id": tenant_id,
            "job_id": job_id,
            "name": name,
            "sha256": digest,
            "bytes": len(data),
            "content_type": content_type,
            "path": str(relative).replace("\\", "/"),
        }

    def get(self, tenant_id, digest):
        base = self.root / tenant_id
        if not base.exists():
            return None, None
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            data = path.read_bytes()
            if hashlib.sha256(data).hexdigest() == digest:
                return data, path
        return None, None
