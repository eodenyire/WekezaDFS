@echo off
echo 🏦 Starting Wekeza Personal Banking Portal on Port 8507...
echo.
echo 📍 Access at: http://localhost:8507
echo 🔑 Demo Login: emmanuel@wekeza.com / password123
echo.
python -m streamlit run personal_banking_portal.py --server.port 8507
pause