from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime

# --- AUTH ---
class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    full_name: str
    email: str
    phone_number: str
    national_id: str
    password: str

# --- RETAIL BANKING ---
class LoanRequest(BaseModel):
    amount: Decimal
    tenure_days: int

# --- CORPORATE BANKING ---
class BusinessCreate(BaseModel):
    business_name: str
    registration_no: str
    kra_pin: str
    sector: str
    director_email: str
    director_password: str

class SmeLoanRequest(BaseModel):
    amount: Decimal
    sector: str
    tenure_months: int