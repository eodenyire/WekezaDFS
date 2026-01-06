#!/usr/bin/env python3

import mysql.connector
import sys
import os
from datetime import datetime

# Add the authorization helper path
sys.path.append(os.path.join(os.path.dirname(__file__), '03_Source_Code', 'branch_operations', 'shared'))

def manually_execute_approved_loan():
    """Manually execute the approved loan that failed to execute"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor(dictionary=True)
        
        print("🔧 Manually executing approved loan AQ2026010421305155F5...")
        
        # Get the approved loan from authorization queue
        cursor.execute("""
            SELECT * FROM authorization_queue 
            WHERE queue_id = %s AND status = 'APPROVED'
        """, ('AQ2026010421305155F5',))
        
        approved_loan = cursor.fetchone()
        
        if approved_loan:
            print("✅ Found approved loan in queue")
            
            # Parse operation data
            operation_data = eval(approved_loan['operation_data'])
            print(f"📋 Operation data: {operation_data}")
            
            # Create the loan application record
            cursor.execute("""
                INSERT INTO loan_applications (
                    application_id, account_number, customer_type, loan_type, loan_amount,
                    interest_rate, tenure_months, purpose, monthly_payment, processing_fee,
                    status, created_by, approved_by, approved_at, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'APPROVED', %s, %s, %s, %s)
            """, (
                operation_data.get('application_id'), operation_data.get('account_number'),
                operation_data.get('customer_type', 'individual'), operation_data.get('loan_type'),
                operation_data.get('loan_amount'), operation_data.get('interest_rate'),
                operation_data.get('tenure_months'), operation_data.get('purpose'),
                operation_data.get('monthly_payment'), operation_data.get('processing_fee'),
                operation_data.get('created_by'), approved_loan['approved_by'], 
                approved_loan['approved_at'], approved_loan['created_at']
            ))
            
            conn.commit()
            print("✅ Loan application created successfully in loan_applications table")
            
            # Verify it was created
            cursor.execute("""
                SELECT application_id, loan_type, loan_amount, status, approved_by, approved_at
                FROM loan_applications 
                WHERE application_id = %s
            """, (operation_data.get('application_id'),))
            
            created_loan = cursor.fetchone()
            if created_loan:
                print("🎉 Verification successful:")
                print(f"  - Application ID: {created_loan['application_id']}")
                print(f"  - Loan Type: {created_loan['loan_type']}")
                print(f"  - Amount: KES {created_loan['loan_amount']:,.2f}")
                print(f"  - Status: {created_loan['status']}")
                print(f"  - Approved by: {created_loan['approved_by']}")
                print(f"  - Approved at: {created_loan['approved_at']}")
            
        else:
            print("❌ Approved loan not found in authorization queue")
        
        conn.close()
        
        print("\n🎯 EXECUTION COMPLETE!")
        print("✅ The loan should now appear as APPROVED in personal banking portal")
        print("🔄 Refresh the personal banking portal to see the updated status")
        
    except Exception as e:
        print(f"❌ Error executing approved loan: {e}")

if __name__ == "__main__":
    manually_execute_approved_loan()