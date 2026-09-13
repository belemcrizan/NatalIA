# Diagnose interpreter, venv, imports and port 8000.

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $Root
Write-Host "cwd: $Root"

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
        & $exe -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)"
        if ($LASTEXITCODE -eq 0) {
            return $exe, $ver
        }
        Write-Host "Ignoring $exe ($ver): NatalIA requires Python >= 3.12"
    }
    return $null, $null
}

$python, $version = Find-Python
if ($python) {
    Write-Host "Interpreter: $python"
    Write-Host "Version: $version"
} else {
    Write-Host "No compatible Python (>= 3.12) on PATH. Python 3.13.3 was tested on Windows; 3.12 remains the CI baseline."
}

$venvPython = Join-Path $Root ".venv\Scripts\python.exe"
if (Test-Path -LiteralPath $venvPython) {
    Write-Host "venv python: $venvPython"
    & $venvPython -c "import sys,natalia; print(sys.version); print('natalia', natalia.__version__)"
} else {
    Write-Host "venv: missing (run scripts/setup.ps1 first; this script will not activate a missing venv)"
}

$tcp = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Where-Object { $_.State -eq "Listen" }
if ($tcp) { Write-Host "port 8000: in use by PID $($tcp.OwningProcess)" } else { Write-Host "port 8000: free" }
try {
    $health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health/ready" -TimeoutSec 2
    Write-Host "API ready schema $($health.schema_version)"
} catch {
    Write-Host "API: not responding on 8000 (start scripts/run.ps1 to verify)"
}
