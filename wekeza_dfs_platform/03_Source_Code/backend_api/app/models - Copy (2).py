from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DECIMAL, Enum, TIMESTAMP, JSON, Date
from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy.sql import func
import enum


# In User Class
business_id = Column(Integer, ForeignKey("businesses.business_id"), nullable=True)

# In Account Class
business_id = Column(Integer, ForeignKey("businesses.business_id"), nullable=True)

# --- ENUMS ---
class KycTier(str, enum.Enum):
    TIER_1 = "TIER_1"
    TIER_2 = "TIER_2"
    TIER_3 = "TIER_3"

class LoanStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    PAID = "PAID"
    DEFAULTED = "DEFAULTED"

class AccountStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"
    DISABLED = "DISABLED"
    DORMANT = "DORMANT"

# --- MODELS ---
class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    phone_number = Column(String(15), unique=True, index=True)
    national_id = Column(String(20), unique=True)
    password_hash = Column(String(255))
    kyc_tier = Column(Enum(KycTier), default=KycTier.TIER_1)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    accounts = relationship("Account", back_populates="owner")
    loans = relationship("Loan", back_populates="borrower")
    policies = relationship("UserPolicy", back_populates="holder")

class Account(Base):
    __tablename__ = "accounts"
    account_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    account_number = Column(String(20), unique=True)
    balance = Column(DECIMAL(15, 2), default=0.00)
    status = Column(Enum(AccountStatus), default=AccountStatus.ACTIVE)
    owner = relationship("User", back_populates="accounts")

class Loan(Base):
    __tablename__ = "loans"
    loan_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    principal_amount = Column(DECIMAL(15, 2))
    interest_amount = Column(DECIMAL(15, 2))
    total_due_amount = Column(DECIMAL(15, 2))
    balance_remaining = Column(DECIMAL(15, 2))
    status = Column(Enum(LoanStatus), default=LoanStatus.PENDING)
    created_at = Column(TIMESTAMP, server_default=func.now())
    borrower = relationship("User", back_populates="loans")

class Transaction(Base):
    __tablename__ = "transactions"
    transaction_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"))
    loan_id = Column(Integer, ForeignKey("loans.loan_id"), nullable=True)
    txn_type = Column(String(50)) # DEPOSIT, WITHDRAWAL, DISBURSEMENT, REPAYMENT
    amount = Column(DECIMAL(15, 2))
    reference_code = Column(String(50), unique=True)
    description = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())

class RiskScore(Base):
    __tablename__ = "risk_scores"
    score_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    credit_score = Column(Integer)
    risk_tier = Column(String(20))
    model_version = Column(String(50))
    input_payload = Column(JSON)
    decision = Column(String(20))
    created_at = Column(TIMESTAMP, server_default=func.now())

# --- INSURANCE MODELS ---
class InsuranceProduct(Base):
    __tablename__ = "insurance_products"
    product_id = Column(Integer, primary_key=True)
    product_name = Column(String(100))
    product_code = Column(String(20), unique=True)
    premium_amount = Column(DECIMAL(15, 2))
    cover_amount = Column(DECIMAL(15, 2))

class UserPolicy(Base):
    __tablename__ = "user_policies"
    policy_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    product_id = Column(Integer, ForeignKey("insurance_products.product_id"))
    policy_number = Column(String(50), unique=True)
    status = Column(String(20), default="ACTIVE")
    holder = relationship("User", back_populates="policies")
    
# --- BUSINESS BANKING MODELS ---

class Business(Base):
    __tablename__ = "businesses"
    business_id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String(100))
    registration_no = Column(String(50), unique=True) # Cert of Incorporation
    kra_pin = Column(String(20), unique=True)
    sector = Column(String(50)) # Retail, Agric, Tech
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    accounts = relationship("Account", back_populates="business_owner")
    users = relationship("User", back_populates="business")

# Update User table to link to Business
# Add this column to your existing User class:
# business_id = Column(Integer, ForeignKey("businesses.business_id"), nullable=True)
# business = relationship("Business", back_populates="users")

# Update Account table to belong to EITHER a User OR a Business
# Add this column to your existing Account class:
# business_id = Column(Integer, ForeignKey("businesses.business_id"), nullable=True)
# business_owner = relationship("Business", back_populates="accounts")

class BulkTransfer(Base):
    __tablename__ = "bulk_transfers"
    batch_id = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey("businesses.business_id"))
    total_amount = Column(DECIMAL(15, 2))
    status = Column(String(20)) # PENDING, APPROVED, PROCESSED
    created_by = Column(Integer, ForeignKey("users.user_id")) # Maker
    approved_by = Column(Integer, ForeignKey("users.user_id"), nullable=True) # Checker
    created_at = Column(TIMESTAMP, server_default=func.now())    
    
    
# --- ADD AT THE BOTTOM OF models.py ---

class Business(Base):
    __tablename__ = "businesses"
    business_id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String(100))
    registration_no = Column(String(50), unique=True) # Cert of Incorporation
    kra_pin = Column(String(20), unique=True)
    sector = Column(String(50)) # Retail, Agric, Tech
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # One Business has many Signatories (Users)
    signatories = relationship("User", back_populates="business")

class BulkTransfer(Base):
    __tablename__ = "bulk_transfers"
    batch_id = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey("businesses.business_id"))
    total_amount = Column(DECIMAL(15, 2))
    status = Column(String(20), default="PENDING") # PENDING, APPROVED
    description = Column(String(100))
    created_at = Column(TIMESTAMP, server_default=func.now())

# --- UPDATE User CLASS ---
# You must modify the existing User class to add this Relationship:
# class User(Base):
#     ... existing columns ...
#     business_id = Column(Integer, ForeignKey("businesses.business_id"), nullable=True)
#     business = relationship("Business", back_populates="signatories")    