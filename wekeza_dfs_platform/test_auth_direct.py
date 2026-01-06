#!/usr/bin/env python3
"""
Direct test of authentication logic
"""

import sys
import os

# Add the app directory to Python path
app_dir = os.path.join(os.path.dirname(__file__), '03_Source_Code', 'backend_api', 'app')
sys.path.insert(0, app_dir)

try:
    print("Testing authentication components...")
    
    import database
    import models
    import security
    from sqlalchemy.orm import Session
    
    print("✅ All modules imported")
    
    # Test database connection
    db = next(database.get_db())
    print("✅ Database connection established")
    
    # Test user lookup
    user = db.query(models.User).filter(models.User.email == "john@test.com").first()
    if user:
        print(f"✅ Found user: {user.full_name}")
        
        # Test password verification
        test_password = "password123"
        is_valid = security.verify_password(test_password, user.password_hash)
        print(f"✅ Password verification: {is_valid}")
        
        if is_valid:
            # Test token creation
            token = security.create_access_token(data={"sub": user.email})
            print(f"✅ Token created: {token[:50]}...")
        else:
            print("❌ Password verification failed")
    else:
        print("❌ User not found")
    
    db.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()