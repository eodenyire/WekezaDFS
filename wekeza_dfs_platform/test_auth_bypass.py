#!/usr/bin/env python3
"""
Test Authentication Bypass - Verify that login works without password validation
"""

import requests
import json

API_URL = "http://localhost:8000"

def test_login_bypass():
    """Test that any password works for existing users"""
    
    # Test users from our database
    test_users = [
        "john@test.com",
        "jane@test.com", 
        "mike@test.com",
        "sarah@test.com",
        "david@test.com"
    ]
    
    print("🔐 Testing Authentication Bypass...")
    print("=" * 50)
    
    for email in test_users:
        print(f"\n📧 Testing: {email}")
        
        # Try login with any password
        response = requests.post(f"{API_URL}/token", 
                               data={"username": email, "password": "any_password_works"})
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data['access_token']
            print(f"✅ Login SUCCESS - Token: {token[:30]}...")
            
            # Test API call with token
            headers = {"Authorization": f"Bearer {token}"}
            account_response = requests.get(f"{API_URL}/accounts/me", headers=headers)
            
            if account_response.status_code == 200:
                account_data = account_response.json()
                print(f"✅ Account Access SUCCESS - Balance: KES {account_data['balance']:,.2f}")
            else:
                print(f"❌ Account Access FAILED - {account_response.status_code}")
        else:
            print(f"❌ Login FAILED - {response.status_code}: {response.text}")
    
    print("\n" + "=" * 50)
    print("🎯 Authentication bypass test complete!")

if __name__ == "__main__":
    test_login_bypass()