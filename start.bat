@echo off
setlocal enabledelayedexpansion
title Sovereign AI Workbench Launcher

:: Set project root and python path for all 5 modules
set "PROJECT_ROOT=%~dp0"
set "PYTHONPATH=%PROJECT_ROOT%member-2-backend;%PROJECT_ROOT%member-3-ai;%PROJECT_ROOT%member-4-rag-multimodal;%PROJECT_ROOT%member-5-security-integration"

cls
echo ===============================================================================
echo                SOVEREIGN INDUSTRIAL AGENTIC AI WORKBENCH
echo                             (SIH26117)
echo ===============================================================================
echo.

if "%1"=="backend" goto start_backend
if "%1"=="frontend" goto start_frontend
if "%1"=="docker" goto start_docker
if "%1"=="verify" goto start_verify
if "%1"=="all" goto start_all

echo Select startup option:
echo   [1] Start Full Workbench (Backend FastAPI + Frontend Vite) [DEFAULT]
echo   [2] Start Backend Only (FastAPI - http://127.0.0.1:8000)
echo   [3] Start Frontend Only (Vite - http://localhost:3000)
echo   [4] Install Python Dependencies (pip install -r requirements.txt)
echo   [5] Start Docker Stack (Ollama + ChromaDB + Backend + Frontend)
echo   [6] Run Full System Verification
echo   [7] Exit
echo.

set /p choice="Enter choice [1-7] (Default: 1): "
if "%choice%"=="" set choice=1
if "%choice%"=="1" goto start_all
if "%choice%"=="2" goto start_backend
if "%choice%"=="3" goto start_frontend
if "%choice%"=="4" goto install_deps
if "%choice%"=="5" goto start_docker
if "%choice%"=="6" goto start_verify
if "%choice%"=="7" goto end


:start_all
echo.
echo ===============================================================================
echo Starting Sovereign AI Workbench...
echo ===============================================================================
echo.

:: Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not found in system PATH.
    pause
    exit /b 1
)

:: Check Node.js
where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js / NPM is not installed or not found in system PATH.
    pause
    exit /b 1
)

echo [1/2] Launching Backend FastAPI Service on http://127.0.0.1:8000 ...
start "Sovereign AI Backend (FastAPI)" cmd /k "title Sovereign AI Backend (Port 8000) && cd /d "%PROJECT_ROOT%" && set "PYTHONPATH=%PYTHONPATH%" && python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/2] Launching Frontend Vite Service on http://localhost:3000 ...
start "Sovereign AI Frontend (Vite)" cmd /k "title Sovereign AI Frontend (Port 3000) && cd /d "%PROJECT_ROOT%member-1-platform\frontend" && npm run dev"

echo.
echo ===============================================================================
echo  SUCCESS: Sovereign AI Workbench startup initiated!
echo ===============================================================================
echo  - Frontend UI:  http://localhost:3000
echo  - Backend API:  http://127.0.0.1:8000
echo  - OpenAPI Docs: http://127.0.0.1:8000/docs
echo ===============================================================================
echo.
echo Opening browser in 3 seconds...
timeout /t 3 >nul
start http://localhost:3000
goto end

:start_backend
echo.
echo Starting FastAPI Backend...
echo Backend API will be available at: http://127.0.0.1:8000
echo API Documentation available at: http://127.0.0.1:8000/docs
echo.
cd /d "%PROJECT_ROOT%"
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
goto end

:start_frontend
echo.
echo Starting Vite Frontend...
echo Frontend UI will be available at: http://localhost:3000
echo.
cd /d "%PROJECT_ROOT%member-1-platform\frontend"
npm run dev
goto end

:start_docker
echo.
echo Starting Docker Compose Stack...
echo.
cd /d "%PROJECT_ROOT%member-5-security-integration\docker"
docker-compose up --build
goto end

:start_verify
echo.
echo Running Full System Verification Check...
echo.
cd /d "%PROJECT_ROOT%"
set "PYTHONPATH=%PYTHONPATH%"
python "%PROJECT_ROOT%member-5-security-integration\integration\run_all_modules_check.py"
pause
:install_deps
echo.
echo Installing Python dependencies from requirements.txt...
echo.
cd /d "%PROJECT_ROOT%"
pip install -r requirements.txt
echo.
echo [Frontend] Installing Node.js packages...
cd /d "%PROJECT_ROOT%member-1-platform\frontend"
npm install
echo.
echo All dependencies installed successfully!
pause
goto end

:end

