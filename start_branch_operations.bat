@echo off
echo Starting Branch Operations System (Core Banking)...
cd 03_Source_Code\branch_operations
python -m streamlit run main_branch_system.py --server.port 8506