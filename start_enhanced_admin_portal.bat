@echo off
echo Starting Enhanced Wekeza Admin Portal...
cd /d "F:\Software Engineering\Banking\Wekeza Bank DFS System\wekeza_dfs_platform\03_Source_Code\web_portal_admin"
python -m streamlit run enhanced_admin_dashboard.py --server.port 8503
pause