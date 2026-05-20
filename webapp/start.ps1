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

$WebPort = 10744
$BackendPort = 10745
$ProjectRoot = Split-Path -Parent $PSScriptRoot

# ---------------------------------------------------------------------------
# Helper: check if a port is accepting connections
# ---------------------------------------------------------------------------
function Test-Port($port) {
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $tcp.Connect("127.0.0.1", $port)
        $tcp.Close()
        return $true
    } catch { return $false }
}

function Wait-Port($port, $secs, $label) {
    Write-Host "  Waiting for $label (:$port)..." -ForegroundColor DarkGray -NoNewline
    for ($i = 0; $i -lt $secs; $i++) {
        if (Test-Port $port) { Write-Host " ready." -ForegroundColor Green; return $true }
        Start-Sleep -Seconds 1
        Write-Host "." -NoNewline
    }
    Write-Host " TIMEOUT." -ForegroundColor Red
    return $false
}

# ---------------------------------------------------------------------------
# 1. Dependency: calibre-mcp backend (:10720)
# ---------------------------------------------------------------------------
Write-Host "Checking calibre-mcp (:10720)..." -ForegroundColor Yellow
if (-not (Test-Port 10720)) {
    Write-Host "  calibre-mcp offline - starting headless..." -ForegroundColor Cyan
    $calibreBackendDir = "D:\Dev\repos\calibre-mcp\webapp\backend"
    $calibreProjectRoot = "D:\Dev\repos\calibre-mcp"
    $cmd = "Set-Location '$calibreBackendDir'; uv run --project '$calibreProjectRoot' uvicorn app.main:app --host 127.0.0.1 --port 10720 --log-level warning"
    Start-Process powershell -ArgumentList "-NoProfile", "-WindowStyle", "Hidden", "-Command", $cmd
    $calibreOk = Wait-Port 10720 20 "calibre-mcp"
} else {
    Write-Host "  calibre-mcp already running." -ForegroundColor Green
    $calibreOk = $true
}

# ---------------------------------------------------------------------------
# 2. Dependency: plex-mcp backend (:10740)
# ---------------------------------------------------------------------------
Write-Host "Checking plex-mcp (:10740)..." -ForegroundColor Yellow
if (-not (Test-Port 10740)) {
    Write-Host "  plex-mcp offline - starting headless..." -ForegroundColor Cyan
    $plexBackendDir = "D:\Dev\repos\plex-mcp\webapp\backend"
    $plexProjectRoot = "D:\Dev\repos\plex-mcp"
    $cmd = "Set-Location '$plexBackendDir'; `$env:PYTHONPATH = '$plexProjectRoot\src;$plexBackendDir'; & '$plexProjectRoot\.venv\Scripts\python.exe' -m uvicorn app.main:app --host 127.0.0.1 --port 10740 --log-level warning"
    Start-Process powershell -ArgumentList "-NoProfile", "-WindowStyle", "Hidden", "-Command", $cmd
    $plexOk = Wait-Port 10740 20 "plex-mcp"
} else {
    Write-Host "  plex-mcp already running." -ForegroundColor Green
    $plexOk = $true
}

if (-not $calibreOk) { Write-Host "WARNING: calibre-mcp failed to start. Library will show partial results." -ForegroundColor Red }
if (-not $plexOk)    { Write-Host "WARNING: plex-mcp failed to start. Library will show partial results." -ForegroundColor Red }

# ---------------------------------------------------------------------------
# 3. Kill port squatters on actuator ports
# ---------------------------------------------------------------------------
Write-Host "Checking for port squatters on $WebPort and $BackendPort..." -ForegroundColor Yellow
$pids = Get-NetTCPConnection -LocalPort $WebPort, $BackendPort -ErrorAction SilentlyContinue |
    Where-Object { $_.OwningProcess -gt 4 } | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($p in $pids) {
    Write-Host "Found squatter (PID: $p). Terminating..." -ForegroundColor Red
    try { Stop-Process -Id $p -Force -ErrorAction Stop } catch { Write-Host "Warning: Could not terminate PID $p." -ForegroundColor Gray }
}

# ---------------------------------------------------------------------------
# 4. npm install if needed
# ---------------------------------------------------------------------------
Set-Location $PSScriptRoot
if (-not (Test-Path "node_modules")) { npm install }

# ---------------------------------------------------------------------------
# 5. Start actuator backend (pass dependency status as env vars for /health)
# ---------------------------------------------------------------------------
Write-Host "Starting Python backend on port $BackendPort ..." -ForegroundColor Cyan
$backendCmd = "& { Set-Location '$PSScriptRoot\..'; `$env:PYTHONPATH = 'src'; `$env:UA_CALIBRE_OK = '$calibreOk'; `$env:UA_PLEX_OK = '$plexOk'; uv run uvicorn universal_actuator_mcp.server:mcp.http_app --factory --host 127.0.0.1 --port $BackendPort --log-level warning }"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

# ---------------------------------------------------------------------------
# 6. Vite + browser autoopen
# ---------------------------------------------------------------------------
Write-Host "Starting Vite frontend on port $WebPort ..." -ForegroundColor Green

Start-Job -ScriptBlock {
    param($port)
    $url = "http://127.0.0.1:$port"
    for ($i = 0; $i -lt 30; $i++) {
        Start-Sleep -Seconds 1
        try {
            $r = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 1 -ErrorAction SilentlyContinue
            if ($r.StatusCode -lt 500) { Start-Process $url; break }
        } catch { }
    }
} -ArgumentList $WebPort | Out-Null

npm run dev -- --port $WebPort --host
