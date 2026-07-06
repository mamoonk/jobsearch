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

:: Write PowerShell launcher script
set PS_SCRIPT=%TEMP%\jobsearch-launcher.ps1
> "%PS_SCRIPT%" (
    echo $root = Get-Location
    echo $bp = Start-Process -FilePath "uvicorn" -ArgumentList "app.main:app --reload --port 8000" -WorkingDirectory (Join-Path $root "backend") -PassThru
    echo $fp = Start-Process -FilePath "npm" -ArgumentList "run dev -- --port 3001" -WorkingDirectory (Join-Path $root "frontend") -PassThru
    echo Write-Host ""
    echo Write-Host "[DONE] Both services are running:"
    echo Write-Host "  Frontend : http://localhost:3001"
    echo Write-Host "  Backend  : http://localhost:8000"
    echo Write-Host "  Docs     : http://localhost:8000/docs"
    echo Write-Host ""
    echo Start-Sleep -Seconds 2
    echo Start-Process "http://localhost:3001"
    echo Write-Host "Press any key to stop both services..."
    echo $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    echo Write-Host "[STOP] Shutting down..."
    echo $bp.Kill()
    echo $fp.Kill()
    echo Write-Host "[DONE] Services stopped."
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%PS_SCRIPT%"
del "%PS_SCRIPT%" 2>nul
