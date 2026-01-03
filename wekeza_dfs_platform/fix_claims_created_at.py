import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='wekeza_dfs_db'
)
cursor = conn.cursor()

print("🛡️ Adding created_at to insurance_claims table...")

try:
    cursor.execute("ALTER TABLE insurance_claims ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    print("✅ Added created_at column")
except:
    print("ℹ️ created_at column already exists")

# Check the current structure
cursor.execute("DESCRIBE insurance_claims")
columns = cursor.fetchall()
print("\nCurrent insurance_claims columns:")
for col in columns:
    print(f"  - {col[0]} ({col[1]})")

conn.commit()
conn.close()

print("✅ Insurance claims table updated!")