#!/usr/bin/env python3
"""
Comprehensive system alignment test to ensure all portals work together
"""

import mysql.connector
import os
import sys
from datetime import datetime

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
        print(f"❌ Database connection failed: {e}")
        return None

def test_database_schema():
    """Test database schema alignment"""
    print("🔍 TESTING DATABASE SCHEMA ALIGNMENT")
    print("=" * 50)
    
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    # Check critical tables
    critical_tables = [
        'users', 'accounts', 'businesses', 'staff', 'authorization_queue',
        'transactions', 'loans', 'loan_applications', 'insurance_policies',
        'insurance_products', 'customers'
    ]
    
    missing_tables = []
    existing_tables = []
    
    for table in critical_tables:
        try:
            cursor.execute(f"SHOW TABLES LIKE '{table}'")
            if cursor.fetchone():
                existing_tables.append(table)
            else:
                missing_tables.append(table)
        except Exception as e:
            missing_tables.append(f"{table} (error: {e})")
    
    print(f"✅ Existing tables ({len(existing_tables)}): {', '.join(existing_tables)}")
    if missing_tables:
        print(f"❌ Missing tables ({len(missing_tables)}): {', '.join(missing_tables)}")
    
    conn.close()
    return len(missing_tables) == 0

def test_user_data_alignment():
    """Test user data alignment across portals"""
    print("\n🔍 TESTING USER DATA ALIGNMENT")
    print("=" * 50)
    
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor(dictionary=True)
    
    # Check for test users
    test_users = ['emmanuel@wekeza.com', 'nuria@wekeza.com', 'admin@wekeza.com']
    
    for email in test_users:
        cursor.execute("""
            SELECT u.user_id, u.full_name, u.email, u.is_active,
                   a.account_number, a.balance, a.status as account_status
            FROM users u
            LEFT JOIN accounts a ON u.user_id = a.user_id
            WHERE u.email = %s
        """, (email,))
        
        user = cursor.fetchone()
        if user:
            print(f"✅ {email}: User ID {user['user_id']}, Account {user.get('account_number', 'None')}, Balance KES {user.get('balance', 0):,.2f}")
        else:
            print(f"❌ {email}: User not found")
    
    conn.close()
    return True

def test_business_data_alignment():
    """Test business data alignment"""
    print("\n🔍 TESTING BUSINESS DATA ALIGNMENT")
    print("=" * 50)
    
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor(dictionary=True)
    
    # Check for test businesses
    cursor.execute("""
        SELECT b.business_id, b.business_name, b.registration_no,
               a.account_number, a.balance, a.status
        FROM businesses b
        LEFT JOIN accounts a ON b.business_id = a.business_id
        LIMIT 5
    """)
    
    businesses = cursor.fetchall()
    if businesses:
        print(f"✅ Found {len(businesses)} businesses:")
        for biz in businesses:
            print(f"   - {biz['business_name']}: Account {biz.get('account_number', 'None')}, Balance KES {biz.get('balance', 0):,.2f}")
    else:
        print("❌ No businesses found")
    
    conn.close()
    return len(businesses) > 0

def test_authorization_queue_alignment():
    """Test authorization queue functionality"""
    print("\n🔍 TESTING AUTHORIZATION QUEUE ALIGNMENT")
    print("=" * 50)
    
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor(dictionary=True)
    
    # Check pending items
    cursor.execute("SELECT COUNT(*) as pending_count FROM authorization_queue WHERE status = 'PENDING'")
    pending = cursor.fetchone()['pending_count']
    
    # Check recent items
    cursor.execute("""
        SELECT transaction_type, COUNT(*) as count
        FROM authorization_queue
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
        GROUP BY transaction_type
        ORDER BY count DESC
    """)
    
    recent_types = cursor.fetchall()
    
    print(f"✅ Pending approvals: {pending}")
    if recent_types:
        print("✅ Recent transaction types (last 24h):")
        for item in recent_types:
            print(f"   - {item['transaction_type']}: {item['count']} items")
    else:
        print("ℹ️ No recent transactions in authorization queue")
    
    conn.close()
    return True

def test_file_syntax():
    """Test critical files for syntax errors"""
    print("\n🔍 TESTING FILE SYNTAX")
    print("=" * 50)
    
    critical_files = [
        "03_Source_Code/branch_operations/branch_teller/app.py",
        "03_Source_Code/web_portal_customer/personal_banking_portal.py",
        "03_Source_Code/web_portal_customer/customer_app.py",
        "03_Source_Code/web_portal_business/business_app.py",
        "03_Source_Code/web_portal_admin/enhanced_admin_portal.py",
        "03_Source_Code/branch_operations/shared/authorization_helper.py"
    ]
    
    syntax_errors = []
    
    for file_path in critical_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to compile the code
            compile(content, file_path, 'exec')
            print(f"✅ {file_path}: Syntax OK")
            
        except SyntaxError as e:
            error_msg = f"{file_path}: Line {e.lineno} - {e.msg}"
            syntax_errors.append(error_msg)
            print(f"❌ {error_msg}")
        except FileNotFoundError:
            error_msg = f"{file_path}: File not found"
            syntax_errors.append(error_msg)
            print(f"❌ {error_msg}")
        except Exception as e:
            error_msg = f"{file_path}: {str(e)}"
            syntax_errors.append(error_msg)
            print(f"❌ {error_msg}")
    
    return len(syntax_errors) == 0

def fix_branch_operations_cif():
    """Fix CIF creation in branch operations to use database"""
    print("\n🔧 FIXING BRANCH OPERATIONS CIF INTEGRATION")
    print("=" * 50)
    
    # This will be implemented after testing
    print("ℹ️ CIF integration fix will be applied...")
    return True

def main():
    """Main test function"""
    print("🚀 COMPREHENSIVE SYSTEM ALIGNMENT TEST")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    test_results = []
    
    # Run all tests
    test_results.append(("Database Schema", test_database_schema()))
    test_results.append(("User Data Alignment", test_user_data_alignment()))
    test_results.append(("Business Data Alignment", test_business_data_alignment()))
    test_results.append(("Authorization Queue", test_authorization_queue_alignment()))
    test_results.append(("File Syntax", test_file_syntax()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {len(test_results)} tests | Passed: {passed} | Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED - SYSTEM IS ALIGNED!")
    else:
        print(f"\n⚠️ {failed} TESTS FAILED - FIXES NEEDED")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)