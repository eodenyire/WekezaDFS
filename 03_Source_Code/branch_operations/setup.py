#!/usr/bin/env python3
"""
Wekeza DFS Branch Operations System - Setup Script
This script automates the setup process for the branch operations system.
"""

import os
import sys
import subprocess
import mysql.connector
from pathlib import Path

def print_header():
    """Print setup header"""
    print("=" * 60)
    print("🏦 Wekeza DFS Branch Operations System Setup")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("📋 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_mysql_connection():
    """Check MySQL connection"""
    print("\n🗄️ Checking MySQL connection...")
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root'
        )
        conn.close()
        print("✅ MySQL connection successful")
        return True
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        print("   Please ensure MySQL is installed and running")
        print("   Default credentials: user='root', password='root'")
        return False

def create_virtual_environment():
    """Create virtual environment"""
    print("\n🐍 Creating virtual environment...")
    try:
        if not os.path.exists('venv'):
            subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
            print("✅ Virtual environment created")
        else:
            print("✅ Virtual environment already exists")
        return True
    except Exception as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    try:
        # Determine pip path based on OS
        if os.name == 'nt':  # Windows
            pip_path = os.path.join('venv', 'Scripts', 'pip')
        else:  # macOS/Linux
            pip_path = os.path.join('venv', 'bin', 'pip')
        
        # Install requirements
        subprocess.run([pip_path, 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_database():
    """Setup database and tables"""
    print("\n🗄️ Setting up database...")
    try:
        # Navigate to parent directory for database scripts
        parent_dir = Path(__file__).parent.parent.parent
        
        # Check if database scripts exist
        scripts = [
            'create_user.py',
            'create_staff_tables.py', 
            'create_loan_tables.py',
            'create_insurance_tables.py'
        ]
        
        missing_scripts = []
        for script in scripts:
            script_path = parent_dir / script
            if not script_path.exists():
                missing_scripts.append(script)
        
        if missing_scripts:
            print(f"⚠️ Some database setup scripts not found: {missing_scripts}")
            print("   Please run them manually from the parent directory")
            return True  # Don't fail setup for this
        
        # Run database setup scripts
        original_dir = os.getcwd()
        os.chdir(parent_dir)
        
        for script in scripts:
            print(f"   Running {script}...")
            try:
                subprocess.run([sys.executable, script], check=True, capture_output=True)
                print(f"   ✅ {script} completed")
            except subprocess.CalledProcessError as e:
                print(f"   ⚠️ {script} had issues (may be normal if already setup)")
        
        os.chdir(original_dir)
        print("✅ Database setup completed")
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def verify_installation():
    """Verify the installation"""
    print("\n✅ Verifying installation...")
    
    # Check if main application file exists
    if not os.path.exists('main_branch_system.py'):
        print("❌ Main application file not found")
        return False
    
    # Check if all module directories exist
    modules = ['branch_teller', 'supervision', 'customer_ops', 'credit_ops', 'bancassurance']
    for module in modules:
        if not os.path.exists(module):
            print(f"❌ Module directory '{module}' not found")
            return False
        
        app_file = os.path.join(module, 'app.py')
        if not os.path.exists(app_file):
            print(f"❌ Module file '{app_file}' not found")
            return False
    
    print("✅ All application files verified")
    
    # Test database connection with application database
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        conn.close()
        
        if len(tables) > 0:
            print(f"✅ Database verified ({len(tables)} tables found)")
        else:
            print("⚠️ Database exists but no tables found")
        
    except Exception as e:
        print(f"⚠️ Database verification failed: {e}")
    
    return True

def print_completion_message():
    """Print setup completion message"""
    print("\n" + "=" * 60)
    print("🎉 Setup Complete!")
    print("=" * 60)
    print()
    print("📋 Next Steps:")
    print("1. Activate virtual environment:")
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
    else:  # macOS/Linux
        print("   source venv/bin/activate")
    
    print()
    print("2. Start the application:")
    print("   streamlit run main_branch_system.py --server.port 8501")
    print()
    print("3. Access the application:")
    print("   http://localhost:8501")
    print()
    print("4. Login with default credentials:")
    print("   Staff Code: SUP001")
    print("   Password: password123")
    print()
    print("📚 Documentation:")
    print("   - README.md: Complete system documentation")
    print("   - INSTALLATION.md: Detailed installation guide")
    print()
    print("🔧 Troubleshooting:")
    print("   - Check INSTALLATION.md for common issues")
    print("   - Verify MySQL service is running")
    print("   - Ensure all dependencies are installed")
    print()

def main():
    """Main setup function"""
    print_header()
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    if not check_mysql_connection():
        print("\n⚠️ MySQL connection failed. Please:")
        print("   1. Install MySQL Server")
        print("   2. Start MySQL service")
        print("   3. Set root password to 'root' (or update connection settings)")
        print("   4. Run this setup script again")
        sys.exit(1)
    
    # Setup steps
    steps = [
        ("Create virtual environment", create_virtual_environment),
        ("Install dependencies", install_dependencies),
        ("Setup database", setup_database),
        ("Verify installation", verify_installation)
    ]
    
    failed_steps = []
    for step_name, step_func in steps:
        if not step_func():
            failed_steps.append(step_name)
    
    if failed_steps:
        print(f"\n❌ Setup failed at: {', '.join(failed_steps)}")
        print("   Please check the error messages above and try again")
        print("   Refer to INSTALLATION.md for detailed troubleshooting")
        sys.exit(1)
    
    print_completion_message()

if __name__ == "__main__":
    main()