@echo off
REM Install Email Notification Dependencies
REM This script installs Flask-Mail which is required for email notifications

echo Installing required packages...
python -m pip install --upgrade pip
python -m pip install Flask==2.3.2
python -m pip install Flask-CORS==4.0.0
python -m pip install Flask-MySQLdb==2.0.0
python -m pip install Flask-Mail==0.9.1
python -m pip install python-dotenv==1.0.0

echo.
echo ====================================================
echo Installation Complete!
echo.
echo Next steps:
echo 1. Copy .env.example to .env
echo 2. Edit .env with your Gmail credentials
echo 3. Run: python backend/app.py
echo ====================================================
echo.
pause
