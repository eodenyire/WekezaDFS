# Wekeza Bank Digital Financial Services (DFS) Platform

![Status](https://img.shields.io/badge/Status-Production%20Ready-success) ![Tech Stack](https://img.shields.io/badge/Stack-FastAPI%20%7C%20MySQL%20%7C%20Docker%20%7C%20Streamlit-blue) ![Domain](https://img.shields.io/badge/Domain-Fintech%20%26%20Bancassurance-orange) ![License](https://img.shields.io/badge/License-MIT-lightgrey)

## 🏦 Executive Summary

**Wekeza Bank DFS** is a cloud-native, end-to-end Universal Banking Platform designed to bridge the gap between traditional brick-and-mortar banking and modern digital ecosystems. 

Architected around the **BIMS Model (Borrow, Insure, Move, Save)**, the system enables seamless financial inclusion for both **Retail Customers (Personal Banking)** and **SME/Corporate Clients (Business Banking)**. Unlike standard loan apps, Wekeza incorporates a **Full Core Banking Logic**, including double-entry ledgers, dynamic risk scoring, branch teller operations, and bancassurance integration.

---

## 🏗️ System Architecture

The platform operates on a **Microservices-style Architecture**, fully containerized using Docker. It separates the "Core Engine" from the various "Channels" (Frontends), ensuring security and scalability.



| Component | Technology | Description | Port |
| :--- | :--- | :--- | :--- |
| **Core Engine (Backend)** | Python (FastAPI) | The central brain handling Auth, Ledgers, Risk Engine, and Transactions. | `8000` |
| **Database** | MySQL 8.0 | ACID-compliant relational database for Users, Accounts, Loans, and Policies. | `3306` |
| **Retail Channel** | Streamlit (Python) | **Personal Banking Portal** for individual customers (Juma). | `8502` |
| **Corporate Channel** | Streamlit (Python) | **Business Banking Portal** for SMEs and Directors. | `8504` |
| **Branch Channel** | Streamlit (Python) | **Teller Terminal** for physical cash deposits and agency banking. | `8503` |
| **Admin Channel** | Streamlit (Python) | **Risk Management Dashboard** for monitoring the loan book and system health. | `8501` |

---

## 🎯 The BIMS Model Implementation

The system implements the **BIMS** framework end-to-end across both Retail and Corporate segments.

### 1. 📉 Borrow (Lending & Credit)
* **Retail Risk Engine:** Real-time credit scoring based on *Wallet Behavior* and KYC Tier.
* **SME Risk Engine:** Turnover-based capacity assessment and *Sector Risk* analysis (Agriculture vs. Tech).
* **Lifecycle:** Application -> Real-time Scoring -> Automated Disbursement -> Repayment -> Closure.

### 2. 🛡️ Insure (Bancassurance)
* **Personal:** On-demand **Personal Accident Cover** (monthly subscription).
* **Business:**
    * **WIBA (Work Injury Benefits Act):** Automated premium calculation based on Payroll.
    * **Asset All Risk:** Coverage for stock and equipment based on declared value.

### 3. 💸 Move (Payments & Transfers)
* **P2P:** Internal transfers between personal accounts.
* **Bulk Payments:** Corporate module for processing **Payroll Batches** (CSV upload simulation).
* **Repayments:** Wallet-to-Loan settlement logic.

### 4. 💰 Save (Deposits & Ledgers)
* **Wallets:** Digital storage of value with immutable audit trails.
* **Branch Integration:** Physical cash deposits via the **Teller App** reflect instantly in digital wallets.
* **Statements:** On-demand transaction history.

---

## 🚀 Key Features

### 🔒 Security & Compliance
* **JWT Authentication:** Stateless, token-based security for all API endpoints.
* **Role-Based Access Control (RBAC):** Segregation of duties between Customers, Directors, Tellers, and Admins.
* **KYC Tiering:** Tier 1 (Low Limits) to Tier 3 (High Limits) validation logic.

### 🤖 Intelligent Logic
* **Maker-Checker Ready:** Logic for Corporate Bulk Transfers.
* **Audit Trails:** Every transaction (Deposit, Loan, Fee) is logged with a unique Reference Code (e.g., `BR-XA123`).

---

## 🛠️ Installation & Setup

The entire bank is Dockerized. You can run the full ecosystem with a single command.

### Prerequisites
* Docker & Docker Compose installed on your machine.

### Quick Start
1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/your-username/wekeza-dfs-platform.git](https://github.com/your-username/wekeza-dfs-platform.git)
    cd wekeza-dfs-platform
    ```

2.  **Launch the System:**
    ```bash
    docker-compose up --build
    ```
    *Wait approx. 30 seconds for the Database to initialize.*

3.  **Access the Platforms:**
    * **Retail App:** [http://localhost:8502](http://localhost:8502)
    * **Corporate App:** [http://localhost:8504](http://localhost:8504)
    * **Teller Terminal:** [http://localhost:8503](http://localhost:8503)
    * **Risk Admin:** [http://localhost:8501](http://localhost:8501)
    * **API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📖 User Manual (How to Demo)

### Scenario A: The Retail Customer ("Juma")
1.  Open **Retail App (8502)**.
2.  **Register** a new account.
3.  Go to **Borrow Tab**: Apply for KES 5,000. (See instant approval/rejection).
4.  Go to **Insure Tab**: Buy a Personal Accident Cover.
5.  Check **Save Tab**: View your statement.

### Scenario B: The Corporate Client ("Wekeza Hardware Ltd")
1.  *Pre-requisite:* Register a business via API (Swagger) or use the provided script.
2.  Open **Corporate App (8504)** and Login.
3.  **SME Finance:** Apply for Working Capital based on turnover.
4.  **Insure:** Get a Quote for WIBA (Payroll Insurance) and Pay.
5.  **Move:** Upload a "Payroll Batch".

### Scenario C: The Branch Teller
1.  Open **Teller Terminal (8503)**.
2.  Enter Juma's **National ID**.
3.  Deposit **KES 50,000** Cash.
4.  *Verification:* Refresh Juma's Retail App to see the balance update instantly.

### Scenario D: The Risk Manager
1.  Open **Admin Dashboard (8501)**.
2.  View **Global Overview**: Total Loan Book & NPLs.
3.  Switch to **Corporate View**: See the list of registered SMEs and Insurance policies sold.

---

## 📂 Project Structure

```text
wekeza-dfs-platform/
├── docker-compose.yml              # Master Orchestrator
├── README.md                       # Documentation
├── 03_Source_Code/
│   ├── backend_api/                # The Core Engine (FastAPI)
│   │   ├── app/
│   │   │   ├── main.py             # API Routes (BIMS Logic)
│   │   │   ├── models.py           # Database Schema (SQLAlchemy)
│   │   │   ├── risk_engine.py      # Credit Scoring Models (Retail & SME)
│   │   │   └── ...
│   ├── web_portal_customer/        # Retail Frontend
│   ├── web_portal_business/        # Corporate Frontend
│   ├── web_portal_admin/           # Risk Dashboard
│   └── branch_teller/              # Branch Ops Frontend