#!/usr/bin/env python3
"""
Test FastAPI authentication endpoint directly
"""

import sys
import os

# Add the app directory to Python path
app_dir = os.path.join(os.path.dirname(__file__), '03_Source_Code', 'backend_api', 'app')
sys.path.insert(0, app_dir)

import models, schemas, database, security
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

def test_login_logic():
    print("🔍 Testing FastAPI login logic...")
    
    try:
        # Simulate the login endpoint logic
        db = next(database.get_db())
        
        # Simulate form data
        username = "john@test.com"
        password = "test123"
        
        print(f"Testing login for: {username}")
        
        # Find user
        user = db.query(models.User).filter(models.User.email == username).first()
        if not user:
            print("❌ User not found")
            return
        
        print(f"✅ User found: {user.full_name}")
        
        # Test password verification
        is_valid = security.verify_password(password, user.password_hash)
        print(f"✅ Password verification: {is_valid}")
        
        if not is_valid:
            print("❌ Password verification failed")
            return
        
        # Test token creation
        token = security.create_access_token(data={"sub": user.email})
        print(f"✅ Token created: {token[:50]}...")
        
        # Test response format
        response = {
            "access_token": token,
            "token_type": "bearer"
        }
        print(f"✅ Response format: {response}")
        
        print("🎉 Login logic works perfectly!")
        
    except Exception as e:
        print(f"❌ Error in login logic: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_login_logic()