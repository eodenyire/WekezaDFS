## **cash_office/README.md**

```markdown
# Cash Office Module – Wekeza Bank DFS System

This module handles all **cash operations** within a branch, including:

- Vault management
- Issuing and receiving cash from tellers
- ATM cash loading and offloading
- End-of-day (EOD) cash reconciliation
- Supervisor approval checks
- Cash limits enforcement

It is designed for **branch cash officers, supervisors, and tellers**.

---

## **Folder Structure**

```

cash_office/
├── **init**.py                   # Marks folder as a Python package
├── app.py                        # Main Streamlit UI entry point
├── vault_open_close.py            # Vault opening/closing and limits
├── teller_cash_issue.py           # Issuing cash to tellers
├── teller_cash_receive.py         # Receiving cash from tellers
├── atm_cash_loading.py            # Loading cash into ATMs
├── atm_cash_offloading.py         # Removing cash from ATMs
├── cash_reconciliation.py        # End-of-day reconciliation
├── common.py                      # Shared utilities (validation, receipts)
└── services/
├── **init**.py               # Marks services as a package
├── api_client.py             # Centralized backend API calls
└── permissions.py            # Role-based permissions and cash limits

````

---

## **Roles & Permissions**

| Role                  | Responsibilities                                                                 | Approval/Limit Rules                                      |
|-----------------------|-------------------------------------------------------------------------------|-----------------------------------------------------------|
| **Cash Officer**      | Manages vault, ATMs, and teller cash transactions                             | Can issue/receive cash up to defined limits              |
| **Teller**            | Receives cash from cash office, deposits/withdrawals to/from customers        | Cannot exceed individual teller cash limit               |
| **Supervisor**        | Approves large cash operations                                               | Required for operations above `SUPERVISOR_APPROVAL_THRESHOLD` |
| **Branch Manager**    | Oversees branch cash operations and reconciliation                            | Can view reports, authorize exceptions                   |

---

## **Module Features**

### 1. Vault Management (`vault_open_close.py`)
- Open/close vault
- Track current vault cash balance
- Enforce vault cash limit (`VAULT_LIMIT`)
- Supervisor approval for unusual transactions

### 2. Teller Cash Operations
#### a. Cash Issue (`teller_cash_issue.py`)
- Issue cash to tellers
- Validate teller ID and cash denominations
- Enforce teller cash limits
- Supervisor approval for large amounts
- Generates digital receipt

#### b. Cash Receive (`teller_cash_receive.py`)
- Receive cash from tellers
- Validate denominations and amounts
- Supervisor approval for large cash returns
- Generates digital receipt

### 3. ATM Cash Operations
#### a. ATM Loading (`atm_cash_loading.py`)
- Load cash into ATMs
- Validate denominations
- Enforce ATM cash limits
- Supervisor approval for large loads
- Generates digital receipt

#### b. ATM Offloading (`atm_cash_offloading.py`)
- Remove cash from ATMs back to vault
- Validate denominations and amounts
- Supervisor approval for large offloads
- Generates digital receipt

### 4. End-of-Day Reconciliation (`cash_reconciliation.py`)
- Compares **vault, teller, and ATM balances** with core banking ledger
- Highlights discrepancies
- Generates digital reconciliation receipt for audit

### 5. Common Utilities (`common.py`)
- `validate_amount(amount)` – Ensures positive cash amounts
- `validate_teller_id(teller_id)` – Checks teller ID format
- `show_cash_receipt(title, data_dict)` – Generates digital receipts
- `get_cash_officer_info(officer_id, branch_code)` – Retrieves officer details

### 6. Services (`services/`)
#### a. API Client (`api_client.py`)
- Centralized backend calls using GET and POST
- Handles connection errors, HTTP errors, and unexpected exceptions
- All UI modules call backend via this client

#### b. Permissions (`permissions.py`)
- Role-based cash limits and rules
- Functions:
  - `requires_supervisor_approval(officer_id, amount)`
  - `teller_limit_check(teller_id, amount)`
  - `vault_limit_check(current_balance, amount_to_add)`
  - `atm_limit_check(current_balance, amount_to_load)`

---

## **Integration**

- All UI modules are built using **Streamlit**
- Backend endpoints:
  - `/cash-office/vault/open`
  - `/cash-office/vault/close`
  - `/cash-office/teller-issue`
  - `/cash-office/teller-receive`
  - `/cash-office/atm-load`
  - `/cash-office/atm-offload`
  - `/cash-office/reconciliation`
- Services (`api_client.py`) centralizes HTTP calls for all modules
- Permissions enforce **role-based access and cash limits**

---

## **Usage**

1. Install dependencies:
```bash
pip install streamlit requests pandas
````

2. Set backend API URL:

```bash
export API_URL="http://127.0.0.1:8000"
```

3. Run the Cash Office UI:

```bash
streamlit run cash_office/app.py
```

4. Navigate tabs for:

* Vault management
* Teller cash issue/receive
* ATM cash loading/offloading
* EOD reconciliation

---

## **Notes**

* Supervisor approval triggers are **warnings** in the UI; integration with real **approval workflow** is required.
* Denominations must be entered in the format: `1000x50, 500x100`
* All transactions generate **digital receipts** for **audit and compliance**
* Backend must implement **transaction logging, validation, and reconciliation**

---

## **Contributing**

* Follow the folder structure and coding standards
* Use `common.py` and `services/api_client.py` for shared logic
* Update `permissions.py` for new limits or branch-specific rules

---

## **License**

* Wekeza Bank DFS System – Internal Production Module
* Not for public distribution

```
