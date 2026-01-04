```markdown
# Wekeza Bank DFS System – Branch Management Module

## Overview
The **branch_management** module provides end-to-end functionality for branch operations, allowing **branch managers** to monitor and manage **cash positions, branch performance, staff, reports, end-of-day approvals, and overrides**.  
It integrates with other branch modules such as **teller operations, supervision, cash office, and customer operations**.

---

## Folder Structure

```

branch_management/
├── **init**.py                    # Marks the folder as a Python package
├── app.py                         # Main entry point (Streamlit dashboard)
├── branch_cash_position.py        # View total branch cash (vaults, ATMs, tellers)
├── branch_performance.py          # Track branch KPIs, transactions, teller performance
├── branch_reporting.py            # Generate branch reports (daily/weekly/monthly)
├── staff_management.py            # Add, update, monitor branch staff
├── end_of_day_approval.py         # Approve branch end-of-day balances & reconciliation
├── overrides.py                   # Manager-level overrides for approvals or exceptions
├── branch_overview.py             # Consolidated dashboard aggregating all branch modules
├── common.py                      # Shared utilities (formatting, validation, session helpers)
├── services/
│   ├── **init**.py                # Marks services as a package
│   ├── api_client.py              # Centralized backend API calls (GET, POST, PUT, DELETE)
│   └── permissions.py             # Role-based access control & branch-level authorization

````

---

## Module Features

### 1. Branch Overview (`branch_overview.py`)
- Centralized dashboard aggregating all branch operations
- Tabs include:
  - **Cash Position** – Vault, ATMs, tellers
  - **Branch Performance** – KPIs, teller stats, transaction trends
  - **Reports** – Download daily, weekly, monthly reports
  - **Staff Management** – View/add/update staff
  - **End-of-Day Approval** – Approve or reject EOD balances
  - **Manager Overrides** – Override exceptions or approvals

### 2. Branch Cash Position (`branch_cash_position.py`)
- View real-time cash positions across:
  - Vault
  - ATMs
  - Teller tills
- Integrated with **backend APIs** for live updates

### 3. Branch Performance (`branch_performance.py`)
- Track branch KPIs:
  - Transaction volumes (deposits, withdrawals)
  - Teller performance
  - Trend analysis over time
- Graphs and tables for visual insights

### 4. Branch Reporting (`branch_reporting.py`)
- Generate reports in:
  - Daily, weekly, monthly formats
- Export options: CSV, Excel, PDF
- Filter by **teller, transaction type, and branch**

### 5. Staff Management (`staff_management.py`)
- Add or update branch staff
- Assign roles (`Teller`, `LoanOfficer`, `CashOfficer`, etc.)
- Activate or deactivate staff
- Audit trail of all updates

### 6. End-of-Day Approval (`end_of_day_approval.py`)
- Review daily cash positions and reconciliation
- Approve or reject EOD balances
- Rejection requires reason for audit
- Integrated with **backend EOD APIs**

### 7. Overrides (`overrides.py`)
- Managers can override transactions or approvals
- Digital receipts generated for audit
- All actions logged with timestamp and manager ID

---

## Common Utilities (`common.py`)
- **Formatting Helpers**
  - `format_currency(amount)` – KES formatting
  - `format_date(date_str)` – ISO to YYYY-MM-DD
- **Validation Helpers**
  - `validate_staff_id(staff_id)`
  - `validate_transaction_id(txn_id)`
- **Session Helpers**
  - `get_branch_manager_info(manager_id, branch_code)` – retrieves manager info
- **UI Helpers**
  - `show_override_receipt(title, data)` – displays digital receipt

---

## Services (`services/`)
### 1. API Client (`api_client.py`)
- Centralized backend requests
- Functions:
  - `get_request(url, params=None, headers=None)`
  - `post_request(url, payload, headers=None)`
  - `put_request(url, payload, headers=None)`
  - `delete_request(url, params=None, headers=None)`
- Features:
  - Timeout support
  - Error handling and logging

### 2. Permissions (`permissions.py`)
- Role-based access control
- Branch-level authorization
- Utilities:
  - `has_permission(role, action)` – check action permission
  - `check_branch_access(user_branch, target_branch)` – ensure branch access
  - `require_permission(role, action, user_branch, target_branch)` – enforce permission

---

## Usage Guidelines

1. **Starting the Branch Dashboard**
```bash
streamlit run branch_management/branch_overview.py
````

2. **Environment Variables**

* `API_URL` – Base URL for backend core banking APIs (default: `http://127.0.0.1:8000`)

3. **Manager Login**

* Provide `Manager ID` and `Branch Code` in sidebar

4. **Performing Actions**

* Only actions permitted by role are available
* Unauthorized actions trigger a **permission error**

5. **Extending Module**

* Add new modules by creating a `render_<feature>_ui(manager, api_url)` function
* Add new roles/actions in `permissions.py`
* Use `common.py` helpers for formatting, validation, and UI consistency

---

## Backend API Endpoints (Example)

| Endpoint                | Method   | Purpose                                  |
| ----------------------- | -------- | ---------------------------------------- |
| `/branch/cash-position` | GET      | Fetch vault, ATM, teller cash totals     |
| `/branch/performance`   | GET      | Fetch KPIs and branch metrics            |
| `/branch/reports`       | GET/POST | Fetch or generate reports                |
| `/branch/staff`         | GET/POST | Fetch/add/update staff                   |
| `/branch/eod-summary`   | GET      | Fetch end-of-day summary                 |
| `/branch/eod-approval`  | POST     | Submit EOD approval/rejection            |
| `/branch/overrides`     | POST     | Perform manager override on transactions |

---

## Workflows

1. **Branch Cash & Teller Monitoring**

   * Tellers perform cash operations
   * Cash Office updates vault/ATM balances
   * Branch Overview displays totals

2. **Staff Management Workflow**

   * Branch manager adds new staff
   * Role and branch assignment validated by `permissions.py`
   * Staff performs operations based on role

3. **End-of-Day Approval Workflow**

   * Cash, deposits, withdrawals reconciled
   * Manager reviews summary
   * Approves or rejects EOD
   * Logs stored for audit

4. **Manager Overrides**

   * Overrides logged with reason, timestamp, and manager ID
   * Receipts generated via `show_override_receipt()`

---

## Dependencies

* Python 3.10+
* Streamlit
* Requests
* Pandas
* Logging (Python standard library)

---

## Notes

* All modules are **modular** and **reusable**.
* Backend API integration is centralized via `services/api_client.py`.
* Role-based security is enforced via `services/permissions.py`.
* Formatting and shared utilities in `common.py` ensure **UI consistency**.
* This module is designed for **branch managers** and integrates seamlessly with **teller operations, supervision, cash office, and customer operations**.
---

```


