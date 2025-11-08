# PowerShell script to run frontend Jest tests and coverage from project root
Write-Host "Running frontend Jest tests with coverage..."
Set-Location app/frontend
yarn test --coverage --watchAll=false
Set-Location ../..
