# ✅ `bancassurance/README.md`

```markdown
# Bancassurance Module (`bancassurance/`)

## Overview

The **Bancassurance module** integrates insurance services into the branch banking ecosystem. It is primarily used by **Bancassurance Officers** to manage:

- Selling insurance policies
- Collecting premiums
- Tracking claims
- Generating reports

This module ensures **role-based access**, **auditability**, and **compliance** with regulatory requirements. It integrates directly with the **core banking backend** and follows the same architectural patterns as other branch modules (`teller/`, `customer_ops/`, `cash_office/`).

---

## Folder Structure

```

bancassurance/
├── **init**.py                     # Marks folder as a Python package
├── app.py                          # Main Streamlit UI entry point
├── policy_sales.py                 # Selling new insurance policies
├── premium_collection.py           # Collect and manage premiums
├── claims_tracking.py              # Track and manage claims
├── reports.py                      # Generate sales and claims reports

├── common.py                       # Shared validators, formatters, and UI helpers
├── services/
│   ├── **init**.py
│   ├── api_client.py               # Centralized backend API calls
│   └── permissions.py              # Role-based access & limits

````

---

## Module Details

### 1. `app.py`

- **Purpose**: Entry point for Bancassurance UI
- **Responsibilities**:
  - Handle officer login and session management
  - Render tabs for all bancassurance operations:
    - Policy sales
    - Premium collection
    - Claims tracking
    - Reporting
- **Example**:

```python
from policy_sales import render_policy_sales_ui
from premium_collection import render_premium_collection_ui
from claims_tracking import render_claims_tracking_ui
from reports import render_reports_ui

tab1, tab2, tab3, tab4 = st.tabs([
    "Policy Sales", "Premium Collection", "Claims Tracking", "Reports"
])

with tab1:
    render_policy_sales_ui()

with tab2:
    render_premium_collection_ui()

with tab3:
    render_claims_tracking_ui()

with tab4:
    render_reports_ui()
````

---

### 2. `policy_sales.py`

* **Purpose**: Sell new insurance policies to customers
* **Responsibilities**:

  * Collect customer details and policy type
  * Calculate premium schedules
  * Validate customer eligibility
  * Submit new policy to backend
* **Backend API Example**: `POST /bancassurance/policy-sale`

---

### 3. `premium_collection.py`

* **Purpose**: Collect and record premium payments
* **Responsibilities**:

  * Record payment transactions (cash, bank transfer, mobile)
  * Update policy status with collected premiums
  * Generate receipts for customers
* **Backend API Example**: `POST /bancassurance/premium-collection`

---

### 4. `claims_tracking.py`

* **Purpose**: Track customer insurance claims
* **Responsibilities**:

  * Record claims submissions
  * Monitor claim status (pending, approved, rejected)
  * Notify officer for follow-ups
* **Backend API Examples**:

  * `GET /bancassurance/claims-status`
  * `POST /bancassurance/claims-update`

---

### 5. `reports.py`

* **Purpose**: Generate operational and performance reports
* **Responsibilities**:

  * Track policy sales, premiums collected, and claims processed
  * Generate daily, weekly, monthly reports
  * Export reports in CSV/PDF formats
* **Backend API Example**: `GET /bancassurance/reports`

---

### 6. `common.py`

* **Purpose**: Shared utilities for all modules
* **Features**:

  * Validators: `validate_customer_id()`, `validate_policy_number()`, `validate_amount()`
  * Formatting: `format_currency()`, `format_date()`
  * UI Helpers: `show_receipt()`
  * Session Helper: `get_bancassurance_officer_info()`

---

### 7. `services/api_client.py`

* **Purpose**: Centralized API client for all bancassurance operations
* **Features**:

  * GET, POST, PUT, DELETE requests
  * Retry logic for network issues
  * Automatic inclusion of authentication headers
* **Usage Example**:

```python
from services.api_client import post_request

payload = {
    "officer_id": officer_id,
    "customer_id": customer_id,
    "policy_type": "Life",
    "premium_amount": 5000
}

response = post_request("/bancassurance/policy-sale", payload)
```

---

### 8. `services/permissions.py`

* **Purpose**: Role-based access control for bancassurance operations

* **Responsibilities**:

  * Enforce limits on policy issuance, premium collection, and claim approvals
  * Ensure only authorized officers can approve high-value claims
  * Maintain compliance with regulatory and internal policies

* **Example Functions**:

```python
can_sell_policy(officer_role)
can_collect_premium(officer_role, amount)
can_approve_claim(officer_role, claim_amount)
```

---

## Usage Guidelines

1. **Login**

   * Officers must log in via `app.py`
   * Session data is retrieved via `get_bancassurance_officer_info()`

2. **Role Enforcement**

   * All operations check permissions in `permissions.py`
   * High-value policies or claims require supervisor approval

3. **Receipts**

   * Use `common.show_receipt()` for all customer-facing receipts

4. **Error Handling**

   * All backend communication goes through `services/api_client.py`
   * Exceptions are captured and displayed in the UI

---

## Development Notes

* **Extensibility**: Supports addition of new products, advanced reporting, and digital policy issuance
* **Consistency**: Follows same modular structure as teller, customer_ops, and cash_office
* **Security & Audit**: Role-based access and full logging for regulatory compliance
* **Testing**: Mock backend APIs can be used during development and testing

---

## Author & Maintainers

* **Team**: Core Banking Development Team – Wekeza Bank DFS System
* **Module Owner**: Bancassurance Operations Lead
* **Last Updated**: 2026-01-03

```
---
```
