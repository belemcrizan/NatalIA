# Diagnose interpreter, venv, imports and port 8000.

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $Root
Write-Host "cwd: $Root"
$py = Get-Command python -ErrorAction SilentlyContinue
if ($py) {
    Write-Host "python: $($py.Source)"
    & python -c "import sys; print('version', sys.version)"
}
$venvPython = Join-Path $Root ".venv\Scripts\python.exe"
if (Test-Path -LiteralPath $venvPython) {
    Write-Host "venv python: $venvPython"
    & $venvPython -c "import sys,natalia; print(sys.version); print('natalia', natalia.__version__)"
} else {
    Write-Host "venv: missing"
}
$tcp = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Where-Object { $_.State -eq "Listen" }
if ($tcp) { Write-Host "port 8000: in use by PID $($tcp.OwningProcess)" } else { Write-Host "port 8000: free" }
