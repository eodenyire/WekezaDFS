import mysql.connector
from datetime import datetime, timedelta
import uuid

# Test the insurance system
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='wekeza_dfs_db'
)
cursor = conn.cursor(dictionary=True)

print("🛡️ Testing Insurance System...")

# Check insurance products
cursor.execute("SELECT * FROM insurance_products WHERE is_active = 1")
products = cursor.fetchall()

print(f"📋 Available Insurance Products: {len(products)}")
for product in products:
    print(f"  {product['product_id']}. {product['product_name']} - KES {product['premium_amount']}/month")

# Get a test user
cursor.execute("SELECT user_id, full_name, email FROM users WHERE business_id IS NULL LIMIT 1")
test_user = cursor.fetchone()

if test_user:
    print(f"\n👤 Test User: {test_user['full_name']} ({test_user['email']})")
    
    # Check user's account balance
    cursor.execute("SELECT balance FROM accounts WHERE user_id = %s", (test_user['user_id'],))
    account = cursor.fetchone()
    if account:
        print(f"   Account Balance: KES {account['balance']:,.2f}")
    
    # Create a test insurance policy
    if products:
        test_product = products[0]  # Personal Accident Cover
        policy_number = f"POL{uuid.uuid4().hex[:8].upper()}"
        
        start_date = datetime.now().date()
        end_date = datetime(start_date.year + 1, start_date.month, start_date.day).date()
        
        cursor.execute("""
            INSERT INTO user_policies (user_id, product_id, policy_number, start_date, end_date, 
                                     status, auto_renew, premium_paid, cover_amount, created_at)
            VALUES (%s, %s, %s, %s, %s, 'ACTIVE', 1, %s, %s, %s)
        """, (test_user['user_id'], test_product['product_id'], policy_number, start_date, end_date,
              test_product['premium_amount'], test_product['cover_amount'], datetime.now()))
        
        policy_id = cursor.lastrowid
        
        # Create a test insurance claim
        claim_ref = f"CLM{uuid.uuid4().hex[:8].upper()}"
        cursor.execute("""
            INSERT INTO insurance_claims (policy_id, user_id, claim_reference, claim_type, claim_amount, 
                                        description, status, created_at)
            VALUES (%s, %s, %s, 'Medical Emergency', 15000.00, 'Emergency hospital treatment', 'SUBMITTED', %s)
        """, (policy_id, test_user['user_id'], claim_ref, datetime.now()))
        
        claim_id = cursor.lastrowid
        conn.commit()
        
        print(f"\n✅ Test insurance policy created:")
        print(f"   Policy Number: {policy_number}")
        print(f"   Product: {test_product['product_name']}")
        print(f"   Premium: KES {test_product['premium_amount']}/month")
        print(f"   Coverage: KES {test_product['cover_amount']:,.2f}")
        print(f"   Status: ACTIVE")
        
        print(f"\n✅ Test insurance claim created:")
        print(f"   Claim Reference: {claim_ref}")
        print(f"   Claim Type: Medical Emergency")
        print(f"   Claim Amount: KES 15,000.00")
        print(f"   Status: SUBMITTED")
        
        print(f"\n🔄 System is ready for testing!")
        print(f"   1. Go to Customer Portal → Insure tab")
        print(f"   2. View 'My Policies' to see the test policy")
        print(f"   3. Go to Admin Portal → Manage Insurance")
        print(f"   4. Process the pending claim (ID: {claim_id})")

else:
    print("❌ No test user found!")

conn.close()