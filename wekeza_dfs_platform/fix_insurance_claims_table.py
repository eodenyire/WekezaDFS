import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='wekeza_dfs_db'
)
cursor = conn.cursor()

print("🛡️ Fixing insurance claims table...")

# Add missing columns
try:
    cursor.execute("ALTER TABLE insurance_claims ADD COLUMN claim_amount DECIMAL(15,2) DEFAULT 0.00")
    print("✅ Added claim_amount column")
except:
    print("ℹ️ claim_amount column already exists")

try:
    cursor.execute("ALTER TABLE insurance_claims ADD COLUMN user_id INT")
    print("✅ Added user_id column")
except:
    print("ℹ️ user_id column already exists")

conn.commit()
conn.close()

print("✅ Insurance claims table fixed!")