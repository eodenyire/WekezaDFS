from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DECIMAL, Enum, TIMESTAMP, JSON
from sqlalchemy.orm import relationship
import database
from sqlalchemy.sql import func
import enum

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

# --- CORE ENTITIES ---

class Business(database.Base):
    __tablename__ = "businesses"
    business_id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String(100))
    registration_no = Column(String(50), unique=True)
    kra_pin = Column(String(20), unique=True)
    sector = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    signatories = relationship("User", back_populates="business")
    accounts = relationship("Account", back_populates="business_owner")

class User(database.Base):
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
    
    # Links
    business_id = Column(Integer, ForeignKey("businesses.business_id"), nullable=True)
    business = relationship("Business", back_populates="signatories")
    
    accounts = relationship("Account", back_populates="owner")
    loans = relationship("Loan", back_populates="borrower")
    policies = relationship("UserPolicy", back_populates="holder")

class Account(database.Base):
    __tablename__ = "accounts"
    account_id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String(20), unique=True)
    balance = Column(DECIMAL(15, 2), default=0.00)
    status = Column(Enum(AccountStatus), default=AccountStatus.ACTIVE)
    
    # Can belong to User OR Business
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    business_id = Column(Integer, ForeignKey("businesses.business_id"), nullable=True)
    
    owner = relationship("User", back_populates="accounts")
    business_owner = relationship("Business", back_populates="accounts")

# --- BIMS PRODUCTS ---

class Loan(database.Base):
    __tablename__ = "loans"
    loan_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id")) # Linked to Director/Individual
    principal_amount = Column(DECIMAL(15, 2))
    total_due_amount = Column(DECIMAL(15, 2))
    balance_remaining = Column(DECIMAL(15, 2))
    status = Column(Enum(LoanStatus), default=LoanStatus.PENDING)
    created_at = Column(TIMESTAMP, server_default=func.now())
    borrower = relationship("User", back_populates="loans")

class UserPolicy(database.Base):
    __tablename__ = "user_policies"
    policy_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    product_code = Column(String(20))
    policy_number = Column(String(50), unique=True)
    status = Column(String(20), default="ACTIVE")
    holder = relationship("User", back_populates="policies")

class Transaction(database.Base):
    __tablename__ = "transactions"
    transaction_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"))
    txn_type = Column(String(50)) 
    amount = Column(DECIMAL(15, 2))
    reference_code = Column(String(50), unique=True)
    description = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())

class RiskScore(database.Base):
    __tablename__ = "risk_scores"
    score_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id")) # Or Business ID logic
    credit_score = Column(Integer)
    decision = Column(String(20))
    created_at = Column(TIMESTAMP, server_default=func.now())

class BulkTransfer(database.Base):
    __tablename__ = "bulk_transfers"
    batch_id = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey("businesses.business_id"))
    total_amount = Column(DECIMAL(15, 2))
    status = Column(String(20), default="PENDING")
    description = Column(String(100))
    created_at = Column(TIMESTAMP, server_default=func.now())    