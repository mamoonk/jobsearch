@echo off
cd /d "%~dp0"
title JobSearch AI

:: ─── Colors ───────────────────────────────────────────
set "ESC="
for /f "delims=#" %%a in ('"prompt #$E# & for %%b in (1) do rem"') do set "ESC=%%a"
set "GREEN=%ESC%[32m"
set "YELLOW=%ESC%[33m"
set "RED=%ESC%[31m"
set "CYAN=%ESC%[36m"
set "RESET=%ESC%[0m"

echo %CYAN%╔══════════════════════════════════════════╗
echo ║         JobSearch AI - Launcher             ║
echo ╚══════════════════════════════════════════╝%RESET%
echo.

:: ─── Detect Docker ───────────────────────────────
where docker >nul 2>&1
if %errorlevel% equ 0 (
    echo %GREEN%[INFO] Docker detected - launching full stack%RESET%
    echo.
    if not exist .env (
        if exist .env.example (
            echo %YELLOW%[WARN] No .env file found. Copying from .env.example...%RESET%
            copy .env.example .env >nul
            echo %RED%[!!] Edit .env with your API keys before using AI features%RESET%
        ) else (
            echo %RED%[ERROR] No .env or .env.example found%RESET%
            pause
            exit /b 1
        )
    )
    docker compose up -d --wait 2>&1
    if %errorlevel% equ 0 (
        echo.
        echo %GREEN%[DONE] Stack is running:%RESET%
        echo   Frontend : http://localhost:3000
        echo   Backend  : http://localhost:8000
        echo   Docs     : http://localhost:8000/docs
        echo.
        echo %YELLOW%Press any key to stop...%RESET%
        pause >nul
        docker compose down
    ) else (
        echo %RED%[ERROR] Docker compose failed. Check logs with: docker compose logs%RESET%
        pause
    )
    exit /b
)

echo %YELLOW%[INFO] Docker not found - starting services directly%RESET%
echo %YELLOW%[INFO] PostgreSQL + Redis required for full functionality%RESET%
echo.

:: ─── Check .env ──────────────────────────────────
if not exist backend\.env (
    if exist .env.example (
        copy .env.example backend\.env >nul 2>&1
    )
)

:: ─── Start Backend ───────────────────────────────
echo %CYAN%[1/2] Starting backend on http://localhost:8000 ...%RESET%
start "JobSearch-Backend" /D "backend" uvicorn app.main:app --reload --port 8000

:: ─── Start Frontend ──────────────────────────────
echo %CYAN%[2/2] Starting frontend on http://localhost:3000 ...%RESET%
start "JobSearch-Frontend" /D "frontend" npm run dev

echo.
echo %GREEN%[DONE] Both services are starting:%RESET%
echo   Frontend : %CYAN%http://localhost:3000%RESET%
echo   Backend  : %CYAN%http://localhost:8000%RESET%
echo   Docs     : %CYAN%http://localhost:8000/docs%RESET%
echo.
echo %YELLOW%Close the terminal windows to stop the services.%RESET%
echo.
timeout /t 3 >nul
start http://localhost:3000
