@echo off
chcp 65001 >nul
cd /d "%~dp0"
title SQL Practice 1
set "PY=%~dp0.venv\Scripts\python.exe"

if not exist "%PY%" (
  echo [X] Cannot find .venv\Scripts\python.exe
  echo     This file must stay in the project folder.
  pause
  exit /b 1
)

echo.
echo   Press ENTER  = continue from where you stopped last time
echo   Type 1       = start over from question 1
echo   Type 5       = jump to question 5
echo.
set "START="
set /p "START=Start from [1-5]: "

echo.
"%PY%" sql_practice.py %START%

echo.
pause
