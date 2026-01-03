This is the comprehensive **End-to-End Documentation** for the Personal Banking Module of Wekeza Bank.

This document serves as the "User Manual" and "Technical Specification" combined. It bridges the gap between the code you wrote and the business value it delivers. You should save this file as **`docs/01_PERSONAL_BANKING_MODULE.md`** in your repository.

---

# Wekeza Bank: Personal Banking Module (Web Channel)

**Version:** 1.0.0
**Module Owner:** Emmanuel Odenyire Anyira
**Status:** Live (MVP)

## 1. Executive Overview

The Personal Banking Module is the flagship component of the Wekeza Digital Financial Services (DFS) platform. It allows individual retail customers to access banking services purely through a secure Web Interface, eliminating the need for physical branches or USSD codes.

The system is built on the **BIMS Model**:

* **Borrow:** Automated algorithmic lending.
* **Insure:** *[Scheduled for Phase 2]*
* **Move:** Internal transfers and loan repayments.
* **Save:** Digital wallet management and deposits.

---

## 2. System Architecture

The module runs on a **Three-Tier Architecture**, ensuring security and scalability.

1. **Frontend (The Channel):**
* **Customer Portal:** A React/Streamlit web app for self-service.
* **Banker Workbench:** An admin dashboard for staff to view profiles and override decisions.


2. **Backend (The Core):**
* **FastAPI Engine:** Handles authentication (JWT), transaction ledgers, and orchestrations.
* **Risk Brain:** A dedicated Python module for real-time credit scoring.


3. **Database (The Ledger):**
* **MySQL 8.0:** Stores ACID-compliant financial records.



---

## 3. End-to-End User Journeys

This section documents the specific workflows implemented in the code.

### 3.1 Onboarding & Security

**Objective:** Securely register a customer and assign a KYC Tier.

1. **Registration:**
* User visits Web Portal -> Clicks "Register".
* Inputs: `Full Name`, `ID Number`, `Phone`, `Email`, `Password`.
* **System Action:** Hashes password (Bcrypt), creates `User` record, sets `KYC_Tier = TIER_1`.


2. **Authentication:**
* User inputs Email + Password.
* **System Action:** Validates Hash -> Issues **JWT Token** (valid for 30 mins).
* *Note:* All subsequent requests must carry this Token in the Header.



### 3.2 The "Save" Journey (Wallets & Deposits)

**Objective:** Enable the customer to store value (Simulating account opening).

1. **View Balance:**
* User logs in -> Dashboard shows "Current Balance".
* *Technical:* API calls `GET /accounts/me` -> DB queries `accounts` table.


2. **Deposit Funds:**
* User clicks "Top Up" -> Enters Amount (e.g., KES 5,000).
* **System Action:**
* Creates a `Transaction` record (`type=DEPOSIT`).
* Updates `accounts.balance = balance + 5000`.


* *Result:* User sees updated balance immediately.



### 3.3 The "Borrow" Journey (Lending)

**Objective:** Provide instant credit based on data.

1. **Check Limit:**
* User clicks "Loans" tab.
* **System Action:** Calls `Risk Engine`.
* *Logic:* `Limit = Average_Deposit * 0.8`.
* *Display:* "You qualify for up to KES 15,000".


2. **Apply for Loan:**
* User selects Amount (KES 5,000) and Tenure (30 Days).
* User accepts terms (Interest: 5%).


3. **Risk Scoring (The "Brain"):**
* System calculates Score (0-1000).
* **Approval Rule:** If `Score > 600` AND `Active_Loans == 0` -> **APPROVE**.


4. **Disbursement:**
* **System Action:**
* Creates `Loan` record (`status=ACTIVE`).
* Creates `Transaction` (`type=DISBURSEMENT`).
* Updates Wallet: `Wallet Balance + 5,000`.


* *Result:* Money is instantly available in the user's "Save" wallet.



### 3.4 The "Move" Journey (Repayment)

**Objective:** Close the lending loop.

1. **Repayment:**
* User views "Active Loan" (Balance: KES 5,250).
* User enters Repayment Amount (e.g., KES 5,250).
* User clicks "Pay from Wallet".


2. **Validation:**
* System checks: `Wallet Balance >= Repayment Amount`.


3. **Processing:**
* **Debit Wallet:** `Balance - 5,250`.
* **Credit Loan:** `Loan Balance - 5,250`.
* **Closure:** If `Loan Balance == 0`, set `Loan Status = PAID`.



---

## 4. The Banker & Admin Experience

While customers self-serve, the internal bank staff needs visibility.

### 4.1 The Banker (Branch Ops)

* **Customer 360:** Can search any user by ID Number.
* **View Statement:** See the last 10 transactions (Deposits/Loans) to answer queries like "Why is my balance low?"
* **KYC Upgrade:** Can manually upgrade a customer from `TIER_1` to `TIER_2` (increasing their loan limit) after verifying physical documents.

### 4.2 The Admin (Risk Ops)

* **Portfolio Health:** View total "Portfolio at Risk" (PAR).
* **Audit Trail:** View every single credit decision made by the algorithm (`APPROVED` vs `REJECTED`) to detect model drift.
* **Override:** Ability to force-stop lending if a system error is detected.

---

## 5. Technical Reference

### 5.1 Database Schema (MySQL)

| Table | Description | Key Fields |
| --- | --- | --- |
| **Users** | Identity Data | `user_id`, `password_hash`, `kyc_tier` |
| **Accounts** | The Wallet Ledger | `account_id`, `user_id`, `balance` |
| **Loans** | Credit Products | `loan_id`, `principal`, `interest`, `status` |
| **Risk_Scores** | Decision Logs | `score_id`, `input_payload`, `model_version`, `decision` |
| **Transactions** | Audit Trail | `txn_id`, `amount`, `txn_type`, `reference` |

### 5.2 API Endpoints (FastAPI)

| Method | Endpoint | Function | Access |
| --- | --- | --- | --- |
| `POST` | `/token` | Login (Get JWT) | Public |
| `GET` | `/users/me` | Get Profile | **Secured** |
| `POST` | `/accounts/deposit` | Simulate Deposit | **Secured** |
| `POST` | `/loans/apply` | Apply for Loan | **Secured** |
| `GET` | `/loans/active` | Check Status | **Secured** |
| `POST` | `/loans/repay` | Repay Loan | **Secured** |

---

## 6. Implementation Status (Checklist)

* [x] **Web Channel:** Customer Portal (Streamlit) is live.
* [x] **Core Banking:** Ledger system is ACID compliant.
* [x] **Security:** JWT Authentication is enforced.
* [x] **Lending Cycle:** Apply -> Approve -> Repay is fully functional.
* [ ] **Insurance:** (Pending Phase 2).
* [ ] **Business Banking:** (Pending Phase 3).

---

### **How to Use This Documentation**

1. **For Recruiters:** Show them the "End-to-End User Journeys" to prove you understand Product and Operations, not just Code.
2. **For Technical Interviews:** Walk them through the "Database Schema" and "API Endpoints" to prove Engineering competence.
3. **For Implementation:** Use the "Implementation Status" as your project roadmap.
