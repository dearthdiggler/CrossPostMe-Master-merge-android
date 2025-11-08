# PowerShell script to run backend tests and coverage from project root
$testPath = "app/backend/tests/"
$covPath = "app/backend"
Write-Host "Running backend tests with coverage..."
python -m pytest --cov=$covPath $testPath
