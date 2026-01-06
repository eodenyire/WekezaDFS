@echo off
REM Wekeza Personal Banking Portal - Windows Startup Script

echo ========================================
echo 🏦 Wekeza Personal Banking Portal
echo ========================================
echo.

REM Check if main application exists
if not exist "personal_banking_portal.py" (
    echo ❌ Personal banking portal file not found!
    echo Please ensure you're in the correct directory.
    echo.
    pause
    exit /b 1
)

REM Start the application
echo 🚀 Starting Personal Banking Portal...
echo.
echo 📍 Application will be available at:
echo    http://localhost:8507
echo.
echo 🔑 Demo login credentials:
echo    Email: emmanuel@wekeza.com
echo    Password: password123
echo.
echo 💡 Press Ctrl+C to stop the application
echo ========================================
echo.

REM Start Streamlit application
python -m streamlit run personal_banking_portal.py --server.port 8507

REM If we get here, the application has stopped
echo.
echo 🛑 Personal Banking Portal stopped.
pause