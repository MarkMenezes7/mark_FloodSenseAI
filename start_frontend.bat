@echo off
echo ========================================
echo   FloodSenseAI - Starting Frontend
echo ========================================
cd /d %~dp0frontend
npm run dev
pause
