@echo off
chcp 65001 >nul
cd /d "%~dp0"
title AI Chat
set "PY=%~dp0.venv\Scripts\python.exe"

if not exist "%PY%" (
  echo [X] Cannot find .venv\Scripts\python.exe
  echo     This file must stay in the project folder.
  pause
  exit /b 1
)

"%PY%" -c "import openai" >nul 2>&1
if errorlevel 1 (
  echo [X] openai is missing from the virtual environment.
  echo     Run run_check.bat to see details.
  pause
  exit /b 1
)

"%PY%" chat.py

if errorlevel 1 (
  echo.
  echo [X] Something went wrong. Copy the text above.
  pause
) else (
  echo.
  pause
)
