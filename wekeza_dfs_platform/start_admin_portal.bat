@echo off
echo Starting Admin Portal (Risk Ops)...
cd 03_Source_Code\web_portal_admin
streamlit run admin_dashboard.py --server.port 8503