"""Restore a backup by copying to a new writable path. Never overwrites."""

import argparse
import shutil
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args(argv)
    if not args.source.is_file():
        parser.error("Source backup does not exist")
    if args.destination.exists():
        parser.error("Destination already exists; refusing to overwrite")
    args.destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(args.source, args.destination)
    print(f"Restored copy written to {args.destination}")


if __name__ == "__main__":
    main()
