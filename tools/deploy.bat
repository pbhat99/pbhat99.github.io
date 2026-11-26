@echo off
setlocal enabledelayedexpansion

echo ======================================================================
echo             Pra - Motions: Build and Deploy to GitHub
echo ======================================================================
echo.

cd /d "%~dp0.."

:: 1. Verify Prerequisites & Resolve Python
if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" (
    set "PATH=%LOCALAPPDATA%\Programs\Python\Python314;%LOCALAPPDATA%\Programs\Python\Python314\Scripts;%LOCALAPPDATA%\Programs\Python\Launcher;%PATH%"
    set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
) else (
    set "PY_EXE=python"
)

"%PY_EXE%" --version >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not working!
    pause
    exit /b 1
)

where git >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Git is not installed or not in PATH!
    pause
    exit /b 1
)

:: 2. Run Site-Wide WebP Conversion, Thumb Generation, Asset Check, and Build
echo [1/5] Running WebP optimization, thumbs sync, asset audit, and rebuilding all pages...
"%PY_EXE%" tools\build.py --convert-webp --thumbs --check-assets --prompt-resize
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Build failed! Please review the error above.
    pause
    exit /b %ERRORLEVEL%
)

:: 3. Run Site Verification
echo.
echo [2/5] Verifying site links, CSS, JS, and image assets...
"%PY_EXE%" tools/verify_site.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Site verification failed!
    pause
    exit /b %ERRORLEVEL%
)

:: 4. Stage & Commit Changes on dev
echo.
echo [3/5] Staging and committing changes to dev...
git add -A

set "COMMIT_MSG=%~1"
if "!COMMIT_MSG!"=="" (
    set "COMMIT_MSG=deploy: site update, assets, and WebP optimization"
)

git diff --cached --quiet
if %ERRORLEVEL% neq 0 (
    git commit -m "!COMMIT_MSG!"
    echo Committed: "!COMMIT_MSG!"
) else (
    echo No new changes to commit on dev.
)

:: 6. Push dev branch to remote
echo.
echo [4/5] Pushing dev branch to origin/dev...
git push origin dev
if %ERRORLEVEL% neq 0 (
    echo.
    echo [WARNING] Failed to push dev branch to origin. Check internet/git credentials.
)

:: 7. Replace main branch ENTIRELY with current dev branch
echo.
echo [5/5] Mirroring dev branch to main (replaces main entirely on GitHub)...
:: Update local main branch pointer to match dev exactly
git branch -f main dev

:: Force-push dev directly into origin/main so main is an exact 1:1 mirror of dev (all updates, deletions, modifications)
git push origin dev:main --force
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Failed to push to origin/main!
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo  SUCCESS: Site successfully built, optimized, committed, and deployed!
echo  main branch on GitHub is now an exact 1:1 mirror of dev.
echo  GitHub Pages is deploying your latest changes.
echo ======================================================================
echo.
pause
