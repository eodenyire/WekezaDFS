from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import mysql.connector
from decimal import Decimal
import uuid

app = FastAPI(title="Wekeza Bank - Simple Auth", version="1.0.0")

# Test endpoint
@app.get("/")
def root():
    return {"message": "Wekeza Bank API is running", "version": "1.0.0"}

@app.get("/test")
def test():
    return {"status": "Backend is working", "endpoints": ["login", "accounts", "admin/login"]}

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root', 
        password='root',
        database='wekeza_dfs_db'
    )

# Simple request models
class LoginRequest(BaseModel):
    email: str
    password: str

class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str
    phone_number: str = None
    national_id: str = None

# SIMPLE LOGIN - NO JWT
@app.post("/login")
def simple_login(login_data: LoginRequest):
    """Simple login - just check email and password"""
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Check if user exists with this email and password
        cursor.execute("""
            SELECT user_id, full_name, email, business_id 
            FROM users 
            WHERE email = %s AND password_hash = %s AND is_active = 1
        """, (login_data.email, login_data.password))
        
        user = cursor.fetchone()
        
        if user:
            return {
                "success": True,
                "user_id": user['user_id'],
                "full_name": user['full_name'],
                "email": user['email'],
                "is_business": user['business_id'] is not None
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid email or password")
            
    finally:
        conn.close()

# ADMIN LOGIN
@app.post("/admin/login")
def admin_login(login_data: LoginRequest):
    """Admin login with hardcoded admin/admin"""
    
    if login_data.email == "admin" and login_data.password == "admin":
        return {
            "success": True,
            "user_id": 0,
            "full_name": "Administrator",
            "email": "admin",
            "is_admin": True
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")

# CREATE USER
@app.post("/users/create")
def create_user(user_data: UserCreate):
    """Create new user with simple password storage"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Insert user with plain password (no hashing)
        cursor.execute("""
            INSERT INTO users (full_name, email, phone_number, national_id, password_hash, is_active)
            VALUES (%s, %s, %s, %s, %s, 1)
        """, (user_data.full_name, user_data.email, user_data.phone_number, 
              user_data.national_id, user_data.password))
        
        user_id = cursor.lastrowid
        
        # Create account for user
        account_number = f"ACC{1000000 + user_id}"
        cursor.execute("""
            INSERT INTO accounts (user_id, account_number, balance, status)
            VALUES (%s, %s, 10000.00, 'ACTIVE')
        """, (user_id, account_number))
        
        conn.commit()
        
        return {
            "success": True,
            "user_id": user_id,
            "account_number": account_number,
            "message": "User created successfully"
        }
        
    except mysql.connector.IntegrityError as e:
        raise HTTPException(status_code=400, detail="Email already exists")
    finally:
        conn.close()

# GET USER ACCOUNT INFO
@app.get("/accounts/{user_id}")
def get_account_info(user_id: int):
    """Get account information for user"""
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT a.account_number, a.balance, a.status, u.full_name
            FROM accounts a
            JOIN users u ON a.user_id = u.user_id
            WHERE a.user_id = %s
        """, (user_id,))
        
        account = cursor.fetchone()
        
        if account:
            return account
        else:
            raise HTTPException(status_code=404, detail="Account not found")
            
    finally:
        conn.close()

# SIMPLE TRANSFER
@app.post("/transfer")
def simple_transfer(from_user_id: int, to_account: str, amount: float):
    """Simple money transfer"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get sender account
        cursor.execute("SELECT account_id, balance FROM accounts WHERE user_id = %s", (from_user_id,))
        sender = cursor.fetchone()
        
        if not sender or sender[1] < amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        
        # Get receiver account
        cursor.execute("SELECT account_id FROM accounts WHERE account_number = %s", (to_account,))
        receiver = cursor.fetchone()
        
        if not receiver:
            raise HTTPException(status_code=404, detail="Receiver account not found")
        
        # Update balances
        cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s", 
                      (amount, sender[0]))
        cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s", 
                      (amount, receiver[0]))
        
        # Record transaction
        ref_code = f"TXN{uuid.uuid4().hex[:8].upper()}"
        cursor.execute("""
            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description)
            VALUES (%s, 'TRANSFER_OUT', %s, %s, %s)
        """, (sender[0], amount, ref_code, f"Transfer to {to_account}"))
        
        cursor.execute("""
            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description)
            VALUES (%s, 'TRANSFER_IN', %s, %s, %s)
        """, (receiver[0], amount, ref_code, f"Transfer from account"))
        
        conn.commit()
        
        return {"success": True, "reference": ref_code}
        
    finally:
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)