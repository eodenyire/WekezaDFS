import mysql.connector

print("🧹 Clearing users table data...")

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='wekeza_dfs_db'
)
cursor = conn.cursor()

# Clear users table
cursor.execute("DELETE FROM users")
print(f"✅ Cleared {cursor.rowcount} users")

# Check what's left
cursor.execute("SELECT COUNT(*) FROM users")
count = cursor.fetchone()[0]
print(f"📊 Users table now has {count} records")

conn.commit()
conn.close()

print("🎉 Done! Users table is now empty and ready for admin panel to create new users.")