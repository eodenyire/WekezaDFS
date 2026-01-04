# ✅ `supervision/README.md`

```markdown
# Supervision Module (`supervision/`)

## Overview

The **Supervision module** is designed for **branch supervisors and managers** to enforce **maker–checker workflows**, monitor branch operations, and ensure **compliance and risk management**. This module handles:

- Approval of teller, customer, and credit transactions
- Reversals of erroneous or failed transactions
- Exception handling for special or irregular cases
- Viewing and managing the authorization queue

It integrates with the **core banking backend** via REST APIs and enforces **role-based access control**.

---

## Folder Structure

```

supervision/
├── **init**.py                    # Marks folder as a Python package
├── app.py                         # Main Streamlit UI entry point
├── authorization_queue.py         # Queue of transactions pending approval
├── transaction_approvals.py       # Approve or reject transactions
├── reversals.py                   # Reverse erroneous or failed transactions
├── exception_handling.py          # Handle exceptions or special cases

├── common.py                      # Shared validators, formatting, and UI helpers
├── services/
│   ├── **init**.py
│   ├── api_client.py              # Centralized backend API calls
│   └── permissions.py             # Role-based access & approval limits

````

---

## Module Details

### 1. `app.py`
- **Purpose**: Entry point for Streamlit UI
- **Responsibilities**:
  - Handle supervisor login and session management
  - Render tabs for each module (authorization queue, transaction approvals, reversals, exception handling)
  - Central hub for all supervision tasks
- **Example Usage**:
```python
from authorization_queue import render_queue_ui
from transaction_approvals import render_approvals_ui

tab1, tab2 = st.tabs(["Authorization Queue", "Transaction Approvals"])
with tab1:
    render_queue_ui()
with tab2:
    render_approvals_ui()
````

---

### 2. `authorization_queue.py`

* **Purpose**: Display all transactions pending approval
* **Responsibilities**:

  * Fetch pending transactions from backend
  * Filter by type, branch, amount, or teller
  * Allow supervisor to review before approving or rejecting
* **Backend API Example**: `GET /supervision/authorization-queue`

---

### 3. `transaction_approvals.py`

* **Purpose**: Approve or reject transactions
* **Responsibilities**:

  * Approve teller, customer, or credit operations exceeding limits
  * Reject invalid or suspicious transactions
  * Record approvals/rejections with supervisor ID and timestamp
* **Backend API Examples**:

  * `POST /supervision/approve-transaction`
  * `POST /supervision/reject-transaction`

---

### 4. `reversals.py`

* **Purpose**: Reverse erroneous or failed transactions
* **Responsibilities**:

  * Identify transactions eligible for reversal
  * Process reversal requests
  * Update branch ledger and notify relevant staff
* **Backend API Example**: `POST /supervision/reverse-transaction`

---

### 5. `exception_handling.py`

* **Purpose**: Handle special cases or exceptions
* **Responsibilities**:

  * Resolve failed deposits, withdrawals, or cheque processing errors
  * Handle teller, vault, or ATM discrepancies
  * Provide workflow for exception resolution
* **Backend API Example**: `POST /supervision/handle-exception`

---

### 6. `common.py`

* **Purpose**: Shared utilities for all supervision modules
* **Features**:

  * Validators: `validate_transaction_id()`, `validate_amount()`
  * Formatting: `format_currency()`, `format_date()`
  * UI helpers: `show_approval_receipt()`
  * Session helpers: `get_supervisor_info()`

---

### 7. `services/api_client.py`

* **Purpose**: Centralized API client for supervision operations
* **Features**:

  * GET, POST, PUT, DELETE with error handling
  * Retry logic for transient network errors
  * Handles authentication headers automatically

---

### 8. `services/permissions.py`

* **Purpose**: Role-based access & approval limits
* **Responsibilities**:

  * Determine if supervisor/manager is authorized to approve or reverse a transaction
  * Enforce approval thresholds by transaction type or amount
  * Maintain audit compliance

---

## 🔹 Example Usage

**transaction_approvals.py**

```python
from common import validate_transaction_id, show_approval_receipt, get_supervisor_info
from services.api_client import post_request
from services.permissions import can_approve_transaction

supervisor = get_supervisor_info()

if not can_approve_transaction(supervisor['role'], transaction_amount):
    st.error("You are not authorized to approve this transaction.")
else:
    if not validate_transaction_id(transaction_id):
        st.error("Invalid transaction ID")
    else:
        payload = {
            "supervisor_id": supervisor["supervisor_id"],
            "transaction_id": transaction_id,
            "action": "approve"
        }
        response = post_request("/supervision/approve-transaction", payload)
        show_approval_receipt("Transaction Approval Receipt", response)
```

---

## 🔹 Key Benefits

* **Compliance**: Enforces maker–checker principles for all critical transactions
* **Auditable**: Logs all approvals, reversals, and exceptions with timestamps
* **Secure**: Role-based permissions ensure only authorized supervisors act
* **Modular**: Each function (queue, approvals, reversals, exceptions) is independent
* **Extensible**: Supports future workflows such as automated risk scoring or alert-based approvals

---

## 🔹 Usage Guidelines

1. **Login & Session**

   * Supervisors must log in via `app.py`
   * Session data accessed via `get_supervisor_info()`

2. **Approvals & Reversals**

   * Always use `permissions.py` to verify authorization
   * All actions generate audit logs

3. **Exception Handling**

   * Use `exception_handling.py` for resolving discrepancies
   * Ensure resolution is recorded with timestamps and supervisor ID

---

## Author & Maintainers

* **Team**: Core Banking Development Team – Wekeza Bank DFS System
* **Module Owner**: Branch Supervision Lead
* **Last Updated**: 2026-01-03

```

