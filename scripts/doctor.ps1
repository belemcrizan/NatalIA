# NatalIA system diagnostics — inspect runtime, environment, dependencies, and port.

[CmdletBinding()]
param(
    [Parameter()]
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
$OutputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

# Resolve project root relative to script location
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$Root = Split-Path -Parent $scriptDir

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

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " NatalIA Diagnostic Tool" -ForegroundColor Cyan
Write-Host " Working Directory: $Root" -ForegroundColor Gray
Write-Host "============================================================" -ForegroundColor Cyan

$venvPython = Join-Path $Root ".venv\Scripts\python.exe"
if (Test-Path -LiteralPath $venvPython) {
    Write-Host "[INFO] Using virtual environment: $venvPython" -ForegroundColor Green
    & "$venvPython" -m natalia doctor --port $Port
} else {
    Write-Host "[WARN] Virtual environment (.venv) is not installed." -ForegroundColor Yellow
    Write-Host "Please run .\scripts\setup.ps1 to create the environment." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Checking local HTTP API on port $Port..." -ForegroundColor Gray
try {
    $health = Invoke-RestMethod -Uri "http://127.0.0.1:${Port}/health/ready" -TimeoutSec 2
    Write-Host "[OK] API server is responding: ready (schema version $($health.schema_version))" -ForegroundColor Green
} catch {
    Write-Host "[INFO] API server is not running on port $Port (start with .\scripts\run.ps1)" -ForegroundColor Gray
}

Write-Host "============================================================" -ForegroundColor Cyan
