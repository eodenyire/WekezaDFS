# ---------------------------------------------------------------------------
# customer_ops/services/permissions.py
# ---------------------------------------------------------------------------
# Role-based access control (RBAC) and limits for customer_ops
# ---------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Role Definitions
# -----------------------------------------------------------------------------
ROLES = {
    "relationship_officer": {
        "cif_create": True,
        "account_opening": True,
        "account_maintenance": True,
        "account_closure": False,
        "mandate_management": True,
        "enquiries": True
    },
    "relationship_manager": {
        "cif_create": True,
        "account_opening": True,
        "account_maintenance": True,
        "account_closure": True,
        "mandate_management": True,
        "enquiries": True
    },
    "branch_manager": {
        "cif_create": True,
        "account_opening": True,
        "account_maintenance": True,
        "account_closure": True,
        "mandate_management": True,
        "enquiries": True
    }
}

# -----------------------------------------------------------------------------
# Permission Check
# -----------------------------------------------------------------------------
def can_perform_action(role: str, action: str) -> bool:
    """
    Check if the given role is authorized to perform a specific action
    """
    if role not in ROLES:
        return False
    return ROLES[role].get(action, False)

# -----------------------------------------------------------------------------
# Optional: Define Limits per Role
# -----------------------------------------------------------------------------
LIMITS = {
    "relationship_officer": {
        "max_daily_accounts": 5,     # max accounts officer can open per day
        "max_cif_per_day": 10
    },
    "relationship_manager": {
        "max_daily_accounts": 20,
        "max_cif_per_day": 50
    }
}

def get_role_limit(role: str, limit_type: str) -> int:
    """
    Retrieve the limit value for a role
    """
    return LIMITS.get(role, {}).get(limit_type, 0)
