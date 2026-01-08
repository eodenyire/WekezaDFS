@echo off
echo Starting Wekeza Backend API...
cd 03_Source_Code\backend_api
call venv\Scripts\activate
uvicorn app.main:app --reload --port 8000