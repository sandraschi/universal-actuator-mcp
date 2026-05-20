Param([switch]$Headless)

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

$env:FASTMCP_LOG_LEVEL = 'WARNING'
$env:FASTMCP_SHOW_SERVER_BANNER = 'false'
# universal-actuator-mcp Start - Standards-Compliant SOTA
Write-Host 'Starting universal-actuator-mcp...' -ForegroundColor Cyan

$BackendPort = 10745
if ($env:UA_SSE_PORT) {
    $BackendPort = [int]$env:UA_SSE_PORT
}
Write-Host "SSE port: $BackendPort (set UA_SSE_PORT to override)" -ForegroundColor DarkGray

try {
    $conns = Get-NetTCPConnection -LocalPort $BackendPort -ErrorAction SilentlyContinue
    if ($conns) {
        $conns | ForEach-Object {
            if ($_.OwningProcess -gt 4) {
                Write-Host "  Stopping PID $($_.OwningProcess) on port $BackendPort" -ForegroundColor Yellow
                Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
            }
        }
        Start-Sleep -Seconds 1
    }
} catch {
    Write-Host "  Port cleanup skipped: $_" -ForegroundColor DarkGray
}

# Package has no __main__.py; server entry is universal_actuator_mcp.server (see server.py if __name__ == "__main__")
$env:UA_SSE_PORT = "$BackendPort"
uv run python -m universal_actuator_mcp.server