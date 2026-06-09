@echo off
echo ========================================
echo   FloodSenseAI - Starting Backend
echo ========================================
cd /d %~dp0backend
python run.py
pause
