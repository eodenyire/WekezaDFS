from pydantic import BaseModel, EmailStr
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

# --- USER & AUTH ---
class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone_number: str
    national_id: str
    password: str

class UserResponse(BaseModel):
    user_id: int
    full_name: str
    kyc_tier: str
    is_active: bool
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# --- LOANS (BORROW) ---
class LoanRequest(BaseModel):
    amount: Decimal
    tenure_days: int

class LoanResponse(BaseModel):
    loan_id: int
    status: str
    total_due_amount: Decimal
    balance_remaining: Decimal

# --- INSURANCE (INSURE) ---
class PolicyResponse(BaseModel):
    policy_number: str
    status: str
    product_code: str

# --- TRANSACTIONS (MOVE/SAVE) ---
# Used for Branch Deposits & Internal Transfers
class TransferRequest(BaseModel):
    target_acc: str
    amount: Decimal

class DepositRequest(BaseModel):
    national_id: str
    amount: Decimal
    teller_id: str

class TransactionResponse(BaseModel):
    transaction_id: int
    txn_type: str
    amount: Decimal
    reference_code: str
    created_at: datetime
    class Config:
        from_attributes = True
        
# --- BUSINESS BANKING SCHEMAS ---
class BusinessCreate(BaseModel):
    business_name: str
    registration_no: str
    kra_pin: str
    sector: str
    director_email: EmailStr
    director_password: str # For the initial user

class BusinessResponse(BaseModel):
    business_id: int
    business_name: str
    sector: str

class SmeLoanRequest(BaseModel):
    amount: Decimal
    sector: str
    tenure_months: int

class BulkTransferRequest(BaseModel):
    total_amount: Decimal
    description: str
    # In real life, you'd pass a list of beneficiaries here        