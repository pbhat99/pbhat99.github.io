@echo off
setlocal
cd /d "%~dp0"
echo ===================================================
echo   Pra - Motions Local Preview ^& Live Testing
echo ===================================================
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\preview.ps1"
endlocal
