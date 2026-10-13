#Requires -Version 5.1
# Shim (assfix 2026-10-13): the canonical pack pipeline lives in mcp-central-docs
# so fixes apply fleet-wide. The previous 272-line local pipeline is retired
# (backup: mcpb/pack.ps1.<timestamp>.bak, gitignored).
$central = Join-Path (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)) 'mcp-central-docs\scripts\fleet-mcpb-pack.ps1'
if (-not (Test-Path $central)) { throw "Canonical pack script missing: $central (clone mcp-central-docs next to this repo)" }
& $central -RepoRoot (Split-Path -Parent $PSScriptRoot)
exit $LASTEXITCODE
