#Requires -Version 5.1
# Pre-commit guard: never commit timestamped .bak safety copies.
$bad = git diff --cached --name-only | Where-Object { $_ -match '\.bak($|\.)' }
if ($bad) {
  Write-Host ('Blocked .bak files: ' + ($bad -join ', ')) -ForegroundColor Red
  exit 1
}
exit 0
