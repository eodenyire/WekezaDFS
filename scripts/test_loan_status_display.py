#!/usr/bin/env python3

import mysql.connector

def test_loan_status_display():
    """Test the fixed loan status display logic"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor(dictionary=True)
        
        print("🧪 Testing fixed loan status display logic...")
        
        # Test the same query that personal banking portal uses
        user_id = 14  # Emmanuel's user ID
        account_number = 'ACC1000014'
        
        cursor.execute("""
            SELECT 
                aq.queue_id as application_id,
                aq.transaction_type,
                aq.amount as loan_amount,
                aq.description as loan_type,
                aq.status,
                aq.created_at,
                aq.priority,
                CASE 
                    WHEN aq.status = 'PENDING' THEN 'PENDING_APPROVAL'
                    WHEN aq.status = 'APPROVED' THEN 'APPROVED_IN_QUEUE'
                    WHEN aq.status = 'REJECTED' THEN 'REJECTED_IN_QUEUE'
                    ELSE aq.status
                END as display_status,
                aq.operation_data
            FROM authorization_queue aq
            WHERE aq.maker_id LIKE %s AND aq.transaction_type = 'LOAN_APPLICATION'
            
            UNION ALL
            
            SELECT 
                la.application_id,
                'LOAN_APPLICATION' as transaction_type,
                la.loan_amount,
                la.loan_type,
                la.status,
                la.created_at,
                'APPROVED' as priority,
                la.status as display_status,
                '' as operation_data
            FROM loan_applications la
            WHERE la.account_number = %s AND la.status IN ('APPROVED', 'DISBURSED', 'REJECTED')
            
            ORDER BY created_at DESC
        """, (f"%{user_id}%", account_number))
        
        user_loans = cursor.fetchall()
        
        print(f"\n📋 Found {len(user_loans)} loans for user {user_id}:")
        
        pending_count = 0
        approved_count = 0
        rejected_count = 0
        
        for loan in user_loans:
            print(f"\n  - Application ID: {loan['application_id']}")
            print(f"    Amount: KES {loan['loan_amount']:,.2f}")
            print(f"    Database Status: {loan['status']}")
            print(f"    Display Status: {loan['display_status']}")
            print(f"    Created: {loan['created_at']}")
            
            if loan['display_status'] == 'PENDING_APPROVAL':
                pending_count += 1
                print(f"    🟡 Will show as: PENDING SUPERVISOR APPROVAL")
            elif loan['display_status'] == 'APPROVED_IN_QUEUE':
                approved_count += 1
                print(f"    🟢 Will show as: APPROVED (Processing)")
            elif loan['display_status'] == 'REJECTED_IN_QUEUE':
                rejected_count += 1
                print(f"    ❌ Will show as: REJECTED")
            elif loan['display_status'] == 'APPROVED':
                approved_count += 1
                print(f"    ✅ Will show as: APPROVED")
        
        print(f"\n📊 Summary:")
        print(f"  - Pending loans (will show warning): {pending_count}")
        print(f"  - Approved loans: {approved_count}")
        print(f"  - Rejected loans: {rejected_count}")
        
        if pending_count == 0:
            print("\n✅ SUCCESS: No pending loans - warning should NOT appear!")
        else:
            print(f"\n⚠️ {pending_count} pending loans - warning will appear")
        
        # Check specifically for the problematic loan
        problematic_loan = next((loan for loan in user_loans if loan['application_id'] == 'AQ2026010421305155F5'), None)
        if problematic_loan:
            print(f"\n🔍 Problematic loan AQ2026010421305155F5:")
            print(f"  - Database Status: {problematic_loan['status']}")
            print(f"  - Display Status: {problematic_loan['display_status']}")
            if problematic_loan['display_status'] == 'APPROVED_IN_QUEUE':
                print("  ✅ FIXED: Will now show as APPROVED (Processing) instead of pending!")
            else:
                print("  ❌ Still showing as pending")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error testing loan status: {e}")

if __name__ == "__main__":
    test_loan_status_display()