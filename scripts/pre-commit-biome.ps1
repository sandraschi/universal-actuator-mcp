#Requires -Version 5.1
<#
.SYNOPSIS
  Fleet Biome gate for webapp/ (pre-commit local hook).
  Runs `biome ci` on each known web root; fails the commit on violations.
#>
$ErrorActionPreference = 'Continue'
$repoRoot = Split-Path -Parent $PSScriptRoot
$webRoots = @('webapp', 'web_sota', 'webapp/frontend', 'web') | ForEach-Object {
  Join-Path $repoRoot $_
} | Where-Object { Test-Path (Join-Path $_ 'package.json') }

if (-not $webRoots) { Write-Host 'biome: no web root, skipping.'; exit 0 }

$failed = $false
foreach ($root in $webRoots) {
  Push-Location $root
  try {
    if (Test-Path 'bun.lock') {
      $out = & "$env:USERPROFILE\.bun\bin\bun.exe" run biome:ci 2>&1
    } else {
      $out = & npm run biome:ci 2>&1
    }
    $code = $LASTEXITCODE
    $out | Write-Host
    if ($code -ne 0) { $failed = $true }
  } finally { Pop-Location }
}
if ($failed) { Write-Host 'biome: violations found.' -ForegroundColor Red; exit 1 }
Write-Host 'biome: clean.' -ForegroundColor Green
