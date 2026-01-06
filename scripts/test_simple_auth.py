#!/usr/bin/env python3
"""
Test simple authentication directly
"""

import sys
import os
import hashlib

# Add the app directory to Python path
app_dir = os.path.join(os.path.dirname(__file__), '03_Source_Code', 'backend_api', 'app')
sys.path.insert(0, app_dir)

import database
import models
from sqlalchemy.orm import Session

def simple_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

def test_simple_auth():
    print("🔍 Testing simple authentication...")
    
    # Test database connection
    db = next(database.get_db())
    
    # Test user lookup
    user = db.query(models.User).filter(models.User.email == "john@test.com").first()
    if user:
        print(f"✅ Found user: {user.full_name}")
        print(f"   Email: {user.email}")
        print(f"   Stored hash: {user.password_hash}")
        
        # Test password
        test_password = "test123"
        expected_hash = simple_hash(test_password)
        print(f"   Expected hash: {expected_hash}")
        print(f"   Match: {user.password_hash == expected_hash}")
        
        if user.password_hash == expected_hash:
            print("✅ Authentication should work!")
        else:
            print("❌ Hash mismatch - authentication will fail")
    else:
        print("❌ User not found")
    
    db.close()

if __name__ == "__main__":
    test_simple_auth()