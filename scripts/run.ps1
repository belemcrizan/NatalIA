# Start NatalIA on loopback. Uses the venv interpreter directly.

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
$OutputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$Root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $Root
$venvPython = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $venvPython)) {
    throw "Missing .venv. Run scripts/setup.ps1 first."
}
$listener = [System.Net.Sockets.TcpListener]::new([Net.IPAddress]::Loopback, 8000)
try {
    $listener.Start()
    $listener.Stop()
} catch {
    throw "Port 8000 is already in use. Stop the other process or choose another port."
}
Write-Host "Open http://127.0.0.1:8000"
Write-Host "Stop with Ctrl+C"
$env:PYTHONUTF8 = "1"
& $venvPython -m uvicorn natalia.api:create_app --factory --host 127.0.0.1 --port 8000 --workers 1
