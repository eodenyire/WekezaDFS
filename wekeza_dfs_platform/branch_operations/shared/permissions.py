# shared/permissions.py

# --- ROLE DEFINITIONS ---
# Example roles in the banking system
ROLE_PERMISSIONS = {
    "teller": {
        "cash_deposit": True,
        "cash_withdrawal": True,
        "cheque_deposit": True,
        "balance_enquiry": True,
        "statement_view": True,
        "cash_position_view": False,
        "eod_approval": False
    },
    "loan_officer": {
        "loan_application": True,
        "loan_disbursement": False,
        "loan_repayment_tracking": True,
        "loan_restructuring": True
    },
    "relationship_officer": {
        "cif_create": True,
        "account_opening": True,
        "account_maintenance": True,
        "account_closure": True,
        "mandate_management": True,
        "enquiries": True
    },
    "supervisor": {
        "authorization_queue": True,
        "transaction_approvals": True,
        "reversals": True,
        "exception_handling": True
    },
    "branch_manager": {
        "overrides": True,
        "branch_cash_position": True,
        "branch_performance": True,
        "end_of_day_approval": True
    },
    "cash_office": {
        "vault_open_close": True,
        "teller_cash_issue": True,
        "teller_cash_receive": True,
        "atm_cash_loading": True,
        "atm_cash_offloading": True,
        "cash_reconciliation": True
    },
    "bancassurance_officer": {
        "policy_sales": True,
        "premium_collection": True,
        "claims_tracking": False,
        "reports": False
    },
    "bancassurance_supervisor": {
        "policy_sales": True,
        "premium_collection": True,
        "claims_tracking": True,
        "reports": True
    }
}

# --- PERMISSION CHECK HELPERS ---
def has_permission(role, operation):
    """
    Check if a role is authorized to perform a given operation.
    
    Args:
        role (str): User role
        operation (str): Operation to check
    Returns:
        bool
    """
    return ROLE_PERMISSIONS.get(role, {}).get(operation, False)


# --- OPERATION-SPECIFIC CHECKS ---
def can_deposit_cash(role):
    return has_permission(role, "cash_deposit")

def can_withdraw_cash(role):
    return has_permission(role, "cash_withdrawal")

def can_view_balance(role):
    return has_permission(role, "balance_enquiry")

def can_approve_eod(role):
    return has_permission(role, "end_of_day_approval")

def can_manage_loans(role):
    return any([
        has_permission(role, "loan_application"),
        has_permission(role, "loan_repayment_tracking"),
        has_permission(role, "loan_restructuring")
    ])

def can_open_account(role):
    return has_permission(role, "account_opening")

def can_collect_premium(role):
    return has_permission(role, "premium_collection")

def can_manage_claims(role):
    return has_permission(role, "claims_tracking")

def can_view_reports(role):
    return has_permission(role, "reports")
