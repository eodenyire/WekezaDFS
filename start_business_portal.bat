@echo off
echo Starting Wekeza Business Banking Portal...
cd /d "F:\Software Engineering\Banking\Wekeza Bank DFS System\wekeza_dfs_platform\03_Source_Code\web_portal_business"
python -m streamlit run business_app.py --server.port 8504
pause