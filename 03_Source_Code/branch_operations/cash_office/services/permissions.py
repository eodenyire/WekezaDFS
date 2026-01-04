"""
Permissions and Cash Limits for Cash Office Operations
"""

# Example configuration for cash limits and roles
TELLER_CASH_LIMITS = {
    "TEL-001": 200000.0,  # Max cash a teller can hold at any time
    "TEL-002": 150000.0,
    "TEL-003": 100000.0,
}

VAULT_LIMIT = 5000000.0  # Max cash allowed in vault
ATM_LIMIT = 1000000.0    # Max cash allowed in a single ATM

SUPERVISOR_APPROVAL_THRESHOLD = 1000000.0  # Any cash operation above this requires supervisor approval


# --- Check if supervisor approval is required ---
def requires_supervisor_approval(officer_id, amount):
    """
    Returns True if a cash operation requires supervisor approval.
    """
    return amount >= SUPERVISOR_APPROVAL_THRESHOLD


# --- Teller cash limit check ---
def teller_limit_check(teller_id, amount):
    """
    Ensures that a teller does not exceed their cash holding limit.
    Returns True if within limit, False if exceeded.
    """
    limit = TELLER_CASH_LIMITS.get(teller_id, 100000.0)  # Default limit if not configured
    if amount > limit:
        return False
    return True


# --- Vault limit check ---
def vault_limit_check(current_vault_balance, amount_to_add):
    """
    Ensures the vault does not exceed its maximum allowed cash limit.
    Returns True if within limit, False if exceeded.
    """
    if current_vault_balance + amount_to_add > VAULT_LIMIT:
        return False
    return True


# --- ATM limit check ---
def atm_limit_check(current_atm_balance, amount_to_load):
    """
    Ensures an ATM does not exceed its maximum cash limit.
    Returns True if within limit, False if exceeded.
    """
    if current_atm_balance + amount_to_load > ATM_LIMIT:
        return False
    return True
