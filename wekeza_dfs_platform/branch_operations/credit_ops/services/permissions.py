# credit_ops/services/permissions.py

# -----------------------------------------------------------------------------
# ROLE-BASED PERMISSIONS
# -----------------------------------------------------------------------------
ROLE_PERMISSIONS = {
    "loan_officer": [
        "loan_application",
        "disbursement",
        "repayment_tracking",
    ],
    "supervisor": [
        "loan_application",
        "loan_setup",
        "disbursement",
        "repayment_tracking",
        "restructuring",
    ],
    "manager": [
        "loan_application",
        "loan_setup",
        "disbursement",
        "repayment_tracking",
        "restructuring",
    ],
}

# -----------------------------------------------------------------------------
# OFFICER LIMITS (for Maker-Checker)
# -----------------------------------------------------------------------------
OFFICER_LIMITS = {
    # officer_id: max_loan_amount_without_supervisor
    "LO-001": 500_000,
    "LO-002": 750_000,
    "SUP-001": 2_000_000,
    "MGR-001": 10_000_000
}

# -----------------------------------------------------------------------------
# CHECK PERMISSIONS
# -----------------------------------------------------------------------------
def can_perform_action(role: str, action: str) -> bool:
    """
    Check if a role is authorized to perform an action.
    """
    allowed_actions = ROLE_PERMISSIONS.get(role, [])
    return action in allowed_actions

# -----------------------------------------------------------------------------
# MAKER-CHECKER / SUPERVISOR APPROVAL
# -----------------------------------------------------------------------------
def requires_supervisor_approval(officer_id: str, amount: float) -> bool:
    """
    Determine if a transaction requires supervisor approval based on officer limits.
    """
    limit = OFFICER_LIMITS.get(officer_id, 0)
    return amount > limit
