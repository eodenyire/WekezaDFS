# shared/audit.py

import os
import json
from datetime import datetime
from shared.constants import DATETIME_FORMAT

# --- CONFIGURATION ---
AUDIT_LOG_FILE = os.getenv("AUDIT_LOG_FILE", "audit_log.json")  # default local file


# --- UTILITY FUNCTIONS ---
def _current_timestamp():
    """Return current timestamp in standardized format."""
    return datetime.now().strftime(DATETIME_FORMAT)


def _write_to_file(log_entry):
    """Append audit entry to local JSON log file."""
    try:
        # Read existing logs
        if os.path.exists(AUDIT_LOG_FILE):
            with open(AUDIT_LOG_FILE, "r") as f:
                logs = json.load(f)
        else:
            logs = []

        # Append new entry
        logs.append(log_entry)

        # Save back to file
        with open(AUDIT_LOG_FILE, "w") as f:
            json.dump(logs, f, indent=4)

    except Exception as e:
        print(f"Audit Logging Error: {e}")


# --- AUDIT LOGGING FUNCTION ---
def log_action(user_id, role, branch_code, operation, details=None, severity="INFO"):
    """
    Log any system action for audit / compliance.

    Args:
        user_id (str): Identifier of the user performing the action
        role (str): Role of the user (teller, supervisor, manager, etc.)
        branch_code (str): Branch code
        operation (str): Operation performed (e.g., 'cash_deposit', 'loan_approval')
        details (dict, optional): Any additional contextual info
        severity (str): Log level ('INFO', 'WARNING', 'ERROR')
    """
    log_entry = {
        "timestamp": _current_timestamp(),
        "user_id": user_id,
        "role": role,
        "branch_code": branch_code,
        "operation": operation,
        "details": details or {},
        "severity": severity
    }

    # Write log entry to file
    _write_to_file(log_entry)

    # Optionally, print to console for dev/debug
    print(f"[{log_entry['timestamp']}] {severity} - {user_id} ({role}) @ {branch_code} - {operation}")


# --- EXAMPLE USAGE ---
if __name__ == "__main__":
    log_action(
        user_id="TEL-001",
        role="teller",
        branch_code="NBO-HQ",
        operation="cash_deposit",
        details={"amount": 2500, "customer_id": "12345678"}
    )
