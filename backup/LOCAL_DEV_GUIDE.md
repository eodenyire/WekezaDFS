# Wekeza DFS Platform - Local Development Guide

## Prerequisites

1. **MySQL Server** running on your laptop
   - Host: `localhost`
   - User: `root`
   - Password: `root`

2. **Python 3.9+** installed

## Quick Setup

### 1. Database Setup
Open MySQL Workbench or Terminal and run:
```sql
CREATE DATABASE IF NOT EXISTS wekeza_dfs_db;
```

### 2. Automated Setup (Recommended)
Run the setup script:
```cmd
setup_local_dev.bat
```

### 3. Manual Setup (Alternative)

#### Backend API Setup
```cmd
cd 03_Source_Code\backend_api
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

#### Install Streamlit Dependencies
```cmd
pip install streamlit requests pandas
```

## Running the Applications

### Option 1: Use Startup Scripts
- **Backend API**: `start_backend.bat`
- **Customer Portal**: `start_customer_portal.bat`
- **Business Portal**: `start_business_portal.bat`
- **Admin Portal**: `start_admin_portal.bat`

### Option 2: Manual Commands

#### Terminal 1 - Backend API (The Engine)
```cmd
cd 03_Source_Code\backend_api
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```
**Success Check**: Visit http://localhost:8000/docs (Swagger UI)

#### Terminal 2 - Customer Portal (Juma's Phone)
```cmd
cd 03_Source_Code\web_portal_customer
streamlit run customer_app.py --server.port 8502
```
**Access**: http://localhost:8502

#### Terminal 3 - Business Portal (SME)
```cmd
cd 03_Source_Code\web_portal_business
streamlit run business_app.py --server.port 8504
```
**Access**: http://localhost:8504

#### Terminal 4 - Admin Portal (Risk Ops)
```cmd
cd 03_Source_Code\web_portal_admin
streamlit run admin_dashboard.py --server.port 8503
```
**Access**: http://localhost:8503

## Application URLs

| Component | URL | Description |
|-----------|-----|-------------|
| Backend API | http://localhost:8000 | FastAPI with Swagger docs |
| Customer Portal | http://localhost:8502 | Personal banking interface |
| Admin Portal | http://localhost:8503 | Risk operations dashboard |
| Business Portal | http://localhost:8504 | SME banking interface |

## Configuration Notes

- All web portals are configured to use `http://localhost:8000` for local development
- Database connection uses localhost MySQL with root/root credentials
- Backend API uses environment variable `DB_HOST` (defaults to localhost)

## Troubleshooting

1. **Database Connection Issues**: Ensure MySQL is running and credentials are correct
2. **Port Conflicts**: Check if ports 8000, 8502, 8503, 8504 are available
3. **Module Not Found**: Ensure all dependencies are installed in the virtual environment
4. **API Connection**: Verify backend is running before starting web portals

## Development Workflow

1. Start Backend API first
2. Verify API is working at http://localhost:8000/docs
3. Start the web portals you need for testing
4. Make changes and test instantly (all services have auto-reload enabled)