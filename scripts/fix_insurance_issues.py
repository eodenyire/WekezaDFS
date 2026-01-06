#!/usr/bin/env python3
"""
Fix Insurance Issues Script
- Check for approved policy sales in authorization queue
- Execute approved policy sales that are stuck
- Fix claims query issues
- Verify insurance data integrity
"""

import mysql.connector
from datetime import datetime, timedelta
import uuid
import json

def get_db_connection():
    """Get database connection"""
    try:
        return mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

def check_insurance_data():
    """Check current insurance data"""
    print("=== INSURANCE DATA ANALYSIS ===")
    
    try:
        conn = get_db_connection()
        if not conn:
            return
        
        cursor = conn.cursor(dictionary=True)
        
        # Check authorization queue for approved policy sales
        print("\n1. CHECKING AUTHORIZATION QUEUE FOR APPROVED POLICY SALES:")
        cursor.execute("""
            SELECT queue_id, transaction_type, amount, description, status, 
                   created_at, operation_data, maker_name
            FROM authorization_queue 
            WHERE transaction_type = 'POLICY_SALE' 
            ORDER BY created_at DESC
        """)
        queue_policies = cursor.fetchall()
        
        if queue_policies:
            print(f"Found {len(queue_policies)} policy sales in authorization queue:")
            for policy in queue_policies:
                print(f"  - Queue ID: {policy['queue_id']}")
                print(f"    Status: {policy['status']}")
                print(f"    Amount: KES {policy['amount']:,.2f}")
                print(f"    Description: {policy['description']}")
                print(f"    Created: {policy['created_at']}")
                print(f"    Maker: {policy['maker_name']}")
                if policy['operation_data']:
                    try:
                        op_data = eval(policy['operation_data'])
                        print(f"    Product: {op_data.get('product_name', 'N/A')}")
                        print(f"    Account: {op_data.get('account_number', 'N/A')}")
                    except:
                        pass
                print()
        else:
            print("  No policy sales found in authorization queue")
        
        # Check existing insurance policies
        print("\n2. CHECKING EXISTING INSURANCE POLICIES:")
        cursor.execute("""
            SELECT policy_id, policy_number, account_number, policy_type, 
                   coverage_amount, annual_premium, status, created_at
            FROM insurance_policies 
            ORDER BY created_at DESC
        """)
        existing_policies = cursor.fetchall()
        
        if existing_policies:
            print(f"Found {len(existing_policies)} existing insurance policies:")
            for policy in existing_policies:
                print(f"  - Policy: {policy['policy_number']}")
                print(f"    Account: {policy['account_number']}")
                print(f"    Type: {policy['policy_type']}")
                print(f"    Coverage: KES {policy['coverage_amount']:,.2f}")
                print(f"    Status: {policy['status']}")
                print(f"    Created: {policy['created_at']}")
                print()
        else:
            print("  No existing insurance policies found")
        
        # Check insurance claims
        print("\n3. CHECKING INSURANCE CLAIMS:")
        cursor.execute("""
            SELECT c.claim_id, c.claim_reference, c.policy_id, c.user_id,
                   c.claim_type, c.claim_amount, c.status, c.created_at,
                   p.policy_number, p.account_number
            FROM insurance_claims c
            LEFT JOIN insurance_policies p ON c.policy_id = p.policy_id
            ORDER BY c.created_at DESC
        """)
        claims = cursor.fetchall()
        
        if claims:
            print(f"Found {len(claims)} insurance claims:")
            for claim in claims:
                print(f"  - Claim: {claim['claim_reference']}")
                print(f"    Policy: {claim.get('policy_number', 'N/A')}")
                print(f"    Account: {claim.get('account_number', 'N/A')}")
                print(f"    Type: {claim['claim_type']}")
                print(f"    Amount: KES {claim['claim_amount']:,.2f}")
                print(f"    Status: {claim['status']}")
                print(f"    Created: {claim['created_at']}")
                print()
        else:
            print("  No insurance claims found")
        
        # Check premium payments
        print("\n4. CHECKING PREMIUM PAYMENTS:")
        cursor.execute("""
            SELECT payment_id, policy_number, payment_amount, 
                   payment_date, payment_method, processed_by
            FROM premium_payments 
            ORDER BY payment_date DESC
            LIMIT 10
        """)
        payments = cursor.fetchall()
        
        if payments:
            print(f"Found {len(payments)} recent premium payments:")
            for payment in payments:
                print(f"  - Payment: {payment['payment_id']}")
                print(f"    Policy: {payment['policy_number']}")
                print(f"    Amount: KES {payment['payment_amount']:,.2f}")
                print(f"    Date: {payment['payment_date']}")
                print(f"    Method: {payment['payment_method']}")
                print()
        else:
            print("  No premium payments found")
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking insurance data: {e}")

def execute_approved_policy_sales():
    """Execute approved policy sales that are stuck in queue"""
    print("\n=== EXECUTING APPROVED POLICY SALES ===")
    
    try:
        conn = get_db_connection()
        if not conn:
            return
        
        cursor = conn.cursor(dictionary=True)
        
        # Get approved policy sales from authorization queue
        cursor.execute("""
            SELECT queue_id, operation_data, amount, created_at
            FROM authorization_queue 
            WHERE transaction_type = 'POLICY_SALE' AND status = 'APPROVED'
        """)
        approved_policies = cursor.fetchall()
        
        if not approved_policies:
            print("No approved policy sales found in queue")
            return
        
        print(f"Found {len(approved_policies)} approved policy sales to execute:")
        
        executed_count = 0
        for policy_queue in approved_policies:
            try:
                # Parse operation data
                operation_data = eval(policy_queue['operation_data'])
                
                print(f"\nExecuting policy sale for Queue ID: {policy_queue['queue_id']}")
                print(f"  Account: {operation_data.get('account_number')}")
                print(f"  Product: {operation_data.get('product_name')}")
                print(f"  Coverage: KES {operation_data.get('coverage_amount', 0):,.2f}")
                
                # Execute the policy sale
                result = execute_policy_sale_direct(operation_data)
                
                if result['success']:
                    # Update authorization queue status
                    cursor.execute("""
                        UPDATE authorization_queue 
                        SET status = 'COMPLETED', processed_at = %s
                        WHERE queue_id = %s
                    """, (datetime.now(), policy_queue['queue_id']))
                    
                    executed_count += 1
                    print(f"  ✅ SUCCESS: {result['message']}")
                else:
                    print(f"  ❌ FAILED: {result['error']}")
                
            except Exception as e:
                print(f"  ❌ ERROR executing policy {policy_queue['queue_id']}: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Successfully executed {executed_count} policy sales")
        
    except Exception as e:
        print(f"Error executing approved policy sales: {e}")

def execute_policy_sale_direct(data):
    """Execute policy sale directly (fixed version)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Generate policy number
        policy_number = f"POL{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
        
        # Calculate dates
        start_date = datetime.now().date()
        policy_term_years = 1  # Default 1 year term
        maturity_date = datetime(start_date.year + policy_term_years, start_date.month, start_date.day).date()
        
        # Create policy with required fields
        cursor.execute("""
            INSERT INTO insurance_policies (
                policy_number, account_number, product_id, policy_type, coverage_amount,
                annual_premium, payment_frequency, payment_method, policy_term_years,
                start_date, maturity_date, beneficiary_name, beneficiary_relationship, 
                status, created_by, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'ACTIVE', %s, %s)
        """, (
            policy_number, 
            data['account_number'], 
            data.get('product_id'), 
            data['product_name'], 
            data['coverage_amount'], 
            data['annual_premium'], 
            'Monthly', 
            'Direct Debit', 
            policy_term_years, 
            start_date, 
            maturity_date,
            data.get('beneficiary_name', ''),
            data.get('beneficiary_relationship', ''),
            f"CUSTOMER_{data['user_id']}", 
            datetime.now()
        ))
        
        # Deduct premium from account
        cursor.execute("""
            UPDATE accounts SET balance = balance - %s WHERE account_number = %s
        """, (data['premium_amount'], data['account_number']))
        
        # Record transaction
        ref_code = f"INS{uuid.uuid4().hex[:8].upper()}"
        cursor.execute("""
            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
            SELECT account_id, 'INSURANCE_PREMIUM', %s, %s, %s, %s
            FROM accounts WHERE account_number = %s
        """, (
            data['premium_amount'], 
            ref_code, 
            f"Insurance premium for policy {policy_number} - Approved", 
            datetime.now(), 
            data['account_number']
        ))
        
        conn.commit()
        conn.close()
        return {"success": True, "message": f"Insurance policy {policy_number} created successfully"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def fix_claims_table():
    """Fix claims table structure if needed"""
    print("\n=== FIXING CLAIMS TABLE STRUCTURE ===")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if claims table exists and has correct structure
        cursor.execute("DESCRIBE insurance_claims")
        columns = cursor.fetchall()
        
        print("Current insurance_claims table structure:")
        for col in columns:
            print(f"  {col[0]} - {col[1]}")
        
        # Check if created_at column exists
        column_names = [col[0] for col in columns]
        if 'created_at' not in column_names:
            print("Adding missing created_at column...")
            cursor.execute("""
                ALTER TABLE insurance_claims 
                ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """)
            print("✅ Added created_at column")
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"Error fixing claims table: {e}")

def main():
    """Main function"""
    print("🛡️ INSURANCE SYSTEM DIAGNOSTIC AND REPAIR TOOL")
    print("=" * 50)
    
    # Step 1: Check current data
    check_insurance_data()
    
    # Step 2: Fix claims table structure
    fix_claims_table()
    
    # Step 3: Execute approved policy sales
    execute_approved_policy_sales()
    
    # Step 4: Final verification
    print("\n=== FINAL VERIFICATION ===")
    check_insurance_data()
    
    print("\n🎉 Insurance system diagnostic and repair completed!")

if __name__ == "__main__":
    main()