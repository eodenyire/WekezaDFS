#!/usr/bin/env python3
"""
Test script to verify withdrawal validation improvements
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '03_Source_Code', 'branch_operations', 'branch_teller'))

# Mock streamlit for testing
class MockStreamlit:
    def error(self, msg):
        print(f"ERROR: {msg}")

sys.modules['streamlit'] = MockStreamlit()

# Import the functions we want to test
from app import process_withdrawal, get_account_details, get_daily_withdrawal_total

def test_withdrawal_validation():
    """Test various withdrawal scenarios"""
    
    print("🧪 Testing Withdrawal Validation System")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "name": "Valid withdrawal within limits",
            "account": "ACC1000014",
            "amount": 5000,
            "expected_success": True
        },
        {
            "name": "Withdrawal amount too high (above 100k)",
            "account": "ACC1000014", 
            "amount": 150000,
            "expected_success": False,
            "expected_error_type": "ABOVE_MAXIMUM"
        },
        {
            "name": "Withdrawal amount too low (below 100)",
            "account": "ACC1000014",
            "amount": 50,
            "expected_success": False,
            "expected_error_type": "BELOW_MINIMUM"
        },
        {
            "name": "Insufficient funds",
            "account": "ACC1000014",
            "amount": 999999999,  # Very large amount
            "expected_success": False,
            "expected_error_type": "INSUFFICIENT_FUNDS"
        },
        {
            "name": "Invalid account",
            "account": "INVALID123",
            "amount": 5000,
            "expected_success": False,
            "expected_error_type": "ACCOUNT_NOT_FOUND"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        print(f"   Account: {test_case['account']}, Amount: KES {test_case['amount']:,.2f}")
        
        try:
            result = process_withdrawal(
                test_case['account'], 
                test_case['amount'], 
                "Test withdrawal", 
                "TELLER001"
            )
            
            if result and result.get('success') == test_case['expected_success']:
                if test_case['expected_success']:
                    print(f"   ✅ PASS - Withdrawal processed successfully")
                    print(f"      Reference: {result.get('reference_code', 'N/A')}")
                else:
                    error_type = result.get('error_type', 'UNKNOWN')
                    if error_type == test_case.get('expected_error_type'):
                        print(f"   ✅ PASS - Correctly rejected with error: {error_type}")
                        print(f"      Message: {result.get('error', 'No message')}")
                    else:
                        print(f"   ❌ FAIL - Wrong error type. Expected: {test_case.get('expected_error_type')}, Got: {error_type}")
            else:
                print(f"   ❌ FAIL - Unexpected result")
                print(f"      Expected success: {test_case['expected_success']}")
                print(f"      Actual success: {result.get('success') if result else 'None'}")
                if result:
                    print(f"      Error: {result.get('error', 'No error message')}")
                
        except Exception as e:
            print(f"   ❌ ERROR - Exception occurred: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

if __name__ == "__main__":
    test_withdrawal_validation()