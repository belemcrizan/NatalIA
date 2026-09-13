"""Build or evaluate PhysVerifyBench. Separate from the unit-test suite."""

import argparse
import json
import platform
import sys
from pathlib import Path

from natalia import __version__
from natalia.bench import dump, evaluate, load, summarize
from natalia.engine import verify

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "natalia" / "bench_data" / "v0.1"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true", help="Write instances and exit")
    parser.add_argument("--quick", action="store_true", help="One instance per family")
    parser.add_argument("--split", default="all", choices=["all", "dev", "val", "test"])
    args = parser.parse_args()
    if args.build or not (DATA / "instances.jsonl").exists():
        manifest, instances = dump(DATA)
        print(json.dumps({"built": True, "count": manifest["count"], "families": manifest["families"]}, indent=2))
        if args.build:
            return
    else:
        manifest, instances = load(DATA)
    if args.split != "all":
        instances = [item for item in instances if item["split"] == args.split]
    if args.quick:
        chosen, seen = [], set()
        for item in instances:
            if item["family"] in seen:
                continue
            seen.add(item["family"])
            chosen.append(item)
        instances = chosen
    rows = evaluate(instances, runner=verify)
    report = summarize(rows, manifest)
    report["environment"] = {
        "natalia": __version__,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "runner": "natalia.engine.verify (in-process; not the HTTP worker)",
        "subset": "quick-one-per-family" if args.quick else args.split,
    }
    artifacts = ROOT / "artifacts"
    artifacts.mkdir(exist_ok=True)
    out = artifacts / "physverifybench-report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("corpus", "n", "overall", "calibration")}, indent=2))
    mismatches = [row for row in rows if not row["match"]]
    if mismatches:
        print("mismatches", len(mismatches), file=sys.stderr)
        for row in mismatches[:20]:
            print(row["id"], row["system_expected"], row["predicted"], row["reason"], file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
