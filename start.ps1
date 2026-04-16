# Webapp Start - Standardized SOTA (Auto-Repaired V3.2)
$WebPort = 10744
$BackendPort = 10745
$BridgePort = 10746  # Media Hub Bridge (WebSocket + Registry)

# Launch Federated Backends
Write-Host "Initializing Federated Media Fleet..." -ForegroundColor White
powershell -ExecutionPolicy Bypass -File "$PSScriptRoot\start_fleet.ps1"

# 1. Kill any process squatting on the ports
Write-Host "Checking for port squatters on $WebPort, $BackendPort, and $BridgePort..." -ForegroundColor Yellow
$pids = Get-NetTCPConnection -LocalPort $WebPort, $BackendPort, $BridgePort, 10701 -ErrorAction SilentlyContinue | Where-Object { $_.OwningProcess -gt 4 } | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($p in $pids) {
    Write-Host "Found squatter (PID: $p). Terminating..." -ForegroundColor Red
    try { Stop-Process -Id $p -Force -ErrorAction Stop } catch { Write-Host "Warning: Could not terminate PID $p." -ForegroundColor Gray }
}

# 2. Setup
Set-Location $PSScriptRoot

# 3. Start the Python backend (Background)
Write-Host "Starting Universal Actuator Backend on port $BackendPort ..." -ForegroundColor Cyan

# Use uv run for industrial-grade environment management
# We escape the $env:PYTHONPATH to ensure it's evaluated in the target shell
$backendCmd = "& { Set-Location '$PSScriptRoot'; `$env:PYTHONPATH = 'src'; uv run uvicorn universal_actuator_mcp.server:app --host 127.0.0.1 --port 10745 --log-level info }"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

# 3b. Start the Media Hub Bridge (Background)
Write-Host "Starting Media Hub Bridge on port $BridgePort ..." -ForegroundColor Magenta
$bridgeCmd = "& { Set-Location '$PSScriptRoot'; `$env:PYTHONPATH = 'src'; uv run media_hub_bridge.py }"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $bridgeCmd -WindowStyle Normal

# 4. Run Frontend (Next.js in webapp folder)
if (Test-Path "webapp") {
    Write-Host "Starting Next.js frontend on port $WebPort ..." -ForegroundColor Green
    Set-Location webapp
    if (-not (Test-Path "node_modules")) { 
        Write-Host "node_modules missing. Running npm install..." -ForegroundColor Gray
        npm install 
    }
    # Start frontend in a separate window to keep logs separate
    $frontendCmd = "& { Set-Location '$PSScriptRoot\webapp'; npm run dev -- --port $WebPort --host }"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd -WindowStyle Normal
} else {
    Write-Host "Error: 'webapp' folder not found. Cannot start frontend." -ForegroundColor Red
}

# 5. Open in browser
Write-Host "Waiting for services to warm up..." -ForegroundColor Gray
Start-Sleep -Seconds 3
Start-Process "http://127.0.0.1:$WebPort"

Write-Host "`nFederation Gateway deployment sequence initiated." -ForegroundColor Green
Write-Host "Check the separate console windows for logs." -ForegroundColor Gray
