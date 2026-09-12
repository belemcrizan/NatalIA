"""Consistent online SQLite backup (including committed WAL contents)."""

import argparse
import sqlite3
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("destination", type=Path)
parser.add_argument("--source", type=Path, default=Path("data/natalia.db"))
args = parser.parse_args()
if not args.source.is_file():
    parser.error("Source database does not exist")
if args.destination.exists():
    parser.error("Destination already exists; select a new path")
args.destination.parent.mkdir(parents=True, exist_ok=True)
with sqlite3.connect(args.source.resolve().as_uri() + "?mode=ro", uri=True) as source:
    with sqlite3.connect(args.destination) as destination:
        source.backup(destination)
print(f"Backup written to {args.destination}")
