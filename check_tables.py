import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='wekeza_dfs_db'
)
cursor = conn.cursor()

print("📋 All tables in database:")
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()

for table in tables:
    print(f"  - {table[0]}")

conn.close()