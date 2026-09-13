"""Frontend build identity written by Vite and read by FastAPI."""

from __future__ import annotations

import json
from pathlib import Path

PACKAGE = Path(__file__).parent
WEB = PACKAGE / "web"


def frontend_status():
    index = WEB / "index.html"
    assets = WEB / "assets"
    meta_path = WEB / "build.json"
    meta = {}
    if meta_path.is_file():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            meta = {"error": "build.json is not valid JSON"}
    present = index.is_file()
    asset_count = len(list(assets.glob("*"))) if assets.is_dir() else 0
    return {
        "present": present,
        "index": str(index) if present else None,
        "asset_count": asset_count,
        "build_id": meta.get("buildId") or meta.get("build_id"),
        "app_version": meta.get("version"),
        "built_at": meta.get("builtAt") or meta.get("built_at"),
        "missing_reason": None
        if present
        else (
            "Frontend build missing at natalia/web/index.html. "
            "Run scripts/setup.ps1 or scripts/setup.sh, or npm --prefix frontend ci && npm --prefix frontend run build. "
            "The retired HTML UI is not served."
        ),
    }
