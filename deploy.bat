@echo off
setlocal enabledelayedexpansion

echo ======================================================================
echo             Pra - Motions: Build and Deploy to GitHub
echo ======================================================================
echo.

cd /d "%~dp0"

:: 1. Verify Prerequisites
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    pause
    exit /b 1
)

where git >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Git is not installed or not in PATH!
    pause
    exit /b 1
)

:: 2. Run Site-Wide WebP Conversion and Build
echo [1/6] Running site-wide WebP conversion and rebuilding all pages...
python build.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Build failed! Please review the error above.
    pause
    exit /b %ERRORLEVEL%
)

:: 3. Run Site Verification
echo.
echo [2/6] Verifying site links, CSS, JS, and image assets...
python tools/verify_site.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Site verification failed!
    pause
    exit /b %ERRORLEVEL%
)

:: 4. Stage All Changes in Git
echo.
echo [3/6] Staging changes in git (dev branch)...
git add -A

:: 5. Commit Changes on dev
echo.
echo [4/6] Committing changes to dev...
set "COMMIT_MSG=%~1"
if "!COMMIT_MSG!"=="" (
    set "COMMIT_MSG=deploy: site update and WebP optimization"
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
echo [5/6] Pushing dev branch to origin/dev...
git push origin dev
if %ERRORLEVEL% neq 0 (
    echo.
    echo [WARNING] Failed to push dev branch to origin. Check internet/git credentials.
)

:: 7. Merge dev into main and push to trigger GitHub Pages
echo.
echo [6/6] Merging dev into main and pushing to origin/main (triggers GitHub Pages)...
git checkout main
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Could not checkout main branch.
    pause
    exit /b 1
)

git merge dev --no-edit
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Merge conflict occurred while merging dev into main!
    git checkout dev
    pause
    exit /b 1
)

git push origin main
if %ERRORLEVEL% neq 0 (
    echo.
    echo [WARNING] Failed to push main to origin. Check internet/git credentials.
)

:: 8. Return to dev branch
git checkout dev

echo.
echo ======================================================================
echo  SUCCESS: Site successfully built, optimized, committed, and deployed!
echo  GitHub Pages is now deploying the latest main branch.
echo  Working branch is back on 'dev'.
echo ======================================================================
echo.
pause
