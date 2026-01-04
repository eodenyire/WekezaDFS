@echo off
echo 🏦 Starting Wekeza Branch Operations System with Role-Based Access Control
echo.
echo ✅ Features:
echo - Database-authenticated login
echo - Role-based module access
echo - Centralized session management
echo - Audit trail logging
echo.
echo 🔑 Test Login Credentials:
echo - TELLER001 / teller123 / BR001 (Teller Operations Only)
echo - SUP001 / supervisor123 / BR001 (Supervision + Multiple Modules)
echo - ADMIN001 / admin / HQ001 (Admin - All Modules)
echo - EG-74255 / password123 / BR001 (Teller Operations)
echo.
echo 🌐 Starting on http://localhost:8507
echo.
python -m streamlit run "03_Source_Code/branch_operations/main_branch_system.py" --server.port 8507
pause