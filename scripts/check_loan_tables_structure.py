#!/usr/bin/env python3

import mysql.connector

def check_loan_tables_structure():
    """Check the structure and data in loan-related tables"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor(dictionary=True)
        
        print("🔍 Checking loan-related tables for ACC1000014...")
        
        # Check loan_applications table
        print("\n📋 1. LOAN_APPLICATIONS Table:")
        cursor.execute("""
            SELECT application_id, loan_type, loan_amount, status, created_at, approved_at
            FROM loan_applications 
            WHERE account_number = 'ACC1000014'
            ORDER BY created_at DESC
        """)
        loan_apps = cursor.fetchall()
        
        if loan_apps:
            for app in loan_apps:
                print(f"  - {app['application_id']}: {app['loan_type']} - KES {app['loan_amount']:,.2f} - {app['status']}")
        else:
            print("  - No entries found")
        
        # Check loan_accounts table (where active loans are stored)
        print("\n📋 2. LOAN_ACCOUNTS Table:")
        cursor.execute("""
            SELECT loan_id, application_id, loan_amount, outstanding_balance, 
                   monthly_payment, status, disbursement_date, maturity_date
            FROM loan_accounts 
            WHERE application_id IN (
                SELECT application_id FROM loan_applications WHERE account_number = 'ACC1000014'
            )
            ORDER BY disbursement_date DESC
        """)
        loan_accounts = cursor.fetchall()
        
        if loan_accounts:
            for acc in loan_accounts:
                print(f"  - Loan ID: {acc['loan_id']}")
                print(f"    Application: {acc['application_id']}")
                print(f"    Amount: KES {acc['loan_amount']:,.2f}")
                print(f"    Outstanding: KES {acc['outstanding_balance']:,.2f}")
                print(f"    Monthly Payment: KES {acc['monthly_payment']:,.2f}")
                print(f"    Status: {acc['status']}")
                print(f"    Disbursed: {acc['disbursement_date']}")
                print("    ---")
        else:
            print("  - No entries found")
        
        # Check loan_payments table
        print("\n📋 3. LOAN_PAYMENTS Table:")
        cursor.execute("""
            SELECT lp.payment_id, lp.loan_id, lp.payment_amount, lp.payment_date, lp.payment_type
            FROM loan_payments lp
            JOIN loan_accounts la ON lp.loan_id = la.loan_id
            JOIN loan_applications lap ON la.application_id = lap.application_id
            WHERE lap.account_number = 'ACC1000014'
            ORDER BY lp.payment_date DESC
            LIMIT 5
        """)
        loan_payments = cursor.fetchall()
        
        if loan_payments:
            for payment in loan_payments:
                print(f"  - Payment ID: {payment['payment_id']}")
                print(f"    Loan ID: {payment['loan_id']}")
                print(f"    Amount: KES {payment['payment_amount']:,.2f}")
                print(f"    Date: {payment['payment_date']}")
                print(f"    Type: {payment['payment_type']}")
                print("    ---")
        else:
            print("  - No entries found")
        
        # Check what the personal banking portal is currently querying
        print("\n📋 4. What Personal Banking Portal Currently Sees:")
        cursor.execute("""
            SELECT la.application_id, la.loan_type, la.loan_amount, la.status
            FROM loan_applications la
            WHERE la.account_number = 'ACC1000014' AND la.status = 'ACTIVE'
        """)
        active_loans_pb = cursor.fetchall()
        
        if active_loans_pb:
            print("  - Personal Banking sees these as ACTIVE loans:")
            for loan in active_loans_pb:
                print(f"    {loan['application_id']}: {loan['loan_type']} - KES {loan['loan_amount']:,.2f}")
        else:
            print("  - Personal Banking sees NO active loans (this is the problem!)")
        
        conn.close()
        
        print("\n🎯 DIAGNOSIS:")
        if loan_accounts and not active_loans_pb:
            print("❌ PROBLEM IDENTIFIED:")
            print("  - Loans exist in loan_accounts (branch operations can see them)")
            print("  - But loan_applications status is not 'ACTIVE' (personal banking can't see them)")
            print("  - Personal banking needs to query loan_accounts table for active loans")
        
    except Exception as e:
        print(f"❌ Error checking loan tables: {e}")

if __name__ == "__main__":
    check_loan_tables_structure()