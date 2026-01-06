#!/usr/bin/env python3

import mysql.connector
from datetime import datetime
import uuid
from decimal import Decimal

def make_test_payment():
    """Make a test loan payment to verify the system works"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor(dictionary=True)
        
        print("💳 Making test loan payment...")
        
        # Get the active loan and user info
        cursor.execute("""
            SELECT lac.*, a.user_id, a.balance
            FROM loan_accounts lac
            JOIN accounts a ON lac.account_number = a.account_number
            WHERE lac.loan_id = 'LN20260104004' AND lac.status = 'ACTIVE'
        """)
        
        loan = cursor.fetchone()
        if not loan:
            print("❌ No active loan found")
            return
        
        print(f"✅ Found active loan:")
        print(f"  - Loan ID: {loan['loan_id']}")
        print(f"  - Outstanding Balance: KES {loan['outstanding_balance']:,.2f}")
        print(f"  - Account Balance: KES {loan['balance']:,.2f}")
        
        # Make a test payment of KES 1,000
        payment_amount = Decimal('1000.00')
        
        if loan['balance'] < payment_amount:
            print(f"❌ Insufficient balance for payment of KES {payment_amount}")
            return
        
        # Calculate principal and interest portions
        payment_float = float(payment_amount)
        principal_amount = payment_float * 0.8  # 80% to principal
        interest_amount = payment_float * 0.2   # 20% to interest
        
        # Generate payment ID
        payment_id = f"LP{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:4].upper()}"
        
        print(f"\n💰 Processing payment:")
        print(f"  - Payment Amount: KES {payment_amount}")
        print(f"  - Principal: KES {principal_amount:.2f}")
        print(f"  - Interest: KES {interest_amount:.2f}")
        print(f"  - Payment ID: {payment_id}")
        
        # Update account balance
        cursor.execute("UPDATE accounts SET balance = balance - %s WHERE user_id = %s", 
                      (payment_amount, loan['user_id']))
        
        # Record loan payment
        cursor.execute("""
            INSERT INTO loan_payments (payment_id, loan_id, payment_amount, principal_amount, 
                                     interest_amount, payment_date, payment_method, processed_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (payment_id, loan['loan_id'], payment_amount, principal_amount, 
              interest_amount, datetime.now().date(), 'Account Balance', f"USER_{loan['user_id']}"))
        
        # Update outstanding balance
        cursor.execute("""
            UPDATE loan_accounts SET outstanding_balance = outstanding_balance - %s,
                                   updated_at = %s
            WHERE loan_id = %s
        """, (principal_amount, datetime.now(), loan['loan_id']))
        
        # Record transaction
        ref_code = f"LRP{uuid.uuid4().hex[:8].upper()}"
        cursor.execute("""
            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
            SELECT account_id, 'LOAN_REPAYMENT', %s, %s, %s, %s
            FROM accounts WHERE user_id = %s
        """, (payment_amount, ref_code, f"Loan payment for {loan['loan_type']} - {loan['loan_id']}", 
              datetime.now(), loan['user_id']))
        
        conn.commit()
        
        # Get updated balances
        cursor.execute("SELECT outstanding_balance FROM loan_accounts WHERE loan_id = %s", (loan['loan_id'],))
        updated_loan = cursor.fetchone()
        
        cursor.execute("SELECT balance FROM accounts WHERE user_id = %s", (loan['user_id'],))
        updated_account = cursor.fetchone()
        
        conn.close()
        
        print(f"\n✅ Payment processed successfully!")
        print(f"  - New Outstanding Balance: KES {updated_loan['outstanding_balance']:,.2f}")
        print(f"  - New Account Balance: KES {updated_account['balance']:,.2f}")
        print(f"  - Transaction Reference: {ref_code}")
        
        print(f"\n🎉 Test payment completed! You can now test the personal banking portal.")
        
    except Exception as e:
        print(f"❌ Payment failed: {e}")
        import traceback
        print(f"Error details: {traceback.format_exc()}")

if __name__ == "__main__":
    make_test_payment()