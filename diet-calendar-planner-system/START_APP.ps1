# Diet Calendar Planner - PowerShell Startup Script
# Run this script to start the app with automatic checks

Write-Host ""
Write-Host "============================================================"
Write-Host "  DIET CALENDAR PLANNER - STARTUP"
Write-Host "============================================================"
Write-Host ""

# Check if running from correct directory
if (-not (Test-Path "backend\app.py")) {
    Write-Host "ERROR: Cannot find backend\app.py" -ForegroundColor Red
    Write-Host "Please run this script from: c:\xampp\htdocs\diet-calendar-planner-system" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Optional: Ask for email configuration
Write-Host ""
Write-Host "Would you like to configure email notifications?"
Write-Host "(You need Gmail credentials for this)"
Write-Host ""
$emailConfig = Read-Host "Configure email now? (y/n)"

if ($emailConfig -eq "y" -or $emailConfig -eq "Y") {
    Clear-Host
    Write-Host ""
    Write-Host "============================================================"
    Write-Host "  EMAIL CONFIGURATION"
    Write-Host "============================================================"
    Write-Host ""
    Write-Host "1. Go to: https://myaccount.google.com/apppasswords"
    Write-Host "2. Select: Mail and Windows PC"
    Write-Host "3. Copy the 16-character password"
    Write-Host ""
    
    $gmailEmail = Read-Host "Enter your Gmail address"
    $gmailPassword = Read-Host "Enter your 16-character App Password"
    
    # Set environment variables for current session
    $env:MAIL_USERNAME = $gmailEmail
    $env:MAIL_PASSWORD = $gmailPassword
    
    # Set permanently (requires admin)
    try {
        [Environment]::SetEnvironmentVariable("MAIL_USERNAME", $gmailEmail, "User")
        [Environment]::SetEnvironmentVariable("MAIL_PASSWORD", $gmailPassword, "User")
        Write-Host ""
        Write-Host "✅ Environment variables set for this session and permanently!" -ForegroundColor Green
    } catch {
        Write-Host ""
        Write-Host "Note: Could not set permanent variables (requires admin)" -ForegroundColor Yellow
        Write-Host "✅ Environment variables set for this session" -ForegroundColor Green
    }
    Write-Host ""
}

# Check Python
Write-Host ""
Write-Host "Checking Python installation..."
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.7 or later from https://www.python.org" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check dependencies
Write-Host "Checking dependencies..."
try {
    pip show Flask-Mail | Out-Null
    Write-Host "✅ Flask-Mail found" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Flask-Mail not found. Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Check MySQL
Write-Host ""
Write-Host "Checking MySQL connection..."
try {
    mysql -u root -e "SELECT 1;" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ MySQL is running" -ForegroundColor Green
    } else {
        throw "MySQL not responding"
    }
} catch {
    Write-Host ""
    Write-Host "⚠️ WARNING: Cannot connect to MySQL" -ForegroundColor Yellow
    Write-Host "Please start MySQL in XAMPP Control Panel before continuing" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter after starting MySQL"
    Clear-Host
}

# Clear screen and start app
Clear-Host
Write-Host ""
Write-Host "============================================================"
Write-Host "  STARTING DIET CALENDAR PLANNER"
Write-Host "============================================================"
Write-Host ""
Write-Host "🚀 Flask server starting at http://localhost:5000"
Write-Host ""
Write-Host "To stop the server: Press Ctrl+C"
Write-Host ""
Write-Host "============================================================"
Write-Host ""

# Check if email is configured
if (-not $env:MAIL_USERNAME) {
    Write-Host "Note: Email notifications not configured" -ForegroundColor Yellow
    Write-Host "Set MAIL_USERNAME and MAIL_PASSWORD environment variables to enable" -ForegroundColor Yellow
    Write-Host ""
}

# Start the Flask app
python backend/app.py

# If we get here, app crashed
Write-Host ""
Write-Host "❌ Flask app stopped or crashed" -ForegroundColor Red
Write-Host "Check the error message above"
Read-Host "Press Enter to exit"
