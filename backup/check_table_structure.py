import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='wekeza_dfs_db'
)
cursor = conn.cursor()

print("📋 Checking user_policies table structure...")
cursor.execute("DESCRIBE user_policies")
columns = cursor.fetchall()

print("Current columns:")
for col in columns:
    print(f"  - {col[0]} ({col[1]})")

conn.close()