"""NatalIA command-line interface.

Provides cross-platform entry points for running the server, running
diagnostics, verifying claims offline, and inspecting environment status.
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
from pathlib import Path

from natalia import __version__


def check_port_available(host: str, port: int) -> bool:
    """Check whether a TCP port is free on the specified host."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        try:
            sock.bind((host, port))
            return True
        except OSError:
            return False


def cmd_run(args: argparse.Namespace) -> int:
    """Run the NatalIA local verification server."""
    import os

    import uvicorn

    host = args.host
    port = args.port

    if not check_port_available(host, port):
        sys.stderr.write(
            f"ERROR: Port {port} on {host} is already in use.\n"
            f"To run on another port, use: natalia run --port <port>\n"
            f"Or stop the process currently using port {port}.\n"
        )
        return 1

    os.environ["PYTHONUTF8"] = "1"
    if args.profile:
        os.environ["NATALIA_PROFILE"] = args.profile
    if args.db_path:
        os.environ["NATALIA_DB_PATH"] = args.db_path
    if args.artifact_dir:
        os.environ["NATALIA_ARTIFACT_DIR"] = args.artifact_dir

    print("==================================================")
    print(f" NatalIA Verification Workbench v{__version__}")
    print(f" Web Interface: http://{host}:{port}")
    print(f" API Ready:     http://{host}:{port}/health/ready")
    print(f" Mode:          {args.profile}")
    print(" Stop with Ctrl+C (in your terminal)")
    print("==================================================")

    uvicorn.run(
        "natalia.api:create_app",
        factory=True,
        host=host,
        port=port,
        workers=args.workers,
        log_level="info",
    )
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    """Run diagnostic checks on the environment and dependencies."""
    all_ok = True
    print(f"NatalIA Diagnostic Report (v{__version__})")
    print("-" * 50)

    # 1. Python runtime
    py_ver = sys.version_info
    py_ver_str = f"{py_ver.major}.{py_ver.minor}.{py_ver.micro}"
    if py_ver >= (3, 12):
        print(f"[OK] Python executable: {sys.executable} ({py_ver_str})")
    else:
        print(f"[FAIL] Python {py_ver_str} is incompatible. NatalIA requires Python >= 3.12.")
        all_ok = False

    # 2. Key library imports
    libs = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("z3", "Z3 SMT Solver"),
        ("sympy", "SymPy Symbolic Engine"),
        ("pydantic", "Pydantic"),
        ("natalia", "NatalIA Core"),
    ]
    for mod_name, label in libs:
        try:
            mod = __import__(mod_name)
            ver = getattr(mod, "__version__", "available")
            print(f"[OK] {label}: {ver}")
        except ImportError as exc:
            print(f"[FAIL] {label} import failed: {exc}")
            all_ok = False

    # 3. Port availability check
    port = args.port or 8000
    if check_port_available("127.0.0.1", port):
        print(f"[OK] Port {port}: available for loopback binding")
    else:
        print(f"[WARN] Port {port}: currently in use by another process")

    # 4. Storage & persistence check
    import tempfile

    from natalia.storage import RunStore

    try:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            test_db = Path(tmp) / "doctor_check.db"
            store = RunStore(test_db)
            if store.ready():
                print("[OK] SQLite storage engine: verified writable and schema initialized")
            else:
                print("[FAIL] SQLite storage engine failed readiness check")
                all_ok = False
    except Exception as exc:
        print(f"[FAIL] Storage check encountered error: {exc}")
        all_ok = False

    print("-" * 50)
    if all_ok:
        print("Diagnostic summary: All primary requirements satisfied. System ready.")
        return 0
    else:
        print("Diagnostic summary: Failures detected. Please review above output.")
        return 1


def cmd_verify(args: argparse.Namespace) -> int:
    """Verify a claim JSON file directly via the verification engine."""
    from natalia.engine import verify
    from natalia.textio import read_json

    path = Path(args.file)
    if not path.is_file():
        sys.stderr.write(f"ERROR: File not found: {path}\n")
        return 1

    try:
        data = read_json(path)
    except Exception as exc:
        sys.stderr.write(f"ERROR: Failed to parse JSON: {exc}\n")
        return 1

    submission = data.get("submission", data)
    print(f"Verifying: {submission.get('title', 'Untitled')}")
    print(f"Source:    {submission.get('source_latex', '(none)')}")

    result = verify(submission)
    print("-" * 50)
    print(f"Verdict:         {result.get('verdict')}")
    print(f"Guarantee Level: {result.get('guarantee_level')}")
    print(f"Conclusion:      {result.get('conclusion')}")
    print(f"Duration:        {result.get('duration_ms')} ms")
    print(f"Obligations:     {len(result.get('obligations', []))}")

    for obl in result.get("obligations", []):
        print(f"  - [{obl.get('status')}] {obl.get('claim_id')}: {obl.get('reason')}")
        witness = obl.get("counterexample") or obl.get("artifacts", {}).get("counterexample")
        if witness:
            print(f"    Counterexample: {json.dumps(witness)}")

    print("-" * 50)
    return 0 if result.get("verdict") == "ACCEPTED" else 1


def cmd_version(args: argparse.Namespace) -> int:
    """Print NatalIA version information."""
    print(f"NatalIA version {__version__}")
    print(f"Python: {sys.version.split()[0]} ({sys.executable})")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="natalia",
        description="NatalIA: Local evidence-first verification workbench for physics claims",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # run
    run_parser = subparsers.add_parser("run", help="Start the verification server")
    run_parser.add_argument("--host", default="127.0.0.1", help="Host address to bind (default: 127.0.0.1)")
    run_parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    run_parser.add_argument("--workers", type=int, default=1, help="Number of server workers (default: 1)")
    run_parser.add_argument("--profile", default="local", choices=["local", "distributed"], help="Runtime profile")
    run_parser.add_argument("--db-path", default=None, help="Custom database path")
    run_parser.add_argument("--artifact-dir", default=None, help="Custom artifact directory")

    # doctor
    doctor_parser = subparsers.add_parser("doctor", help="Check local environment and prerequisites")
    doctor_parser.add_argument("--port", type=int, default=8000, help="Port to test availability (default: 8000)")

    # verify
    verify_parser = subparsers.add_parser("verify", help="Verify a claim JSON file directly")
    verify_parser.add_argument("file", help="Path to JSON file containing submission")

    # version
    subparsers.add_parser("version", help="Show version information")

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 0

    commands = {
        "run": cmd_run,
        "doctor": cmd_doctor,
        "verify": cmd_verify,
        "version": cmd_version,
    }
    handler = commands.get(args.command)
    if handler:
        return handler(args)
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
