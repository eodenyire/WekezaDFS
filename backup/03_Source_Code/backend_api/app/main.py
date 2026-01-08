from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from decimal import Decimal
import uuid
import models, schemas, database, risk_engine, security

# 1. SETUP
database.Base.metadata.create_all(bind=database.engine)
app = FastAPI(title="Wekeza Bank Universal Core", version="5.0.0")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 2. AUTHENTICATION - COMPLETELY DISABLED
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    # Extract email from simple token
    if token.startswith("simple_token_"):
        email = token.replace("simple_token_", "")
        user = db.query(models.User).filter(models.User.email == email).first()
        if user:
            return user
    raise HTTPException(status_code=401)

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    # NO AUTHENTICATION - Just find user by email
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Return simple token - no password checking at all
    return {"access_token": f"simple_token_{user.email}", "token_type": "bearer"}

# ==========================================
# PART A: PERSONAL BANKING (RETAIL)
# ==========================================

@app.post("/users/")
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    hashed_pwd = security.get_password_hash(user.password)
    new_user = models.User(full_name=user.full_name, email=user.email, national_id=user.national_id, password_hash=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create Personal Wallet
    acc = models.Account(user_id=new_user.user_id, account_number=f"P-{uuid.uuid4().hex[:6].upper()}", balance=0)
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
def repay_retail_loan(amount: float, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    loan = db.query(models.Loan).filter(models.Loan.user_id == current_user.user_id, models.Loan.status == "ACTIVE").first()
    acc = db.query(models.Account).filter(models.Account.user_id == current_user.user_id).first()
    
    if not loan: raise HTTPException(status_code=400, detail="No active loan")
    if acc.balance < Decimal(amount): raise HTTPException(status_code=400, detail="Insufficient Funds")
    
    acc.balance -= Decimal(amount)
    loan.balance_remaining -= Decimal(amount)
    if loan.balance_remaining <= 0: loan.status = "PAID"
    db.commit()
    return {"status": "SUCCESS", "remaining": loan.balance_remaining}

@app.post("/transfers/internal")
def transfer_internal(target_acc: str, amount: float, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    sender = db.query(models.Account).filter(models.Account.user_id == current_user.user_id).first()
    receiver = db.query(models.Account).filter(models.Account.account_number == target_acc).first()
    
    if not receiver: raise HTTPException(status_code=404, detail="Receiver not found")
    if sender.balance < Decimal(amount): raise HTTPException(status_code=400, detail="Insufficient Funds")
    
    sender.balance -= Decimal(amount)
    receiver.balance += Decimal(amount)
    db.commit()
    return {"status": "SUCCESS", "msg": "Transfer Complete"}

@app.post("/insurance/buy")
def buy_personal_insurance(product_code: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    acc = db.query(models.Account).filter(models.Account.user_id == current_user.user_id).first()
    premium = Decimal(100.00)
    if acc.balance < premium: raise HTTPException(status_code=400, detail="Insufficient Funds")
    
    acc.balance -= premium
    policy = models.UserPolicy(user_id=current_user.user_id, product_code=product_code, policy_number=f"POL-{uuid.uuid4().hex[:6]}")
    db.add(policy)
    db.commit()
    return {"status": "ACTIVE", "policy": policy.policy_number}

# ==========================================
# PART B: BUSINESS BANKING (CORPORATE)
# ==========================================

@app.post("/business/register")
def register_business(biz: schemas.BusinessCreate, db: Session = Depends(database.get_db)):
    # 1. Business Entity
    new_biz = models.Business(business_name=biz.business_name, registration_no=biz.registration_no, kra_pin=biz.kra_pin, sector=biz.sector)
    db.add(new_biz)
    db.commit()
    db.refresh(new_biz)
    
    # 2. Director
    hashed_pwd = security.get_password_hash(biz.director_password)
    director = models.User(full_name=f"Director - {biz.business_name}", email=biz.director_email, password_hash=hashed_pwd, business_id=new_biz.business_id)
    db.add(director)
    
    # 3. Corporate Wallet
    biz_acc = models.Account(business_id=new_biz.business_id, account_number=f"B-{uuid.uuid4().hex[:6].upper()}", balance=0)
    db.add(biz_acc)
    db.commit()
    return {"status": "CREATED", "business_id": new_biz.business_id}

@app.post("/business/loans/apply")
def apply_sme_loan(req: schemas.SmeLoanRequest, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    if not current_user.business_id: raise HTTPException(status_code=403, detail="Not a Business Account")
    
    risk = risk_engine.calculate_sme_score(current_user.business_id, float(req.amount), req.sector)
    if risk["decision"] == "REJECTED": raise HTTPException(status_code=400, detail=risk["reason"])
    
    biz_acc = db.query(models.Account).filter(models.Account.business_id == current_user.business_id).first()
    biz_acc.balance += req.amount
    
    # Note: Linking loan to Director for MVP tracking
    loan = models.Loan(user_id=current_user.user_id, principal_amount=req.amount, total_due_amount=req.amount*Decimal(1.1), balance_remaining=req.amount*Decimal(1.1), status="ACTIVE")
    db.add(loan)
    db.commit()
    return {"status": "APPROVED", "new_balance": biz_acc.balance}

@app.post("/business/insurance/quote")
def quote_biz_insurance(product_type: str, value: float, current_user: models.User = Depends(get_current_user)):
    rate = 0.005 if product_type == "WIBA" else 0.0025 # WIBA 0.5%, Asset 0.25%
    premium = max(value * rate, 5000)
    return {"calculated_premium": premium, "declared_value": value}

@app.post("/business/insurance/buy")
def buy_biz_insurance(product_type: str, declared_value: float, premium_amount: float, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    if not current_user.business_id: raise HTTPException(status_code=403, detail="Not Corporate")
    
    biz_acc = db.query(models.Account).filter(models.Account.business_id == current_user.business_id).first()
    if biz_acc.balance < Decimal(premium_amount): raise HTTPException(status_code=400, detail="Insufficient Corporate Funds")
    
    biz_acc.balance -= Decimal(premium_amount)
    
    policy = models.UserPolicy(business_id=current_user.business_id, product_code=product_type, policy_number=f"BZ-{uuid.uuid4().hex[:6]}", premium_paid=premium_amount, cover_amount=declared_value)
    db.add(policy)
    db.commit()
    return {"status": "SUCCESS", "policy_number": policy.policy_number}

# ==========================================
# PART C: BRANCH OPERATIONS
# ==========================================

@app.post("/branch/deposit")
def branch_cash_deposit(national_id: str, amount: float, teller_id: str, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.national_id == national_id).first()
    if not user: raise HTTPException(status_code=404, detail="Customer Not Found")
    
    # Intelligent Routing: Deposit to Business Account if Business User, else Personal
    if user.business_id:
        acc = db.query(models.Account).filter(models.Account.business_id == user.business_id).first()
    else:
        acc = db.query(models.Account).filter(models.Account.user_id == user.user_id).first()
        
    acc.balance += Decimal(amount)
    
    txn = models.Transaction(account_id=acc.account_id, txn_type="DEPOSIT", amount=amount, reference_code=f"BR-{uuid.uuid4().hex[:6]}", description=f"Teller {teller_id}")
    db.add(txn)
    db.commit()
    return {"status": "SUCCESS", "new_balance": acc.balance, "customer": user.full_name}

@app.get("/accounts/statement")
def get_account_statement(current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    acc = db.query(models.Account).filter(models.Account.user_id == current_user.user_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    
    transactions = db.query(models.Transaction).filter(models.Transaction.account_id == acc.account_id).order_by(models.Transaction.created_at.desc()).limit(20).all()
    return [{"created_at": t.created_at, "txn_type": t.txn_type, "amount": t.amount, "reference_code": t.reference_code, "description": t.description} for t in transactions]

@app.post("/accounts/lifecycle")
def account_lifecycle(action: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    acc = db.query(models.Account).filter(models.Account.user_id == current_user.user_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if action == "DISABLE":
        acc.status = "FROZEN"
    elif action == "ACTIVATE":
        acc.status = "ACTIVE"
    
    db.commit()
    return {"status": "SUCCESS", "new_status": acc.status}

@app.get("/business/accounts/me")
def get_business_balance(current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    if not current_user.business_id:
        raise HTTPException(status_code=403, detail="Not a business account")
    
    biz_acc = db.query(models.Account).filter(models.Account.business_id == current_user.business_id).first()
    if not biz_acc:
        raise HTTPException(status_code=404, detail="Business account not found")
    
    loan = db.query(models.Loan).filter(models.Loan.user_id == current_user.user_id, models.Loan.status == "ACTIVE").first()
    return {"balance": biz_acc.balance, "status": biz_acc.status, "active_loan": loan.balance_remaining if loan else 0}