@echo off
echo Stopping Ocean Hazard Backend Application...
echo ============================================

echo Stopping Celery Worker...
taskkill /f /im celery.exe >nul 2>&1

echo Stopping Celery Beat...
taskkill /f /im celery.exe >nul 2>&1

echo Stopping FastAPI server (uvicorn)...
taskkill /f /im python.exe >nul 2>&1

echo Stopping Redis server...
taskkill /f /im redis-server.exe >nul 2>&1

echo Stopping Node.js processes (frontend)...
taskkill /f /im node.exe >nul 2>&1

echo ============================================
echo All services stopped successfully!
echo.
pause
