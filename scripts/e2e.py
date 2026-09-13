"""Production-build browser tests against FastAPI, not Vite."""

import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import httpx
from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / "docs" / "ui"


def wait_ready(url: str):
    for _ in range(100):
        try:
            if httpx.get(url + "/health/ready", trust_env=False).status_code == 200:
                return
        except httpx.ConnectError:
            pass
        time.sleep(0.1)
    raise RuntimeError("API did not become ready")


def main():
    artifacts = ROOT / "artifacts"
    artifacts.mkdir(exist_ok=True)
    UI.mkdir(parents=True, exist_ok=True)
    web = ROOT / "natalia" / "web" / "index.html"
    if not web.is_file():
        raise SystemExit("Frontend build missing. Run scripts/setup.ps1 or npm --prefix frontend run build.")
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
        env = {**os.environ, "NATALIA_DB_PATH": str(Path(temp) / "e2e.db"), "PYTHONUTF8": "1"}
        with (artifacts / "e2e-server.log").open("w", encoding="utf-8") as log:
            process = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "uvicorn",
                    "natalia.api:create_app",
                    "--factory",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(port),
                ],
                cwd=ROOT,
                env=env,
                stdout=log,
                stderr=log,
            )
            try:
                url = f"http://127.0.0.1:{port}"
                wait_ready(url)
                home = httpx.get(url + "/", trust_env=False)
                assert home.status_code == 200
                assert "/assets/" in home.text
                spa = httpx.get(url + "/library", trust_env=False)
                assert spa.status_code == 200
                assert "text/html" in spa.headers["content-type"]
                missing = httpx.get(url + "/api/does-not-exist", trust_env=False)
                assert missing.status_code == 404
                with sync_playwright() as p:
                    browser = p.chromium.launch(executable_path=os.getenv("NATALIA_CHROMIUM_PATH"))
                    page = browser.new_page(viewport={"width": 1440, "height": 1050}, device_scale_factor=1)
                    errors = []
                    page.on("pageerror", lambda e: errors.append(str(e)))
                    page.goto(url)
                    expect(page.get_by_role("link", name="Start an investigation")).to_be_visible()
                    page.screenshot(path=str(artifacts / "home-desktop.png"), full_page=True)
                    (UI / "home-desktop.png").write_bytes((artifacts / "home-desktop.png").read_bytes())
                    page.get_by_role("link", name="Explore examples").click()
                    expect(page.get_by_text("A progression of educational models")).to_be_visible()
                    page.screenshot(path=str(artifacts / "library-desktop.png"), full_page=True)
                    (UI / "library-desktop.png").write_bytes((artifacts / "library-desktop.png").read_bytes())
                    page.locator("a[href^='/investigate/']").first.click()
                    expect(page.get_by_role("button", name="Run verification")).to_be_visible()
                    page.screenshot(path=str(artifacts / "investigation-desktop.png"), full_page=True)
                    (UI / "investigation-desktop.png").write_bytes((artifacts / "investigation-desktop.png").read_bytes())
                    page.get_by_role("link", name="Claim builder").click()
                    expect(page.get_by_role("button", name="Run verification")).to_be_enabled()
                    page.screenshot(path=str(artifacts / "laboratory-desktop.png"), full_page=True)
                    (UI / "laboratory-desktop.png").write_bytes((artifacts / "laboratory-desktop.png").read_bytes())
                    cases = httpx.get(url + "/api/examples", trust_env=False).json()
                    for case in cases:
                        page.select_option("#example", case["id"])
                        page.get_by_role("button", name="Advanced DSL").click()
                        page.get_by_role("button", name="Run verification").click()
                        expect(page.get_by_text(case["expected_verdict"], exact=False).first).to_be_visible(timeout=30000)
                        if case["expected_verdict"] == "REFUTED":
                            expect(page.locator(".witness").first).to_be_visible()
                            page.screenshot(path=str(artifacts / "counterexample-desktop.png"), full_page=True)
                            (UI / "counterexample-desktop.png").write_bytes(
                                (artifacts / "counterexample-desktop.png").read_bytes()
                            )
                    page.get_by_role("button", name="Advanced DSL").click()
                    page.locator("#dsl").fill("{broken")
                    page.get_by_role("button", name="Run verification").click()
                    expect(page.get_by_role("alert").first).to_contain_text("Invalid JSON")
                    page.get_by_role("link", name="History").click()
                    expect(page.locator("table tbody tr")).to_have_count(9)
                    page.reload()
                    expect(page.locator("table tbody tr")).to_have_count(9)
                    page.locator("table tbody a").first.click()
                    expect(page.get_by_text("Advanced evidence")).to_be_visible()
                    page.get_by_role("link", name="Diagnostics").click()
                    expect(page.get_by_text("Frontend")).to_be_visible()
                    page.screenshot(path=str(artifacts / "observability-desktop.png"), full_page=True)
                    (UI / "observability-desktop.png").write_bytes(
                        (artifacts / "observability-desktop.png").read_bytes()
                    )
                    hostile = cases[0]["submission"]
                    hostile["title"] = '<img src=x onerror="window.XSS=true">'
                    assert (
                        httpx.post(url + "/api/runs", json=hostile, timeout=20, trust_env=False).status_code
                        == 201
                    )
                    page.get_by_role("link", name="History").click()
                    page.get_by_role("button", name="Refresh").click()
                    expect(page.locator("table tbody tr")).to_have_count(10)
                    assert page.locator("table img").count() == 0
                    assert page.evaluate("window.XSS") is None
                    page.set_viewport_size({"width": 390, "height": 844})
                    page.get_by_role("link", name="Home").click()
                    expect(page.get_by_role("heading", name="Check a declared claim, then read the evidence.")).to_be_visible()
                    page.screenshot(path=str(artifacts / "home-mobile.png"), full_page=True)
                    (UI / "home-mobile.png").write_bytes((artifacts / "home-mobile.png").read_bytes())
                    page.get_by_role("link", name="Claim builder").click()
                    expect(page.get_by_role("button", name="Run verification")).to_be_visible()
                    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
                    page.screenshot(path=str(artifacts / "laboratory-mobile.png"), full_page=True)
                    (UI / "laboratory-mobile.png").write_bytes((artifacts / "laboratory-mobile.png").read_bytes())
                    page.set_viewport_size({"width": 768, "height": 1024})
                    page.goto(url + "/library")
                    expect(page.get_by_text("A progression of educational models")).to_be_visible()
                    assert not errors, errors
                    browser.close()
                size = sum(p.stat().st_size for p in (ROOT / "natalia" / "web" / "assets").glob("*"))
                print(
                    f"E2E PASS: React workspace, examples, history, XSS, mobile. Bundle assets bytes={size}"
                )
            finally:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()


if __name__ == "__main__":
    main()
