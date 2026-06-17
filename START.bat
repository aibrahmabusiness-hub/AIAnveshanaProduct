@echo off
echo Starting Agent AI Workflow Platform (V1)...
echo.

echo [1/1] Starting FastAPI Backend...
cd backend
start "Backend" cmd /k "python -m uvicorn main:app --reload --port 8000"
timeout /t 3

echo.
echo ============================================
echo Agent AI is starting...
echo Open browser: http://localhost:8000/
echo ============================================
echo.
echo Press Ctrl+C in any window to stop services
pause
