#!/usr/bin/env python3
"""
Simple test to verify the system is working
"""

import requests
import json

def test_simple_api():
    """Test basic API connectivity"""
    
    print("🔍 Testing API Connectivity...")
    print("=" * 40)
    
    try:
        # Test docs endpoint
        response = requests.get("http://localhost:8000/docs")
        if response.status_code == 200:
            print("✅ API is running - Docs accessible")
        else:
            print(f"❌ API docs failed - {response.status_code}")
            return
        
        # Test a simple login attempt
        print("\n🔐 Testing Login Endpoint...")
        
        login_data = {
            "username": "test@example.com",
            "password": "any_password"
        }
        
        response = requests.post("http://localhost:8000/token", data=login_data)
        print(f"Login response status: {response.status_code}")
        print(f"Login response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Login endpoint working!")
        elif response.status_code == 401:
            print("ℹ️ Login endpoint working (user not found - expected)")
        else:
            print(f"❌ Login endpoint error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    test_simple_api()