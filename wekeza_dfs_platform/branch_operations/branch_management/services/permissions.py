# branch_management/services/permissions.py
"""
permissions.py

Role-based access control and branch-level authorization for branch management.
"""

from typing import List

# -----------------------------
# Define Roles and Permissions
# -----------------------------
# Each role maps to allowed actions within the branch_management module
ROLE_PERMISSIONS = {
    "BranchManager": [
        "view_cash_position",
        "view_performance",
        "view_reports",
        "download_reports",
        "manage_staff",
        "approve_eod",
        "perform_overrides"
    ],
    "Supervisor": [
        "view_cash_position",
        "view_performance",
        "view_reports",
        "approve_transactions",
        "handle_reversals",
        "handle_exceptions"
    ],
    "Teller": [
        "cash_deposit",
        "cash_withdrawal",
        "view_balance",
        "deposit_cheque",
        "view_statement"
    ],
    "CashOfficer": [
        "vault_open_close",
        "teller_cash_issue",
        "teller_cash_receive",
        "atm_cash_loading",
        "atm_cash_offloading",
        "cash_reconciliation"
    ],
    "LoanOfficer": [
        "loan_application",
        "loan_disbursement",
        "loan_repayment_tracking",
        "loan_restructuring"
    ],
    "RelationshipOfficer": [
        "cif_create",
        "account_opening",
        "account_maintenance",
        "account_closure",
        "mandate_management",
        "customer_enquiries"
    ]
}


# -----------------------------
# Permission Check Utilities
# -----------------------------
def has_permission(role: str, action: str) -> bool:
    """
    Check if a role has permission to perform a specific action.

    Args:
        role (str): Staff or manager role
        action (str): Action to check

    Returns:
        bool: True if allowed, False otherwise
    """
    allowed_actions = ROLE_PERMISSIONS.get(role, [])
    return action in allowed_actions


def check_branch_access(user_branch: str, target_branch: str) -> bool:
    """
    Check if the user has access to perform actions on the given branch.

    Args:
        user_branch (str): Branch code of the user
        target_branch (str): Branch code where action is performed

    Returns:
        bool: True if user can access target branch, False otherwise
    """
    # For now, users can only operate within their branch
    return user_branch == target_branch


def require_permission(role: str, action: str, user_branch: str, target_branch: str):
    """
    Raises an exception if the user does not have the required permission
    or branch access.

    Args:
        role (str): User role
        action (str): Action to validate
        user_branch (str): User's branch code
        target_branch (str): Target branch code for action
    """
    if not has_permission(role, action):
        raise PermissionError(f"Role '{role}' does not have permission to perform '{action}'.")

    if not check_branch_access(user_branch, target_branch):
        raise PermissionError(f"Access denied: Role '{role}' cannot perform actions on branch '{target_branch}'.")
