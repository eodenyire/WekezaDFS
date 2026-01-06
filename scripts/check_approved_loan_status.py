#!/usr/bin/env python3

import mysql.connector

def check_approved_loan_status():
    """Check the actual status of the approved loan"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor(dictionary=True)
        
        print("🔍 Checking status of loan AQ2026010421305155F5...")
        
        # Check authorization queue status
        cursor.execute("""
            SELECT queue_id, transaction_type, reference_id, amount, status, 
                   created_at, approved_by, approved_at, operation_data
            FROM authorization_queue 
            WHERE queue_id = %s
        """, ('AQ2026010421305155F5',))
        
        queue_item = cursor.fetchone()
        
        if queue_item:
            print("📋 Authorization Queue Status:")
            print(f"  - Queue ID: {queue_item['queue_id']}")
            print(f"  - Reference: {queue_item['reference_id']}")
            print(f"  - Amount: KES {queue_item['amount']:,.2f}")
            print(f"  - Status: {queue_item['status']}")
            print(f"  - Created: {queue_item['created_at']}")
            print(f"  - Approved by: {queue_item['approved_by']}")
            print(f"  - Approved at: {queue_item['approved_at']}")
            
            if queue_item['status'] == 'APPROVED':
                print("✅ Loan is APPROVED in authorization queue")
                
                # Check if loan was created in loan_applications table
                cursor.execute("""
                    SELECT application_id, loan_type, loan_amount, status, created_at, approved_by, approved_at
                    FROM loan_applications 
                    WHERE application_id = %s
                """, (queue_item['reference_id'],))
                
                loan_app = cursor.fetchone()
                
                if loan_app:
                    print("\n📋 Loan Applications Table:")
                    print(f"  - Application ID: {loan_app['application_id']}")
                    print(f"  - Loan Type: {loan_app['loan_type']}")
                    print(f"  - Amount: KES {loan_app['loan_amount']:,.2f}")
                    print(f"  - Status: {loan_app['status']}")
                    print(f"  - Approved by: {loan_app['approved_by']}")
                    print(f"  - Approved at: {loan_app['approved_at']}")
                    print("✅ Loan was successfully created after approval")
                else:
                    print("\n❌ Loan NOT found in loan_applications table")
                    print("⚠️ This means the execution after approval failed")
            else:
                print(f"⚠️ Loan status is: {queue_item['status']}")
        else:
            print("❌ Loan not found in authorization queue")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking loan status: {e}")

if __name__ == "__main__":
    check_approved_loan_status()