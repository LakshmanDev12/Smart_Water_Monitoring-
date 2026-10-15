@echo off
TITLE Smart Water Quality Monitoring - One-Click Setup
cls
echo ============================================================
echo   🌊 SMART WATER QUALITY MONITORING ^& DIGITAL TWIN SYSTEM
echo ============================================================
echo.
echo Launching automated setup PowerShell script...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File ".\setup.ps1"

echo.
echo Press any key to exit setup...
pause >nul
