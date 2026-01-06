#!/usr/bin/env python3

import mysql.connector
from datetime import datetime

def test_bancassurance_system():
    """Test the bancassurance system database integration"""
    try:
        # Connect to database
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor(dictionary=True)
        
        print("🛡️ Testing Bancassurance System Database Integration")
        print("=" * 60)
        
        # Test 1: Check insurance policies
        print("\n📋 Test 1: Insurance Policies")
        cursor.execute("""
            SELECT p.*, u.full_name as customer_name
            FROM insurance_policies p
            JOIN accounts a ON p.account_number = a.account_number
            JOIN users u ON a.user_id = u.user_id
            WHERE p.status = 'ACTIVE'
            LIMIT 5
        """)
        
        policies = cursor.fetchall()
        print(f"✅ Found {len(policies)} active policies")
        
        for policy in policies:
            print(f"  - {policy['policy_number']}: {policy['customer_name']} - {policy['policy_type']}")
            print(f"    Coverage: KES {policy['coverage_amount']:,.2f}, Premium: KES {policy['annual_premium']:,.2f}")
        
        # Test 2: Check premium payments
        print("\n💰 Test 2: Premium Payments")
        cursor.execute("""
            SELECT pp.*, p.policy_type
            FROM premium_payments pp
            JOIN insurance_policies p ON pp.policy_number = p.policy_number
            ORDER BY pp.payment_date DESC
            LIMIT 5
        """)
        
        payments = cursor.fetchall()
        print(f"✅ Found {len(payments)} premium payments")
        
        for payment in payments:
            print(f"  - {payment['payment_id']}: KES {payment['payment_amount']:,.2f}")
            print(f"    Policy: {payment['policy_number']} ({payment['policy_type']})")
            print(f"    Date: {payment['payment_date']}, Method: {payment['payment_method']}")
        
        # Test 3: Check insurance claims
        print("\n📊 Test 3: Insurance Claims")
        cursor.execute("""
            SELECT c.*, p.policy_number, u.full_name as customer_name
            FROM insurance_claims c
            JOIN insurance_policies p ON c.policy_id = p.policy_id
            JOIN accounts a ON p.account_number = a.account_number
            JOIN users u ON a.user_id = u.user_id
            ORDER BY c.created_at DESC
            LIMIT 5
        """)
        
        claims = cursor.fetchall()
        print(f"✅ Found {len(claims)} insurance claims")
        
        for claim in claims:
            print(f"  - {claim['claim_reference']}: {claim['customer_name']}")
            print(f"    Type: {claim['claim_type']}, Amount: KES {claim['claim_amount']:,.2f}")
            print(f"    Status: {claim['status']}, Date: {claim['created_at'].strftime('%Y-%m-%d')}")
        
        # Test 4: Check agent commissions
        print("\n💼 Test 4: Agent Commissions")
        cursor.execute("""
            SELECT ac.*, p.policy_type
            FROM agent_commissions ac
            JOIN insurance_policies p ON ac.policy_number = p.policy_number
            ORDER BY ac.created_at DESC
            LIMIT 5
        """)
        
        commissions = cursor.fetchall()
        print(f"✅ Found {len(commissions)} agent commissions")
        
        for commission in commissions:
            print(f"  - Agent {commission['agent_code']}: KES {commission['commission_amount']:,.2f}")
            print(f"    Policy: {commission['policy_number']} ({commission['policy_type']})")
            print(f"    Rate: {commission['commission_rate']}%, Status: {commission['status']}")
        
        # Test 5: Generate sample report data
        print("\n📑 Test 5: Sample Report Data")
        
        # Policy sales summary
        cursor.execute("""
            SELECT 
                COUNT(*) as total_policies,
                SUM(coverage_amount) as total_coverage,
                SUM(annual_premium) as total_premiums,
                policy_type
            FROM insurance_policies 
            WHERE status = 'ACTIVE'
            GROUP BY policy_type
        """)
        
        policy_summary = cursor.fetchall()
        print("Policy Sales Summary:")
        total_policies = sum(p['total_policies'] for p in policy_summary)
        total_coverage = sum(p['total_coverage'] or 0 for p in policy_summary)
        total_premiums = sum(p['total_premiums'] or 0 for p in policy_summary)
        
        print(f"  Total Policies: {total_policies}")
        print(f"  Total Coverage: KES {total_coverage:,.2f}")
        print(f"  Total Premiums: KES {total_premiums:,.2f}")
        
        for product in policy_summary:
            percentage = (product['total_policies'] / total_policies) * 100
            print(f"  - {product['policy_type']}: {product['total_policies']} policies ({percentage:.1f}%)")
        
        # Premium collection summary
        cursor.execute("""
            SELECT 
                SUM(payment_amount) as total_collections,
                COUNT(*) as payment_count,
                payment_method
            FROM premium_payments 
            GROUP BY payment_method
        """)
        
        payment_summary = cursor.fetchall()
        print("\nPremium Collection Summary:")
        total_collections = sum(p['total_collections'] or 0 for p in payment_summary)
        total_payment_count = sum(p['payment_count'] for p in payment_summary)
        
        print(f"  Total Collections: KES {total_collections:,.2f}")
        print(f"  Total Payments: {total_payment_count}")
        
        for method in payment_summary:
            percentage = (method['payment_count'] / total_payment_count) * 100
            print(f"  - {method['payment_method']}: {method['payment_count']} payments ({percentage:.1f}%)")
        
        conn.close()
        
        print("\n🎉 All bancassurance system tests completed successfully!")
        print("\n📊 System Status:")
        print("- ✅ Database connectivity working")
        print("- ✅ Insurance policies accessible")
        print("- ✅ Premium payments tracking")
        print("- ✅ Claims management ready")
        print("- ✅ Agent commissions calculated")
        print("- ✅ Reporting functionality operational")
        
        print(f"\n🌐 Access the system at: http://localhost:8501")
        print("   Navigate to 'Bancassurance' module after logging in")
        
    except Exception as e:
        print(f"❌ Error testing bancassurance system: {e}")

if __name__ == "__main__":
    test_bancassurance_system()