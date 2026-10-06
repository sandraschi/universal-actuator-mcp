# Universal Actuator — Dependency Install + Smoke Test
# Run from: D:\Dev\repos\universal-actuator-mcp\
# Usage: powershell -ExecutionPolicy Bypass -File .\scripts\install_and_test.ps1

$py = "C:\Users\sandr\AppData\Local\Programs\Python\Python313\python.exe"
$repo = "D:\Dev\repos\universal-actuator-mcp"
$tmp = "D:\Dev\repos\temp"

Write-Host "=== Step 1: Install dependencies ===" -ForegroundColor Cyan
$out = "$tmp\pip_ua_$(Get-Date -Format 'HHmmss').txt"
Start-Process -FilePath $py -ArgumentList "-m pip install `"fastmcp>=3.0.0`" lancedb `"sentence-transformers>=3.4.0`" pyarrow psutil --break-system-packages -q" -Wait -RedirectStandardOutput $out -WindowStyle Hidden
Get-Content $out -ErrorAction SilentlyContinue
Write-Host "Pip done." -ForegroundColor Green

Write-Host "`n=== Step 2: Syntax check ===" -ForegroundColor Cyan
foreach ($f in @("backend\server.py", "backend\fleet.py", "backend\rag.py")) {
    $full = "$repo\$f"
    $chk = "$tmp\syntax_$(Get-Date -Format 'HHmmss').txt"
    Start-Process -FilePath $py -ArgumentList "-c `"import ast; ast.parse(open(r'$full').read()); print('OK: $f')`" -Wait -RedirectStandardOutput $chk -RedirectStandardError "$tmp\syntax_err.txt" -WindowStyle Hidden
    Start-Sleep 1
    Get-Content $chk,"$tmp\syntax_err.txt" -ErrorAction SilentlyContinue
}

Write-Host "`n=== Step 3: Import check (no server start) ===" -ForegroundColor Cyan
$importcheck = "$tmp\import_ua_$(Get-Date -Format 'HHmmss').txt"
$importscript = @"
import sys
sys.path.insert(0, r'$repo\backend')
sys.path.insert(0, r'$repo\src')
import rag
import fleet
print('rag.py import OK')
print('fleet.py import OK')
try:
    import lancedb
    print(f'lancedb {lancedb.__version__} OK')
except ImportError as e:
    print(f'lancedb MISSING: {e}')
try:
    from sentence_transformers import SentenceTransformer
    print('sentence-transformers OK')
except ImportError:
    print('sentence-transformers not installed (hash fallback will be used)')
"@
$importscript | Set-Content "$tmp\importcheck.py" -Encoding UTF8
Start-Process -FilePath $py -ArgumentList "$tmp\importcheck.py" -Wait -RedirectStandardOutput $importcheck -RedirectStandardError "$tmp\import_err.txt" -WindowStyle Hidden
Start-Sleep 2
Get-Content $importcheck,"$tmp\import_err.txt" -ErrorAction SilentlyContinue

Write-Host "`n=== Done. If all OK, start the server with: ===" -ForegroundColor Green
Write-Host "  cd $repo\backend" -ForegroundColor Yellow
Write-Host "  $py server.py" -ForegroundColor Yellow
Write-Host "  Server will listen on SSE port 10721" -ForegroundColor Yellow
