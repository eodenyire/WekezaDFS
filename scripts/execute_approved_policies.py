#!/usr/bin/env python3

import mysql.connector
from datetime import datetime
import uuid
import sys
import os

# Add the authorization helper path
sys.path.append(os.path.join(os.path.dirname(__file__), '03_Source_Code', 'branch_operations', 'shared'))
from authorization_helper import execute_approved_operation

def execute_approved_policies():
    """Execute all approved policy sales that are stuck in the authorization queue"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor(dictionary=True)
        
        print("🔧 Executing approved policy sales...")
        
        # Get approved policy sales from authorization queue
        cursor.execute("""
            SELECT * FROM authorization_queue 
            WHERE transaction_type = 'POLICY_SALE' AND status = 'APPROVED'
            ORDER BY created_at ASC
        """)
        
        approved_policies = cursor.fetchall()
        print(f"✅ Found {len(approved_policies)} approved policy sales to execute")
        
        executed_count = 0
        failed_count = 0
        
        for policy in approved_policies:
            print(f"\n🔄 Processing Queue ID: {policy['queue_id']}")
            print(f"  - Amount: KES {policy['amount']:,.2f}")
            print(f"  - Description: {policy['description']}")
            
            try:
                # Execute the approved operation
                result = execute_approved_operation(policy)
                
                if result.get('success'):
                    print(f"  ✅ Executed successfully: {result['message']}")
                    
                    # Update queue status to COMPLETED
                    cursor.execute("""
                        UPDATE authorization_queue 
                        SET status = 'COMPLETED' 
                        WHERE queue_id = %s
                    """, (policy['queue_id'],))
                    
                    executed_count += 1
                else:
                    print(f"  ❌ Execution failed: {result.get('error', 'Unknown error')}")
                    failed_count += 1
                    
            except Exception as e:
                print(f"  ❌ Error executing policy: {e}")
                failed_count += 1
        
        conn.commit()
        conn.close()
        
        print(f"\n🎉 EXECUTION COMPLETE!")
        print(f"✅ Successfully executed: {executed_count} policies")
        print(f"❌ Failed executions: {failed_count} policies")
        
        if executed_count > 0:
            print(f"\n💡 Refresh the personal banking portal to see the new active policies!")
        
    except Exception as e:
        print(f"❌ Error executing approved policies: {e}")

if __name__ == "__main__":
    execute_approved_policies()