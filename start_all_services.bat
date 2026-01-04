@echo off
echo ========================================
echo Starting Wekeza DFS Platform - All Services
echo ========================================
echo.

echo Starting Backend API (Port 8000)...
start "Backend API" cmd /k "cd 03_Source_Code\backend_api && python start_server.py"
timeout /t 3 /nobreak >nul

echo Starting Customer Portal (Port 8502)...
start "Customer Portal" cmd /k "cd 03_Source_Code\web_portal_customer && python -m streamlit run customer_app.py --server.port 8502"
timeout /t 2 /nobreak >nul

echo Starting Admin Portal (Port 8503)...
start "Admin Portal" cmd /k "cd 03_Source_Code\web_portal_admin && python -m streamlit run admin_dashboard.py --server.port 8503"
timeout /t 2 /nobreak >nul

echo Starting Business Portal (Port 8504)...
start "Business Portal" cmd /k "cd 03_Source_Code\web_portal_business && python -m streamlit run business_app.py --server.port 8504"
timeout /t 2 /nobreak >nul

echo Starting Branch Teller (Port 8505)...
start "Branch Teller" cmd /k "cd 03_Source_Code\branch_teller && python -m streamlit run teller_app.py --server.port 8505"
timeout /t 2 /nobreak >nul

echo Starting Branch Operations (Port 8506)...
start "Branch Operations" cmd /k "cd 03_Source_Code\branch_operations && python -m streamlit run main_branch_system.py --server.port 8506"
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo All services are starting up...
echo ========================================
echo.
echo Access URLs:
echo - Backend API:        http://127.0.0.1:8000/docs
echo - Customer Portal:    http://localhost:8502
echo - Admin Dashboard:    http://localhost:8503
echo - Business Portal:    http://localhost:8504
echo - Branch Teller:      http://localhost:8505
echo - Branch Operations:  http://localhost:8506
echo.
echo Press any key to exit...
pause >nul