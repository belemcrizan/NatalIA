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
Write-Host "Setup complete. Run scripts/run.ps1"
