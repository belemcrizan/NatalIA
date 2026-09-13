# NatalIA startup script for Windows PowerShell
# Starts NatalIA on loopback using the project virtual environment.

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [int]$Port = 8000,

    [Parameter()]
    [string]$HostAddress = "127.0.0.1",

    [Parameter()]
    [int]$Workers = 1
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

$venvPython = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $venvPython)) {
    Write-Error "Virtual environment not found at: $venvPython`nPlease run .\scripts\setup.ps1 first."
    exit 1
}

if ($Workers -ne 1) {
    Write-Error "This local release requires -Workers 1. Multiple uvicorn processes are not coordinated for job recovery."
    exit 1
}

# Check if requested port is available; do not label invalid hosts as occupied.
$listener = $null
try {
    $ip = [System.Net.IPAddress]::Parse($HostAddress)
    $listener = [System.Net.Sockets.TcpListener]::new($ip, $Port)
    $listener.Start()
    $listener.Stop()
} catch [System.FormatException] {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Yellow
    Write-Host "Host '$HostAddress' is not a valid IP address." -ForegroundColor Yellow
    Write-Host "This is not an occupied-port error. Use 127.0.0.1 for local loopback." -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Yellow
    Write-Host ""
    exit 1
} catch {
    $conn = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Where-Object { $_.State -eq "Listen" }
    if (-not $conn) {
        Write-Host ""
        Write-Host "============================================================" -ForegroundColor Yellow
        Write-Host "Cannot bind ${HostAddress}:${Port}: $($_.Exception.Message)" -ForegroundColor Yellow
        Write-Host "This is not classified as an occupied port." -ForegroundColor Cyan
        Write-Host "============================================================" -ForegroundColor Yellow
        Write-Host ""
        exit 1
    }
    $pidInfo = " (PID: $($conn.OwningProcess))"
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Yellow
    Write-Host "Port $Port is already in use$pidInfo." -ForegroundColor Yellow
    Write-Host "To run NatalIA on a different port, specify -Port:" -ForegroundColor Cyan
    Write-Host "    .\scripts\run.ps1 -Port $($Port + 1)" -ForegroundColor Cyan
    Write-Host "Or terminate the process using port $Port and retry." -ForegroundColor Gray
    Write-Host "============================================================" -ForegroundColor Yellow
    Write-Host ""
    exit 1
} finally {
    if ($listener) {
        try { $listener.Stop() } catch { }
    }
}

$env:PYTHONUTF8 = "1"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host " NatalIA Verification Workbench" -ForegroundColor Green
Write-Host " NatalIA is starting. A printed URL is not a readiness probe." -ForegroundColor Cyan
Write-Host " Open http://${HostAddress}:${Port} after GET /health/ready returns 200." -ForegroundColor Cyan
Write-Host " Readiness:     http://${HostAddress}:${Port}/health/ready" -ForegroundColor Cyan
Write-Host " Project Root:  $Root" -ForegroundColor Gray
Write-Host " To stop the server, press Ctrl + C in this terminal window." -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

& "$venvPython" -m uvicorn natalia.api:create_app --factory --host $HostAddress --port $Port --workers $Workers
exit $LASTEXITCODE
