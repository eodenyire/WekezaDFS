# bancassurance/services/permissions.py

# --- ROLE DEFINITIONS ---
# Example roles: 'bancassurance_officer', 'bancassurance_supervisor', 'bancassurance_manager'
ROLE_PERMISSIONS = {
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
    },
    "bancassurance_manager": {
        "policy_sales": True,
        "premium_collection": True,
        "claims_tracking": True,
        "reports": True
    }
}


# --- PERMISSION CHECK FUNCTIONS ---
def can_sell_policy(role):
    """
    Check if role is authorized to sell policies.
    """
    return ROLE_PERMISSIONS.get(role, {}).get("policy_sales", False)


def can_collect_premium(role, amount=None):
    """
    Check if role is authorized to collect premiums.
    Optionally, you could enforce limits on amounts for lower-level officers.
    """
    # Example: officers can collect up to KES 500,000
    if role == "bancassurance_officer" and amount and amount > 500_000:
        return False
    return ROLE_PERMISSIONS.get(role, {}).get("premium_collection", False)


def can_manage_claims(role):
    """
    Check if role is authorized to manage (update) claims.
    """
    return ROLE_PERMISSIONS.get(role, {}).get("claims_tracking", False)


def can_view_reports(role):
    """
    Check if role is authorized to view reports.
    """
    return ROLE_PERMISSIONS.get(role, {}).get("reports", False)
