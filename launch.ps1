$root = Split-Path -Parent $MyInvocation.MyCommand.Path

$bp = Start-Process -FilePath "uvicorn" -ArgumentList "app.main:app --reload --port 8000" `
    -WorkingDirectory (Join-Path $root "backend") -PassThru

$fp = Start-Process -FilePath "npm" -ArgumentList "run dev -- --port 3001" `
    -WorkingDirectory (Join-Path $root "frontend") -PassThru

Write-Host ""
Write-Host "[DONE] Both services are running:"
Write-Host "  Frontend : http://localhost:3001"
Write-Host "  Backend  : http://localhost:8000"
Write-Host "  Docs     : http://localhost:8000/docs"
Write-Host ""

Start-Sleep -Seconds 2
Start-Process "http://localhost:3001"

Write-Host "Press any key to stop both services..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host "[STOP] Shutting down..."
$bp.Kill()
$fp.Kill()
Write-Host "[DONE] Services stopped."
