#!/usr/bin/env python3
"""
Simple API Testing Script for Wekeza DFS Platform
Run this script to test if your backend API is working correctly.
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

def test_api_health():
    """Test if API is running and accessible"""
    print("🔍 Testing API Health...")
    try:
        response = requests.get(f"{API_BASE}/docs")
        if response.status_code == 200:
            print("✅ API is running - Swagger UI accessible")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API - Make sure backend is running on port 8000")
        return False
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def test_user_registration():
    """Test user registration endpoint"""
    print("\n🔍 Testing User Registration...")
    
    test_user = {
        "full_name": "Test User",
        "email": "test@wekeza.com",
        "phone_number": "0712345678",
        "national_id": "12345678",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{API_BASE}/users/", json=test_user)
        if response.status_code == 200:
            print("✅ User registration successful")
            return True
        elif response.status_code == 400:
            print("⚠️  User might already exist (this is normal)")
            return True
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing registration: {e}")
        return False

def test_user_login():
    """Test user login and token generation"""
    print("\n🔍 Testing User Login...")
    
    login_data = {
        "username": "test@wekeza.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{API_BASE}/token", data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Login successful - Token received")
            return token_data.get("access_token")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error testing login: {e}")
        return None

def test_protected_endpoint(token):
    """Test accessing protected endpoint with token"""
    print("\n🔍 Testing Protected Endpoint...")
    
    if not token:
        print("❌ No token available - skipping protected endpoint test")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE}/accounts/me", headers=headers)
        if response.status_code == 200:
            print("✅ Protected endpoint accessible with token")
            account_data = response.json()
            print(f"   Account Balance: KES {account_data.get('balance', 'N/A')}")
            return True
        else:
            print(f"❌ Protected endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing protected endpoint: {e}")
        return False

def test_database_connection():
    """Test if database tables are created"""
    print("\n🔍 Testing Database Connection...")
    print("   (Check your MySQL database for these tables:)")
    print("   - users")
    print("   - accounts") 
    print("   - loans")
    print("   - transactions")
    print("   - user_policies")
    print("   ✅ Run: 'USE wekeza_dfs_db; SHOW TABLES;' in MySQL to verify")

def main():
    """Run all API tests"""
    print("🚀 Wekeza DFS Platform API Testing")
    print("=" * 50)
    
    # Test 1: API Health
    if not test_api_health():
        print("\n❌ API is not running. Please start the backend first:")
        print("   cd 03_Source_Code/backend_api")
        print("   python -m uvicorn app.main:app --reload --port 8000")
        return
    
    # Test 2: User Registration
    test_user_registration()
    
    # Test 3: User Login
    token = test_user_login()
    
    # Test 4: Protected Endpoint
    test_protected_endpoint(token)
    
    # Test 5: Database Info
    test_database_connection()
    
    print("\n" + "=" * 50)
    print("🎉 API Testing Complete!")
    print("\nNext Steps:")
    print("1. Open http://localhost:8000/docs to explore all endpoints")
    print("2. Test the web portals:")
    print("   - Customer: http://localhost:8502")
    print("   - Business: http://localhost:8504") 
    print("   - Admin: http://localhost:8503")

if __name__ == "__main__":
    main()