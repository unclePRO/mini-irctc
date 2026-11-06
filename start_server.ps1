# PowerShell helper to start Railway Reservation System
$pythonPath = "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python313\python.exe"

if (-not (Test-Path $pythonPath)) {
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd) {
        $pythonPath = $pythonCmd.Source
    } else {
        $pythonPath = "python"
    }
}

Write-Host "Using Python runtime at: $pythonPath" -ForegroundColor Cyan
Write-Host "Pre-initializing database..." -ForegroundColor Yellow
& $pythonPath db.py init

Write-Host "`nStarting server on http://127.0.0.1:5000 ..." -ForegroundColor Green
Write-Host "Open http://127.0.0.1:5000 in your web browser.`n" -ForegroundColor Green

& $pythonPath app.py
