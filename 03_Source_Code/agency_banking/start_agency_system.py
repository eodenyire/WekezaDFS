"""
Startup script for Wekeza Agency Banking System
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'streamlit',
        'mysql-connector-python',
        'pandas'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall missing packages with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_database_setup():
    """Check if agency banking tables exist"""
    try:
        import mysql.connector
        
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES LIKE 'agents'")
        
        if not cursor.fetchone():
            print("❌ Agency banking tables not found!")
            print("Run setup first: python setup_agency_db.py")
            return False
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Make sure MySQL is running and database exists")
        return False

def start_agency_portal():
    """Start the agency banking portal"""
    try:
        ui_path = Path(__file__).parent / "ui" / "agent_portal.py"
        
        print("🚀 Starting Wekeza Agency Banking Portal...")
        print("=" * 50)
        print("Portal will open in your browser at: http://localhost:8501")
        print("Use Ctrl+C to stop the server")
        print("=" * 50)
        
        # Start Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(ui_path), 
            "--server.port=8501",
            "--server.address=localhost",
            "--browser.gatherUsageStats=false"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Agency Banking Portal stopped")
    except Exception as e:
        print(f"❌ Failed to start portal: {e}")

def main():
    """Main startup function"""
    print("🏪 Wekeza Agency Banking System")
    print("=" * 40)
    
    # Check dependencies
    print("📦 Checking dependencies...")
    if not check_dependencies():
        return
    print("✅ Dependencies OK")
    
    # Check database setup
    print("🗄️  Checking database setup...")
    if not check_database_setup():
        return
    print("✅ Database OK")
    
    # Start the portal
    start_agency_portal()

if __name__ == "__main__":
    main()