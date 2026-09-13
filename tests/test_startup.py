"""Tests for startup, CLI commands, and environment diagnostics."""

import subprocess
import sys
from pathlib import Path

from natalia import __version__
from natalia.cli import check_port_available, main


def test_cli_version(capsys):
    ret = main(["version"])
    assert ret == 0
    captured = capsys.readouterr()
    assert f"NatalIA version {__version__}" in captured.out
    assert "Python:" in captured.out


def test_cli_doctor(capsys):
    ret = main(["doctor"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Diagnostic Report" in captured.out
    assert "[OK] Python executable:" in captured.out
    assert "[OK] FastAPI:" in captured.out
    assert "[OK] Z3 SMT Solver:" in captured.out
    assert "[OK] SQLite storage engine:" in captured.out


def test_cli_verify_accepted(capsys):
    root = Path(__file__).resolve().parents[1]
    example = root / "natalia" / "examples" / "01-energy.json"
    ret = main(["verify", str(example)])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Verdict:         ACCEPTED" in captured.out
    assert "Guarantee Level: SMT_RELATIVE" in captured.out


def test_cli_verify_refuted(capsys):
    root = Path(__file__).resolve().parents[1]
    example = root / "natalia" / "examples" / "02-counterexample.json"
    ret = main(["verify", str(example)])
    assert ret == 1
    captured = capsys.readouterr()
    assert "Verdict:         REFUTED" in captured.out
    assert "Counterexample:" in captured.out


def test_check_port_available():
    # An ephemeral port or localhost check should return a boolean
    free = check_port_available("127.0.0.1", 0)
    assert isinstance(free, bool)


def test_python_module_invocation():
    root = Path(__file__).resolve().parents[1]
    res = subprocess.run(
        [sys.executable, "-m", "natalia", "version"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    assert f"NatalIA version {__version__}" in res.stdout
