
# Fast port helpers (scripts/PortHelpers.ps1)
$__PortHelpers = Join-Path $PSScriptRoot 'scripts\PortHelpers.ps1'
if (Test-Path -LiteralPath $__PortHelpers) { . $__PortHelpers }
Param([switch]$Headless)  # --- SOTA Headless Standard --- if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {     Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden     exit } $WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' } # ------------------------------  $env:FASTMCP_LOG_LEVEL = 'WARNING' $env:FASTMCP_SHOW_SERVER_BANNER = 'false' # universal-actuator-mcp Start - Standards-Compliant SOTA Write-Host 'Starting universal-actuator-mcp...' -ForegroundColor Cyan  $BackendPort = 10745 if ($env:UA_SSE_PORT) {     $BackendPort = [int]$env:UA_SSE_PORT } Write-Host "SSE port: $BackendPort (set UA_SSE_PORT to override)" -ForegroundColor DarkGray  try {     $procIds = Get-PortListenerPidsFast -Port $port
