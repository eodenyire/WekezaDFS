# 🚀 Quick Start Guide - Wekeza DFS Branch Operations System

## ⚡ 5-Minute Setup

### **Prerequisites Check**
- ✅ Python 3.8+ installed
- ✅ MySQL Server running
- ✅ Git installed (optional)

### **1. Download/Clone**
```bash
# If using Git
git clone [repository-url]
cd wekeza_dfs_platform/03_Source_Code/branch_operations

# Or download and extract files, then navigate to:
cd path/to/wekeza_dfs_platform/03_Source_Code/branch_operations
```

### **2. Automated Setup**
```bash
# Run the setup script
python setup.py
```

### **3. Start Application**

#### **Windows**
```bash
# Double-click or run:
start_branch_operations.bat
```

#### **macOS/Linux**
```bash
# Make executable and run:
chmod +x start_branch_operations.sh
./start_branch_operations.sh
```

#### **Manual Start**
```bash
# Activate virtual environment
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Start application
streamlit run main_branch_system.py --server.port 8501
```

### **4. Access & Login**
- **URL**: http://localhost:8501
- **Staff Code**: SUP001
- **Password**: password123

---

## 🎯 What You Get

### **5 Complete Banking Modules**
1. **Teller Operations** - Cash transactions, transfers, bill payments
2. **Supervision** - Transaction approvals, reversals, exception handling
3. **Customer Operations** - Account opening, CIF creation, maintenance
4. **Credit Operations** - Loan products, applications, disbursements
5. **Bancassurance** - Insurance sales, premium collection, claims

### **Real Database Integration**
- Live MySQL database with sample data
- Cross-platform transaction synchronization
- Complete audit trail and reporting

### **Role-Based Access**
- TELLER: Teller operations only
- SUPERVISOR: Multiple modules access
- BRANCH_MANAGER/ADMIN: Full system access

---

## 🔧 Troubleshooting

### **Setup Issues**
```bash
# MySQL connection failed
# Solution: Start MySQL service and verify credentials

# Python version error
# Solution: Install Python 3.8+ and add to PATH

# Dependencies failed
# Solution: pip install -r requirements.txt
```

### **Application Issues**
```bash
# Port already in use
streamlit run main_branch_system.py --server.port 8502

# Module not found
# Solution: Ensure you're in the correct directory
cd wekeza_dfs_platform/03_Source_Code/branch_operations
```

---

## 📚 Documentation

- **README.md** - Complete system documentation
- **INSTALLATION.md** - Detailed installation guide
- **requirements.txt** - Python dependencies
- **setup.py** - Automated setup script

---

## 🎉 Success!

If you can login and see the module selection screen, you're ready to go!

**Next Steps:**
1. Explore each module with the SUP001 account
2. Test transactions with sample accounts (ACC1000014, ACC1000015)
3. Review the complete documentation in README.md
4. Configure for your specific environment

---

*Need help? Check INSTALLATION.md for detailed troubleshooting or contact the development team.*