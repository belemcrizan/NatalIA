# NatalIA setup — fail fast, never delete data.

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
$OutputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$Root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $Root

function Find-Python {
    $candidates = @()
    if (Get-Command py -ErrorAction SilentlyContinue) {
        foreach ($tag in @("-3.13", "-3.12", "-3")) {
            try { $candidates += (& py $tag -c "import sys; print(sys.executable)") } catch { }
        }
    }
    if (Get-Command python -ErrorAction SilentlyContinue) {
        $candidates += (Get-Command python).Source
    }
    foreach ($exe in $candidates | Where-Object { $_ } | Select-Object -Unique) {
        $ver = & $exe -c "import sys; print('%d.%d.%d' % sys.version_info[:3])"
        $ok = & $exe -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)"
        if ($LASTEXITCODE -eq 0) {
            return $exe, $ver
        }
        Write-Host "Ignoring $exe ($ver): NatalIA requires Python >= 3.12"
    }
    throw "No compatible Python (>= 3.12) found. Python 3.13.3 was tested on Windows; 3.12 remains the CI baseline."
}

function Find-Node {
    if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
        throw "Node.js is required to build the React frontend. Install Node 20.19+ or 22.12+ (Vite 8). This script does not delete data or environments."
    }
    $raw = node -v
    Write-Host "Node: $raw"
    $parts = $raw.TrimStart("v").Split(".")
    $major = [int]$parts[0]
    $minor = [int]$parts[1]
    $ok = ($major -eq 20 -and $minor -ge 19) -or ($major -eq 22 -and $minor -ge 12) -or ($major -ge 23)
    if (-not $ok) {
        throw "Node.js $raw is too old. NatalIA needs 20.19+ or 22.12+ to build the frontend."
    }
}

Find-Node
Write-Host "Installing frontend dependencies and building React assets"
Push-Location -LiteralPath (Join-Path $Root "frontend")
if (Test-Path -LiteralPath "package-lock.json") {
    npm ci
} else {
    npm install
}
if ($LASTEXITCODE -ne 0) { throw "npm install failed" }
npm run build
if ($LASTEXITCODE -ne 0) { throw "frontend build failed" }
Pop-Location

$python, $version = Find-Python
Write-Host "Interpreter: $python"
Write-Host "Version: $version"

$venvPython = Join-Path $Root ".venv\Scripts\python.exe"
if (Test-Path -LiteralPath $venvPython) {
    Write-Host "Found existing virtualenv at .venv"
    & $venvPython -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)"
    if ($LASTEXITCODE -ne 0) {
        throw "Existing .venv is not Python >= 3.12. Remove it yourself if you want it recreated; this script will not delete it."
    }
} else {
    Write-Host "Creating .venv"
    & $python -m venv .venv
}

Write-Host "Installing locked dependencies"
& $venvPython -m pip install -r (Join-Path $Root "requirements.lock")
if ($LASTEXITCODE -ne 0) { throw "pip install failed" }
& $venvPython -m pip install --no-deps -e $Root
if ($LASTEXITCODE -ne 0) { throw "editable install failed" }
& $venvPython -c "import natalia, fastapi, z3, sympy; print('imports ok', natalia.__version__)"
if ($LASTEXITCODE -ne 0) { throw "import check failed" }
Write-Host "Setup complete."
Write-Host "Start the packaged app with: .\scripts\run.ps1"
Write-Host "Then open http://127.0.0.1:8000 (FastAPI serves the React build; Node is not required at runtime)."
Write-Host "Frontend development mode (optional): run the API, then in another terminal: npm --prefix frontend run dev"
Write-Host "Vite proxies /api to http://127.0.0.1:8000. Browser origin host must match the API host (127.0.0.1 vs localhost)."
