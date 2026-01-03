# --- ADD THESE IMPORTS AT THE TOP ---
# --- IMPORTS ---
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from . import models, schemas, database, risk_engine, security
import datetime
from sqlalchemy.orm import Session
import uuid



# Create tables automatically (if they don't exist)
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Wekeza Bank DFS Engine",
    description="Professional API for Digital Lending & Risk Scoring",
    version="1.0.0"
)

# --- Routes ---

@app.get("/")
def health_check():
    return {"status": "active", "system": "Wekeza Core Engine"}

@app.post("/users/", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # 1. Check if email exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 2. Create User (Simplified logic - in prod we hash passwords!)
    new_user = models.User(
        full_name=user.full_name,
        email=user.email,
        phone_number=user.phone_number,
        national_id=user.national_id,
        password_hash=user.password # TODO: Hash this!
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user_profile(user_id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
    
# --- ADD THIS NEW ENDPOINT AT THE BOTTOM ---

@app.post("/loans/apply", response_model=schemas.LoanResponse)
def apply_for_loan(application: schemas.LoanRequest, db: Session = Depends(database.get_db)):
    """
    Full Digital Lending Flow:
    1. Validate User
    2. Run Risk Engine (Real-time Scoring)
    3. Create Loan Record (if Approved)
    4. Return Decision
    """
    
    # 1. Check if User Exists
    user = db.query(models.User).filter(models.User.user_id == application.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # 2. Check for Active Loans (Rule: One active loan at a time)
    active_loan = db.query(models.Loan).filter(
        models.Loan.user_id == application.user_id,
        models.Loan.status.in_(["PENDING", "ACTIVE"])
    ).first()
    
    if active_loan:
        raise HTTPException(status_code=400, detail="User already has an active loan")

    # 3. CALL THE RISK ENGINE (The "Brain")
    risk_result = risk_engine.calculate_credit_score(
        user_id=user.user_id,
        amount=float(application.amount),
        kyc_tier=user.kyc_tier
    )
    
    # 4. Save the Logic to 'Risk Scores' Table (Audit Trail)
    # This is crucial for Model Risk Management (your job at Equity!)
    db_score = models.RiskScore(
        user_id=user.user_id,
        credit_score=risk_result["credit_score"],
        risk_tier=risk_result["risk_tier"],
        model_version="v1.0_RuleEngine",
        input_payload={"requested_amount": float(application.amount)},
        decision=risk_result["decision"]
    )
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    
    # 5. Process Decision
    if risk_result["decision"] == "REJECTED":
        raise HTTPException(status_code=400, detail=f"Loan Rejected: {risk_result['reason']}")
    
    # ... inside apply_for_loan function ...
    
    # 6. If APPROVED -> Calculate Fees
    principal = float(application.amount)
    interest_rate = 0.05
    interest_amount = principal * interest_rate
    
    # --- NEW: Credit Life Calculation ---
    insurance_fee = 0.0
    if principal > 10000: # Only for loans above 10k
        insurance_fee = principal * 0.01 # 1% Premium
    
    # Total Due = Principal + Interest (Insurance is usually deducted from disbursement or added to due)
    # Let's deduct from disbursement (Net Disbursement)
    net_disbursement = principal - insurance_fee
    total_due = principal + interest_amount
    
    # Save Loan
    new_loan = models.Loan(
        # ... existing fields ...
        principal_amount=principal,
        total_due_amount=total_due,
        # ...
    )
    
    # If Insurance was charged, create a Policy record automatically
    if insurance_fee > 0:
        # Code to insert into user_policies table linked to this loan_id
        pass 
        
    # ...
    
    return {
        "loan_id": new_loan.loan_id,
        "status": "APPROVED",
        "net_disbursement": net_disbursement, # User gets less than requested due to insurance
        "insurance_fee": insurance_fee
    }
    
    
    # 6. If APPROVED -> Create the Loan
    # Calculate Interest (Flat 5% for now)
    interest_rate = 0.05 
    interest_amount = float(application.amount) * interest_rate
    total_due = float(application.amount) + interest_amount
    
    new_loan = models.Loan(
        user_id=user.user_id,
        risk_score_id=db_score.score_id,
        principal_amount=application.amount,
        interest_rate=interest_rate * 100,
        interest_amount=interest_amount,
        total_due_amount=total_due,
        balance_remaining=total_due,
        due_date=datetime.datetime.now() + datetime.timedelta(days=application.tenure_days),
        status="ACTIVE"
    )
    
    db.add(new_loan)
    db.commit()
    db.refresh(new_loan)
    
    return {
        "loan_id": new_loan.loan_id,
        "status": "APPROVED",
        "total_due_amount": new_loan.total_due_amount
    }    
    

# ... (Database init remains the same) ...

app = FastAPI(title="Wekeza Bank DFS Engine (Secured)", version="2.0.0")

# Security Scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- DEPENDENCY: Get Current User ---
# This function acts as the "Gatekeeper". It checks the token before letting anyone pass.
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

# --- AUTH ROUTES ---

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    # 1. Find User by Email (form_data.username contains email)
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    # 2. Check Password
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Generate Token
    access_token = security.create_access_token(
        data={"sub": user.email, "user_id": user.user_id}
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- UPDATED USER REGISTRATION (Now with Hashing) ---

@app.post("/users/", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # HASH THE PASSWORD HERE!
    hashed_pwd = security.get_password_hash(user.password)
    
    new_user = models.User(
        full_name=user.full_name,
        email=user.email,
        phone_number=user.phone_number,
        national_id=user.national_id,
        password_hash=hashed_pwd # Saved securely
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# --- SECURED LOAN ROUTE ---

@app.post("/loans/apply", response_model=schemas.LoanResponse)
def apply_for_loan(
    application: schemas.LoanRequest, 
    current_user: models.User = Depends(get_current_user), # <--- THIS IS THE LOCK
    db: Session = Depends(database.get_db)
):
    # Notice: We no longer trust 'application.user_id'. We use 'current_user' from the Token.
    
    # 1. Check Active Loans
    active_loan = db.query(models.Loan).filter(
        models.Loan.user_id == current_user.user_id,
        models.Loan.status.in_([models.LoanStatus.PENDING, models.LoanStatus.ACTIVE])
    ).first()
    
    if active_loan:
        raise HTTPException(status_code=400, detail="User already has an active loan")

    # 2. Run Risk Engine
    risk_result = risk_engine.calculate_credit_score(
        user_id=current_user.user_id,
        amount=float(application.amount),
        kyc_tier=current_user.kyc_tier
    )
    
    # ... (Rest of logic is same, just replace user.user_id with current_user.user_id) ...
    # Copy/Paste the saving logic from previous step here using `current_user`
    
    # (Abbreviated for clarity - ensure you copy the saving logic from Step 3 here)
    # ...
    
    # Temporary return for brevity if you haven't copied full logic:
    return {"loan_id": 999, "status": "APPROVED", "total_due_amount": 0.0}    
    
    
---

### 2. Closing the "End-to-End" Gap (Code Logic)
# To fulfill the specific requirement of **"Repaying Loans"** and **"Checking Loan Status"**, we need to add a few final logic blocks to your `backend_api`.

#### A. The Repayment Logic (`POST /loans/repay`)
# *Add this to `main.py`. It handles the "Move" logic (Money moves from Wallet -> Loan).*

@app.post("/loans/repay")
def repay_loan(
    amount: float, 
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    # 1. Get Active Loan
    loan = db.query(models.Loan).filter(
        models.Loan.user_id == current_user.user_id,
        models.Loan.status == models.LoanStatus.ACTIVE
    ).first()
    
    if not loan:
        raise HTTPException(status_code=400, detail="No active loan found to repay.")

    # 2. Check Wallet Balance (BIMS "Save" -> "Borrow" movement)
    wallet = db.query(models.Account).filter(models.Account.user_id == current_user.user_id).first()
    if wallet.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient funds in Wallet.")

    # 3. Process Transaction (ACID Transaction)
    # Debit Wallet
    wallet.balance -= Decimal(amount)
    
    # Credit Loan
    loan.balance_remaining -= Decimal(amount)
    
    # Check if fully paid
    if loan.balance_remaining <= 0:
        loan.status = models.LoanStatus.PAID
        loan.balance_remaining = 0
        msg = "Loan Fully Repaid! Congratulations."
    else:
        msg = f"Partial Repayment Successful. Remaining: {loan.balance_remaining}"

    # Log the Transaction
    txn = models.Transaction(
        account_id=wallet.account_id,
        loan_id=loan.loan_id,
        txn_type="REPAYMENT",
        amount=amount,
        reference_code=f"REP-{uuid.uuid4().hex[:8].upper()}",
        description="Loan Repayment via Web"
    )
    
    db.add(txn)
    db.commit()
    
    return {"status": "SUCCESS", "message": msg, "remaining_balance": loan.balance_remaining}    
    
@app.post("/accounts/deposit")
def deposit_cash(
    amount: float, 
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    # 1. Get Wallet
    wallet = db.query(models.Account).filter(models.Account.user_id == current_user.user_id).first()
    
    # 2. Simulate External Inflow (e.g. from M-Pesa)
    wallet.balance += Decimal(amount)
    
    # 3. Log
    txn = models.Transaction(
        account_id=wallet.account_id,
        txn_type="DEPOSIT",
        amount=amount,
        reference_code=f"DEP-{uuid.uuid4().hex[:8].upper()}",
        description="Cash Deposit via Web Agent"
    )
    
    db.add(txn)
    db.commit()
    
    return {"status": "SUCCESS", "new_balance": wallet.balance}    
    

@app.post("/insurance/buy")
def buy_insurance(
    product_code: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    # 1. Fetch Product
    product = db.query(models.InsuranceProduct).filter(
        models.InsuranceProduct.product_code == product_code
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # 2. Check Wallet Balance
    wallet = db.query(models.Account).filter(models.Account.user_id == current_user.user_id).first()
    if wallet.balance < product.premium_amount:
        raise HTTPException(status_code=400, detail="Insufficient funds for premium.")

    # 3. Process Payment (The "Move" Pillar)
    wallet.balance -= product.premium_amount
    
    # 4. Generate Policy
    policy_num = f"POL-{uuid.uuid4().hex[:8].upper()}"
    new_policy = models.UserPolicy(
        user_id=current_user.user_id,
        product_id=product.product_id,
        policy_number=policy_num,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=30), # Assuming Monthly
        status="ACTIVE",
        auto_renew=True
    )
    
    # 5. Log Transaction
    txn = models.Transaction(
        account_id=wallet.account_id,
        txn_type="FEE", # Insurance is a fee/payment
        amount=product.premium_amount,
        reference_code=f"INS-{uuid.uuid4().hex[:8].upper()}",
        description=f"Premium: {product.product_name}"
    )

    db.add(new_policy)
    db.add(txn)
    db.commit()

    return {"status": "SUCCESS", "policy_number": policy_num, "message": "You are now covered!"}    
    
# --- NEW: ACCOUNT LIFECYCLE (Activate/Disable) ---
@app.post("/accounts/status")
def change_account_status(
    action: str, # "ACTIVATE", "DISABLE", "FREEZE"
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    account = db.query(models.Account).filter(models.Account.user_id == current_user.user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Logic to change status
    if action == "DISABLE":
        account.status = "DISABLED"
        msg = "Account has been disabled. You cannot transact."
    elif action == "ACTIVATE":
        account.status = "ACTIVE"
        msg = "Account successfully activated."
    elif action == "FREEZE":
        # Usually done by Admin, but for self-service let's allow "Locking" funds
        account.status = "FROZEN"
        msg = "Account frozen for security."
    else:
        raise HTTPException(status_code=400, detail="Invalid Action")
    
    db.commit()
    return {"status": "SUCCESS", "new_state": account.status, "message": msg}

# --- NEW: STATEMENTS (The "Save" Pillar) ---
@app.get("/accounts/statement")
def get_statement(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    # Fetch last 20 transactions joined with account
    account = db.query(models.Account).filter(models.Account.user_id == current_user.user_id).first()
    
    txns = db.query(models.Transaction).filter(
        models.Transaction.account_id == account.account_id
    ).order_by(models.Transaction.created_at.desc()).limit(20).all()
    
    return txns

# --- NEW: BRANCH DEPOSIT (The "Teller" Endpoint) ---
# Note: In prod, this would use a "Teller" token. For MVP, we allow open access but log heavily.
@app.post("/branch/deposit")
def branch_cash_deposit(
    national_id: str,
    amount: float,
    teller_id: str,
    db: Session = Depends(database.get_db)
):
    # 1. Find User by ID (Teller doesn't know User_ID, they know National ID)
    user = db.query(models.User).filter(models.User.national_id == national_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    account = db.query(models.Account).filter(models.Account.user_id == user.user_id).first()
    
    # 2. Check if Account is Active
    if account.status != "ACTIVE":
         raise HTTPException(status_code=400, detail=f"Account is {account.status}. Cannot deposit.")

    # 3. Credit Account
    account.balance += Decimal(amount)
    
    # 4. Log as BRANCH_DEPOSIT
    txn = models.Transaction(
        account_id=account.account_id,
        txn_type="DEPOSIT",
        amount=amount,
        reference_code=f"BR-{uuid.uuid4().hex[:6].upper()}",
        description=f"Branch Cash Deposit by Teller {teller_id}"
    )
    
    db.add(txn)
    db.commit()
    
    return {"status": "SUCCESS", "new_balance": account.balance, "customer": user.full_name}

# --- NEW: INTERNAL TRANSFER (The "Move" Pillar) ---
@app.post("/transfers/internal")
def move_money(
    target_account_no: str,
    amount: float,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    # 1. Get Sender
    sender_acc = db.query(models.Account).filter(models.Account.user_id == current_user.user_id).first()
    if sender_acc.balance < Decimal(amount):
        raise HTTPException(status_code=400, detail="Insufficient Funds")
        
    if sender_acc.status != "ACTIVE":
        raise HTTPException(status_code=400, detail="Account Disabled")

    # 2. Get Receiver
    receiver_acc = db.query(models.Account).filter(models.Account.account_number == target_account_no).first()
    if not receiver_acc:
        raise HTTPException(status_code=404, detail="Beneficiary Account Not Found")

    # 3. Execute Transfer
    sender_acc.balance -= Decimal(amount)
    receiver_acc.balance += Decimal(amount)
    
    # 4. Log (Double Entry)
    txn_out = models.Transaction(
        account_id=sender_acc.account_id, txn_type="WITHDRAWAL", amount=amount,
        reference_code=f"TRF-{uuid.uuid4().hex[:6]}", description=f"Transfer to {target_account_no}"
    )
    txn_in = models.Transaction(
        account_id=receiver_acc.account_id, txn_type="DEPOSIT", amount=amount,
        reference_code=f"RCV-{uuid.uuid4().hex[:6]}", description=f"Received from {current_user.full_name}"
    )
    
    db.add_all([txn_out, txn_in])
    db.commit()
    
    return {"status": "SUCCESS", "msg": "Transfer Complete"}    