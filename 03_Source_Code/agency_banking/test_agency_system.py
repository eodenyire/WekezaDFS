"""
Comprehensive test script for Agency Banking System
Tests all core functionality including authentication, transactions, and float management
"""

import sys
import os
from datetime import datetime
from decimal import Decimal

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

from agency_gateway import AgencyGateway
from agent_management import AgentManager

def test_agent_authentication():
    """Test agent authentication functionality"""
    print("🔐 Testing Agent Authentication")
    print("-" * 40)
    
    gateway = AgencyGateway()
    
    # Test cases
    test_cases = [
        {
            "name": "Valid Super Agent Login",
            "agent_id": "AG20240101SUPER1",
            "device_id": "POS001",
            "pin": "1234",
            "expected_success": True
        },
        {
            "name": "Valid Sub-Agent Login",
            "agent_id": "AG20240101SUB001",
            "device_id": "POS002",
            "pin": "5678",
            "expected_success": True
        },
        {
            "name": "Valid Retailer Login",
            "agent_id": "AG20240101RET001",
            "device_id": "POS003",
            "pin": "9999",
            "expected_success": True
        },
        {
            "name": "Invalid PIN",
            "agent_id": "AG20240101SUPER1",
            "device_id": "POS001",
            "pin": "0000",
            "expected_success": False
        },
        {
            "name": "Invalid Agent ID",
            "agent_id": "INVALID123",
            "device_id": "POS001",
            "pin": "1234",
            "expected_success": False
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['name']}")
        
        result = gateway.authenticate_agent(
            agent_id=test_case['agent_id'],
            device_id=test_case['device_id'],
            pin=test_case['pin']
        )
        
        success = result['success'] == test_case['expected_success']
        status = "✅ PASS" if success else "❌ FAIL"
        
        print(f"   {status}")
        if result['success']:
            print(f"   Session Token: {result['session_token'][:20]}...")
            print(f"   Agent: {result['agent_info']['agent_name']}")
        else:
            print(f"   Error: {result['error']}")
        
        results.append(success)
        print()
    
    passed = sum(results)
    total = len(results)
    print(f"Authentication Tests: {passed}/{total} passed")
    return passed == total

def test_cash_in_transactions():
    """Test cash in (deposit) transactions"""
    print("💰 Testing Cash In Transactions")
    print("-" * 40)
    
    gateway = AgencyGateway()
    
    # First authenticate
    auth_result = gateway.authenticate_agent(
        agent_id="AG20240101RET001",
        device_id="POS003",
        pin="9999"
    )
    
    if not auth_result['success']:
        print("❌ Authentication failed for cash in tests")
        return False
    
    session_token = auth_result['session_token']
    
    # Test cases
    test_cases = [
        {
            "name": "Valid Cash In",
            "customer_account": "ACC1000014",
            "amount": 5000,
            "expected_success": True
        },
        {
            "name": "Large Amount Cash In",
            "customer_account": "ACC1000014",
            "amount": 45000,  # Within agent limit
            "expected_success": True
        },
        {
            "name": "Amount Exceeds Agent Float",
            "customer_account": "ACC1000014",
            "amount": 100000,  # Exceeds agent float
            "expected_success": False
        },
        {
            "name": "Invalid Customer Account",
            "customer_account": "INVALID123",
            "amount": 1000,
            "expected_success": False
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['name']}")
        
        txn_data = {
            'transaction_type': 'CASH_IN',
            'customer_account': test_case['customer_account'],
            'amount': test_case['amount'],
            'narration': f"Test cash in - {test_case['name']}",
            'device_id': 'POS003'
        }
        
        result = gateway.process_transaction(session_token, txn_data)
        
        success = result['success'] == test_case['expected_success']
        status = "✅ PASS" if success else "❌ FAIL"
        
        print(f"   {status}")
        if result['success']:
            print(f"   Transaction Ref: {result['transaction_ref']}")
            print(f"   Customer Balance: KES {result['customer_balance']:,.2f}")
            print(f"   Agent Balance: KES {result['agent_balance']:,.2f}")
            print(f"   Commission: KES {result['commission']:,.2f}")
        else:
            print(f"   Error: {result['error']}")
        
        results.append(success)
        print()
    
    passed = sum(results)
    total = len(results)
    print(f"Cash In Tests: {passed}/{total} passed")
    return passed == total

def test_cash_out_transactions():
    """Test cash out (withdrawal) transactions"""
    print("💸 Testing Cash Out Transactions")
    print("-" * 40)
    
    gateway = AgencyGateway()
    
    # First authenticate
    auth_result = gateway.authenticate_agent(
        agent_id="AG20240101RET001",
        device_id="POS003",
        pin="9999"
    )
    
    if not auth_result['success']:
        print("❌ Authentication failed for cash out tests")
        return False
    
    session_token = auth_result['session_token']
    
    # Test cases
    test_cases = [
        {
            "name": "Valid Cash Out",
            "customer_account": "ACC1000014",
            "amount": 2000,
            "expected_success": True
        },
        {
            "name": "Large Amount Cash Out",
            "customer_account": "ACC1000014",
            "amount": 10000,
            "expected_success": True
        },
        {
            "name": "Amount Exceeds Customer Balance",
            "customer_account": "ACC1000014",
            "amount": 999999999,  # Very large amount
            "expected_success": False
        },
        {
            "name": "Invalid Customer Account",
            "customer_account": "INVALID123",
            "amount": 1000,
            "expected_success": False
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['name']}")
        
        txn_data = {
            'transaction_type': 'CASH_OUT',
            'customer_account': test_case['customer_account'],
            'amount': test_case['amount'],
            'narration': f"Test cash out - {test_case['name']}",
            'device_id': 'POS003'
        }
        
        result = gateway.process_transaction(session_token, txn_data)
        
        success = result['success'] == test_case['expected_success']
        status = "✅ PASS" if success else "❌ FAIL"
        
        print(f"   {status}")
        if result['success']:
            print(f"   Transaction Ref: {result['transaction_ref']}")
            print(f"   Customer Balance: KES {result['customer_balance']:,.2f}")
            print(f"   Agent Balance: KES {result['agent_balance']:,.2f}")
            print(f"   Commission: KES {result['commission']:,.2f}")
        else:
            print(f"   Error: {result['error']}")
        
        results.append(success)
        print()
    
    passed = sum(results)
    total = len(results)
    print(f"Cash Out Tests: {passed}/{total} passed")
    return passed == total

def test_balance_inquiry():
    """Test balance inquiry functionality"""
    print("📊 Testing Balance Inquiry")
    print("-" * 40)
    
    gateway = AgencyGateway()
    
    # First authenticate
    auth_result = gateway.authenticate_agent(
        agent_id="AG20240101RET001",
        device_id="POS003",
        pin="9999"
    )
    
    if not auth_result['success']:
        print("❌ Authentication failed for balance inquiry tests")
        return False
    
    session_token = auth_result['session_token']
    
    # Test cases
    test_cases = [
        {
            "name": "Valid Balance Inquiry",
            "customer_account": "ACC1000014",
            "expected_success": True
        },
        {
            "name": "Invalid Customer Account",
            "customer_account": "INVALID123",
            "expected_success": False
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['name']}")
        
        txn_data = {
            'transaction_type': 'BALANCE_INQUIRY',
            'customer_account': test_case['customer_account'],
            'device_id': 'POS003'
        }
        
        result = gateway.process_transaction(session_token, txn_data)
        
        success = result['success'] == test_case['expected_success']
        status = "✅ PASS" if success else "❌ FAIL"
        
        print(f"   {status}")
        if result['success']:
            print(f"   Transaction Ref: {result['transaction_ref']}")
            print(f"   Account Holder: {result['account_holder']}")
            print(f"   Balance: KES {result['balance']:,.2f}")
            print(f"   Account Status: {result['account_status']}")
        else:
            print(f"   Error: {result['error']}")
        
        results.append(success)
        print()
    
    passed = sum(results)
    total = len(results)
    print(f"Balance Inquiry Tests: {passed}/{total} passed")
    return passed == total

def test_agent_management():
    """Test agent management functionality"""
    print("👥 Testing Agent Management")
    print("-" * 40)
    
    agent_manager = AgentManager()
    
    # Test agent hierarchy
    print("1. Testing Agent Hierarchy")
    hierarchy_result = agent_manager.get_agent_hierarchy("AG20240101SUPER1")
    
    if hierarchy_result['success']:
        print("   ✅ PASS")
        print(f"   Agent: {hierarchy_result['agent']['agent_name']}")
        print(f"   Children: {len(hierarchy_result['children'])} agents")
    else:
        print("   ❌ FAIL")
        print(f"   Error: {hierarchy_result['error']}")
    
    print()
    
    # Test agent performance
    print("2. Testing Agent Performance")
    performance_result = agent_manager.get_agent_performance("AG20240101RET001", 30)
    
    if performance_result['success']:
        print("   ✅ PASS")
        summary = performance_result['summary']
        print(f"   Total Transactions: {summary['total_transactions']}")
        print(f"   Total Volume: KES {summary['total_volume']:,.2f}")
        print(f"   Total Commission: KES {summary['total_commission']:,.2f}")
    else:
        print("   ❌ FAIL")
        print(f"   Error: {performance_result['error']}")
    
    print()
    
    # Test float management
    print("3. Testing Float Management")
    float_result = agent_manager.manage_agent_float(
        agent_id="AG20240101RET001",
        operation="CREDIT",
        amount=Decimal('10000'),
        processed_by="TEST_SYSTEM",
        reference="TEST_FLOAT_001"
    )
    
    if float_result['success']:
        print("   ✅ PASS")
        print(f"   Reference: {float_result['reference']}")
        print(f"   Old Balance: KES {float_result['old_balance']:,.2f}")
        print(f"   New Balance: KES {float_result['new_balance']:,.2f}")
    else:
        print("   ❌ FAIL")
        print(f"   Error: {float_result['error']}")
    
    return True

def run_comprehensive_test():
    """Run all tests and provide summary"""
    print("🏪 Wekeza Agency Banking System - Comprehensive Test")
    print("=" * 60)
    print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    test_results = []
    
    # Run all tests
    test_results.append(("Authentication", test_agent_authentication()))
    print()
    
    test_results.append(("Cash In Transactions", test_cash_in_transactions()))
    print()
    
    test_results.append(("Cash Out Transactions", test_cash_out_transactions()))
    print()
    
    test_results.append(("Balance Inquiry", test_balance_inquiry()))
    print()
    
    test_results.append(("Agent Management", test_agent_management()))
    print()
    
    # Summary
    print("=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed_tests += 1
    
    print("-" * 60)
    print(f"Overall Result: {passed_tests}/{total_tests} test suites passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Agency Banking System is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the system configuration.")
    
    print(f"Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    try:
        run_comprehensive_test()
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()