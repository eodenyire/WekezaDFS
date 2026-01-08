from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from decimal import Decimal
import uuid
import datetime

# Internal Imports
from . import models, schemas, database, risk_engine, security

# Initialize DB
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Wekeza Bank DFS Engine (BIMS Complete)", version="3.0.0")

# --- SECURITY DEPENDENCY ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = security.jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except security.JWTError:
        raise credentials_exception
        
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# --- AUTH ENDPOINTS ---
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/")
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # Hash password and create user + default account
    hashed_pwd = security.get_password_hash(user.password)
    new_user = models.User(
        full_name=user.full_name, email=user.email, phone_number=user.phone_number,
        national_id=user.national_id, password_hash=hashed_pwd
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Auto-create Wallet
    new_acc = models.Account(
        user_id=new_user.user_id, account_number=f"100{new_user.user_id}", balance=0.00
    )
    db.add(new_acc)
    db.commit()
    return new_user

# --- BIMS PILLAR 1: BORROW (Loans) ---
@app.post("/loans/apply")
def apply_loan(application: schemas.LoanRequest, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    # 1. Check Existing Loans
    active = db.query(models.Loan).filter(models.Loan.user_id == current_user.user_id, models.Loan.status == "ACTIVE").first()
    if active: raise HTTPException(status_code=400, detail="Pending Loan Exists")
    
    # 2. Risk Engine
    risk = risk_engine.calculate_credit_score(current_user.user_id, float(application.amount), current_user.kyc_tier)
    
    # 3. Log Score
    score_entry = models.RiskScore(user_id=current_user.user_id, credit_score=risk["credit_score"], 
                                 risk_tier=risk["risk_tier"], model_version="v1", decision=risk["decision"])
    db.add(score_entry)
    db.commit()

    if risk["decision"] == "REJECTED":
        raise HTTPException(status_code=400, detail=f"Loan Rejected: {risk['reason']}")
    
    # 4. Disburse
    interest = Decimal(application.amount) * Decimal(0.05)
    total = Decimal(application.amount) + interest
    
    loan = models.Loan(user_id=current_user.user_id, principal_amount=application.amount, 
                     interest_amount=interest, total_due_amount=total, balance_remaining=total, status="ACTIVE")
    
    # Credit Wallet
    wallet = db.query(models.Account).filter(models.Account.user_id == current_user.user_id).first()
    wallet.balance += Decimal(application.amount)
    
    db.add(loan)
    db.commit()
    return {"status": "APPROVED", "msg": "Funds credited to wallet"}

@app.post("/loans/repay")
def repay_loan(amount: float, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    loan = db.query(models.Loan).filter(models.Loan.user_id == current_user.user_id, models.Loan.status == "ACTIVE").first()
    if not loan: raise HTTPException(status_code=400, detail="No active loan")
    
    wallet = db.query(models.Account).filter(models.Account.user_id == current_user.user_id).first()
    if wallet.balance < Decimal(amount): raise HTTPException(status_code=400, detail="Insufficient Wallet Funds")
    
    # Execute Repayment
    wallet.balance -= Decimal(amount)
    loan.balance_remaining -= Decimal(amount)
    if loan.balance_remaining <= 0: loan.status = "PAID"
    
    db.commit()
    return {"status": "SUCCESS", "remaining_loan": loan.balance_remaining}

# --- BIMS PILLAR 2: INSURE (Insurance) ---
@app.post("/insurance/buy")
def buy_insurance(product_code: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    # Simple hardcoded check for MVP
    premium = Decimal(100.00)
    wallet = db.query(models.Account).filter(models.Account.user_id == current_user.user_id).first()
    
    if wallet.balance < premium: raise HTTPException(status_code=400, detail="Insufficient Funds")
    
    wallet.balance -= premium
    policy = models.UserPolicy(user_id=current_user.user_id, product_id=1, policy_number=f"POL-{uuid.uuid4().hex[:6]}", status="ACTIVE")
    db.add(policy)
    db.commit()
    return {"status": "SUCCESS", "policy": policy.policy_number}

# --- BIMS PILLAR 3: MOVE (Transfers) ---
@app.post("/transfers/internal")
def transfer_internal(target_acc: str, amount: float, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    sender = db.query(models.Account).filter(models.Account.user_id == current_user.user_id).first()
    receiver = db.query(models.Account).filter(models.Account.account_number == target_acc).first()
    
    if not receiver: raise HTTPException(status_code=404, detail="Receiver not found")
    if sender.balance < Decimal(amount): raise HTTPException(status_code=400, detail="Insufficient Funds")
    
    sender.balance -= Decimal(amount)
    receiver.balance += Decimal(amount)
    
    txn = models.Transaction(account_id=sender.account_id, txn_type="TRANSFER", amount=amount, reference_code=f"TRF-{uuid.uuid4().hex[:6]}")
    db.add(txn)
    db.commit()
    return {"status": "SUCCESS", "msg": "Transfer Complete"}

# --- BIMS PILLAR 4: SAVE (Account Ops) ---
@app.get("/accounts/me")
def get_my_account(current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    acc = db.query(models.Account).filter(models.Account.user_id == current_user.user_id).first()
    loan = db.query(models.Loan).filter(models.Loan.user_id == current_user.user_id, models.Loan.status == "ACTIVE").first()
    return {
        "account_number": acc.account_number,
        "balance": acc.balance,
        "status": acc.status,
        "active_loan": loan.balance_remaining if loan else 0.00
    }

@app.get("/accounts/statement")
def statement(current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    acc = db.query(models.Account).filter(models.Account.user_id == current_user.user_id).first()
    return db.query(models.Transaction).filter(models.Transaction.account_id == acc.account_id).limit(10).all()

@app.post("/accounts/lifecycle")
def lifecycle(action: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    acc = db.query(models.Account).filter(models.Account.user_id == current_user.user_id).first()
    if action == "DISABLE": acc.status = "DISABLED"
    elif action == "ACTIVATE": acc.status = "ACTIVE"
    db.commit()
    return {"status": acc.status}

# --- STAFF OPS: BRANCH TELLER ---
@app.post("/branch/deposit")
def branch_deposit(national_id: str, amount: float, teller_id: str, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.national_id == national_id).first()
    if not user: raise HTTPException(status_code=404, detail="Customer Not Found")
    
    acc = db.query(models.Account).filter(models.Account.user_id == user.user_id).first()
    if acc.status != "ACTIVE": raise HTTPException(status_code=400, detail="Account Inactive")
    
    acc.balance += Decimal(amount)
    txn = models.Transaction(account_id=acc.account_id, txn_type="DEPOSIT", amount=amount, 
                           reference_code=f"BR-{uuid.uuid4().hex[:6]}", description=f"Teller {teller_id}")
    db.add(txn)
    db.commit()
    return {"status": "SUCCESS", "new_balance": acc.balance, "customer": user.full_name}
    
# --- BUSINESS BANKING ENDPOINTS ---

@app.post("/business/register")
def register_business(biz: schemas.BusinessCreate, db: Session = Depends(database.get_db)):
    # 1. Create Business Entity
    new_biz = models.Business(
        business_name=biz.business_name,
        registration_no=biz.registration_no,
        kra_pin=biz.kra_pin,
        sector=biz.sector
    )
    db.add(new_biz)
    db.commit()
    db.refresh(new_biz)
    
    # 2. Create Director (User) linked to Business
    hashed_pwd = security.get_password_hash(biz.director_password)
    director = models.User(
        full_name=f"Director - {biz.business_name}",
        email=biz.director_email,
        password_hash=hashed_pwd,
        # We need to link this user to the business (Requires model update from Phase 3, Step 3A)
        # Assuming you added 'business_id' to User model as instructed previously
        business_id=new_biz.business_id 
    )
    db.add(director)
    
    # 3. Create Corporate Operating Account
    biz_acc = models.Account(
        account_number=f"BIZ-{uuid.uuid4().hex[:6].upper()}",
        balance=Decimal(0.00),
        status="ACTIVE",
        # Assuming you added 'business_id' to Account model
        business_id=new_biz.business_id
    )
    db.add(biz_acc)
    db.commit()
    
    return {"status": "SUCCESS", "business_id": new_biz.business_id, "message": "Corporate Account Created"}

@app.post("/business/loans/apply")
def apply_sme_loan(
    request: schemas.SmeLoanRequest, 
    current_user: models.User = Depends(get_current_user), 
    db: Session = Depends(database.get_db)
):
    # 1. Verify User is a Business User
    if not current_user.business_id:
        raise HTTPException(status_code=403, detail="Not a Business User")
        
    # 2. Run SME Risk Engine
    risk_result = risk_engine.calculate_sme_score(
        business_id=current_user.business_id, 
        requested_amount=float(request.amount), 
        sector=request.sector
    )
    
    # 3. Process Decision
    if risk_result["decision"] == "REJECTED":
        raise HTTPException(status_code=400, detail=f"Loan Rejected: {risk_result['reason']}")
        
    # 4. Disburse (Simplified)
    # Find Business Account
    biz_acc = db.query(models.Account).filter(models.Account.business_id == current_user.business_id).first()
    biz_acc.balance += request.amount
    
    # Log Loan (Reusing Loan Model, linking to User (Director) for now)
    # In full system, Loan table needs a 'business_id' column too.
    new_loan = models.Loan(
        user_id=current_user.user_id, # Linking to Director for MVP
        principal_amount=request.amount,
        total_due_amount=request.amount * Decimal(1.1), # 10% Flat Rate
        balance_remaining=request.amount * Decimal(1.1),
        status="ACTIVE"
    )
    db.add(new_loan)
    db.commit()
    
    return {"status": "APPROVED", "new_balance": biz_acc.balance}    