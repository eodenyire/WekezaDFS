#!/usr/bin/env python3
"""
Simple FastAPI server with no authentication - just for testing
"""

from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import sys
import os

# Add current directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app import database, models

app = FastAPI(title="Wekeza Simple Test API", version="1.0.0")

# Create tables
models.Base.metadata.create_all(bind=database.engine)

@app.get("/")
def root():
    return {"message": "Wekeza Simple API is running!"}

@app.post("/token")
def simple_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    """Super simple login - no password checking at all"""
    try:
        # Just find the user by email
        user = db.query(models.User).filter(models.User.email == form_data.username).first()
        
        if not user:
            return {"error": "User not found", "available_users": [
                "john@test.com", "jane@test.com", "eodenyire@gmail.com", 
                "director@techsolutions.com", "manager@greenfarm.com"
            ]}
        
        # Return a simple token (just the email for testing)
        fake_token = f"token_for_{user.email.replace('@', '_at_').replace('.', '_dot_')}"
        
        return {
            "access_token": fake_token,
            "token_type": "bearer",
            "user_info": {
                "name": user.full_name,
                "email": user.email
            }
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/accounts/me")
def get_account_info(db: Session = Depends(database.get_db)):
    """Get account info without authentication"""
    try:
        # Just return the first user's account for testing
        user = db.query(models.User).first()
        if not user:
            return {"error": "No users found"}
        
        account = db.query(models.Account).filter(models.Account.user_id == user.user_id).first()
        if not account:
            return {"error": "No account found"}
        
        return {
            "user_name": user.full_name,
            "email": user.email,
            "balance": float(account.balance),
            "account_number": account.account_number,
            "status": account.status,
            "active_loan": 0.0  # Simplified
        }
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)