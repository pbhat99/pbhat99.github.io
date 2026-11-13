$ErrorActionPreference = "SilentlyContinue"
$projectRoot = Split-Path -Parent $PSScriptRoot
if (-not $projectRoot) { $projectRoot = Get-Location }
Set-Location $projectRoot

$port = 8080
$conn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue

if (-not $conn) {
    Write-Host "Starting live dev server on http://localhost:$port..." -ForegroundColor Cyan
    Start-Process -FilePath "python" -ArgumentList "watcher.py" -WorkingDirectory $projectRoot -WindowStyle Minimized
    Start-Sleep -Seconds 1
} else {
    Write-Host "Dev server is already active on http://localhost:$port" -ForegroundColor Green
}

# Try to find and focus an existing browser window, then refresh (F5)
$wshell = New-Object -ComObject Wscript.Shell
$activated = $false
$windowCandidates = @("Pra - Motions", "Prasannakumar", "localhost:8080", "VFX |", "About |", "AI & ComfyUI")

foreach ($t in $windowCandidates) {
    if ($wshell.AppActivate($t)) {
        $activated = $true
        Write-Host "Focused existing browser window ('$t') - refreshing page with F5..." -ForegroundColor Green
        Start-Sleep -Milliseconds 250
        $wshell.SendKeys("{F5}")
        break
    }
}

# If no matching browser window is open, launch default browser to localhost:8080
if (-not $activated) {
    Write-Host "Opening http://localhost:$port in your default browser..." -ForegroundColor Yellow
    Start-Process "http://localhost:$port"
}
