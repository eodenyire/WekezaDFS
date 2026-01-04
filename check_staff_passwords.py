import mysql.connector
import pandas as pd

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='wekeza_dfs_db'
)

print("🔑 Checking staff passwords...")

cursor = conn.cursor(dictionary=True)
cursor.execute("""
    SELECT s.staff_code, s.full_name, s.password_hash, s.role, b.branch_code, b.branch_name
    FROM staff s 
    JOIN branches b ON s.branch_id = b.branch_id 
    WHERE s.is_active = TRUE
    ORDER BY s.staff_code
""")

staff_list = cursor.fetchall()

for staff in staff_list:
    print(f"Staff: {staff['staff_code']} | Name: {staff['full_name']} | Role: {staff['role']}")
    print(f"Branch: {staff['branch_code']} | Password: {staff['password_hash']}")
    print("---")

conn.close()

print("\n✅ Staff accounts ready for testing!")
print("Try logging in with:")
print("- TELLER001 / password123 / BR001")
print("- SUP001 / password123 / BR001") 
print("- STAFF001 / password123 / HQ001")