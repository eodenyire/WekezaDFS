#!/usr/bin/env python3

import mysql.connector

def simple_loan_check():
    """Simple check of loan tables"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor(dictionary=True)
        
        print("🔍 Checking loan data for ACC1000014...")
        
        # Check loan_accounts table
        print("\n📋 LOAN_ACCOUNTS (Active Loans):")
        cursor.execute("SELECT * FROM loan_accounts WHERE application_id = 'LA202601042130516F'")
        loan_account = cursor.fetchone()
        
        if loan_account:
            print(f"✅ Found active loan:")
            print(f"  - Loan ID: {loan_account['loan_id']}")
            print(f"  - Outstanding: KES {loan_account['outstanding_balance']:,.2f}")
            print(f"  - Monthly Payment: KES {loan_account['monthly_payment']:,.2f}")
            print(f"  - Status: {loan_account['status']}")
        else:
            print("❌ No active loan found in loan_accounts")
        
        # Check loan_applications table
        print(f"\n📋 LOAN_APPLICATIONS:")
        cursor.execute("SELECT * FROM loan_applications WHERE application_id = 'LA202601042130516F'")
        loan_app = cursor.fetchone()
        
        if loan_app:
            print(f"✅ Found loan application:")
            print(f"  - Status: {loan_app['status']}")
            print(f"  - Amount: KES {loan_app['loan_amount']:,.2f}")
        else:
            print("❌ No loan application found")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    simple_loan_check()