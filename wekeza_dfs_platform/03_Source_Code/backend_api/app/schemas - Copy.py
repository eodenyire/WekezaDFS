from pydantic import BaseModel, EmailStr
from typing import Optional
from decimal import Decimal

# --- User Schemas ---
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

# --- Loan Schemas ---
class LoanRequest(BaseModel):
    user_id: int
    amount: Decimal
    tenure_days: int

class LoanResponse(BaseModel):
    loan_id: int
    status: str
    total_due_amount: Decimal