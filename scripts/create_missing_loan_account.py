#!/usr/bin/env python3

import mysql.connector
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

def create_missing_loan_account():
    """Create the missing loan account entry for the disbursed loan"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor(dictionary=True)
        
        print("🔧 Creating missing loan account entry...")
        
        # Get the loan application details
        cursor.execute("""
            SELECT la.*, u.full_name 
            FROM loan_applications la
            JOIN accounts a ON la.account_number = a.account_number
            JOIN users u ON a.user_id = u.user_id
            WHERE la.application_id = 'LA202601042130516F'
        """)
        
        loan_app = cursor.fetchone()
        
        if not loan_app:
            print("❌ Loan application LA202601042130516F not found")
            return
        
        print(f"✅ Found loan application:")
        print(f"  - Application ID: {loan_app['application_id']}")
        print(f"  - Customer: {loan_app['full_name']}")
        print(f"  - Amount: KES {loan_app['loan_amount']:,.2f}")
        print(f"  - Type: {loan_app['loan_type']}")
        
        # Generate loan ID
        loan_id = f"LN{datetime.now().strftime('%Y%m%d')}004"  # Next in sequence
        
        # Calculate dates
        disbursement_date = date.today()
        next_payment_date = disbursement_date + relativedelta(months=1)
        maturity_date = disbursement_date + relativedelta(months=loan_app['tenure_months'])
        
        # Create loan account entry
        cursor.execute("""
            INSERT INTO loan_accounts (
                loan_id, application_id, account_number, customer_name, loan_type,
                principal_amount, outstanding_balance, interest_rate, tenure_months,
                monthly_payment, next_payment_date, disbursement_date, maturity_date,
                status, days_overdue, created_by, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            loan_id, loan_app['application_id'], loan_app['account_number'], 
            loan_app['full_name'], loan_app['loan_type'],
            loan_app['loan_amount'], loan_app['loan_amount'],  # Outstanding = Principal initially
            loan_app['interest_rate'], loan_app['tenure_months'],
            loan_app['monthly_payment'], next_payment_date, disbursement_date, maturity_date,
            'ACTIVE', 0, 'SYSTEM_FIX', datetime.now(), datetime.now()
        ))
        
        print(f"\n✅ Created loan account entry:")
        print(f"  - Loan ID: {loan_id}")
        print(f"  - Outstanding Balance: KES {loan_app['loan_amount']:,.2f}")
        print(f"  - Monthly Payment: KES {loan_app['monthly_payment']:,.2f}")
        print(f"  - Next Payment: {next_payment_date}")
        print(f"  - Maturity: {maturity_date}")
        
        # Update loan application status to DISBURSED
        cursor.execute("""
            UPDATE loan_applications 
            SET status = 'DISBURSED' 
            WHERE application_id = %s
        """, (loan_app['application_id'],))
        
        print(f"\n✅ Updated loan application status to DISBURSED")
        
        conn.commit()
        conn.close()
        
        print(f"\n🎉 LOAN ACCOUNT CREATED SUCCESSFULLY!")
        print(f"✅ Personal banking portal should now show this as an active loan")
        print(f"✅ Loan payments should now work from personal banking")
        
    except Exception as e:
        print(f"❌ Error creating loan account: {e}")

if __name__ == "__main__":
    create_missing_loan_account()