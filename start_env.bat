@echo off
chcp 65001 >nul
cd /d "%~dp0"
call .venv\Scripts\activate.bat
echo.
echo ============================================
echo  Environment activated. Python 3.10 ready.
echo.
echo  Tip: double-click run_chat.bat  - chat with AI
echo  Tip: double-click run_check.bat - check setup
echo  Type: deactivate to leave
echo ============================================
echo.
cmd /k
