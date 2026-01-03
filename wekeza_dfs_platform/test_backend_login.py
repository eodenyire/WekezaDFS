#!/usr/bin/env python3
"""
Test backend login directly
"""

import requests
import json

def test_backend_login():
    """Test backend login with known users"""
    
    API_URL = "http://localhost:8000"
    
    # Test users from database
    test_users = [
        {"email": "eodenyire@gmail.com", "password": "password123"},
        {"email": "davidmtune@gmail.com", "password": "business123"},
        {"email": "nuriamghoi@gmail.com", "password": "0746883499"}
    ]
    
    print("🔐 Testing Backend Login API...")
    print("=" * 50)
    
    for user in test_users:
        print(f"\n📧 Testing: {user['email']}")
        
        try:
            response = requests.post(f"{API_URL}/login", json=user)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS: {data['full_name']} (ID: {data['user_id']})")
                print(f"   Business: {data.get('is_business', False)}")
            else:
                print(f"❌ FAILED: {response.text}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_backend_login()