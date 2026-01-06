@echo off
echo ========================================
echo Wekeza DFS Platform - Local Dev Setup
echo ========================================

echo.
echo Step 1: Checking MySQL Database...
echo Please ensure MySQL is running and execute this SQL command:
echo CREATE DATABASE IF NOT EXISTS wekeza_dfs_db;
echo.
pause

echo.
echo Step 2: Setting up Backend API...
cd 03_Source_Code\backend_api

echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Backend setup complete!
echo To start the backend API, run:
echo   cd 03_Source_Code\backend_api
echo   venv\Scripts\activate
echo   uvicorn app.main:app --reload --port 8000
echo.
echo Then visit: http://localhost:8000/docs
echo.

cd ..\..
pause

echo.
echo Step 3: Installing Streamlit dependencies...
pip install streamlit requests pandas

echo.
echo Setup complete! 
echo.
echo To run the applications:
echo.
echo Terminal 1 - Backend API:
echo   cd 03_Source_Code\backend_api
echo   venv\Scripts\activate
echo   uvicorn app.main:app --reload --port 8000
echo.
echo Terminal 2 - Customer Portal:
echo   cd 03_Source_Code\web_portal_customer
echo   streamlit run customer_app.py --server.port 8502
echo.
echo Terminal 3 - Business Portal:
echo   cd 03_Source_Code\web_portal_business
echo   streamlit run business_app.py --server.port 8504
echo.
pause