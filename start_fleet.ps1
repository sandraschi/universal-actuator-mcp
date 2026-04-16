# start_fleet.ps1 - Automated Backend Orchestrator for Media Hub
# Authoritative for Calibre, Plex, Immich, DocsOps, and Knowledge nodes.

$ErrorActionPreference = "Continue"

Write-Host "--- Media Hub Fleet Orchestration Sequence ---" -ForegroundColor Yellow

# 1. Calibre MCP (Backend: 10720)
Write-Host "Reclaiming Calibre MCP (10720)..." -ForegroundColor Cyan
$calibrePath = "D:\Dev\repos\calibre-mcp\webapp"
if (Test-Path "$calibrePath\start.ps1") {
    Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy Bypass", "-File", "start.ps1", "-Automated" -WorkingDirectory $calibrePath -WindowStyle Normal
}

# 2. Plex MCP (Backend: 10740)
Write-Host "Reclaiming Plex MCP (10740)..." -ForegroundColor Cyan
$plexPath = "D:\Dev\repos\plex-mcp"
if (Test-Path "$plexPath\start.ps1") {
    Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy Bypass", "-File", "start.ps1", "-Automated" -WorkingDirectory $plexPath -WindowStyle Normal
}

# 3. Immich MCP (Backend: 10839)
Write-Host "Reclaiming Immich MCP (10839)..." -ForegroundColor Cyan
$immichPath = "D:\Dev\repos\immich-mcp\web_sota"
if (Test-Path "$immichPath\start.ps1") {
    Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy Bypass", "-File", "start.ps1", "-Automated" -WorkingDirectory $immichPath -WindowStyle Normal
}

# 4. DocsOps (Backend: 10795)
Write-Host "Reclaiming DocsOps (10795)..." -ForegroundColor Cyan
$docsPath = "D:\Dev\repos\mcp-central-docs\web_sota"
if (Test-Path "$docsPath\start.ps1") {
    Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy Bypass", "-File", "start.ps1", "-Automated" -WorkingDirectory $docsPath -WindowStyle Normal
}

# 5. Knowledge/Advanced Memory (Backend: 10732)
Write-Host "Reclaiming Knowledge Hub (10732)..." -ForegroundColor Cyan
$memoryPath = "D:\Dev\repos\advanced-memory-mcp"
if (Test-Path "$memoryPath\start.ps1") {
    Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy Bypass", "-File", "start.ps1" -WorkingDirectory $memoryPath -WindowStyle Normal
}

Write-Host "`nFleet deployment sequence complete. Waiting for nodes to stabilize..." -ForegroundColor Green
Start-Sleep -Seconds 5
