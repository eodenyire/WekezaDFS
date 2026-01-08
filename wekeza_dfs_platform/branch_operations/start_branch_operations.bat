@echo off
REM Wekeza DFS Branch Operations System - Windows Startup Script

echo ========================================
echo 🏦 Wekeza DFS Branch Operations System
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo ❌ Virtual environment not found!
    echo Please run setup.py first:
    echo    python setup.py
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo 🐍 Activating virtual environment...
call venv\Scripts\activate

REM Check if main application exists
if not exist "main_branch_system.py" (
    echo ❌ Main application file not found!
    echo Please ensure you're in the correct directory.
    echo.
    pause
    exit /b 1
)

REM Start the application
echo 🚀 Starting Branch Operations System...
echo.
echo 📍 Application will be available at:
echo    http://localhost:8501
echo.
echo 🔑 Default login credentials:
echo    Staff Code: SUP001
echo    Password: password123
echo.
echo 💡 Press Ctrl+C to stop the application
echo ========================================
echo.

REM Start Streamlit application
streamlit run main_branch_system.py --server.port 8501

REM If we get here, the application has stopped
echo.
echo 🛑 Application stopped.
pause