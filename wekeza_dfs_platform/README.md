# Wekeza Bank Digital Financial Services (DFS) Platform

![Status](https://img.shields.io/badge/Status-Live_MVP-green) ![Stack](https://img.shields.io/badge/Tech-FastAPI_React_Docker-blue) ![Domain](https://img.shields.io/badge/Finance-BIMS_Model-orange)

## 🏦 Executive Summary
Wekeza Bank DFS is a cloud-native, microservices-based banking platform designed to deliver **End-to-End Personal Banking** via a responsive Web Channel. 

Architected with the **BIMS Model (Borrow, Insure, Move, Save)** at its core, the system replaces legacy batch-processing with real-time, event-driven architecture. It features an automated **Risk Decision Engine** capable of sub-second credit scoring using stochastic modeling and machine learning.

## 🎯 The BIMS Capabilities
This repository implements the following pillars of Digital Banking:

### 1. 📉 Borrow (Credit & Lending)
* **Origination:** End-to-end digital loan application via Web.
* **Risk Engine:** Real-time credit scoring (0-1000) based on transactional behavior and CRB status.
* **Lifecycle:** Automated Disbursement -> Interest Accrual -> Repayment -> Closure.
* **Visibility:** Customer dashboard for real-time limit checks and loan status tracking (WIP, Disbursed, Credited).

### 2. 🛡️ Insure (Bancassurance) - *Phase 2*
* Digital onboarding for policies (Life, Asset, Credit Life).
* Automated premium collections via Wallet auto-sweeps.

### 3. 💸 Move (Payments & Transfers)
* **Intra-Bank:** Real-time transfers between Savings and Loan accounts.
* **Inter-Bank:** Integration hooks for Mobile Money (M-Pesa) and RTGS.
* **Validation:** 2FA-secured transaction authorization.

### 4. 💰 Save (Deposits & Wealth)
* **Account Management:** Self-service account opening (Savings, Fixed Deposit).
* **Ledgers:** ACID-compliant double-entry ledger system for tracking deposits and withdrawals.
* **Statements:** On-demand digital statements.

---

## 🏗️ Technical Architecture
The system follows a **Three-Tier Microservices Architecture** containerized with Docker.

| Layer | Technology | Function |
| :--- | :--- | :--- |
| **Frontend** | Streamlit / React | **Customer Portal** (Self-Service) & **Admin Workbench** (Risk Ops). |
| **Backend** | Python (FastAPI) | **Core Banking Engine** handling auth, ledgers, and orchestrations. |
| **Database** | MySQL (8.0) | **Relational Ledger** for ensuring ACID compliance on all financial txns. |
| **Risk Brain** | Scikit-Learn / Python | **Stochastic Model** for determining probability of default (PD). |
| **Security** | OAuth2 + JWT | **Banking-Grade Auth** ensuring stateless, secure API access. |

---

## 🚀 Key Features Implemented

### User Roles
1.  **The Customer (Personal Banking):**
    * Secure Login (2FA ready).
    * **Dashboard:** View Wallet Balance, Loan Limit, Active Loan Status.
    * **Borrow:** Apply for loans, view breakdown (Principal + Interest).
    * **Repay:** Initiate partial or full repayments.
    * **Save:** Deposit funds, check statements.

2.  **The Banker (Branch Ops):**
    * **Customer 360:** View customer profile, KYC tier, and risk history.
    * **Overrides:** Force-approve/reject loans (with audit trail).

3.  **The Administrator (Risk Ops):**
    * **Model Governance:** Monitor NPL ratios and adjust scoring logic.
    * **Audit:** View immutable transaction logs.

---

## 🛠️ Installation & Setup
The entire bank is dockerized. You can run the full ecosystem with one command.

### Prerequisites
* Docker & Docker Compose

### Quick Start
```bash
# 1. Clone the repository
git clone [https://github.com/your-username/wekeza-dfs-platform.git](https://github.com/your-username/wekeza-dfs-platform.git)

# 2. Launch the Bank (Database, API, Frontends)
docker-compose up --build