set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]

# ── Dashboard ─────────────────────────────────────────────────────────────────

# Display the SOTA Industrial Dashboard
default:
    @$lines = Get-Content '{{justfile()}}'; \
    Write-Host ' [SOTA] Industrial Operations Dashboard v1.3.2' -ForegroundColor White -BackgroundColor Cyan; \
    Write-Host '' ; \
    $currentCategory = ''; \
    foreach ($line in $lines) { \
        if ($line -match '^# ── ([^─]+) ─') { \
            $currentCategory = $matches[1].Trim(); \
            Write-Host "`n  $currentCategory" -ForegroundColor Cyan; \
            Write-Host ('  ' + ('─' * 45)) -ForegroundColor Gray; \
        } elseif ($line -match '^# ([^─].+)') { \
            $desc = $matches[1].Trim(); \
            $idx = [array]::IndexOf($lines, $line); \
            if ($idx -lt $lines.Count - 1) { \
                $nextLine = $lines[$idx + 1]; \
                if ($nextLine -match '^([a-z0-9-]+):') { \
                    $recipe = $matches[1]; \
                    $pad = ' ' * [math]::Max(2, (18 - $recipe.Length)); \
                    Write-Host "    $recipe" -ForegroundColor White -NoNewline; \
                    Write-Host "$pad$desc" -ForegroundColor Gray; \
                } \
            } \
        } \
    } \
    Write-Host "`n  [System State: PROD/HARDENED]" -ForegroundColor DarkGray; \
    Write-Host ''

# ── Quality ───────────────────────────────────────────────────────────────────

# Execute Ruff SOTA v13.1 linting
lint:
    Set-Location '{{justfile_directory()}}'
    uv run ruff check .
    Set-Location '{{justfile_directory()}}\webapp'
    npx @biomejs/biome ci .

# Execute Ruff SOTA v13.1 fix and formatting
fix:
    Set-Location '{{justfile_directory()}}'
    uv run ruff check . --fix --unsafe-fixes
    uv run ruff format .
    Set-Location '{{justfile_directory()}}\webapp'
    npx @biomejs/biome check --write .

# ── Hardening ─────────────────────────────────────────────────────────────────

# Execute Bandit security audit
check-sec:
    Set-Location '{{justfile_directory()}}'
    uv run bandit -r src/

# Execute safety audit of dependencies
audit-deps:
    Set-Location '{{justfile_directory()}}'
    uv run safety check

# ── Operations ─────────────────────────────────────────────────────────────────

# Start the Universal Actuator Hub (SSE)
run:
    Set-Location '{{justfile_directory()}}'
    uv run python -m universal_actuator_mcp.server

# Start the Hub in Dev Mode (Reload)
dev:
    Set-Location '{{justfile_directory()}}'
    uv run uvicorn universal_actuator_mcp.server:app --reload --port 10745

# Trigger industrial RAG ingestion via CLI
ingest:
    Set-Location '{{justfile_directory()}}'
    Invoke-RestMethod -Method POST -Uri http://127.0.0.1:10745/library/ingest | ConvertTo-Json

# Check health of the Hub
status:
    Set-Location '{{justfile_directory()}}'
    Invoke-RestMethod -Method GET -Uri http://127.0.0.1:10745/api/v1/health | ConvertTo-Json

# Check Fleet Telemetry
fleet:
    Set-Location '{{justfile_directory()}}'
    Invoke-RestMethod -Method GET -Uri http://127.0.0.1:10745/telemetry | ConvertTo-Json

# Automated fleet autostart (headless/background)
autostart:
    Set-Location '{{justfile_directory()}}'
    uv run python -c "from universal_actuator_mcp.fleet import FleetManager; import asyncio; fm=FleetManager(); asyncio.run(fm.ensure_all())"

# Run all tests
test:
    Set-Location '{{justfile_directory()}}'
    uv run pytest tests/ -v

# Run tests with coverage
test-cov:
    Set-Location '{{justfile_directory()}}'
    uv run pytest tests/ --cov=src/universal_actuator_mcp --cov-report=term-missing
