import mysql.connector
import pandas as pd

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='wekeza_dfs_db'
)

print("🏪 Branches:")
df_branches = pd.read_sql("SELECT * FROM branches", conn)
print(df_branches.to_string(index=False))

print("\n👥 Staff:")
df_staff = pd.read_sql("""
SELECT s.staff_code, s.full_name, s.email, s.role, b.branch_name, s.is_active
FROM staff s
LEFT JOIN branches b ON s.branch_id = b.branch_id
""", conn)
print(df_staff.to_string(index=False))

conn.close()