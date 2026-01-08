# `credit_ops/` Module – Banking DFS Platform

## Overview

The `credit_ops/` module handles **loan and credit operations** within the branch. It is primarily used by **Loan Officers, Credit Officers, and Supervisors** to manage the **loan lifecycle**, from application to disbursement, repayment tracking, and restructuring.

This module is designed to integrate seamlessly with the **shared services** (`auth`, `api_client`, `permissions`, `audit`, `constants`) and the **branch backend**.

---

## Folder Structure

```
credit_ops/
├── app.py                  # Main entry point for the Credit Operations UI
├── loan_application.py     # Handle new loan applications
├── loan_setup.py           # Configure loan products and schedules
├── disbursement.py         # Disburse loan funds to customer accounts
├── repayment_tracking.py   # Track loan repayments and outstanding balances
└── restructuring.py        # Handle loan restructuring or rescheduling
```

---

## Modules & Functionality

### 1. `app.py`

**Main entry point** for the Credit Operations interface.

* Initializes the module UI (Streamlit / web interface)
* Provides **tabs or menus** for:

  * Loan application submission
  * Disbursement management
  * Repayment tracking
  * Loan restructuring
* Handles **user authentication** and **role-based access**.
* Uses **shared services** for API calls, permissions, and audit logging.

---

### 2. `loan_application.py`

Handles **new loan applications**:

* Input customer details and CIF information
* Loan product selection and eligibility checks
* Credit scoring and risk assessment integration
* Submits applications to backend for approval

**Key Features:**

* Validation of customer eligibility
* Integration with `shared/api_client.py` for backend communication
* Logs all actions using `shared/audit.py`

---

### 3. `loan_setup.py`

Handles **loan product configuration**:

* Define loan types, interest rates, repayment schedules
* Set maximum/minimum loan amounts per product
* Configure fees, penalties, and approval thresholds

**Key Features:**

* Centralized loan setup for branch-wide use
* Role-based access: typically **branch manager or credit supervisor**

---

### 4. `disbursement.py`

Manages **loan disbursement to customer accounts**:

* Approve and release funds to approved applications
* Track disbursement history and status
* Integration with **teller / cash office** if disbursing in cash

**Key Features:**

* API calls via `shared/api_client.py`
* Audit logging for every disbursement
* Validation of available branch cash and teller limits

---

### 5. `repayment_tracking.py`

Tracks **loan repayment schedules** and balances:

* Monitor individual loan repayment history
* Calculate outstanding principal and interest
* Flag overdue payments for follow-up

**Key Features:**

* Integration with core backend
* Alerts and status updates for late payments
* Supports role-based access: loan officer vs. supervisor

---

### 6. `restructuring.py`

Handles **loan rescheduling or restructuring**:

* Modify repayment schedules
* Apply revised interest rates or penalties
* Submit restructuring requests for approval

**Key Features:**

* Supports maker-checker workflow: officer submits, supervisor approves
* Audit logging for compliance and regulatory reporting
* Ensures branch limits and exposure rules are enforced

---

## Shared Module Integration

All modules within `credit_ops/` integrate with **shared services**:

* **Authentication:** `shared/auth.py` ensures secure user sessions
* **API Calls:** `shared/api_client.py` for backend communication
* **Permissions:** `shared/permissions.py` enforces role-based access
* **Audit Logging:** `shared/audit.py` for traceability
* **Constants:** `shared/constants.py` provides system-wide reference values

---

## Roles & Access

| Role              | Permissions in Credit Ops                                      |
| ----------------- | -------------------------------------------------------------- |
| Loan Officer      | Create applications, track repayments, submit restructuring    |
| Credit Supervisor | Approve loan applications, disbursement, restructuring         |
| Branch Manager    | Configure loan products, override approvals, end-of-day checks |

---

## Best Practices

1. **Always validate permissions** before performing any operation.
2. **Audit every critical action** using the shared audit module.
3. **Use constants** for currency, branch codes, and limits.
4. **Handle retries** for all backend API calls using `shared/api_client.py`.
5. **Follow maker-checker workflows** for approvals and restructuring.

---

## Example Usage

```python
from shared.auth import login, validate_session
from shared.api_client import post_request
from shared.permissions import has_permission
from shared.audit import log_action

# Login as loan officer
token = login(user_id="LO-001", role="loan_officer", branch_code="NBO-HQ")

# Validate permission to create loan
if has_permission("loan_officer", "loan_application"):
    payload = {
        "customer_id": "12345678",
        "loan_product": "Personal Loan",
        "amount": 500000
    }
    response = post_request("/credit/loan-application", payload, token=token)
    log_action("LO-001", "loan_officer", "NBO-HQ", "loan_application", details=payload)
```

---

## Notes

* This module is **branch-specific** and designed to work within the **branch operations portal**.
* Integrates fully with **teller operations** for cash disbursement and repayments.
* Supports **maker-checker workflow** for all critical operations.

---

