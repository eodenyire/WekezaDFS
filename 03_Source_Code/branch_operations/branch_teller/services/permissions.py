# -----------------------------------------------------------------------------
# Teller Limits & Role Permissions
# -----------------------------------------------------------------------------

# Example configuration (can also be loaded from DB or config file)
TELLER_LIMITS = {
    "TEL-001": 100000.0,  # max cash withdrawal teller can approve
    "TEL-002": 50000.0,
    "TEL-003": 200000.0,
}

ROLE_PERMISSIONS = {
    "teller": [
        "cash_deposit",
        "cash_withdrawal",
        "cheque_deposit",
        "balance_enquiry",
        "statement_view",
        "cash_position",
        "eod_balance"
    ],
    "supervisor": [
        "approve_withdrawal",
        "approve_cheque",
        "override_eod_discrepancy",
        "view_all_transactions"
    ],
    "manager": [
        "all_permissions"  # full access
    ],
}

# -----------------------------------------------------------------------------
# FUNCTIONS
# -----------------------------------------------------------------------------
def get_teller_limit(teller_id: str) -> float:
    """
    Returns the cash limit for a given teller.
    """
    return TELLER_LIMITS.get(teller_id, 0.0)

def can_perform_action(role: str, action: str) -> bool:
    """
    Checks if a role can perform a specific action.
    """
    if role not in ROLE_PERMISSIONS:
        return False
    permissions = ROLE_PERMISSIONS[role]
    if "all_permissions" in permissions:
        return True
    return action in permissions

def requires_supervisor_approval(teller_id: str, amount: float) -> bool:
    """
    Determines if a transaction requires supervisor approval
    based on teller limit.
    """
    limit = get_teller_limit(teller_id)
    return amount > limit

# -----------------------------------------------------------------------------
# EXAMPLES
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print("TEL-001 Limit:", get_teller_limit("TEL-001"))
    print("Can teller perform cash withdrawal?", can_perform_action("teller", "cash_withdrawal"))
    print("Does TEL-002 require approval for 60000?", requires_supervisor_approval("TEL-002", 60000))
