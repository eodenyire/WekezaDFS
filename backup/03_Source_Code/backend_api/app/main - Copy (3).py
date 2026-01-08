from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from decimal import Decimal
import uuid
from . import models, schemas, database, risk_engine, security

# 1. INIT
models.Base.metadata.create_all(bind=database.engine)
app = FastAPI(title="Wekeza Bank Unified Core", version="4.0.0")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 2. AUTH DEPENDENCY
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    try:
        payload = security.jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email: str = payload.get("sub")
        if email is None: raise HTTPException(status_code=401)
    except: raise HTTPException(status_code=401)
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None: raise HTTPException(status_code=401)
    return user

# --- COMMON ENDPOINTS ---

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    return {"access_token": security.create_access_token(data={"sub": user.email}), "token_type": "bearer"}

# --- PERSONAL BANKING (RETAIL) ---

@app.post("/users/")
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    hashed_pwd = security.get_password_hash(user.password)
    new_user = models.User(full_name=user.full_name, email=user.email, national_id=user.national_id, password_hash=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create Personal Wallet
    acc = models.Account(user_id=new_user.user_id, account_number=f"P-{uuid.uuid4().hex[:6].upper()}")
    db.add(acc)
    db.commit()
    return new_user

@app.get("/accounts/me")
def get_personal_balance(current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    acc = db.query(models.Account).filter(models.Account.user_id == current_user.user_id).first()
    loan = db.query(models.Loan).filter(models.Loan.user_id == current_user.user_id, models.Loan.status == "ACTIVE").first()
    return {"balance": acc.balance, "status": acc.status, "active_loan": loan.balance_remaining if loan else 0}

@app.post("/loans/apply")
def apply_retail_loan(req: schemas.LoanRequest, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    # Personal Risk Check
    risk = risk_engine.calculate_credit_score(current_user.user_id, float(req.amount), "TIER_1")
    if risk["decision"] == "REJECTED": raise HTTPException(status_code=400, detail=risk["reason"])
    
    # Disburse
    acc = db.query(models.Account).filter(models.Account.user_id == current_user.user_id).first()
    acc.balance += req.amount
    
    loan = models.Loan(user_id=current_user.user_id, principal_amount=req.amount, total_due_amount=req.amount*Decimal(1.05), balance_remaining=req.amount*Decimal(1.05), status="ACTIVE")
    db.add(loan)
    db.commit()
    return {"status": "APPROVED", "new_balance": acc.balance}

@app.post("/loans/repay")
def repay_loan(amount: float, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    loan = db.query(models.Loan).filter(models.Loan.user_id == current_user.user_id, models.Loan.status == "ACTIVE").first()
    acc = db.query(models.Account).filter(models.Account.user_id == current_user.user_id).first()
    
    if not loan: raise HTTPException(status_code=400, detail="No active loan")
    if acc.balance < Decimal(amount): raise HTTPException(status_code=400, detail="Insufficient Funds")
    
    acc.balance -= Decimal(amount)
    loan.balance_remaining -= Decimal(amount)
    if loan.balance_remaining <= 0: loan.status = "PAID"
    
    db.commit()
    return {"status": "SUCCESS", "remaining": loan.balance_remaining}

@app.post("/insurance/buy")
def buy_insurance(product_code: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    acc = db.query(models.Account).filter(models.Account.user_id == current_user.user_id).first()
    premium = Decimal(100.00)
    if acc.balance < premium: raise HTTPException(status_code=400, detail="Low Balance")
    
    acc.balance -= premium
    policy = models.UserPolicy(user_id=current_user.user_id, product_code=product_code, policy_number=f"POL-{uuid.uuid4().hex[:6]}")
    db.add(policy)
    db.commit()
    return {"status": "ACTIVE", "policy": policy.policy_number}

# --- BUSINESS BANKING (CORPORATE) ---

@app.post("/business/register")
def register_business(biz: schemas.BusinessCreate, db: Session = Depends(database.get_db)):
    # 1. Create Business
    new_biz = models.Business(business_name=biz.business_name, registration_no=biz.registration_no, kra_pin=biz.kra_pin, sector=biz.sector)
    db.add(new_biz)
    db.commit()
    db.refresh(new_biz)
    
    # 2. Create Director (User)
    hashed_pwd = security.get_password_hash(biz.director_password)
    director = models.User(full_name=f"Director - {biz.business_name}", email=biz.director_email, password_hash=hashed_pwd, business_id=new_biz.business_id)
    db.add(director)
    
    # 3. Create Corporate Account
    biz_acc = models.Account(business_id=new_biz.business_id, account_number=f"B-{uuid.uuid4().hex[:6].upper()}")
    db.add(biz_acc)
    db.commit()
    return {"status": "CREATED", "business_id": new_biz.business_id}

@app.post("/business/loans/apply")
def apply_sme_loan(req: schemas.SmeLoanRequest, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    if not current_user.business_id: raise HTTPException(status_code=403, detail="Not a Business Account")
    
    # SME Risk Check (Turnover Logic)
    risk = risk_engine.calculate_sme_score(current_user.business_id, float(req.amount), req.sector)
    if risk["decision"] == "REJECTED": raise HTTPException(status_code=400, detail=risk["reason"])
    
    # Disburse to Business Account
    biz_acc = db.query(models.Account).filter(models.Account.business_id == current_user.business_id).first()
    biz_acc.balance += req.amount
    
    # Log Loan (Linked to Director for MVP simplicity)
    loan = models.Loan(user_id=current_user.user_id, principal_amount=req.amount, total_due_amount=req.amount*Decimal(1.1), balance_remaining=req.amount*Decimal(1.1), status="ACTIVE")
    db.add(loan)
    db.commit()
    return {"status": "APPROVED", "new_balance": biz_acc.balance}

# --- BRANCH OPERATIONS ---

@app.post("/branch/deposit")
def branch_deposit(national_id: str, amount: float, teller_id: str, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.national_id == national_id).first()
    if not user: raise HTTPException(status_code=404, detail="User Not Found")
    
    # Check if user has personal or business account
    if user.business_id:
        acc = db.query(models.Account).filter(models.Account.business_id == user.business_id).first()
    else:
        acc = db.query(models.Account).filter(models.Account.user_id == user.user_id).first()
        
    acc.balance += Decimal(amount)
    
    txn = models.Transaction(account_id=acc.account_id, txn_type="DEPOSIT", amount=amount, reference_code=f"BR-{uuid.uuid4().hex[:6]}", description=f"Teller {teller_id}")
    db.add(txn)
    db.commit()
    return {"status": "SUCCESS", "new_balance": acc.balance, "customer": user.full_name}
    
# --- BUSINESS INSURANCE ENDPOINTS ---

@app.post("/business/insurance/quote")
def get_business_insurance_quote(
    product_type: str, # "WIBA" or "ASSET"
    value: float,      # Payroll Amount or Asset Value
    current_user: models.User = Depends(get_current_user)
):
    """
    Calculates Premium Logic:
    - WIBA: 0.5% of Annual Payroll
    - ASSET: 0.25% of Asset Value
    """
    if not current_user.business_id:
        raise HTTPException(status_code=403, detail="Not a Business Account")

    if product_type == "WIBA":
        rate = 0.005 # 0.5%
        premium = value * rate
        msg = f"WIBA Cover for Payroll of KES {value:,.2f}"
    elif product_type == "ASSET":
        rate = 0.0025 # 0.25%
        premium = value * rate
        msg = f"Asset All Risk for Value of KES {value:,.2f}"
    else:
        raise HTTPException(status_code=400, detail="Unknown Product")
        
    # Minimum Premium Check
    if premium < 5000: premium = 5000

    return {
        "product": product_type,
        "declared_value": value,
        "calculated_premium": premium,
        "description": msg
    }

@app.post("/business/insurance/buy")
def buy_business_insurance(
    product_type: str,
    declared_value: float,
    premium_amount: float,
    current_user: models.User = Depends(get_current_user), 
    db: Session = Depends(database.get_db)
):
    if not current_user.business_id: raise HTTPException(status_code=403, detail="Auth Error")

    # 1. Check Balance
    biz_acc = db.query(models.Account).filter(models.Account.business_id == current_user.business_id).first()
    if biz_acc.balance < Decimal(premium_amount):
        raise HTTPException(status_code=400, detail="Insufficient Corporate Funds")

    # 2. Process Transaction
    biz_acc.balance -= Decimal(premium_amount)
    
    # 3. Create Policy
    policy_ref = f"BIZ-POL-{uuid.uuid4().hex[:6].upper()}"
    new_policy = models.UserPolicy(
        business_id=current_user.business_id,
        product_code=product_type,
        policy_number=policy_ref,
        premium_paid=premium_amount,
        cover_amount=declared_value,
        status="ACTIVE"
    )
    
    # 4. Log Transaction
    txn = models.Transaction(
        account_id=biz_acc.account_id,
        txn_type="INSURANCE_PAYMENT",
        amount=premium_amount,
        reference_code=policy_ref,
        description=f"Premium: {product_type} Cover"
    )

    db.add(new_policy)
    db.add(txn)
    db.commit()

    return {"status": "SUCCESS", "policy_number": policy_ref, "new_balance": biz_acc.balance}    