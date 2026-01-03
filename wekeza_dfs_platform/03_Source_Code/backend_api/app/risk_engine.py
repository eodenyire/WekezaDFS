import random

# --- RETAIL SCORING (PERSONAL) ---
def calculate_credit_score(user_id: int, amount: float, kyc_tier: str) -> dict:
    """
    Personal Credit Scoring:
    Uses 'Wallet Behavior' and 'Mock CRB' status.
    """
    # 1. Mock Data Source
    crb_status = random.choice(["CLEAN", "CLEAN", "LISTED"]) 
    mpesa_avg = random.uniform(5000, 50000)
    
    score = 300 # Base
    
    # Logic
    if kyc_tier == "TIER_3": score += 200
    elif kyc_tier == "TIER_2": score += 100
    
    if mpesa_avg > amount: score += 150
    
    if crb_status == "LISTED":
        return {"decision": "REJECTED", "reason": "CRB Listed", "credit_score": 0, "risk_tier": "HIGH"}
        
    decision = "APPROVED" if score > 500 else "REJECTED"
    
    return {
        "decision": decision,
        "reason": "Low Score" if decision == "REJECTED" else "Good Standing",
        "credit_score": score,
        "risk_tier": "LOW" if score > 700 else "MEDIUM"
    }

# --- SME SCORING (BUSINESS) ---
def calculate_sme_score(business_id: int, requested_amount: float, sector: str) -> dict:
    """
    Business Credit Scoring:
    Uses 'Turnover Capacity' and 'Sector Risk'.
    """
    # 1. Mock Turnover Data (1M - 50M)
    annual_turnover = random.uniform(1_000_000, 50_000_000)
    
    score = 500 # Base
    
    # Rule 1: Capacity (Max Loan = 20% of Turnover)
    max_limit = annual_turnover * 0.20
    if requested_amount > max_limit:
        return {
            "decision": "REJECTED",
            "reason": f"Amount exceeds capacity (Max: KES {int(max_limit):,})",
            "credit_score": 0,
            "risk_tier": "HIGH"
        }

    # Rule 2: Sector Risk
    if sector == "Agriculture": score -= 50
    elif sector == "Technology": score += 100
    elif sector == "Retail": score += 50
    
    decision = "APPROVED" if score > 550 else "REJECTED"
    
    return {
        "decision": decision,
        "reason": "Sector Risk High" if decision == "REJECTED" else "Strong Turnover",
        "credit_score": score,
        "risk_tier": "LOW" if score > 700 else "MEDIUM"
    }