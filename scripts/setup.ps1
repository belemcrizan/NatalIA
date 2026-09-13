# NatalIA environment setup — fail fast, reliable, never delete data.

[CmdletBinding()]
param(
    [switch]$Dev,
    [switch]$ProdOnly
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
$OutputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

# Resolve project root relative to script location
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$Root = Split-Path -Parent $scriptDir

# Verify project root has pyproject.toml; if not, search upward
if (-not (Test-Path -LiteralPath (Join-Path $Root "pyproject.toml"))) {
    $cursor = $scriptDir
    while ($cursor -and (Test-Path -LiteralPath $cursor)) {
        if (Test-Path -LiteralPath (Join-Path $cursor "pyproject.toml")) {
            $Root = $cursor
            break
        }
        $parent = Split-Path -Parent $cursor
        if ($parent -eq $cursor) { break }
        $cursor = $parent
    }
}

Set-Location -LiteralPath $Root

function Find-Python {
    $candidates = @()
    if (Get-Command py -ErrorAction SilentlyContinue) {
        foreach ($tag in @("-3.13", "-3.12", "-3")) {
            try { 
                $res = & py $tag -c "import sys; print(sys.executable)" 2>$null
                if ($res -and (Test-Path -LiteralPath $res)) { $candidates += $res }
            } catch { }
        }
    }
    if (Get-Command python -ErrorAction SilentlyContinue) {
        $src = (Get-Command python).Source
        if ($src -and (Test-Path -LiteralPath $src)) { $candidates += $src }
    }
    if (Get-Command python3 -ErrorAction SilentlyContinue) {
        $src = (Get-Command python3).Source
        if ($src -and (Test-Path -LiteralPath $src)) { $candidates += $src }
    }
    foreach ($exe in $candidates | Where-Object { $_ } | Select-Object -Unique) {
        try {
            $ver = & "$exe" -c "import sys; print('%d.%d.%d' % sys.version_info[:3])" 2>$null
            & "$exe" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)" 2>$null
            if ($LASTEXITCODE -eq 0) {
                return $exe, $ver
            }
            Write-Host "Ignoring $exe ($ver): NatalIA requires Python >= 3.12" -ForegroundColor Gray
        } catch { }
    }
    throw "No compatible Python (>= 3.12) found. Please install Python 3.12 or 3.13."
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
$frontendDir = Join-Path $Root "frontend"
Push-Location -LiteralPath $frontendDir
try {
    if (Test-Path -LiteralPath "package-lock.json") {
        npm ci
    } else {
        npm install
    }
    if ($LASTEXITCODE -ne 0) { throw "npm install failed" }
    npm run build
    if ($LASTEXITCODE -ne 0) { throw "frontend build failed" }
} finally {
    Pop-Location
}

$python, $version = Find-Python
Write-Host "Selected Python: $python ($version)" -ForegroundColor Green

$venvPython = Join-Path $Root ".venv\Scripts\python.exe"
if (Test-Path -LiteralPath $venvPython) {
    Write-Host "Found existing virtual environment at .venv" -ForegroundColor Cyan
    & "$venvPython" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)"
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "============================================================" -ForegroundColor Red
        Write-Host "Existing .venv is incompatible with Python >= 3.12." -ForegroundColor Red
        Write-Host "To safely recover, delete the .venv folder manually and re-run setup:" -ForegroundColor Yellow
        Write-Host "    Remove-Item -Recurse -Force .venv" -ForegroundColor Yellow
        Write-Host "    .\scripts\setup.ps1" -ForegroundColor Yellow
        Write-Host "============================================================" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Creating virtual environment at .venv..." -ForegroundColor Cyan
    & "$python" -m venv (Join-Path $Root ".venv")
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $venvPython)) {
        Write-Error "Failed to create virtual environment."
        exit 1
    }
}

# Determine which lockfile to install
$lockFile = "requirements.lock"
if ($Dev -or (-not $ProdOnly -and (Test-Path -LiteralPath (Join-Path $Root "requirements-dev.lock")))) {
    $lockFile = "requirements-dev.lock"
}
$reqPath = Join-Path $Root $lockFile

Write-Host "Installing dependencies from $lockFile..." -ForegroundColor Cyan
& "$venvPython" -m pip install -r "$reqPath"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Dependency installation from $lockFile failed."
    exit 1
}

Write-Host "Installing NatalIA package in editable mode..." -ForegroundColor Cyan
& "$venvPython" -m pip install --no-deps -e "$Root"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Editable package installation failed."
    exit 1
}

Write-Host "Verifying core imports..." -ForegroundColor Cyan
& "$venvPython" -c "import natalia, fastapi, z3, sympy; print('Core imports OK! NatalIA version:', natalia.__version__)"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Import verification failed."
    exit 1
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host " NatalIA setup completed successfully!" -ForegroundColor Green
Write-Host " FastAPI serves the React production build (no Node at runtime)." -ForegroundColor Cyan
Write-Host " To start the verification workbench, run:" -ForegroundColor Cyan
Write-Host "     .\scripts\run.ps1" -ForegroundColor Cyan
Write-Host " Optional UI development: npm --prefix frontend run dev (proxy /api to :8000)" -ForegroundColor Gray
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
