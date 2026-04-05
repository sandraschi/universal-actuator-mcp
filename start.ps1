# Webapp Start - Standardized SOTA (Auto-Repaired V3.1)
$WebPort = 10744
$BackendPort = 10745


# 1. Kill any process squatting on the ports
Write-Host "Checking for port squatters on $WebPort and $BackendPort..." -ForegroundColor Yellow
$pids = Get-NetTCPConnection -LocalPort $WebPort, $BackendPort -ErrorAction SilentlyContinue | Where-Object { $_.OwningProcess -gt 4 } | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($p in $pids) {
    Write-Host "Found squatter (PID: $p). Terminating..." -ForegroundColor Red
    try { Stop-Process -Id $p -Force -ErrorAction Stop } catch { Write-Host "Warning: Could not terminate PID $p." -ForegroundColor Gray }
}

# 2. Setup
Set-Location $PSScriptRoot

# 3. Start the Python backend (Background)
Write-Host "Starting Universal Actuator Backend on port $BackendPort ..." -ForegroundColor Cyan

# Use the migrated package: universal_actuator_mcp.server
$backendCmd = @'
$env:PYTHONPATH = "src"
uvicorn universal_actuator_mcp.server:mcp.http_app --factory --host 127.0.0.1 --port 10745 --log-level info
'@

Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PSScriptRoot'; $backendCmd" -WindowStyle Normal

# 4. Run Frontend (Next.js in webapp folder)
if (Test-Path "webapp") {
    Write-Host "Starting Next.js frontend on port $WebPort ..." -ForegroundColor Green
    Set-Location webapp
    if (-not (Test-Path "node_modules")) { npm install }
    npm run dev -- --port $WebPort --host
} else {
    Write-Host "Error: 'webapp' folder not found. Cannot start frontend." -ForegroundColor Red
}


