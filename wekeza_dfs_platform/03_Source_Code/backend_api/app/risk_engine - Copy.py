import random

def calculate_credit_score(user_id: int, amount: float, kyc_tier: str) -> dict:
    """
    Simulates a Real-Time Risk Model (e.g., Logistic Regression / XGBoost).
    In a real scenario, this would load a .pkl model file.
    """
    
    # 1. Fetch External Data (Mocking CRB & M-Pesa Integration)
    # In production, this would be an API call to TransUnion or Metropol
    crb_status = random.choice(["CLEAN", "CLEAN", "CLEAN", "LISTED"]) # 25% chance of being listed
    mpesa_avg_balance = random.uniform(1000, 50000)
    
    # 2. The Scoring Logic (The "Alpha Model")
    score = 300 # Base Score
    
    # Rule 1: KYC Bonus
    if kyc_tier == "TIER_2":
        score += 100
    elif kyc_tier == "TIER_3":
        score += 200
        
    # Rule 2: Financial Health (M-Pesa)
    if mpesa_avg_balance > amount:
        score += 150
    elif mpesa_avg_balance > (amount / 2):
        score += 50
        
    # Rule 3: CRB Knockout
    if crb_status == "LISTED":
        score = 0
        decision = "REJECTED"
        reason = "Customer is CRB Listed"
    else:
        # Final Decision Logic
        if score >= 600:
            decision = "APPROVED"
            reason = "Good Credit Standing"
        else:
            decision = "REJECTED"
            reason = "Low Credit Score"

    return {
        "credit_score": score,
        "risk_tier": "LOW" if score > 700 else "HIGH",
        "decision": decision,
        "reason": reason,
        "max_limit": mpesa_avg_balance * 0.8 # Dynamic Limit Assignment
    }
    
def calculate_sme_score(business_id: int, requested_amount: float, sector: str) -> dict:
    """
    SME Scoring Logic:
    1. Turnover Rule: Loan cannot exceed 20% of annual turnover (Simulated).
    2. Sector Risk: Agriculture is High Risk, Tech is Medium, Retail is Low.
    """
    # 1. Simulate Data
    annual_turnover = random.uniform(500000, 10000000) # 500k to 10M
    
    score = 400 # Base
    
    # Rule 1: Turnover Capacity
    max_loan = annual_turnover * 0.20
    if requested_amount > max_loan:
        return {
            "decision": "REJECTED", 
            "reason": f"Amount exceeds limit based on turnover (Max: {int(max_loan)})",
            "credit_score": 0,
            "risk_tier": "HIGH"
        }

    # Rule 2: Sector Risk
    if sector == "Agriculture":
        score -= 50 # High volatility
    elif sector == "Retail":
        score += 100 # High liquidity
        
    # Final Decision
    if score > 450:
        return {"decision": "APPROVED", "credit_score": score, "risk_tier": "LOW"}
    else:
        return {"decision": "REJECTED", "reason": "Sector Risk too high", "credit_score": score, "risk_tier": "HIGH"}


# --- ADD TO risk_engine.py ---

def calculate_sme_score(business_id: int, requested_amount: float, sector: str):
    """
    SME Scoring Logic:
    1. Turnover Rule: Loan cannot exceed 20% of annual turnover (Simulated).
    2. Sector Risk: Agriculture is High Risk, Tech is Medium.
    """
    # Simulate Turnover Data (In real life, fetch from ERP integration)
    annual_turnover = random.uniform(1_000_000, 50_000_000) # 1M to 50M
    
    score = 500 # SME Base Score
    
    # Rule 1: Capacity Check (20% of Turnover)
    max_limit = annual_turnover * 0.20
    if requested_amount > max_limit:
        return {
            "decision": "REJECTED",
            "reason": f"Amount exceeds capacity (Max: {int(max_limit)})",
            "credit_score": 0,
            "risk_tier": "HIGH"
        }

    # Rule 2: Sector Adjustment
    if sector == "Agriculture": score -= 50
    elif sector == "Technology": score += 100
    
    # Final Decision
    decision = "APPROVED" if score > 550 else "REJECTED"
    
    return {
        "decision": decision,
        "credit_score": score,
        "risk_tier": "LOW" if score > 700 else "MEDIUM",
        "reason": "Sector Risk High" if decision == "REJECTED" else "Strong Turnover"
    }        