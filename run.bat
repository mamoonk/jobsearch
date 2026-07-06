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
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0launch.ps1"
