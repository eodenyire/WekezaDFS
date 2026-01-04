# services/permissions.py

"""
Permissions Module
------------------
Provides role-based access control for branch supervision operations.

Roles can include:
- BranchSupervisor
- BranchManager
- Teller
- LoanOfficer
"""

# -----------------------------
# Permission Checks
# -----------------------------
def can_view_authorization_queue(role: str) -> bool:
    """
    Check if the user role can view the authorization queue.
    """
    allowed_roles = ["BranchSupervisor", "BranchManager"]
    return role in allowed_roles

def can_approve_transaction(role: str) -> bool:
    """
    Check if the user role can approve or reject transactions.
    """
    allowed_roles = ["BranchSupervisor", "BranchManager"]
    return role in allowed_roles

def can_reverse_transaction(role: str) -> bool:
    """
    Check if the user role can reverse transactions.
    """
    allowed_roles = ["BranchSupervisor", "BranchManager"]
    return role in allowed_roles

def can_handle_exceptions(role: str) -> bool:
    """
    Check if the user role can handle exceptions or irregular transactions.
    """
    allowed_roles = ["BranchSupervisor", "BranchManager"]
    return role in allowed_roles

# -----------------------------
# Utility: Combine Checks
# -----------------------------
def has_permission(role: str, action: str) -> bool:
    """
    Generalized permission checker for any action.
    
    Args:
        role (str): User role
        action (str): Action string, e.g. "approve", "reverse", "exceptions"
    
    Returns:
        bool: True if role is allowed, False otherwise
    """
    action_map = {
        "view_queue": can_view_authorization_queue,
        "approve": can_approve_transaction,
        "reverse": can_reverse_transaction,
        "exceptions": can_handle_exceptions
    }
    check_fn = action_map.get(action)
    if check_fn:
        return check_fn(role)
    return False
