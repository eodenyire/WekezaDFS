-- ---------------------------------------------------------
-- Wekeza Bank DFS - Database Schema v1.0
-- Database: MySQL
-- Author: Emmanuel Odenyire Anyira
-- ---------------------------------------------------------

-- 1. Create Database
CREATE DATABASE IF NOT EXISTS wekeza_dfs_db;
USE wekeza_dfs_db;

-- 2. Users Table (KYC & Authentication)
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone_number VARCHAR(15) UNIQUE NOT NULL,
    national_id VARCHAR(20) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    kyc_tier ENUM('TIER_1', 'TIER_2', 'TIER_3') DEFAULT 'TIER_1',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_phone (phone_number),
    INDEX idx_national_id (national_id)
);

-- 3. Accounts Table (The Wallet / Ledger)
-- Rule: One user can have one main wallet account for now.
CREATE TABLE IF NOT EXISTS accounts (
    account_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    account_number VARCHAR(20) UNIQUE NOT NULL,
    balance DECIMAL(15, 2) DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'KES',
    status ENUM('ACTIVE', 'FROZEN', 'DORMANT') DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE RESTRICT
);

-- 4. Risk Scores Table (The "Brain" Memory)
-- Stores the decision logic result BEFORE a loan is created.
CREATE TABLE IF NOT EXISTS risk_scores (
    score_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    credit_score INT NOT NULL, -- Scale 0 to 1000
    risk_tier ENUM('LOW', 'MEDIUM', 'HIGH') NOT NULL,
    model_version VARCHAR(50) NOT NULL, -- e.g., "v1.0_Logistic"
    input_payload JSON, -- Stores the raw data used for scoring (CRB status, M-Pesa avg)
    decision ENUM('APPROVED', 'REJECTED') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 5. Loans Table (The Product)
CREATE TABLE IF NOT EXISTS loans (
    loan_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    risk_score_id INT, -- Links back to the logic used to approve this
    principal_amount DECIMAL(15, 2) NOT NULL,
    interest_rate DECIMAL(5, 2) NOT NULL, -- e.g. 5.00 for 5%
    interest_amount DECIMAL(15, 2) NOT NULL,
    total_due_amount DECIMAL(15, 2) NOT NULL, -- Principal + Interest
    balance_remaining DECIMAL(15, 2) NOT NULL,
    disbursement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP NOT NULL,
    status ENUM('PENDING', 'ACTIVE', 'PAID', 'DEFAULTED', 'WRITTEN_OFF') DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (risk_score_id) REFERENCES risk_scores(score_id),
    INDEX idx_loan_status (status)
);

-- 6. Transactions Table (The Immutable Audit Trail)
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT NOT NULL,
    loan_id INT NULL, -- Nullable because some txns (deposits) aren't linked to loans
    txn_type ENUM('DEPOSIT', 'WITHDRAWAL', 'DISBURSEMENT', 'REPAYMENT', 'FEE') NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    reference_code VARCHAR(50) UNIQUE NOT NULL, -- e.g., M-Pesa Code
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id),
    FOREIGN KEY (loan_id) REFERENCES loans(loan_id),
    INDEX idx_txn_type (txn_type)
);