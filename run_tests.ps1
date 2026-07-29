#!/usr/bin/env pwsh

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Running Backend Tests" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
cd Backend
.venv\Scripts\python manage.py test
$backendStatus = $?
cd ..

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Running Frontend Tests" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
cd Frontend
npm run test
$frontendStatus = $?
cd ..

Write-Host "=========================================" -ForegroundColor Cyan
if ($backendStatus -and $frontendStatus) {
    Write-Host "All tests passed successfully!" -ForegroundColor Green
} else {
    Write-Host "Some tests failed. Please review the output above." -ForegroundColor Red
    exit 1
}
