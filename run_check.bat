@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Environment Check

if not exist ".venv\Scripts\python.exe" (
  echo [X] .venv not found.
  pause
  exit /b 1
)

call ".venv\Scripts\activate.bat"
python check_env.py
echo.
python test_api.py
echo.
echo ============================================
echo  Done. Press any key to close.
echo ============================================
pause >nul
