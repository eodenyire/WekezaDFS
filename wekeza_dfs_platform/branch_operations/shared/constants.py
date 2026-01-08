# shared/constants.py

# --- CURRENCY ---
CURRENCY = "KES"
CURRENCY_SYMBOL = "KSh"

# --- BRANCH CODES ---
BRANCH_CODES = [
    "NBO-HQ",      # Nairobi Headquarters
    "MBO-MKT",     # Mombasa Market Branch
    "KSM-KEN",     # Kisumu Branch
    "NKR-NKR",     # Nakuru Branch
    "ELD-ELD"      # Eldoret Branch
]

# --- TRANSACTION TYPES ---
TRANSACTION_TYPES = {
    "cash_deposit": "Cash Deposit",
    "cash_withdrawal": "Cash Withdrawal",
    "cheque_deposit": "Cheque Deposit",
    "loan_disbursement": "Loan Disbursement",
    "loan_repayment": "Loan Repayment",
    "premium_collection": "Premium Collection",
    "policy_sale": "Policy Sale"
}

# --- LIMITS ---
LIMITS = {
    "teller_cash_hold": 500_000,        # Maximum cash teller can hold in KES
    "cash_office_hold": 10_000_000,    # Maximum cash in vault / cash office
    "atm_cash_capacity": 2_000_000,    # Maximum cash in ATM
    "premium_collection_officer": 500_000,  # Max premium a junior officer can collect
}

# --- STATUS CONSTANTS ---
STATUS = {
    "pending": "Pending",
    "approved": "Approved",
    "rejected": "Rejected",
    "under_review": "Under Review",
    "completed": "Completed",
    "failed": "Failed"
}

# --- DATE FORMATS ---
DATE_FORMAT = "%d-%b-%Y"
DATETIME_FORMAT = "%d-%b-%Y %H:%M:%S"

# --- OTHER CONSTANTS ---
TRANSACTION_PREFIXES = {
    "deposit": "DEP",
    "withdrawal": "WDR",
    "cheque": "CHQ",
    "loan": "LN",
    "premium": "PREM",
    "policy": "POL"
}
