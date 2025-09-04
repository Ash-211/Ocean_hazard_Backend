@echo off
echo Starting Ocean Hazard Backend Application...
echo ============================================

REM Check if Redis is running, if not start it
echo Checking Redis...
redis-cli ping >nul 2>&1
if %errorlevel% neq 0 (
    echo Starting Redis server...
    start /B redis-server
    timeout /t 3 /nobreak >nul
) else (
    echo Redis is already running.
)

echo Starting Celery Worker...
start /B celery -A celery_app worker --loglevel=info

echo Starting Celery Beat...
start /B celery -A celery_app beat --loglevel=info

echo Starting FastAPI server...
start /B uvicorn main:app --reload --host 0.0.0.0 --port 8000

echo Waiting for services to start...
timeout /t 5 /nobreak >nul

echo Starting Frontend Development Server...
cd frontend
start cmd /k "npm run dev"

cd ..
echo ============================================
echo All services started successfully!
echo.
echo Frontend: http://localhost:5173 (Vite dev server)
echo Backend API: http://localhost:8000
echo Redis: localhost:6379
echo.
echo Press any key to close this window...
pause >nul
