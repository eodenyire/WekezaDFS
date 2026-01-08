from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DECIMAL, Enum, TIMESTAMP, JSON
from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy.sql import func
import enum

# Enums for strict type checking
class KycTier(str, enum.Enum):
    TIER_1 = "TIER_1"
    TIER_2 = "TIER_2"
    TIER_3 = "TIER_3"

class LoanStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    PAID = "PAID"
    DEFAULTED = "DEFAULTED"

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

class Account(Base):
    __tablename__ = "accounts"

    account_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    account_number = Column(String(20), unique=True)
    balance = Column(DECIMAL(15, 2), default=0.00)
    status = Column(String(20), default="ACTIVE")
    
    owner = relationship("User", back_populates="accounts")

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


class Loan(Base):
    __tablename__ = "loans"

    loan_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    principal_amount = Column(DECIMAL(15, 2))
    total_due_amount = Column(DECIMAL(15, 2))
    status = Column(Enum(LoanStatus), default=LoanStatus.PENDING)
    
    borrower = relationship("User", back_populates="loans")