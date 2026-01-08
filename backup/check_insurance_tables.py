import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='wekeza_dfs_db'
)
cursor = conn.cursor()

print("📋 Checking insurance tables structure...")

print("\n🛡️ Insurance Products:")
cursor.execute("DESCRIBE insurance_products")
columns = cursor.fetchall()
for col in columns:
    print(f"  - {col[0]} ({col[1]})")

print("\n📋 Current insurance products:")
cursor.execute("SELECT * FROM insurance_products")
products = cursor.fetchall()
for product in products:
    print(f"  {product}")

print("\n👤 User Policies:")
cursor.execute("DESCRIBE user_policies")
columns = cursor.fetchall()
for col in columns:
    print(f"  - {col[0]} ({col[1]})")

print("\n📋 Current user policies:")
cursor.execute("SELECT * FROM user_policies")
policies = cursor.fetchall()
for policy in policies:
    print(f"  {policy}")

conn.close()