import mysql.connector
from datetime import datetime

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='wekeza_dfs_db'
)
cursor = conn.cursor()

print("🏢 Creating branches and staff management tables...")

# Create branches table
cursor.execute("""
CREATE TABLE IF NOT EXISTS branches (
    branch_id INT AUTO_INCREMENT PRIMARY KEY,
    branch_code VARCHAR(10) UNIQUE NOT NULL,
    branch_name VARCHAR(100) NOT NULL,
    location VARCHAR(200) NOT NULL,
    phone_number VARCHAR(20),
    email VARCHAR(100),
    manager_id INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
)
""")

# Create staff table
cursor.execute("""
CREATE TABLE IF NOT EXISTS staff (
    staff_id INT AUTO_INCREMENT PRIMARY KEY,
    staff_code VARCHAR(20) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone_number VARCHAR(20),
    national_id VARCHAR(20) UNIQUE,
    role ENUM('TELLER', 'RELATIONSHIP_MANAGER', 'SUPERVISOR', 'BRANCH_MANAGER', 'ADMIN') NOT NULL,
    branch_id INT,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    hire_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id) ON DELETE SET NULL
)
""")

# Insert default main branch
cursor.execute("""
INSERT IGNORE INTO branches (branch_code, branch_name, location, phone_number, email, is_active)
VALUES ('HQ001', 'Head Office', 'Nairobi CBD, Kenya', '+254700000000', 'hq@wekeza.co.ke', TRUE)
""")

cursor.execute("""
INSERT IGNORE INTO branches (branch_code, branch_name, location, phone_number, email, is_active)
VALUES ('BR001', 'Main Branch', 'Westlands, Nairobi', '+254700000001', 'main@wekeza.co.ke', TRUE)
""")

# Insert default staff members
cursor.execute("""
INSERT IGNORE INTO staff (staff_code, full_name, email, phone_number, national_id, role, branch_id, password_hash, hire_date)
VALUES 
('ADMIN001', 'System Administrator', 'admin@wekeza.co.ke', '+254700000000', '12345678', 'ADMIN', 1, 'admin', '2026-01-01'),
('TELLER001', 'John Doe', 'teller001@wekeza.co.ke', '+254700000001', '12345679', 'TELLER', 2, 'teller123', '2026-01-01'),
('MGR001', 'Jane Smith', 'manager001@wekeza.co.ke', '+254700000002', '12345680', 'BRANCH_MANAGER', 2, 'manager123', '2026-01-01'),
('RM001', 'Peter Kamau', 'rm001@wekeza.co.ke', '+254700000003', '12345681', 'RELATIONSHIP_MANAGER', 2, 'rm123', '2026-01-01'),
('SUP001', 'Mary Wanjiku', 'supervisor001@wekeza.co.ke', '+254700000004', '12345682', 'SUPERVISOR', 2, 'supervisor123', '2026-01-01')
""")

# Update branches table to set manager_id for main branch
cursor.execute("""
UPDATE branches SET manager_id = (SELECT staff_id FROM staff WHERE staff_code = 'MGR001') WHERE branch_code = 'BR001'
""")

conn.commit()
conn.close()

print("✅ Branches and staff tables created successfully!")
print("✅ Default branches and staff members added!")
print("\n📋 Default Staff Credentials:")
print("- Admin: admin@wekeza.co.ke / admin")
print("- Teller: teller001@wekeza.co.ke / teller123") 
print("- Manager: manager001@wekeza.co.ke / manager123")
print("- RM: rm001@wekeza.co.ke / rm123")
print("- Supervisor: supervisor001@wekeza.co.ke / supervisor123")