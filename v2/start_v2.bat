@echo off
REM ============================================
REM Start v2 Workflow Engine
REM ============================================
echo Starting v2 Workflow Engine...
echo.

REM Check if Redis is running
redis-cli ping >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Redis is running
) else (
    echo [STARTING] Redis...
    start redis-server
    timeout /t 3
)

echo.
echo [STARTING] Celery Worker...
start cmd /k "cd /d %~dp0backend && celery -A celery_app worker --loglevel=info"
timeout /t 3

echo.
echo [STARTING] v2 Backend on port 8001...
start cmd /k "cd /d %~dp0backend && python -m uvicorn main:app --reload --port 8001"
timeout /t 3

echo.
echo ============================================
echo v2 Workflow Engine is starting...
echo.
echo Open browser: http://localhost:8001/
echo.
echo [Note] You need to build the frontend first:
echo   cd v2\frontend
echo   npm install
echo   npm run build
echo.
echo Press any key to open browser...
pause >nul
start "" "http://localhost:8001/"
