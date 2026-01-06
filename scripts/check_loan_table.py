import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='wekeza_dfs_db'
)
cursor = conn.cursor()

print("📋 Checking loans table structure...")
cursor.execute("DESCRIBE loans")
columns = cursor.fetchall()

print("Current columns:")
for col in columns:
    print(f"  - {col[0]} ({col[1]})")

print("\n📊 Current loans data:")
cursor.execute("SELECT * FROM loans LIMIT 5")
loans = cursor.fetchall()
for loan in loans:
    print(f"  {loan}")

conn.close()