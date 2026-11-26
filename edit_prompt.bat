@echo off
cd /d "%~dp0"
title Edit Prompt
if not exist "prompt.txt" (
  echo [X] prompt.txt not found in this folder.
  pause
  exit /b 1
)
echo Opening prompt.txt in Notepad...
echo.
echo Change the text, save with Ctrl+S, close Notepad.
echo Then double-click run_chat.bat - the new identity takes effect.
echo.
start "" notepad.exe "%~dp0prompt.txt"
timeout /t 2 >nul
