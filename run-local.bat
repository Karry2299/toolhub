@echo off
cd /d "%~dp0"

echo ========================================
echo  ToolHub local runner
echo ========================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run-local.ps1"

echo.
echo Server stopped. Press any key to close this window.
pause >nul
