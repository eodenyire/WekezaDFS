import pytest
from unittest.mock import patch
from app import risk_engine

# 1. Test the "Happy Path" (Good Customer)
@patch('app.risk_engine.random.choice')
@patch('app.risk_engine.random.uniform')
def test_calculate_credit_score_approved(mock_uniform, mock_choice):
    """
    Scenario: Customer has High M-Pesa balance and is NOT CRB listed.
    Expected: Decision = APPROVED
    """
    # Force the "random" values to be what we want
    mock_choice.return_value = "CLEAN"        # Force CRB Clean
    mock_uniform.return_value = 50000.0       # Force 50k M-Pesa Balance
    
    result = risk_engine.calculate_credit_score(user_id=1, amount=5000, kyc_tier="TIER_3")
    
    assert result["decision"] == "APPROVED"
    assert result["risk_tier"] == "LOW"
    assert result["credit_score"] > 600

# 2. Test the "Knock-Out Rule" (CRB Listed)
@patch('app.risk_engine.random.choice')
def test_calculate_credit_score_rejected_crb(mock_choice):
    """
    Scenario: Customer is CRB Listed.
    Expected: Decision = REJECTED, Score = 0
    """
    mock_choice.return_value = "LISTED"       # Force CRB Listed
    
    result = risk_engine.calculate_credit_score(user_id=1, amount=5000, kyc_tier="TIER_1")
    
    assert result["decision"] == "REJECTED"
    assert result["reason"] == "Customer is CRB Listed"
    assert result["credit_score"] == 0

# 3. Test the "Over-Leveraged" Rule (Low Balance)
@patch('app.risk_engine.random.choice')
@patch('app.risk_engine.random.uniform')
def test_calculate_credit_score_low_funds(mock_uniform, mock_choice):
    """
    Scenario: Customer asking for 5,000 but avg balance is only 1,000.
    Expected: Decision = REJECTED (Score doesn't hit threshold)
    """
    mock_choice.return_value = "CLEAN"
    mock_uniform.return_value = 1000.0        # Low Balance
    
    # Base score 300. TIER_1 (+0). Balance < Amount/2 (+0). Total = 300.
    # Threshold is 600.
    result = risk_engine.calculate_credit_score(user_id=1, amount=5000, kyc_tier="TIER_1")
    
    assert result["decision"] == "REJECTED"
    assert result["reason"] == "Low Credit Score"