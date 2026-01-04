import mysql.connector
from datetime import datetime

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='wekeza_dfs_db'
)
cursor = conn.cursor()

print("🛡️ Updating insurance claims table structure...")

# Check current structure
cursor.execute("DESCRIBE insurance_claims")
columns = cursor.fetchall()
print("Current columns:")
for col in columns:
    print(f"  - {col[0]} ({col[1]})")

# Add missing columns if they don't exist
try:
    cursor.execute("ALTER TABLE insurance_claims ADD COLUMN claim_reference VARCHAR(50)")
    print("✅ Added claim_reference column")
except:
    print("ℹ️ claim_reference column already exists")

try:
    cursor.execute("ALTER TABLE insurance_claims ADD COLUMN claim_type VARCHAR(100)")
    print("✅ Added claim_type column")
except:
    print("ℹ️ claim_type column already exists")

try:
    cursor.execute("ALTER TABLE insurance_claims ADD COLUMN description TEXT")
    print("✅ Added description column")
except:
    print("ℹ️ description column already exists")

try:
    cursor.execute("ALTER TABLE insurance_claims ADD COLUMN status ENUM('PENDING', 'APPROVED', 'REJECTED', 'PAID') DEFAULT 'PENDING'")
    print("✅ Added status column")
except:
    print("ℹ️ status column already exists")

conn.commit()
conn.close()

print("✅ Insurance claims table updated successfully!")