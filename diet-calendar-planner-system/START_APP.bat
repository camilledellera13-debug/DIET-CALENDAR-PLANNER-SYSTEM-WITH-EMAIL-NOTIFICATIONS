@echo off
REM ============================================================
REM Diet Calendar Planner - Startup Script
REM ============================================================

echo.
echo ============================================================
echo   DIET CALENDAR PLANNER - STARTUP
echo ============================================================
echo.

REM Check if running from correct directory
if not exist "backend\app.py" (
    echo ERROR: Cannot find backend\app.py
    echo Please run this script from: c:\xampp\htdocs\diet-calendar-planner-system
    pause
    exit /b 1
)

REM Optional: Ask for email configuration
echo.
echo Would you like to configure email notifications?
echo (You need Gmail credentials for this)
echo.
set /p email_config="Configure email now? (y/n): "

if /i "%email_config%"=="y" (
    cls
    echo.
    echo ============================================================
    echo   EMAIL CONFIGURATION
    echo ============================================================
    echo.
    echo 1. Go to: https://myaccount.google.com/apppasswords
    echo 2. Select: Mail and Windows PC
    echo 3. Copy the 16-character password
    echo.
    set /p gmail_email="Enter your Gmail address: "
    set /p gmail_password="Enter your 16-character App Password: "
    
    setx MAIL_USERNAME "%gmail_email%"
    setx MAIL_PASSWORD "%gmail_password%"
    
    echo.
    echo ✅ Environment variables set!
    echo Note: You may need to restart your terminal for changes to take effect
    echo.
)

REM Check if Python is installed
echo.
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or later from https://www.python.org
    pause
    exit /b 1
)
echo ✅ Python found

REM Check if Flask-Mail is installed
echo Checking Flask-Mail...
pip show Flask-Mail >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Flask-Mail not found. Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed
) else (
    echo ✅ Flask-Mail found
)

REM Check if MySQL is running
echo.
echo Checking MySQL connection...
mysql -u root -e "SELECT 1" >nul 2>&1
if errorlevel 1 (
    echo.
    echo ⚠️ WARNING: Cannot connect to MySQL
    echo Please start MySQL in XAMPP Control Panel before continuing
    echo.
    set /p wait_mysql="Press Enter after starting MySQL, or press Ctrl+C to exit: "
    cls
) else (
    echo ✅ MySQL is running
)

REM Clear screen and start app
cls
echo.
echo ============================================================
echo   STARTING DIET CALENDAR PLANNER
echo ============================================================
echo.
echo 🚀 Flask server starting at http://localhost:5000
echo.
echo To stop the server: Press Ctrl+C
echo.
echo ============================================================
echo.

REM Set environment variables if not already set
if not defined MAIL_USERNAME (
    echo Note: Email notifications not configured
    echo Set MAIL_USERNAME and MAIL_PASSWORD environment variables to enable
)

REM Start the Flask app
python backend/app.py

REM If we get here, app crashed
echo.
echo ❌ Flask app stopped or crashed
echo Check the error message above
pause
