$ErrorActionPreference = "SilentlyContinue"
$projectRoot = Split-Path -Parent $PSScriptRoot
if (-not $projectRoot) { $projectRoot = Get-Location }
Set-Location $projectRoot

# Resolve Python executable
$pyCandidate = "$env:LOCALAPPDATA\Programs\Python\Python314\python.exe"
$pyExe = if (Test-Path $pyCandidate) { $pyCandidate } else { "python" }

$port = 8080

# 1. Release any stale process listening on port 8080
$staleConns = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
if ($staleConns) {
    Write-Host "[Server] Stopping existing process on port $port..." -ForegroundColor Yellow
    foreach ($c in $staleConns) {
        Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Milliseconds 400
}

# 2. Schedule browser focus/refresh (or open) once server starts
$browserTask = [powershell]::Create().AddScript({
    param($p)
    Start-Sleep -Milliseconds 800
    $wshell = New-Object -ComObject Wscript.Shell
    $activated = $false
    $windowCandidates = @("Pra - Motions", "Prasannakumar", "localhost:$p", "VFX |", "About |", "AI & ComfyUI", "Photography |", "Blog |")

    foreach ($t in $windowCandidates) {
        if ($wshell.AppActivate($t)) {
            $activated = $true
            Start-Sleep -Milliseconds 250
            # Ctrl+F5 forces a hard refresh bypassing browser cache
            $wshell.SendKeys("^{F5}")
            break
        }
    }

    if (-not $activated) {
        Start-Process "http://localhost:$p"
    }
}).AddArgument($port)
[void]$browserTask.BeginInvoke()

# 3. Run watcher in the foreground of this terminal window
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Pra - Motions Dev Server & Watcher" -ForegroundColor Cyan
Write-Host "  URL: http://localhost:$port" -ForegroundColor Green
Write-Host "  Closing this terminal window will kill the server." -ForegroundColor Yellow
Write-Host "===================================================" -ForegroundColor Cyan

& $pyExe watcher.py
