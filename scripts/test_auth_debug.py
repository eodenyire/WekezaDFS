import mysql.connector

def test_authentication(staff_code, password, branch_code):
    """Test authentication with debug info"""
    print(f"🔍 Testing authentication for: {staff_code} / {password} / {branch_code}")
    
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        
        cursor = conn.cursor(dictionary=True)
        
        # First, let's see if the staff exists
        cursor.execute("""
            SELECT s.*, b.branch_name, b.branch_code as branch_code_db
            FROM staff s 
            JOIN branches b ON s.branch_id = b.branch_id 
            WHERE s.staff_code = %s
        """, (staff_code,))
        
        staff = cursor.fetchone()
        
        if not staff:
            print(f"❌ Staff {staff_code} not found in database")
            return None
            
        print(f"✅ Staff found: {staff['full_name']}")
        print(f"   - Role: {staff['role']}")
        print(f"   - Branch: {staff['branch_code_db']} ({staff['branch_name']})")
        print(f"   - Active: {staff['is_active']}")
        print(f"   - Password in DB: '{staff['password_hash']}'")
        print(f"   - Password provided: '{password}'")
        
        # Check if staff is active
        if not staff['is_active']:
            print(f"❌ Staff {staff_code} is not active")
            return None
            
        # Check password
        if staff['password_hash'] != password:
            print(f"❌ Password mismatch!")
            print(f"   Expected: '{staff['password_hash']}'")
            print(f"   Got: '{password}'")
            return None
        else:
            print(f"✅ Password matches!")
            
        # Check branch code
        if staff['branch_code_db'] != branch_code:
            print(f"❌ Branch code mismatch!")
            print(f"   Expected: '{staff['branch_code_db']}'")
            print(f"   Got: '{branch_code}'")
            return None
        else:
            print(f"✅ Branch code matches!")
            
        conn.close()
        print(f"🎉 Authentication successful for {staff_code}!")
        return staff
        
    except Exception as e:
        print(f"💥 Authentication error: {e}")
        return None

# Test the accounts
print("🧪 Testing authentication for all accounts...\n")

test_cases = [
    ("TELLER001", "teller123", "BR001"),
    ("SUP001", "supervisor123", "BR001"),
    ("ADMIN001", "admin", "HQ001"),
    ("EG-74255", "password123", "BR001"),
]

for staff_code, password, branch_code in test_cases:
    print("=" * 60)
    result = test_authentication(staff_code, password, branch_code)
    print()