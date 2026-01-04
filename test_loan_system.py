import mysql.connector
from datetime import datetime, timedelta

# Test the loan system
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='wekeza_dfs_db'
)
cursor = conn.cursor(dictionary=True)

print("🧪 Testing Loan System...")

# Get a test user
cursor.execute("SELECT user_id, full_name, email FROM users WHERE business_id IS NULL LIMIT 1")
test_user = cursor.fetchone()

if test_user:
    print(f"📋 Test User: {test_user['full_name']} ({test_user['email']})")
    
    # Create a test loan application
    loan_amount = 25000.0
    interest_rate = 12.0
    interest_amount = loan_amount * (interest_rate / 100)
    total_due = loan_amount + interest_amount
    due_date = datetime.now() + timedelta(days=90)
    
    cursor.execute("""
        INSERT INTO loans (user_id, principal_amount, interest_rate, interest_amount, 
                         total_due_amount, balance_remaining, due_date, status, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'PENDING', %s)
    """, (test_user['user_id'], loan_amount, interest_rate, interest_amount, 
          total_due, total_due, due_date, datetime.now()))
    
    loan_id = cursor.lastrowid
    conn.commit()
    
    print(f"✅ Test loan created: ID {loan_id}")
    print(f"   Amount: KES {loan_amount:,.2f}")
    print(f"   Interest: {interest_rate}% (KES {interest_amount:,.2f})")
    print(f"   Total Due: KES {total_due:,.2f}")
    print(f"   Status: PENDING")
    
    # Check user's account balance before
    cursor.execute("SELECT balance FROM accounts WHERE user_id = %s", (test_user['user_id'],))
    account = cursor.fetchone()
    if account:
        print(f"   Account Balance Before: KES {account['balance']:,.2f}")
    
    print("\n🔄 Loan is ready for admin approval!")
    print("   1. Go to Admin Portal → Manage Loans → Approve/Reject")
    print(f"   2. Approve Loan ID: {loan_id}")
    print("   3. Funds will be automatically disbursed to user account")
    print("   4. User can then make repayments from Customer Portal")

else:
    print("❌ No test user found!")

conn.close()