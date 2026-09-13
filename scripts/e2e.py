"""Real browser + API + isolated solvers + SQLite. Requires playwright install chromium."""

import json
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


def main():
    artifacts = ROOT / "artifacts"
    artifacts.mkdir(exist_ok=True)
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
                for _ in range(100):
                    try:
                        if httpx.get(url + "/health/ready", trust_env=False).status_code == 200:
                            break
                    except httpx.ConnectError:
                        pass
                    time.sleep(0.1)
                else:
                    raise RuntimeError("API did not become ready")
                with sync_playwright() as p:
                    browser = p.chromium.launch(executable_path=os.getenv("NATALIA_CHROMIUM_PATH"))
                    page = browser.new_page(
                        viewport={"width": 1440, "height": 1050}, device_scale_factor=1
                    )
                    errors = []
                    page.on("pageerror", lambda e: errors.append(str(e)))
                    page.goto(url)
                    try:
                        page.wait_for_selector("#onboard[open]", timeout=4000)
                        page.locator("#onboard-skip").click()
                        page.wait_for_selector("#onboard[open]", state="hidden", timeout=4000)
                    except Exception:
                        if page.locator("#onboard").is_visible():
                            page.locator("#onboard-skip").click()
                    expect(page.get_by_role("button", name="New Verification").first).to_be_visible()
                    page.locator("#home-new").click()
                    expect(page.locator("#run")).to_be_enabled()
                    expect(page.locator("#guided")).to_be_visible()
                    page.screenshot(path=str(artifacts / "laboratory-desktop.png"), full_page=True)
                    cases = httpx.get(url + "/api/examples", trust_env=False).json()
                    for case in cases:
                        page.select_option("#example", case["id"])
                        page.click("#run")
                        expect(page.locator("#result > .verdict-row .badge").first).to_have_class(
                            f"badge {case['expected_verdict']}", timeout=30000
                        )
                        expect(page.locator("#run")).to_be_enabled()
                        if case["expected_verdict"] == "REFUTED":
                            expect(page.locator(".witness")).to_contain_text("false")
                            page.screenshot(
                                path=str(artifacts / "counterexample-desktop.png"), full_page=True
                            )
                    page.click("#mode-advanced")
                    expect(page.locator("#dsl")).to_be_visible()
                    with page.expect_download() as download:
                        page.click("#export")
                    target = artifacts / "export.json"
                    download.value.save_as(target)
                    exported = json.loads(target.read_text(encoding="utf-8"))
                    assert exported["submission"]["title"] == cases[-1]["submission"]["title"]
                    page.fill("#dsl", "{broken")
                    page.click("#run")
                    expect(page.locator("#error")).to_contain_text("Invalid JSON")
                    page.click('nav [data-page="history"]')
                    expect(page.locator("#history tbody tr")).to_have_count(9)
                    page.reload()
                    expect(page.locator("#history tbody tr")).to_have_count(9)
                    page.locator("#history tbody button").first.click()
                    expect(page.locator("#result")).to_be_visible()
                    page.click('nav [data-page="observability"]')
                    expect(page.locator("#stats .stat-value").first).to_have_text("9")
                    page.screenshot(
                        path=str(artifacts / "observability-desktop.png"), full_page=True
                    )
                    hostile = cases[0]["submission"]
                    hostile["title"] = '<img src=x onerror="window.XSS=true">'
                    assert (
                        httpx.post(
                            url + "/api/runs", json=hostile, timeout=20, trust_env=False
                        ).status_code
                        == 201
                    )
                    page.click('nav [data-page="history"]')
                    expect(page.locator("#history tbody tr")).to_have_count(10)
                    assert page.locator("#history img").count() == 0
                    assert page.evaluate("window.XSS") is None
                    page.set_viewport_size({"width": 390, "height": 844})
                    page.click('nav [data-page="laboratory"]')
                    expect(page.locator("#run")).to_be_visible()
                    expect(page.locator('nav [data-page="laboratory"]')).to_have_class(
                        "nav-item active"
                    )
                    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
                    page.screenshot(path=str(artifacts / "laboratory-mobile.png"), full_page=True)
                    assert not errors, errors
                    browser.close()
                print(
                    "E2E PASS: guided examples, advanced JSON, history, export, XSS and mobile layout"
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
