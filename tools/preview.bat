@echo off
setlocal
cd /d "%~dp0.."
title Pra - Motions Dev Server (localhost:8080)
echo ===================================================
echo   Pra - Motions Local Preview ^& Live Testing
echo ===================================================
echo.

:: Ensure Python 3.14 is resolved and in PATH
if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" (
    set "PATH=%LOCALAPPDATA%\Programs\Python\Python314;%LOCALAPPDATA%\Programs\Python\Python314\Scripts;%LOCALAPPDATA%\Programs\Python\Launcher;%PATH%"
    set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
) else (
    set "PY_EXE=python"
)

echo [1/3] Clearing Python byte-cache and build cache...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
del /s /q /f *.pyc >nul 2>&1
echo       Cache cleared.
echo.

echo [2/3] Converting and optimizing images across pages/ to WebP...
"%PY_EXE%" tools\build.py --convert-webp
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] WebP conversion and build failed!
    pause
    exit /b %ERRORLEVEL%
)
echo.

echo [3/3] Launching dev server in this terminal window...
echo       NOTE: Closing this window will stop the server.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0preview.ps1"
endlocal
