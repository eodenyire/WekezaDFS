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

# Insert test staff accounts with plain text passwords (like customer/business portals)
test_staff = [
    ("STAFF001", "John Manager", "john.manager@wekeza.co.ke", "+254700000010", "12345678", "BRANCH_MANAGER", 1, "password123"),
    ("TELLER001", "Jane Teller", "jane.teller@wekeza.co.ke", "+254700000011", "12345679", "TELLER", 2, "password123"),
    ("REL001", "Bob Relationship", "bob.rel@wekeza.co.ke", "+254700000012", "12345680", "RELATIONSHIP_MANAGER", 2, "password123"),
    ("SUP001", "Alice Supervisor", "alice.sup@wekeza.co.ke", "+254700000013", "12345681", "SUPERVISOR", 2, "password123"),
    ("ADMIN001", "Admin User", "admin@wekeza.co.ke", "+254700000014", "12345682", "ADMIN", 1, "password123"),
    ("TELLER002", "Mary Teller", "mary.teller@wekeza.co.ke", "+254700000015", "12345683", "TELLER", 2, "password123"),
    ("CREDIT001", "Tom Credit", "tom.credit@wekeza.co.ke", "+254700000016", "12345684", "RELATIONSHIP_MANAGER", 2, "password123"),
    ("CASH001", "Sarah Cash", "sarah.cash@wekeza.co.ke", "+254700000017", "12345685", "SUPERVISOR", 2, "password123"),
]

for staff_data in test_staff:
    cursor.execute("""
        INSERT IGNORE INTO staff (staff_code, full_name, email, phone_number, national_id, role, branch_id, password_hash, is_active, hire_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE, CURDATE())
    """, staff_data)

# Update branches table to set manager_id for main branch
cursor.execute("""
UPDATE branches SET manager_id = (SELECT staff_id FROM staff WHERE staff_code = 'STAFF001') WHERE branch_code = 'HQ001'
""")

cursor.execute("""
UPDATE branches SET manager_id = (SELECT staff_id FROM staff WHERE staff_code = 'TELLER001') WHERE branch_code = 'BR001'
""")

conn.commit()
conn.close()

print("✅ Branches and staff tables created successfully!")
print("✅ Test staff accounts created with PLAIN TEXT passwords (like customer/business portals):")
print("- STAFF001 (Branch Manager) - HQ001")
print("- TELLER001, TELLER002 (Tellers) - BR001") 
print("- REL001 (Relationship Manager) - BR001")
print("- SUP001 (Supervisor) - BR001")
print("- ADMIN001 (Admin) - HQ001")
print("- CREDIT001 (Credit Officer) - BR001")
print("- CASH001 (Cash Officer) - BR001")
print("All passwords: password123")
print("\n🔑 Login Examples:")
print("- Staff Code: TELLER001 | Password: password123 | Branch: BR001")
print("- Staff Code: STAFF001 | Password: password123 | Branch: HQ001")
print("- Staff Code: SUP001 | Password: password123 | Branch: BR001")