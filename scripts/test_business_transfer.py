#!/usr/bin/env python3
"""
Test script to simulate business transfer through maker-checker system
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '03_Source_Code', 'branch_operations', 'shared'))

from authorization_helper import submit_to_authorization_queue, check_authorization_thresholds
from datetime import datetime

def test_business_transfer():
    """Test business transfer submission"""
    print("🏦 Testing Business Transfer through Maker-Checker System")
    print("=" * 60)
    
    # Simulate business transfer data
    business_info = {
        'staff_code': 'BIZ_14',  # Use staff_code instead of teller_id
        'full_name': 'Business User - Test Business',
        'branch_code': 'BIZ001',
        'role': 'business_user'
    }
    
    operation_data = {
        "sender_account": "BIZ1000014",
        "recipient_account": "ACC1000023",
        "amount": 10000.0,
        "fee": 0.0,
        "total_amount": 10000.0,
        "reference": "Business payment - Internal Transfer",
        "transfer_type": "Internal Business Transfer",
        "transaction_date": datetime.now().isoformat(),
        "business_id": "14",
        "branch_code": "BIZ001"
    }
    
    print("📋 Transfer Details:")
    print(f"   From: {operation_data['sender_account']}")
    print(f"   To: {operation_data['recipient_account']}")
    print(f"   Amount: KES {operation_data['amount']:,.2f}")
    print(f"   Business: {business_info['full_name']}")
    print()
    
    # Submit to authorization queue
    print("🔄 Submitting to authorization queue...")
    result = submit_to_authorization_queue(
        operation_type='BANK_TRANSFER',
        operation_data=operation_data,
        maker_info=business_info,
        priority='HIGH'
    )
    
    if result['success']:
        print("✅ SUCCESS: Transfer submitted to authorization queue!")
        print(f"   Queue ID: {result['queue_id']}")
        print(f"   Status: {result['status']}")
        print(f"   Message: {result['message']}")
        print()
        print("🎯 Next Steps:")
        print("   1. Supervisor can approve in Admin Portal")
        print("   2. Transfer will execute after approval")
        print("   3. Account balances will be updated")
        
        return result['queue_id']
    else:
        print(f"❌ FAILED: {result['error']}")
        return None

def check_queue_status(queue_id):
    """Check the status of the submitted transfer"""
    if not queue_id:
        return
    
    print(f"\n🔍 Checking queue status for {queue_id}...")
    
    import mysql.connector
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT queue_id, transaction_type, status, amount, description, created_at
            FROM authorization_queue 
            WHERE queue_id = %s
        """, (queue_id,))
        
        result = cursor.fetchone()
        
        if result:
            print("📋 Queue Item Found:")
            print(f"   Queue ID: {result['queue_id']}")
            print(f"   Type: {result['transaction_type']}")
            print(f"   Status: {result['status']}")
            print(f"   Amount: KES {result['amount']:,.2f}")
            print(f"   Description: {result['description']}")
            print(f"   Created: {result['created_at']}")
        else:
            print("❌ Queue item not found")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking queue: {e}")

def main():
    """Main test function"""
    print("🏦 WEKEZA BANK - BUSINESS TRANSFER TEST")
    print("=" * 60)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        queue_id = test_business_transfer()
        check_queue_status(queue_id)
        
        print("\n" + "=" * 60)
        print("✅ BUSINESS TRANSFER TEST COMPLETED")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()