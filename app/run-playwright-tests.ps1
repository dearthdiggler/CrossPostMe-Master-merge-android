# PowerShell script to run Playwright E2E tests from project root
Write-Host "Running Playwright E2E tests..."
Set-Location app/frontend
npx playwright test playwright-tests
Set-Location ../..
