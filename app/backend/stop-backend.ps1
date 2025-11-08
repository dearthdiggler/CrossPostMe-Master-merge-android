# stop-backend.ps1
# Stop backend processes that look like the Crosspostme uvicorn server started by start-backend.ps1
# Usage: .\stop-backend.ps1

$procs = Get-CimInstance Win32_Process | Where-Object {
    ($_.CommandLine -match '\.venv\\bin\\python') -or
    ($_.CommandLine -match 'uvicorn') -or
    ($_.CommandLine -match 'server:app')
}

if (-not $procs) {
    Write-Host "No matching backend processes found."
    exit 0
}

foreach ($p in $procs) {
    Write-Host "Stopping PID $($p.ProcessId): $($p.CommandLine)"
    Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
}

Write-Host "Done."
