@echo off
echo Starting Wekeza Branch Teller Application...
cd "03_Source_Code\branch_teller"
python -m streamlit run teller_app.py --server.port 8505
pause