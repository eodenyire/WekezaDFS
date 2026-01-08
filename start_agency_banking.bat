@echo off
echo ========================================
echo    Wekeza Agency Banking System
echo ========================================
echo.

cd /d "%~dp0\03_Source_Code\agency_banking"

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo Checking dependencies...
python -c "import streamlit, mysql.connector" >nul 2>&1
if errorlevel 1 (
    echo Installing required dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo Checking database setup...
python -c "import mysql.connector; conn = mysql.connector.connect(host='localhost', user='root', password='root', database='wekeza_dfs_db'); cursor = conn.cursor(); cursor.execute('SHOW TABLES LIKE \"agents\"'); result = cursor.fetchone(); conn.close(); exit(0 if result else 1)" >nul 2>&1
if errorlevel 1 (
    echo Setting up agency banking database...
    python setup_agency_db.py
    if errorlevel 1 (
        echo ERROR: Database setup failed
        echo Make sure MySQL is running and accessible
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo Starting Agency Banking Portal...
echo ========================================
echo Portal URL: http://localhost:8501
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python start_agency_system.py

pause