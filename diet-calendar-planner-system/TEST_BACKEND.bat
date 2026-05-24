@echo off
REM Quick test to verify backend is working

echo.
echo ============================================================
echo   DIET CALENDAR PLANNER - QUICK TEST
echo ============================================================
echo.

echo Testing backend health...
echo.

powershell -Command "
try {
    \$response = Invoke-WebRequest -Uri 'http://localhost:5000/test' -ErrorAction Stop
    \$json = \$response.Content | ConvertFrom-Json
    
    Write-Host 'Success! Response received:' -ForegroundColor Green
    Write-Host (\$json | ConvertTo-Json)
    
    if (\$json.success -eq \$true -and \$json.status -eq 'healthy') {
        Write-Host ''
        Write-Host '✅ Backend is working and MySQL is connected!' -ForegroundColor Green
        Write-Host ''
        Write-Host 'You can now:'
        Write-Host '  1. Open http://localhost:5000 in your browser'
        Write-Host '  2. Register a new account'
        Write-Host '  3. Login with your credentials'
        Write-Host '  4. Add meals and activities'
        Write-Host ''
    } elseif (\$json.status -eq 'unhealthy') {
        Write-Host ''
        Write-Host '❌ MySQL is not connected!' -ForegroundColor Red
        Write-Host ''
        Write-Host 'Fix:'
        Write-Host '  1. Open XAMPP Control Panel'
        Write-Host '  2. Click Start next to MySQL'
        Write-Host '  3. Wait for status to show Running'
        Write-Host '  4. Restart Flask app'
        Write-Host ''
    }
} catch {
    Write-Host 'Error: Could not connect to backend' -ForegroundColor Red
    Write-Host 'Make sure Flask app is running at http://localhost:5000' -ForegroundColor Red
    Write-Host ''
    Write-Host 'Run:'
    Write-Host '  python backend/app.py'
    Write-Host ''
    Write-Host 'Error details:' -ForegroundColor Yellow
    Write-Host \$_.Exception.Message
}
"

pause
