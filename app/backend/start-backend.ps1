# start-backend.ps1
# Start the Crosspostme backend using the repo venv Python. Safe to run multiple times.
# Usage: .\start-backend.ps1 [-Foreground]
param(
    [switch]$Foreground
)

$venvPy = Join-Path $PSScriptRoot '.\.venv\bin\python'
$uvicornArgs = @('-m','uvicorn','server:app','--reload','--host','0.0.0.0','--port','8000','--log-level','info')

if ($Foreground) {
    Write-Host "Starting backend in foreground using $venvPy"
    & $venvPy @uvicornArgs
} else {
    Write-Host "Starting backend in background using $venvPy"
    Start-Process -FilePath $venvPy -ArgumentList $uvicornArgs -WindowStyle Hidden
    Start-Sleep -Seconds 1
    Write-Host "Started. Tail the server log with: Get-Content server.log -Wait -Tail 50"
}
