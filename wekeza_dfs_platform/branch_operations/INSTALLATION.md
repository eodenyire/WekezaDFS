# 🚀 Wekeza DFS Branch Operations System - Installation Guide

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Prerequisites Installation](#prerequisites-installation)
3. [Database Setup](#database-setup)
4. [Application Installation](#application-installation)
5. [Configuration](#configuration)
6. [First Run Setup](#first-run-setup)
7. [Verification & Testing](#verification--testing)
8. [Troubleshooting](#troubleshooting)
9. [Production Deployment](#production-deployment)
10. [Maintenance & Updates](#maintenance--updates)

---

## 🖥️ System Requirements

### **Minimum Requirements**
- **Operating System**: Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Network**: Stable internet connection for external integrations
- **Browser**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+

### **Recommended Specifications**
- **CPU**: Intel i5 or AMD Ryzen 5 (4+ cores)
- **RAM**: 16GB for production environments
- **Storage**: SSD with 10GB+ free space
- **Network**: Gigabit ethernet for production

---

## 🔧 Prerequisites Installation

### **1. Python Installation**

#### **Windows**
```bash
# Download Python 3.8+ from python.org
# During installation, check "Add Python to PATH"
# Verify installation
python --version
pip --version
```

#### **macOS**
```bash
# Using Homebrew (recommended)
brew install python@3.9

# Or download from python.org
# Verify installation
python3 --version
pip3 --version
```

#### **Ubuntu/Linux**
```bash
# Update package list
sudo apt update

# Install Python and pip
sudo apt install python3 python3-pip python3-venv

# Verify installation
python3 --version
pip3 --version
```

### **2. MySQL Server Installation**

#### **Windows**
```bash
# Download MySQL Installer from mysql.com
# Choose "MySQL Server" and "MySQL Workbench"
# During setup:
# - Root password: "root" (for development)
# - Port: 3306 (default)
# - Authentication: Use Legacy Authentication Method
```

#### **macOS**
```bash
# Using Homebrew
brew install mysql

# Start MySQL service
brew services start mysql

# Secure installation (optional for development)
mysql_secure_installation
```

#### **Ubuntu/Linux**
```bash
# Install MySQL Server
sudo apt install mysql-server

# Start MySQL service
sudo systemctl start mysql
sudo systemctl enable mysql

# Secure installation
sudo mysql_secure_installation
```

### **3. Git Installation** (if cloning repository)

#### **Windows**
```bash
# Download Git from git-scm.com
# Use default installation options
```

#### **macOS**
```bash
# Using Homebrew
brew install git

# Or use Xcode Command Line Tools
xcode-select --install
```

#### **Ubuntu/Linux**
```bash
# Install Git
sudo apt install git
```

---

## 🗄️ Database Setup

### **1. MySQL Configuration**

#### **Start MySQL Service**
```bash
# Windows (as Administrator)
net start mysql

# macOS
brew services start mysql

# Linux
sudo systemctl start mysql
```

#### **Connect to MySQL**
```bash
# Connect as root user
mysql -u root -p
# Enter password: root (or your chosen password)
```

### **2. Create Database and User**

```sql
-- Create the main database
CREATE DATABASE wekeza_dfs_db;

-- Create database user (optional, for production)
CREATE USER 'wekeza_user'@'localhost' IDENTIFIED BY 'wekeza_password';
GRANT ALL PRIVILEGES ON wekeza_dfs_db.* TO 'wekeza_user'@'localhost';
FLUSH PRIVILEGES;

-- Verify database creation
SHOW DATABASES;
USE wekeza_dfs_db;
```

### **3. Database Schema Setup**

#### **Download/Clone Repository**
```bash
# If you have the repository
git clone [repository-url]
cd wekeza_dfs_platform

# Or if you have the files locally
cd path/to/wekeza_dfs_platform
```

#### **Run Database Setup Scripts**
```bash
# Navigate to the platform directory
cd wekeza_dfs_platform

# Create basic tables and users
python create_user.py

# Create staff tables and sample data
python create_staff_tables.py

# Create loan tables (for credit operations)
python create_loan_tables.py

# Create insurance tables (for bancassurance)
python create_insurance_tables.py

# Verify table creation
python check_database.py
```

### **4. Sample Data Setup**

```bash
# Insert test users and accounts
python insert_test_users.py

# Setup insurance products
python setup_insurance_products.py

# Verify data insertion
python check_account_data.py
python check_staff_data.py
```

---

## 📦 Application Installation

### **1. Create Virtual Environment** (Recommended)

```bash
# Navigate to branch operations directory
cd wekeza_dfs_platform/03_Source_Code/branch_operations

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### **2. Install Required Packages**

```bash
# Install core dependencies
pip install streamlit==1.28.0
pip install mysql-connector-python==8.2.0
pip install pandas==2.1.0
pip install numpy==1.24.0
pip install python-dateutil==2.8.2

# Or install from requirements file (if available)
pip install -r requirements.txt
```

#### **Create requirements.txt** (if not exists)
```bash
# Create requirements file
cat > requirements.txt << EOF
streamlit==1.28.0
mysql-connector-python==8.2.0
pandas==2.1.0
numpy==1.24.0
python-dateutil==2.8.2
Pillow==10.0.0
plotly==5.17.0
EOF

# Install from requirements
pip install -r requirements.txt
```

### **3. Verify Installation**

```bash
# Check Streamlit installation
streamlit --version

# Check Python packages
pip list | grep streamlit
pip list | grep mysql-connector-python
```

---

## ⚙️ Configuration

### **1. Database Connection Configuration**

#### **Update Database Settings** (if different from defaults)

Edit each module's `app.py` file to update database connection:

```python
# In each module (branch_teller/app.py, supervision/app.py, etc.)
def get_db_connection():
    try:
        return mysql.connector.connect(
            host='localhost',        # Change if MySQL is on different server
            user='root',            # Change if using different user
            password='root',        # Change to your MySQL password
            database='wekeza_dfs_db' # Change if using different database name
        )
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None
```

### **2. Application Configuration**

#### **Streamlit Configuration** (Optional)
```bash
# Create Streamlit config directory
mkdir -p ~/.streamlit

# Create config file
cat > ~/.streamlit/config.toml << EOF
[server]
port = 8501
address = "0.0.0.0"
maxUploadSize = 200

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"

[browser]
gatherUsageStats = false
EOF
```

### **3. Environment Variables** (Optional)

```bash
# Create environment file
cat > .env << EOF
# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=root
DB_NAME=wekeza_dfs_db

# Application Configuration
APP_PORT=8501
APP_HOST=0.0.0.0
DEBUG_MODE=True

# External API URLs (if applicable)
API_URL=http://127.0.0.1:8000/api
EOF
```

---

## 🎯 First Run Setup

### **1. Test Database Connection**

```bash
# Test database connectivity
python -c "
import mysql.connector
try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='wekeza_dfs_db'
    )
    print('✅ Database connection successful!')
    conn.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"
```

### **2. Launch Application**

```bash
# Navigate to branch operations directory
cd wekeza_dfs_platform/03_Source_Code/branch_operations

# Start the application
python -m streamlit run main_branch_system.py --server.port 8501

# Alternative method
streamlit run main_branch_system.py --server.port 8501
```

### **3. Access Application**

Open your web browser and navigate to:
- **Local Access**: http://localhost:8501
- **Network Access**: http://[your-computer-ip]:8501

### **4. First Login**

Use these default credentials for first login:

| Role | Staff Code | Password | Access Level |
|------|------------|----------|--------------|
| Supervisor | SUP001 | password123 | Multiple modules |
| Branch Manager | BM001 | password123 | All modules |
| Admin | ADMIN001 | password123 | Full access |
| Teller | TEL001 | password123 | Teller only |

---

## ✅ Verification & Testing

### **1. System Health Check**

```bash
# Run comprehensive system test
python test_bancassurance_system.py

# Check all database tables
python check_database.py
python check_insurance_tables.py
python check_loan_table.py
```

### **2. Module Testing**

#### **Test Each Module**
1. **Login** with SUP001/password123
2. **Navigate** to each module:
   - Supervision ✅
   - Teller Operations ✅
   - Customer Operations ✅
   - Credit Operations ✅
   - Bancassurance ✅

#### **Test Core Functions**
1. **Teller Operations**:
   - Account verification (use ACC1000014)
   - Deposit transaction (KES 1,000)
   - Balance inquiry

2. **Supervision**:
   - View authorization queue
   - Check transaction approvals

3. **Customer Operations**:
   - CIF creation
   - Account opening simulation

4. **Credit Operations**:
   - Loan product selection
   - Application workflow

5. **Bancassurance**:
   - Policy search (use POL20260104001)
   - Premium collection

### **3. Performance Testing**

```bash
# Test application startup time
time streamlit run main_branch_system.py --server.port 8502 &

# Test database query performance
python -c "
import mysql.connector
import time
start = time.time()
conn = mysql.connector.connect(host='localhost', user='root', password='root', database='wekeza_dfs_db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM transactions')
result = cursor.fetchone()
end = time.time()
print(f'Query executed in {end-start:.2f} seconds')
conn.close()
"
```

---

## 🔧 Troubleshooting

### **Common Installation Issues**

#### **1. Python/Pip Issues**
```bash
# Issue: Python not found
# Solution: Add Python to PATH or use full path
C:\Python39\python.exe --version

# Issue: Pip not working
# Solution: Reinstall pip
python -m ensurepip --upgrade
```

#### **2. MySQL Connection Issues**
```bash
# Issue: Access denied for user 'root'
# Solution: Reset MySQL root password
mysql -u root
ALTER USER 'root'@'localhost' IDENTIFIED BY 'root';
FLUSH PRIVILEGES;

# Issue: MySQL service not running
# Windows: net start mysql
# macOS: brew services start mysql
# Linux: sudo systemctl start mysql
```

#### **3. Streamlit Issues**
```bash
# Issue: Streamlit command not found
# Solution: Reinstall streamlit
pip uninstall streamlit
pip install streamlit==1.28.0

# Issue: Port already in use
# Solution: Use different port
streamlit run main_branch_system.py --server.port 8502
```

#### **4. Module Import Errors**
```bash
# Issue: ModuleNotFoundError
# Solution: Install missing packages
pip install mysql-connector-python pandas numpy

# Issue: Relative import errors
# Solution: Run from correct directory
cd wekeza_dfs_platform/03_Source_Code/branch_operations
python -m streamlit run main_branch_system.py
```

### **Database Issues**

#### **1. Table Creation Errors**
```bash
# Check if database exists
mysql -u root -p -e "SHOW DATABASES;"

# Recreate database if needed
mysql -u root -p -e "DROP DATABASE IF EXISTS wekeza_dfs_db; CREATE DATABASE wekeza_dfs_db;"

# Run setup scripts again
python create_user.py
python create_staff_tables.py
```

#### **2. Data Issues**
```bash
# Clear and recreate test data
python clear_data.py
python insert_test_users.py
python setup_insurance_products.py
```

### **Application Issues**

#### **1. Login Problems**
```bash
# Check staff data
python check_staff_data.py

# Reset staff passwords
python reset_passwords_simple.py
```

#### **2. Module Loading Issues**
```bash
# Check file permissions
ls -la wekeza_dfs_platform/03_Source_Code/branch_operations/

# Verify all module files exist
ls -la */app.py
```

---

## 🚀 Production Deployment

### **1. Production Environment Setup**

#### **Server Requirements**
- **CPU**: 4+ cores
- **RAM**: 16GB+
- **Storage**: 100GB+ SSD
- **Network**: Stable high-speed connection
- **OS**: Ubuntu 20.04 LTS (recommended)

#### **Security Configuration**
```bash
# Create dedicated user
sudo adduser wekeza
sudo usermod -aG sudo wekeza

# Setup firewall
sudo ufw enable
sudo ufw allow 8501/tcp
sudo ufw allow 3306/tcp  # MySQL (restrict to local only)
```

### **2. Production Database Setup**

```sql
-- Create production database user
CREATE USER 'wekeza_prod'@'localhost' IDENTIFIED BY 'secure_production_password';
GRANT ALL PRIVILEGES ON wekeza_dfs_db.* TO 'wekeza_prod'@'localhost';
FLUSH PRIVILEGES;

-- Configure MySQL for production
-- Edit /etc/mysql/mysql.conf.d/mysqld.cnf
-- Add/modify:
-- max_connections = 200
-- innodb_buffer_pool_size = 1G
-- query_cache_size = 64M
```

### **3. Application Deployment**

```bash
# Clone repository to production server
git clone [repository-url] /opt/wekeza_dfs
cd /opt/wekeza_dfs

# Setup production virtual environment
python3 -m venv venv_prod
source venv_prod/bin/activate
pip install -r requirements.txt

# Setup systemd service
sudo cat > /etc/systemd/system/wekeza-branch-ops.service << EOF
[Unit]
Description=Wekeza Branch Operations System
After=network.target mysql.service

[Service]
Type=simple
User=wekeza
WorkingDirectory=/opt/wekeza_dfs/03_Source_Code/branch_operations
Environment=PATH=/opt/wekeza_dfs/venv_prod/bin
ExecStart=/opt/wekeza_dfs/venv_prod/bin/streamlit run main_branch_system.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl enable wekeza-branch-ops
sudo systemctl start wekeza-branch-ops
```

### **4. Reverse Proxy Setup** (Optional)

```bash
# Install Nginx
sudo apt install nginx

# Configure Nginx
sudo cat > /etc/nginx/sites-available/wekeza-branch-ops << EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/wekeza-branch-ops /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔄 Maintenance & Updates

### **1. Regular Maintenance Tasks**

#### **Daily Tasks**
```bash
# Check system status
sudo systemctl status wekeza-branch-ops
sudo systemctl status mysql

# Check disk space
df -h

# Check application logs
journalctl -u wekeza-branch-ops -f
```

#### **Weekly Tasks**
```bash
# Database backup
mysqldump -u root -p wekeza_dfs_db > backup_$(date +%Y%m%d).sql

# Update system packages
sudo apt update && sudo apt upgrade

# Check for Python package updates
pip list --outdated
```

#### **Monthly Tasks**
```bash
# Full system backup
tar -czf wekeza_backup_$(date +%Y%m%d).tar.gz /opt/wekeza_dfs

# Performance monitoring
# Check database performance
# Review application logs
# Update documentation
```

### **2. Update Procedures**

#### **Application Updates**
```bash
# Stop application
sudo systemctl stop wekeza-branch-ops

# Backup current version
cp -r /opt/wekeza_dfs /opt/wekeza_dfs_backup_$(date +%Y%m%d)

# Pull updates
cd /opt/wekeza_dfs
git pull origin main

# Update dependencies
source venv_prod/bin/activate
pip install -r requirements.txt --upgrade

# Run database migrations (if any)
python database_migrations.py

# Start application
sudo systemctl start wekeza-branch-ops

# Verify update
curl http://localhost:8501
```

#### **Database Updates**
```bash
# Backup database before updates
mysqldump -u root -p wekeza_dfs_db > pre_update_backup.sql

# Run update scripts
python update_database_schema.py

# Verify database integrity
python check_database.py
```

### **3. Monitoring & Logging**

#### **Setup Log Rotation**
```bash
# Create logrotate configuration
sudo cat > /etc/logrotate.d/wekeza-branch-ops << EOF
/var/log/wekeza-branch-ops/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 wekeza wekeza
}
EOF
```

#### **Performance Monitoring**
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Monitor system resources
htop
iotop
nethogs

# Monitor MySQL performance
mysql -u root -p -e "SHOW PROCESSLIST;"
mysql -u root -p -e "SHOW STATUS LIKE 'Threads_connected';"
```

---

## 📞 Support & Resources

### **Documentation**
- **User Guide**: README.md
- **API Documentation**: Available in each module
- **Database Schema**: Database Schema.docx
- **Testing Guide**: TESTING_GUIDE.md

### **Support Channels**
- **Technical Issues**: Create issue in repository
- **Installation Help**: Check troubleshooting section
- **Feature Requests**: Submit enhancement requests
- **Security Issues**: Report via secure channels

### **Useful Commands Reference**

```bash
# Quick system check
systemctl status wekeza-branch-ops mysql nginx

# View logs
journalctl -u wekeza-branch-ops -n 50
tail -f /var/log/mysql/error.log

# Database quick check
mysql -u root -p -e "SELECT COUNT(*) FROM wekeza_dfs_db.transactions;"

# Application restart
sudo systemctl restart wekeza-branch-ops

# Full system restart
sudo systemctl restart wekeza-branch-ops mysql nginx
```

---

## ✅ Installation Checklist

- [ ] Python 3.8+ installed and configured
- [ ] MySQL Server 8.0+ installed and running
- [ ] Database `wekeza_dfs_db` created
- [ ] All database tables created successfully
- [ ] Sample data inserted and verified
- [ ] Virtual environment created and activated
- [ ] All Python dependencies installed
- [ ] Application starts without errors
- [ ] All modules load successfully
- [ ] Login functionality working
- [ ] Database connections established
- [ ] Core transactions working
- [ ] System performance acceptable
- [ ] Backup procedures configured
- [ ] Monitoring setup completed
- [ ] Documentation reviewed

---

**Installation Complete! 🎉**

Your Wekeza DFS Branch Operations System is now ready for use. Access the application at http://localhost:8501 and login with the provided credentials to start using the system.

For any issues or questions, refer to the troubleshooting section or contact the development team.

---

*Last Updated: January 4, 2026*  
*Version: 2.0.0*  
*Wekeza DFS Development Team*