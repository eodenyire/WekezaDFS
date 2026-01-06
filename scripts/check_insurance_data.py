#!/usr/bin/env python3

import mysql.connector

def check_insurance_data():
    """Check insurance-related data in the database"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor(dictionary=True)
        
        print("🔍 Checking insurance data...")
        
        # Check insurance_policies table
        cursor.execute("SELECT * FROM insurance_policies WHERE account_number = 'ACC1000014'")
        policies = cursor.fetchall()
        print(f"\n📋 INSURANCE_POLICIES for ACC1000014: {len(policies)} records")
        for policy in policies:
            print(f"  - Policy: {policy['policy_number']} | Status: {policy['status']} | Product: {policy.get('product_id', 'N/A')}")
        
        # Check authorization queue for insurance
        cursor.execute("SELECT * FROM authorization_queue WHERE transaction_type = 'POLICY_SALE' AND maker_id LIKE '%CUSTOMER%'")
        queue_items = cursor.fetchall()
        print(f"\n📋 AUTHORIZATION_QUEUE for POLICY_SALE: {len(queue_items)} records")
        for item in queue_items:
            print(f"  - Queue: {item['queue_id']} | Status: {item['status']} | Amount: {item['amount']}")
        
        # Check insurance_claims table
        cursor.execute("SELECT * FROM insurance_claims")
        claims = cursor.fetchall()
        print(f"\n📋 INSURANCE_CLAIMS: {len(claims)} records")
        for claim in claims:
            print(f"  - Claim: {claim.get('claim_reference', 'N/A')} | Status: {claim['status']} | User: {claim.get('user_id', 'N/A')}")
        
        # Check insurance_products table
        cursor.execute("SELECT * FROM insurance_products WHERE is_active = 1")
        products = cursor.fetchall()
        print(f"\n📋 INSURANCE_PRODUCTS (active): {len(products)} records")
        for product in products:
            print(f"  - Product: {product['product_name']} | Code: {product['product_code']} | Premium: KES {product['premium_amount']}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking insurance data: {e}")

if __name__ == "__main__":
    check_insurance_data()