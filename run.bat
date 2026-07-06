@echo off
cd /d "%~dp0"
title JobSearch AI

where docker >nul 2>&1
if %errorlevel% equ 0 (
    if not exist .env (
        if exist .env.example (
            copy .env.example .env >nul
        )
    )
    echo [INFO] Starting full stack with Docker...
    docker compose up -d --wait
    if %errorlevel% equ 0 (
        echo [DONE] Stack is running:
        echo   Frontend : http://localhost:3001
        echo   Backend  : http://localhost:8000
        echo   Docs     : http://localhost:8000/docs
        echo.
        echo Press any key to stop...
        pause >nul
        docker compose down
    ) else (
        echo [ERROR] Docker compose failed
        pause
    )
    exit /b
)

echo [INFO] Starting services directly (no Docker)...
echo.

:: Use PowerShell to launch both services and wait for exit
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
$root = Get-Location; ^
$bp = Start-Process -FilePath "uvicorn" -ArgumentList "app.main:app --reload --port 8000" -WorkingDirectory (Join-Path $root "backend") -PassThru; ^
$fp = Start-Process -FilePath "npm" -ArgumentList "run dev -- --port 3001" -WorkingDirectory (Join-Path $root "frontend") -PassThru; ^
Write-Host ""; ^
Write-Host "[DONE] Both services are running:"; ^
Write-Host "  Frontend : http://localhost:3001"; ^
Write-Host "  Backend  : http://localhost:8000"; ^
Write-Host "  Docs     : http://localhost:8000/docs"; ^
Write-Host ""; ^
Start-Sleep -Seconds 2; ^
Start-Process "http://localhost:3001"; ^
Write-Host "Press any key to stop both services..."; ^
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown"); ^
Write-Host "[STOP] Shutting down..."; ^
$bp.Kill(); ^
$fp.Kill(); ^
Write-Host "[DONE] Services stopped."
