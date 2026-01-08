# Customer Operations Module (`customer_ops/`)

## Overview

The **Customer Operations module** is designed for **Relationship Officers (Operations)** in a branch to manage the **entire customer lifecycle**. This includes:

- Creating customer profiles (CIF)
- Opening and maintaining accounts
- Managing mandates / signatories
- Closing accounts
- Performing customer enquiries (KYC, balances, account info)

This module integrates with the **core banking backend** via REST APIs and follows **role-based permissions** and **maker–checker workflows** where required.

---

## Folder Structure

customer_ops/
├── init.py # Marks folder as a Python package
├── app.py # Main Streamlit UI entry point
├── cif_create.py # Customer Information File creation (KYC onboarding)
├── account_opening.py # Open new accounts for customers
├── account_maintenance.py # Update customer or account info
├── account_closure.py # Close accounts safely
├── mandate_management.py # Manage authorized signatories or mandates
├── enquiries.py # Check balances, KYC status, account details

├── common.py # Shared validators, formatters, and UI helpers
├── services/
│ ├── init.py
│ ├── api_client.py # Centralized API calls (GET, POST, PUT, DELETE, retries)
│ └── permissions.py # Role-based permissions & operation limits


---

## Module Details

### 1. `app.py`

- **Purpose**: Main entry point for the Streamlit UI
- **Responsibilities**:
  - Handle officer login/session management
  - Render tabs for each customer operation (CIF creation, account opening, maintenance, closure, mandates, enquiries)
- **Example**:

```python
from cif_create import render_cif_ui
from account_opening import render_account_opening_ui

tab1, tab2 = st.tabs(["CIF Creation", "Account Opening"])
with tab1:
    render_cif_ui()
with tab2:
    render_account_opening_ui()
	
	```

### 2. cif_create.py

Purpose: Create new Customer Information Files (CIF) for KYC compliance

Key Responsibilities:

Capture customer personal details (name, DOB, address)

Upload KYC documents (ID, utility bill)

Validate inputs before sending to backend

Support maker–checker workflow for high-risk or high-value customers

Backend API Example: POST /customer/cif-create

### 3. account_opening.py

Purpose: Open new accounts linked to a CIF

Key Responsibilities:

Choose account type (savings, current, etc.)

Assign account number and branch code

Validate account number and customer ID

Submit to backend

Backend API Example: POST /customer/account-open

### 4. account_maintenance.py

Purpose: Update customer or account information

Key Responsibilities:

Update contact info, address, email, phone number

Update account features, limits, linked services

Backend API Example: PUT /customer/account-maintenance

### 5. account_closure.py

Purpose: Close accounts safely

Key Responsibilities:

Ensure no pending transactions or loans

Generate closure confirmation receipt

Maintain audit logs

Backend API Example: POST /customer/account-close

### 6. mandate_management.py

Purpose: Manage authorized signatories or account mandates

Key Responsibilities:

Add/remove signatories

Manage single or joint account mandates

Apply approval workflow for changes exceeding limits

Backend API Example: POST /customer/mandate-update

### 7. enquiries.py

Purpose: Read-only access for officers to check account/customer information

Key Responsibilities:

Check KYC status

Retrieve account balances, mini-statements

Provide search by Customer ID or account number

Backend API Example: GET /customer/enquiry

### 8. common.py

Purpose: Shared utilities for all modules

Key Features:

Validators: validate_customer_id(), validate_account_number(), validate_amount()

Formatting: format_currency(), format_date()

UI Helpers: show_receipt() for displaying receipts

Session Helper: get_officer_info()

### 9. services/api_client.py

Purpose: Centralized backend API client

Responsibilities:

Handle GET, POST, PUT, DELETE requests

Include authentication headers automatically

Retry logic and error handling

Usage Example:

from services.api_client import post_request

payload = {"customer_id": customer_id, "account_no": account_no}
response = post_request("/customer/account-open", payload)

### 10. services/permissions.py

Purpose: Role-based access control

Responsibilities:

Enforce which officers can perform which operations

Check if supervisor/manager approval is required for certain operations

Centralized definition of operation limits

#### Example Functions:

can_perform_action(role="officer", action="account_opening")
requires_supervisor_approval(officer_id, operation_value)

#### Usage Guidelines

Login

Every officer must log in via app.py

Session data is accessed via get_logged_in_officer()

####  Role Enforcement

Use permissions.py in every module to check access

High-risk operations automatically trigger maker-checker workflow

Receipts & Formatting

Use common.show_receipt() to generate receipts

All amounts formatted using common.format_currency()

Error Handling

Use services/api_client.py for all backend communication

Exceptions are captured and shown in the Streamlit UI

Development Notes

Extensibility: Easy to add new operations (e.g., card issuance, mobile banking registration)

Consistency: Follows the same folder structure as teller/ and credit_ops/

Testing: Mock backend APIs can be used during development

Security: All API calls include JWT authentication; role-based access enforced

Author & Maintainers

Team: Core Banking Development Team – Wekeza Bank DFS System

Module Owner: Relationship Operations Lead

Last Updated: 2026-01-03

---

This **README.md** is **complete, detailed, and production-ready**. It will serve as **both a developer guide and reference** for the `customer_ops` module.  

---

