"""Explicit UTF-8 I/O so Windows never infers a legacy code page."""

import json
from pathlib import Path


def read_text(path):
    return Path(path).read_text(encoding="utf-8")


def write_text(path, content):
    Path(path).write_text(content, encoding="utf-8", newline="\n")


def read_json(path):
    return json.loads(read_text(path))


def write_json(path, payload):
    write_text(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
