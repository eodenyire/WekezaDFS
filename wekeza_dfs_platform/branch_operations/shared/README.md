# `shared/` Module – Banking DFS Platform

## Overview

The `shared/` folder contains **reusable, system-wide services and utilities** used across all modules in the banking DFS system (Teller, Customer Ops, Cash Office, Bancassurance, Supervision).
Its purpose is to centralize **authentication, API communication, role-based access, constants, and audit logging**, ensuring consistency, security, and maintainability.

---

## Folder Structure

```
shared/
├── auth.py            # Authentication and JWT token management
├── api_client.py      # Centralized backend API client with retry and token support
├── permissions.py     # Global role-based access control (RBAC)
├── constants.py       # System-wide constants (currencies, branches, limits, transaction types)
└── audit.py           # Audit logging for all system actions
```

---

## Modules

### 1. `auth.py`

Handles **authentication and session management**.

#### Features:

* JWT token generation and validation
* Role-based session enforcement
* Login simulation

#### Example Usage:

```python
from shared.auth import login, validate_session

# Generate session token
token = login(user_id="TEL-001", role="teller", branch_code="NBO-HQ")

# Validate session and role
payload = validate_session(token, required_roles=["teller"])
print(payload["user_id"], payload["role"])
```

---

### 2. `api_client.py`

Provides a **centralized interface for backend API requests**.

#### Features:

* GET, POST, PUT requests
* Optional JWT token authentication
* Retry logic and request timeout
* Unified error handling

#### Example Usage:

```python
from shared.api_client import get_request, post_request

# GET request with optional JWT token
data = get_request("/teller/balance", params={"account_no": "12345678"}, token=token)

# POST request
payload = {"account_no": "12345678", "amount": 1000}
res = post_request("/teller/deposit", payload, token=token)
```

---

### 3. `permissions.py`

Manages **role-based access control (RBAC)** for all modules.

#### Features:

* Central dictionary of roles and allowed operations
* Helper functions for checking permissions per operation
* Easy to extend with new roles and operations

#### Example Usage:

```python
from shared.permissions import can_deposit_cash, can_view_reports

role = "teller"
if can_deposit_cash(role):
    print("User can perform cash deposit")
else:
    print("Access denied")
```

---

### 4. `constants.py`

Contains **system-wide constants**.

#### Features:

* Currency symbols and codes
* Branch codes
* Transaction types
* Transaction limits (teller, cash office, ATM)
* Status constants (pending, approved, rejected)
* Date and datetime formats
* Transaction reference prefixes

#### Example Usage:

```python
from shared.constants import CURRENCY, TRANSACTION_TYPES, LIMITS

print(f"Currency: {CURRENCY}")
print(f"Cash deposit limit for teller: {LIMITS['teller_cash_hold']}")
```

---

### 5. `audit.py`

Handles **centralized audit logging for compliance and traceability**.

#### Features:

* Logs all actions with timestamp, user, role, branch, operation, and details
* Supports severity levels: INFO, WARNING, ERROR
* Persists logs to file (`audit_log.json`) or backend in production

#### Example Usage:

```python
from shared.audit import log_action

log_action(
    user_id="TEL-001",
    role="teller",
    branch_code="NBO-HQ",
    operation="cash_deposit",
    details={"amount": 5000, "customer_id": "12345678"},
    severity="INFO"
)
```

---

## Best Practices

1. **Always validate roles before performing any operation** using `permissions.py`.
2. **Use `api_client.py`** for all backend interactions to maintain consistency and retry logic.
3. **Log all critical operations** using `audit.py` for audit and compliance purposes.
4. **Use constants from `constants.py`** to avoid hardcoding values in the modules.
5. **Authenticate users** with `auth.py` before any sensitive action, preferably with JWT tokens.

---

## Notes

* The `shared/` module is **reusable across all banking modules**.
* It is designed for **production readiness**, with modularity, security, and maintainability in mind.
* Integration with a real **authentication service** and **database-backed audit logging** is recommended for production.

