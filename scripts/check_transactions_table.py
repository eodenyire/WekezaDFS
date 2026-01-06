import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='wekeza_dfs_db'
)

cursor = conn.cursor()

print("📋 Checking transactions table structure...")
cursor.execute("DESCRIBE transactions")
columns = cursor.fetchall()

print("Current columns:")
for col in columns:
    print(f"  - {col[0]} ({col[1]})")

print("\n📊 Sample transactions data:")
cursor.execute("SELECT * FROM transactions LIMIT 5")
transactions = cursor.fetchall()

if transactions:
    # Get column names
    cursor.execute("SHOW COLUMNS FROM transactions")
    column_names = [col[0] for col in cursor.fetchall()]
    print(f"Columns: {column_names}")
    
    for txn in transactions:
        print(f"  {txn}")
else:
    print("  No transactions found")

conn.close()