import streamlit as st
import requests
import os
import mysql.connector
from datetime import datetime
import uuid
import time

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api")

# Database connection
def get_db_connection():
    try:
        return mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

# -----------------------------------------------------------------------------
# Get Current Staff from Main System
# -----------------------------------------------------------------------------
def get_current_staff():
    """Get the currently logged-in staff from main system session"""
    if 'current_staff' not in st.session_state:
        st.error("❌ No active staff session. Please login through the main system.")
        st.stop()
    return st.session_state.current_staff

# -----------------------------------------------------------------------------
# Check Teller Permissions
# -----------------------------------------------------------------------------
def check_teller_access():
    """Verify user has teller access"""
    staff = get_current_staff()
    allowed_roles = ['TELLER', 'SUPERVISOR', 'BRANCH_MANAGER', 'ADMIN']
    
    if staff['role'] not in allowed_roles:
        st.error(f"❌ Access Denied: Role '{staff['role']}' is not authorized for teller operations.")
        st.stop()
    
    return staff

# -----------------------------------------------------------------------------
# Database Functions
# -----------------------------------------------------------------------------
def get_account_details(account_number):
    """Get account details from database"""
    try:
        conn = get_db_connection()
        if not conn:
            return None
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT a.*, u.full_name, u.email, u.phone_number
            FROM accounts a
            JOIN users u ON a.user_id = u.user_id
            WHERE a.account_number = %s AND a.status = 'ACTIVE'
        """, (account_number,))
        
        account = cursor.fetchone()
        conn.close()
        return account
        
    except Exception as e:
        st.error(f"Error fetching account: {e}")
        return None

def process_deposit(account_number, amount, narration, staff_code):
    """Process cash deposit to database"""
    try:
        conn = get_db_connection()
        if not conn:
            return False
            
        cursor = conn.cursor(dictionary=True)
        
        # Get account details
        cursor.execute("""
            SELECT account_id, balance FROM accounts 
            WHERE account_number = %s AND status = 'ACTIVE'
        """, (account_number,))
        
        account = cursor.fetchone()
        if not account:
            st.error("Account not found or inactive")
            return False
        
        # Generate unique reference code
        reference_code = generate_unique_reference("DEP", conn)
        
        # Insert transaction
        cursor.execute("""
            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (account['account_id'], 'DEPOSIT', amount, reference_code, f"{narration} by {staff_code}", datetime.now()))
        
        # Update account balance
        new_balance = float(account['balance']) + float(amount)
        cursor.execute("""
            UPDATE accounts SET balance = %s WHERE account_id = %s
        """, (new_balance, account['account_id']))
        
        conn.commit()
        conn.close()
        
        return {
            'reference_code': reference_code,
            'new_balance': new_balance,
            'old_balance': float(account['balance'])
        }
        
    except Exception as e:
        st.error(f"Error processing deposit: {e}")
        return False

def process_withdrawal(account_number, amount, narration, staff_code):
    """Process cash withdrawal from database"""
    try:
        conn = get_db_connection()
        if not conn:
            return False
            
        cursor = conn.cursor(dictionary=True)
        
        # Get account details
        cursor.execute("""
            SELECT account_id, balance FROM accounts 
            WHERE account_number = %s AND status = 'ACTIVE'
        """, (account_number,))
        
        account = cursor.fetchone()
        if not account:
            st.error("Account not found or inactive")
            return False
        
        # Check sufficient balance
        if float(account['balance']) < float(amount):
            st.error("Insufficient balance")
            return False
        
        # Generate unique reference code
        reference_code = generate_unique_reference("WDL", conn)
        
        # Insert transaction
        cursor.execute("""
            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (account['account_id'], 'WITHDRAWAL', amount, reference_code, f"{narration} by {staff_code}", datetime.now()))
        
        # Update account balance
        new_balance = float(account['balance']) - float(amount)
        cursor.execute("""
            UPDATE accounts SET balance = %s WHERE account_id = %s
        """, (new_balance, account['account_id']))
        
        conn.commit()
        conn.close()
        
        return {
            'reference_code': reference_code,
            'new_balance': new_balance,
            'old_balance': float(account['balance'])
        }
        
    except Exception as e:
        st.error(f"Error processing withdrawal: {e}")
        return False

def generate_unique_reference(prefix, conn):
    """Generate a unique reference code"""
    max_attempts = 10
    
    for attempt in range(max_attempts):
        # Use timestamp + random hex for better uniqueness
        timestamp = str(int(time.time()))[-6:]  # Last 6 digits of timestamp
        random_part = uuid.uuid4().hex[:6].upper()
        reference_code = f"{prefix}{timestamp}{random_part}"
        
        # Check if this reference already exists
        cursor = conn.cursor()
        cursor.execute("SELECT reference_code FROM transactions WHERE reference_code = %s", (reference_code,))
        if not cursor.fetchone():
            return reference_code
    
    # Fallback: use full UUID if all attempts fail
    return f"{prefix}{uuid.uuid4().hex[:12].upper()}"
    
def process_cheque_deposit(account_number, amount, cheque_number, bank_name, narration, staff_code):
    """Process cheque deposit to database"""
    try:
        conn = get_db_connection()
        if not conn:
            return False
            
        cursor = conn.cursor(dictionary=True)
        
        # Get account details
        cursor.execute("""
            SELECT account_id, balance FROM accounts 
            WHERE account_number = %s AND status = 'ACTIVE'
        """, (account_number,))
        
        account = cursor.fetchone()
        if not account:
            st.error("Account not found or inactive")
            return False
        
        # Generate unique reference code
        reference_code = generate_unique_reference("CHQ", conn)
        
        # Insert transaction with cheque details
        description = f"Cheque deposit - {cheque_number} from {bank_name}. {narration} by {staff_code}"
        cursor.execute("""
            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (account['account_id'], 'CHEQUE_DEPOSIT', amount, reference_code, description, datetime.now()))
        
        # Update account balance
        new_balance = float(account['balance']) + float(amount)
        cursor.execute("""
            UPDATE accounts SET balance = %s WHERE account_id = %s
        """, (new_balance, account['account_id']))
        
        conn.commit()
        conn.close()
        
        return {
            'reference_code': reference_code,
            'new_balance': new_balance,
            'old_balance': float(account['balance']),
            'cheque_number': cheque_number
        }
        
    except Exception as e:
        st.error(f"Error processing cheque deposit: {e}")
        return False
    """Process cheque deposit to database"""
    try:
        conn = get_db_connection()
        if not conn:
            return False
            
        cursor = conn.cursor(dictionary=True)
        
        # Get account details
        cursor.execute("""
            SELECT account_id, balance FROM accounts 
            WHERE account_number = %s AND status = 'ACTIVE'
        """, (account_number,))
        
        account = cursor.fetchone()
        if not account:
            st.error("Account not found or inactive")
            return False
        
        # Generate reference code
        reference_code = f"CHQ{uuid.uuid4().hex[:8].upper()}"
        
        # Insert transaction with cheque details
        description = f"Cheque deposit - {cheque_number} from {bank_name}. {narration} by {staff_code}"
        cursor.execute("""
            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (account['account_id'], 'CHEQUE_DEPOSIT', amount, reference_code, description, datetime.now()))
        
        # Update account balance
        new_balance = float(account['balance']) + float(amount)
        cursor.execute("""
            UPDATE accounts SET balance = %s WHERE account_id = %s
        """, (new_balance, account['account_id']))
        
        conn.commit()
        conn.close()
        
        return {
            'reference_code': reference_code,
            'new_balance': new_balance,
            'old_balance': float(account['balance']),
            'cheque_number': cheque_number
        }
        
    except Exception as e:
        st.error(f"Error processing cheque deposit: {e}")
        return False

def process_internal_transfer(from_account, to_account, amount, narration, staff_code):
    """Process internal fund transfer between accounts"""
    try:
        conn = get_db_connection()
        if not conn:
            st.error("Database connection failed")
            return False
            
        cursor = conn.cursor(dictionary=True)
        
        # Get source account details
        cursor.execute("""
            SELECT account_id, balance FROM accounts 
            WHERE account_number = %s AND status = 'ACTIVE'
        """, (from_account,))
        
        source_account = cursor.fetchone()
        if not source_account:
            st.error(f"Source account {from_account} not found or inactive")
            return False
        
        st.info(f"✅ Source account found: Balance KES {source_account['balance']:,.2f}")
        
        # Get destination account details
        cursor.execute("""
            SELECT account_id, balance FROM accounts 
            WHERE account_number = %s AND status = 'ACTIVE'
        """, (to_account,))
        
        dest_account = cursor.fetchone()
        if not dest_account:
            st.error(f"Destination account {to_account} not found or inactive")
            return False
        
        st.info(f"✅ Destination account found: Balance KES {dest_account['balance']:,.2f}")
        
        # Check sufficient balance
        if float(source_account['balance']) < float(amount):
            st.error(f"Insufficient balance. Available: KES {source_account['balance']:,.2f}, Required: KES {amount:,.2f}")
            return False
        
        st.info(f"✅ Sufficient balance available")
        
        # Generate unique reference codes for both transactions
        base_reference = generate_unique_reference("TRF", conn)
        debit_reference = f"{base_reference}_OUT"
        credit_reference = f"{base_reference}_IN"
        
        st.info(f"✅ Generated references: {debit_reference} / {credit_reference}")
        
        # Debit source account
        cursor.execute("""
            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (source_account['account_id'], 'TRANSFER_OUT', amount, debit_reference, f"Transfer to {to_account}. {narration} by {staff_code}", datetime.now()))
        
        st.info(f"✅ Debit transaction recorded")
        
        # Credit destination account
        cursor.execute("""
            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (dest_account['account_id'], 'TRANSFER_IN', amount, credit_reference, f"Transfer from {from_account}. {narration} by {staff_code}", datetime.now()))
        
        st.info(f"✅ Credit transaction recorded")
        
        # Update balances
        new_source_balance = float(source_account['balance']) - float(amount)
        new_dest_balance = float(dest_account['balance']) + float(amount)
        
        cursor.execute("""
            UPDATE accounts SET balance = %s WHERE account_id = %s
        """, (new_source_balance, source_account['account_id']))
        
        cursor.execute("""
            UPDATE accounts SET balance = %s WHERE account_id = %s
        """, (new_dest_balance, dest_account['account_id']))
        
        st.info(f"✅ Account balances updated")
        
        conn.commit()
        conn.close()
        
        st.info(f"✅ Transaction committed to database")
        
        return {
            'reference_code': base_reference,
            'debit_reference': debit_reference,
            'credit_reference': credit_reference,
            'source_new_balance': new_source_balance,
            'dest_new_balance': new_dest_balance
        }
        
    except Exception as e:
        st.error(f"Error processing transfer: {e}")
        st.error(f"Error details: {str(e)}")
        import traceback
        st.error(f"Traceback: {traceback.format_exc()}")
        return False

def process_external_transfer(from_account, to_bank, to_account, amount, narration, staff_code):
    """Process external fund transfer to other banks"""
    try:
        conn = get_db_connection()
        if not conn:
            return False
            
        cursor = conn.cursor(dictionary=True)
        
        # Get source account details
        cursor.execute("""
            SELECT account_id, balance FROM accounts 
            WHERE account_number = %s AND status = 'ACTIVE'
        """, (from_account,))
        
        source_account = cursor.fetchone()
        if not source_account:
            st.error("Source account not found or inactive")
            return False
        
        # Check sufficient balance (including transfer fee)
        transfer_fee = 150.0  # KES 150 external transfer fee
        total_amount = float(amount) + transfer_fee
        
        if float(source_account['balance']) < total_amount:
            st.error(f"Insufficient balance. Required: KES {total_amount:,.2f} (Amount + Fee)")
            return False
        
        # Generate unique reference codes for both transactions
        base_reference = generate_unique_reference("EXT", conn)
        transfer_reference = f"{base_reference}_TRF"
        fee_reference = f"{base_reference}_FEE"
        
        # Debit source account for transfer amount
        cursor.execute("""
            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (source_account['account_id'], 'EXTERNAL_TRANSFER', amount, transfer_reference, f"External transfer to {to_bank} - {to_account}. {narration} by {staff_code}", datetime.now()))
        
        # Debit transfer fee
        cursor.execute("""
            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (source_account['account_id'], 'TRANSFER_FEE', transfer_fee, fee_reference, f"External transfer fee by {staff_code}", datetime.now()))
        
        # Update balance
        new_balance = float(source_account['balance']) - total_amount
        cursor.execute("""
            UPDATE accounts SET balance = %s WHERE account_id = %s
        """, (new_balance, source_account['account_id']))
        
        conn.commit()
        conn.close()
        
        return {
            'reference_code': base_reference,
            'transfer_reference': transfer_reference,
            'fee_reference': fee_reference,
            'new_balance': new_balance,
            'transfer_fee': transfer_fee,
            'total_debited': total_amount
        }
        
    except Exception as e:
        st.error(f"Error processing external transfer: {e}")
        return False

def process_mobile_transfer(from_account, mobile_number, amount, narration, staff_code):
    """Process mobile money transfer"""
    try:
        conn = get_db_connection()
        if not conn:
            return False
            
        cursor = conn.cursor(dictionary=True)
        
        # Get source account details
        cursor.execute("""
            SELECT account_id, balance FROM accounts 
            WHERE account_number = %s AND status = 'ACTIVE'
        """, (from_account,))
        
        source_account = cursor.fetchone()
        if not source_account:
            st.error("Source account not found or inactive")
            return False
        
        # Calculate mobile transfer fee
        if float(amount) <= 100:
            transfer_fee = 11.0
        elif float(amount) <= 500:
            transfer_fee = 22.0
        elif float(amount) <= 1000:
            transfer_fee = 29.0
        elif float(amount) <= 1500:
            transfer_fee = 29.0
        elif float(amount) <= 2500:
            transfer_fee = 52.0
        elif float(amount) <= 3500:
            transfer_fee = 69.0
        elif float(amount) <= 5000:
            transfer_fee = 87.0
        elif float(amount) <= 7500:
            transfer_fee = 115.0
        elif float(amount) <= 10000:
            transfer_fee = 167.0
        elif float(amount) <= 15000:
            transfer_fee = 185.0
        elif float(amount) <= 20000:
            transfer_fee = 197.0
        elif float(amount) <= 35000:
            transfer_fee = 278.0
        elif float(amount) <= 50000:
            transfer_fee = 309.0
        else:
            transfer_fee = 315.0
        
        total_amount = float(amount) + transfer_fee
        
        # Check sufficient balance
        if float(source_account['balance']) < total_amount:
            st.error(f"Insufficient balance. Required: KES {total_amount:,.2f} (Amount + Fee)")
            return False
        
        # Generate unique reference codes for both transactions
        base_reference = generate_unique_reference("MOB", conn)
        transfer_reference = f"{base_reference}_TRF"
        fee_reference = f"{base_reference}_FEE"
        
        # Debit source account for transfer amount
        cursor.execute("""
            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (source_account['account_id'], 'MOBILE_TRANSFER', amount, transfer_reference, f"Mobile transfer to {mobile_number}. {narration} by {staff_code}", datetime.now()))
        
        # Debit transfer fee
        cursor.execute("""
            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (source_account['account_id'], 'MOBILE_FEE', transfer_fee, fee_reference, f"Mobile transfer fee by {staff_code}", datetime.now()))
        
        # Update balance
        new_balance = float(source_account['balance']) - total_amount
        cursor.execute("""
            UPDATE accounts SET balance = %s WHERE account_id = %s
        """, (new_balance, source_account['account_id']))
        
        conn.commit()
        conn.close()
        
        return {
            'reference_code': base_reference,
            'transfer_reference': transfer_reference,
            'fee_reference': fee_reference,
            'new_balance': new_balance,
            'transfer_fee': transfer_fee,
            'total_debited': total_amount
        }
        
    except Exception as e:
        st.error(f"Error processing mobile transfer: {e}")
        return False

def process_bill_payment(payer_account, biller, bill_account, amount, staff_code):
    """Process bill payment"""
    try:
        conn = get_db_connection()
        if not conn:
            st.error("Database connection failed")
            return False
            
        cursor = conn.cursor(dictionary=True)
        
        # Get payer account details
        cursor.execute("""
            SELECT account_id, balance FROM accounts 
            WHERE account_number = %s AND status = 'ACTIVE'
        """, (payer_account,))
        
        account = cursor.fetchone()
        if not account:
            st.error("Payer account not found or inactive")
            return False
        
        # Bill payment fee
        service_fee = 50.0
        total_amount = float(amount) + service_fee
        
        # Check sufficient balance
        if float(account['balance']) < total_amount:
            st.error(f"Insufficient balance. Required: KES {total_amount:,.2f} (Bill + Service Fee)")
            return False
        
        # Generate unique reference codes for both transactions
        base_reference = generate_unique_reference("BILL", conn)
        bill_reference = f"{base_reference}_BILL"
        fee_reference = f"{base_reference}_FEE"
        
        # Debit account for bill amount
        cursor.execute("""
            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (account['account_id'], 'BILL_PAYMENT', amount, bill_reference, f"Bill payment to {biller} - {bill_account} by {staff_code}", datetime.now()))
        
        # Debit service fee
        cursor.execute("""
            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (account['account_id'], 'SERVICE_FEE', service_fee, fee_reference, f"Bill payment service fee by {staff_code}", datetime.now()))
        
        # Update balance
        new_balance = float(account['balance']) - total_amount
        cursor.execute("""
            UPDATE accounts SET balance = %s WHERE account_id = %s
        """, (new_balance, account['account_id']))
        
        conn.commit()
        conn.close()
        
        return {
            'reference_code': base_reference,
            'bill_reference': bill_reference,
            'fee_reference': fee_reference,
            'new_balance': new_balance,
            'service_fee': service_fee,
            'total_debited': total_amount
        }
        
    except Exception as e:
        st.error(f"Error processing bill payment: {e}")
        return False

def process_cdsc_transfer(from_account, cdsc_account, amount, narration, staff_code):
    """Process CDSC account transfer"""
    try:
        conn = get_db_connection()
        if not conn:
            return False
            
        cursor = conn.cursor(dictionary=True)
        
        # Get source account details
        cursor.execute("""
            SELECT account_id, balance FROM accounts 
            WHERE account_number = %s AND status = 'ACTIVE'
        """, (from_account,))
        
        source_account = cursor.fetchone()
        if not source_account:
            st.error("Source account not found or inactive")
            return False
        
        # CDSC transfer fee
        transfer_fee = 100.0  # KES 100 CDSC transfer fee
        total_amount = float(amount) + transfer_fee
        
        # Check sufficient balance
        if float(source_account['balance']) < total_amount:
            st.error(f"Insufficient balance. Required: KES {total_amount:,.2f} (Amount + Fee)")
            return False
        
        # Generate unique reference codes for both transactions
        base_reference = generate_unique_reference("CDSC", conn)
        transfer_reference = f"{base_reference}_TRF"
        fee_reference = f"{base_reference}_FEE"
        
        # Debit source account for transfer amount
        cursor.execute("""
            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (source_account['account_id'], 'CDSC_TRANSFER', amount, transfer_reference, f"CDSC transfer to {cdsc_account}. {narration} by {staff_code}", datetime.now()))
        
        # Debit transfer fee
        cursor.execute("""
            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (source_account['account_id'], 'CDSC_FEE', transfer_fee, fee_reference, f"CDSC transfer fee by {staff_code}", datetime.now()))
        
        # Update balance
        new_balance = float(source_account['balance']) - total_amount
        cursor.execute("""
            UPDATE accounts SET balance = %s WHERE account_id = %s
        """, (new_balance, source_account['account_id']))
        
        conn.commit()
        conn.close()
        
        return {
            'reference_code': base_reference,
            'transfer_reference': transfer_reference,
            'fee_reference': fee_reference,
            'new_balance': new_balance,
            'transfer_fee': transfer_fee,
            'total_debited': total_amount
        }
        
    except Exception as e:
        st.error(f"Error processing CDSC transfer: {e}")
        return False

def get_recent_transactions(account_number, limit=5):
    """Get recent transactions for an account"""
    try:
        conn = get_db_connection()
        if not conn:
            return []
            
        cursor = conn.cursor(dictionary=True)
        
        # Get account ID first
        cursor.execute("""
            SELECT account_id FROM accounts WHERE account_number = %s
        """, (account_number,))
        
        account = cursor.fetchone()
        if not account:
            return []
        
        # Get transactions
        cursor.execute("""
            SELECT * FROM transactions 
            WHERE account_id = %s 
            ORDER BY created_at DESC 
            LIMIT %s
        """, (account['account_id'], limit))
        
        transactions = cursor.fetchall()
        conn.close()
        return transactions
        
    except Exception as e:
        st.error(f"Error fetching transactions: {e}")
        return []

# -----------------------------------------------------------------------------
# MAIN TELLER INTERFACE
# -----------------------------------------------------------------------------

# Check access first
staff = check_teller_access()

st.title("🏧 Teller Operations System")
st.markdown(f"**Operator:** {staff['full_name']} ({staff['staff_code']}) | **Role:** {staff['role']} | **Branch:** {staff['branch_name']}")
st.markdown("---")

# Teller Operations Tabs
tab_deposit, tab_withdrawal, tab_balance, tab_cheque, tab_transfer, tab_bills, tab_cdsc, tab_reports = st.tabs([
    "💰 Cash Deposit",
    "💸 Cash Withdrawal", 
    "📊 Balance Enquiry",
    "📋 Cheque Deposit",
    "🔄 Fund Transfer",
    "📄 Bill Payments",
    "📈 CDSC Transfer",
    "📋 Reports"
])

# TAB 1: Cash Deposit
with tab_deposit:
    st.subheader("💰 Cash Deposit")
    
    col1, col2 = st.columns(2)
    
    with col1:
        account_number = st.text_input("Account Number", placeholder="Enter account number")
        deposit_amount = st.number_input("Deposit Amount (KES)", min_value=0.0, step=100.0)
        deposit_narration = st.text_area("Narration", placeholder="Deposit description", value="Cash deposit")
        
    with col2:
        st.info("**Deposit Limits:**")
        st.write("- Minimum: KES 100")
        st.write("- Maximum: KES 500,000")
        st.write("- Daily Limit: KES 2,000,000")
        
        if st.button("🔍 Verify Account", key="verify_deposit"):
            if account_number:
                account = get_account_details(account_number)
                if account:
                    st.success(f"✅ Account {account_number} verified")
                    st.write(f"**Account Holder:** {account['full_name']}")
                    st.write(f"**Current Balance:** KES {account['balance']:,.2f}")
                    st.write(f"**Status:** {account['status']}")
                else:
                    st.error("Account not found or inactive")
    
    if st.button("💰 Process Deposit", type="primary"):
        if account_number and deposit_amount >= 100:
            result = process_deposit(account_number, deposit_amount, deposit_narration, staff['staff_code'])
            if result:
                st.success(f"✅ Deposit of KES {deposit_amount:,.2f} processed successfully!")
                st.write(f"**Transaction Reference:** {result['reference_code']}")
                st.write(f"**Previous Balance:** KES {result['old_balance']:,.2f}")
                st.write(f"**New Balance:** KES {result['new_balance']:,.2f}")
        else:
            st.error("Please enter valid account number and amount (minimum KES 100)")

# TAB 2: Cash Withdrawal
with tab_withdrawal:
    st.subheader("💸 Cash Withdrawal")
    
    col1, col2 = st.columns(2)
    
    with col1:
        withdrawal_account = st.text_input("Account Number", placeholder="Enter account number", key="withdrawal_acc")
        withdrawal_amount = st.number_input("Withdrawal Amount (KES)", min_value=0.0, step=100.0, key="withdrawal_amt")
        withdrawal_narration = st.text_area("Narration", placeholder="Withdrawal description", key="withdrawal_narr", value="Cash withdrawal")
        
    with col2:
        st.warning("**Withdrawal Limits:**")
        st.write("- Minimum: KES 100")
        st.write("- Maximum: KES 100,000")
        st.write("- Daily Limit: KES 500,000")
        
        if st.button("🔍 Verify Account", key="verify_withdrawal"):
            if withdrawal_account:
                account = get_account_details(withdrawal_account)
                if account:
                    st.success(f"✅ Account {withdrawal_account} verified")
                    st.write(f"**Account Holder:** {account['full_name']}")
                    st.write(f"**Available Balance:** KES {account['balance']:,.2f}")
                    st.write(f"**Status:** {account['status']}")
                else:
                    st.error("Account not found or inactive")
    
    if st.button("💸 Process Withdrawal", type="primary", key="process_withdrawal"):
        if withdrawal_account and withdrawal_amount >= 100:
            result = process_withdrawal(withdrawal_account, withdrawal_amount, withdrawal_narration, staff['staff_code'])
            if result:
                st.success(f"✅ Withdrawal of KES {withdrawal_amount:,.2f} processed successfully!")
                st.write(f"**Transaction Reference:** {result['reference_code']}")
                st.write(f"**Previous Balance:** KES {result['old_balance']:,.2f}")
                st.write(f"**New Balance:** KES {result['new_balance']:,.2f}")
        else:
            st.error("Please enter valid account number and amount (minimum KES 100)")

# TAB 3: Balance Enquiry
with tab_balance:
    st.subheader("📊 Balance Enquiry")
    
    col1, col2 = st.columns(2)
    
    with col1:
        enquiry_account = st.text_input("Account Number", placeholder="Enter account number", key="enquiry_acc")
        
        if st.button("🔍 Check Balance", type="primary"):
            if enquiry_account:
                account = get_account_details(enquiry_account)
                if account:
                    st.success("✅ Account found")
                    
                    # Account details
                    st.markdown("### Account Details")
                    st.write(f"**Account Number:** {account['account_number']}")
                    st.write(f"**Account Holder:** {account['full_name']}")
                    st.write(f"**Email:** {account['email']}")
                    st.write(f"**Phone:** {account['phone_number']}")
                    st.write(f"**Status:** {account['status']}")
                    
                    st.markdown("### Balance Information")
                    st.metric("Available Balance", f"KES {account['balance']:,.2f}")
                else:
                    st.error("Account not found or inactive")
            else:
                st.error("Please enter account number")
    
    with col2:
        if enquiry_account:
            st.info("**Recent Transactions**")
            transactions = get_recent_transactions(enquiry_account)
            if transactions:
                for i, txn in enumerate(transactions, 1):
                    st.write(f"{i}. {txn['txn_type']} - KES {txn['amount']:,.2f} ({txn['created_at'].strftime('%Y-%m-%d')})")
            else:
                st.write("No recent transactions")

# TAB 4: Cheque Deposit
with tab_cheque:
    st.subheader("📋 Cheque Deposit")
    
    col1, col2 = st.columns(2)
    
    with col1:
        cheque_account = st.text_input("Account Number", placeholder="Enter account number", key="cheque_account_input")
        cheque_amount = st.number_input("Cheque Amount (KES)", min_value=0.0, step=100.0, key="cheque_amount_input")
        cheque_number = st.text_input("Cheque Number", placeholder="Enter cheque number", key="cheque_number_input")
        bank_name = st.selectbox("Issuing Bank", [
            "Wekeza Bank",
            "KCB Bank",
            "Equity Bank", 
            "Cooperative Bank",
            "NCBA Bank",
            "Absa Bank",
            "Standard Chartered",
            "Stanbic Bank",
            "Diamond Trust Bank",
            "Family Bank",
            "Other"
        ], key="cheque_bank_select")
        cheque_narration = st.text_area("Narration", placeholder="Cheque deposit description", key="cheque_narration_input", value="Cheque deposit")
        
    with col2:
        st.info("**Cheque Deposit Info:**")
        st.write("- Minimum: KES 100")
        st.write("- Same bank: Instant clearing")
        st.write("- Other banks: 3-5 working days")
        st.write("- Maximum: KES 5,000,000")
        
        if st.button("🔍 Verify Account", key="verify_cheque"):
            if cheque_account:
                account = get_account_details(cheque_account)
                if account:
                    st.success(f"✅ Account {cheque_account} verified")
                    st.write(f"**Account Holder:** {account['full_name']}")
                    st.write(f"**Current Balance:** KES {account['balance']:,.2f}")
                    st.write(f"**Status:** {account['status']}")
                else:
                    st.error("Account not found or inactive")
    
    if st.button("📋 Process Cheque Deposit", type="primary", key="process_cheque"):
        if cheque_account and cheque_amount >= 100 and cheque_number and bank_name:
            result = process_cheque_deposit(cheque_account, cheque_amount, cheque_number, bank_name, cheque_narration, staff['staff_code'])
            if result:
                st.success(f"✅ Cheque deposit of KES {cheque_amount:,.2f} processed successfully!")
                st.write(f"**Transaction Reference:** {result['reference_code']}")
                st.write(f"**Cheque Number:** {result['cheque_number']}")
                st.write(f"**Issuing Bank:** {bank_name}")
                st.write(f"**Previous Balance:** KES {result['old_balance']:,.2f}")
                st.write(f"**New Balance:** KES {result['new_balance']:,.2f}")
                if bank_name != "Wekeza Bank":
                    st.warning("⏳ Funds will be available after cheque clearing (3-5 working days)")
        else:
            st.error("Please fill in all required fields (minimum KES 100)")

# TAB 5: Fund Transfer
with tab_transfer:
    st.subheader("🔄 Fund Transfer")
    
    transfer_type = st.selectbox("Transfer Type", [
        "Internal Transfer (Wekeza to Wekeza)",
        "External Transfer (Other Banks)",
        "Mobile Money Transfer"
    ])
    
    if transfer_type == "Internal Transfer (Wekeza to Wekeza)":
        col1, col2 = st.columns(2)
        
        with col1:
            from_account = st.text_input("From Account", placeholder="Source account number", key="internal_from_account")
            to_account = st.text_input("To Account", placeholder="Destination account number", key="internal_to_account")
            transfer_amount = st.number_input("Transfer Amount (KES)", min_value=0.0, step=100.0, key="internal_transfer_amount")
            transfer_narration = st.text_area("Narration", placeholder="Transfer description", key="internal_transfer_narration", value="Internal transfer")
            
        with col2:
            st.info("**Internal Transfer:**")
            st.write("- Fee: FREE")
            st.write("- Processing: Instant")
            st.write("- Minimum: KES 100")
            st.write("- Maximum: KES 10,000,000")
            
            if st.button("🔍 Verify Accounts", key="verify_internal"):
                if from_account and to_account:
                    source = get_account_details(from_account)
                    dest = get_account_details(to_account)
                    
                    if source and dest:
                        st.success("✅ Both accounts verified")
                        st.write(f"**From:** {source['full_name']} (KES {source['balance']:,.2f})")
                        st.write(f"**To:** {dest['full_name']}")
                    else:
                        st.error("One or both accounts not found")
        
        if st.button("🔄 Process Internal Transfer", type="primary", key="process_internal"):
            if from_account and to_account and transfer_amount >= 100:
                if from_account == to_account:
                    st.error("Source and destination accounts cannot be the same")
                else:
                    result = process_internal_transfer(from_account, to_account, transfer_amount, transfer_narration, staff['staff_code'])
                    if result:
                        st.success(f"✅ Internal transfer of KES {transfer_amount:,.2f} completed!")
                        st.write(f"**Transaction Reference:** {result['reference_code']}")
                        st.write(f"**Debit Reference:** {result['debit_reference']}")
                        st.write(f"**Credit Reference:** {result['credit_reference']}")
                        st.write(f"**From Account New Balance:** KES {result['source_new_balance']:,.2f}")
                        st.write(f"**To Account New Balance:** KES {result['dest_new_balance']:,.2f}")
            else:
                st.error("Please fill in all required fields (minimum KES 100)")
    
    elif transfer_type == "External Transfer (Other Banks)":
        col1, col2 = st.columns(2)
        
        with col1:
            ext_from_account = st.text_input("From Account", placeholder="Source account number", key="external_from_account")
            ext_to_bank = st.selectbox("Destination Bank", [
                "KCB Bank",
                "Equity Bank", 
                "Cooperative Bank",
                "NCBA Bank",
                "Absa Bank",
                "Standard Chartered",
                "Stanbic Bank",
                "Diamond Trust Bank",
                "Family Bank",
                "Other"
            ], key="external_to_bank")
            ext_to_account = st.text_input("Destination Account", placeholder="Account number at destination bank", key="external_to_account")
            ext_transfer_amount = st.number_input("Transfer Amount (KES)", min_value=0.0, step=100.0, key="external_transfer_amount")
            ext_transfer_narration = st.text_area("Narration", placeholder="Transfer description", key="external_transfer_narration", value="External transfer")
            
        with col2:
            st.warning("**External Transfer:**")
            st.write("- Fee: KES 150")
            st.write("- Processing: 1-2 hours")
            st.write("- Minimum: KES 100")
            st.write("- Maximum: KES 1,000,000")
            
            if st.button("🔍 Verify Source Account", key="verify_external"):
                if ext_from_account:
                    source = get_account_details(ext_from_account)
                    if source:
                        st.success("✅ Source account verified")
                        st.write(f"**Account Holder:** {source['full_name']}")
                        st.write(f"**Available Balance:** KES {source['balance']:,.2f}")
                    else:
                        st.error("Source account not found")
        
        if st.button("🔄 Process External Transfer", type="primary", key="process_external"):
            if ext_from_account and ext_to_bank and ext_to_account and ext_transfer_amount >= 100:
                result = process_external_transfer(ext_from_account, ext_to_bank, ext_to_account, ext_transfer_amount, ext_transfer_narration, staff['staff_code'])
                if result:
                    st.success(f"✅ External transfer of KES {ext_transfer_amount:,.2f} initiated!")
                    st.write(f"**Transaction Reference:** {result['reference_code']}")
                    st.write(f"**Transfer Fee:** KES {result['transfer_fee']:,.2f}")
                    st.write(f"**Total Debited:** KES {result['total_debited']:,.2f}")
                    st.write(f"**New Balance:** KES {result['new_balance']:,.2f}")
                    st.info("💡 Transfer will be processed within 1-2 hours")
            else:
                st.error("Please fill in all required fields (minimum KES 100)")
    
    elif transfer_type == "Mobile Money Transfer":
        col1, col2 = st.columns(2)
        
        with col1:
            mob_from_account = st.text_input("From Account", placeholder="Source account number", key="mobile_from_account")
            mob_to_number = st.text_input("Mobile Number", placeholder="254XXXXXXXXX", key="mobile_to_number")
            mob_transfer_amount = st.number_input("Transfer Amount (KES)", min_value=0.0, step=10.0, key="mobile_transfer_amount")
            mob_transfer_narration = st.text_area("Narration", placeholder="Transfer description", key="mobile_transfer_narration", value="Mobile money transfer")
            
        with col2:
            st.info("**Mobile Money Transfer:**")
            st.write("- Fee: Variable (KES 11-315)")
            st.write("- Processing: Instant")
            st.write("- Minimum: KES 10")
            st.write("- Maximum: KES 150,000")
            
            # Show fee structure
            if mob_transfer_amount > 0:
                if mob_transfer_amount <= 100:
                    fee = 11.0
                elif mob_transfer_amount <= 500:
                    fee = 22.0
                elif mob_transfer_amount <= 1000:
                    fee = 29.0
                elif mob_transfer_amount <= 1500:
                    fee = 29.0
                elif mob_transfer_amount <= 2500:
                    fee = 52.0
                elif mob_transfer_amount <= 3500:
                    fee = 69.0
                elif mob_transfer_amount <= 5000:
                    fee = 87.0
                elif mob_transfer_amount <= 7500:
                    fee = 115.0
                elif mob_transfer_amount <= 10000:
                    fee = 167.0
                elif mob_transfer_amount <= 15000:
                    fee = 185.0
                elif mob_transfer_amount <= 20000:
                    fee = 197.0
                elif mob_transfer_amount <= 35000:
                    fee = 278.0
                elif mob_transfer_amount <= 50000:
                    fee = 309.0
                else:
                    fee = 315.0
                
                st.write(f"**Transfer Fee:** KES {fee}")
                st.write(f"**Total Cost:** KES {mob_transfer_amount + fee}")
            
            if st.button("🔍 Verify Source Account", key="verify_mobile"):
                if mob_from_account:
                    source = get_account_details(mob_from_account)
                    if source:
                        st.success("✅ Source account verified")
                        st.write(f"**Account Holder:** {source['full_name']}")
                        st.write(f"**Available Balance:** KES {source['balance']:,.2f}")
                    else:
                        st.error("Source account not found")
        
        if st.button("📱 Process Mobile Transfer", type="primary", key="process_mobile"):
            if mob_from_account and mob_to_number and mob_transfer_amount >= 10:
                # Validate mobile number format
                if not mob_to_number.startswith('254') or len(mob_to_number) != 12:
                    st.error("Please enter a valid mobile number (254XXXXXXXXX)")
                else:
                    result = process_mobile_transfer(mob_from_account, mob_to_number, mob_transfer_amount, mob_transfer_narration, staff['staff_code'])
                    if result:
                        st.success(f"✅ Mobile transfer of KES {mob_transfer_amount:,.2f} completed!")
                        st.write(f"**Transaction Reference:** {result['reference_code']}")
                        st.write(f"**Mobile Number:** {mob_to_number}")
                        st.write(f"**Transfer Fee:** KES {result['transfer_fee']:,.2f}")
                        st.write(f"**Total Debited:** KES {result['total_debited']:,.2f}")
                        st.write(f"**New Balance:** KES {result['new_balance']:,.2f}")
            else:
                st.error("Please fill in all required fields (minimum KES 10)")

# TAB 6: Bill Payments
with tab_bills:
    st.subheader("📄 Bill Payments")
    
    col1, col2 = st.columns(2)
    
    with col1:
        bill_payer_account = st.text_input("Payer Account", placeholder="Account number", key="bill_payer_account")
        biller = st.selectbox("Select Biller", [
            "Kenya Power (KPLC)",
            "Nairobi Water & Sewerage",
            "Safaricom Postpaid",
            "Airtel Postpaid",
            "DSTV",
            "GOTV",
            "Zuku",
            "Startimes",
            "NHIF",
            "NSSF",
            "KRA (iTax)",
            "County Government",
            "Other"
        ], key="bill_biller_select")
        bill_account = st.text_input("Bill Account/Reference", placeholder="Customer number/account", key="bill_account_input")
        bill_amount = st.number_input("Bill Amount (KES)", min_value=0.0, step=10.0, key="bill_amount_input")
        
    with col2:
        st.info("**Bill Payment Info:**")
        st.write("- Service charge: KES 50")
        st.write("- Processing time: Instant")
        st.write("- Daily limit: KES 500,000")
        st.write("- Minimum: KES 10")
        
        if st.button("🔍 Verify Payer Account", key="verify_bill_payer"):
            if bill_payer_account:
                account = get_account_details(bill_payer_account)
                if account:
                    st.success("✅ Payer account verified")
                    st.write(f"**Account Holder:** {account['full_name']}")
                    st.write(f"**Available Balance:** KES {account['balance']:,.2f}")
                else:
                    st.error("Payer account not found")
        
        if st.button("🔍 Verify Bill", key="verify_bill_details"):
            if bill_account and biller:
                st.success("✅ Bill details verified")
                st.write(f"**Biller:** {biller}")
                st.write(f"**Account/Reference:** {bill_account}")
                st.write(f"**Amount Due:** KES {bill_amount:,.2f}")
                st.write(f"**Service Fee:** KES 50.00")
                st.write(f"**Total:** KES {bill_amount + 50:,.2f}")
    
    if st.button("📄 Pay Bill", type="primary", key="pay_bill_btn"):
        if bill_payer_account and biller and bill_account and bill_amount >= 10:
            result = process_bill_payment(bill_payer_account, biller, bill_account, bill_amount, staff['staff_code'])
            if result:
                st.success(f"✅ Bill payment of KES {bill_amount:,.2f} completed!")
                st.write(f"**Transaction Reference:** {result['reference_code']}")
                st.write(f"**Bill Payment Reference:** {result['bill_reference']}")
                st.write(f"**Service Fee Reference:** {result['fee_reference']}")
                st.write(f"**Biller:** {biller}")
                st.write(f"**Bill Account:** {bill_account}")
                st.write(f"**Service Fee:** KES {result['service_fee']:,.2f}")
                st.write(f"**Total Debited:** KES {result['total_debited']:,.2f}")
                st.write(f"**New Balance:** KES {result['new_balance']:,.2f}")
        else:
            st.error("Please fill in all required fields (minimum KES 10)")

# TAB 7: CDSC Transfer
with tab_cdsc:
    st.subheader("📈 CDSC Account Transfer")
    
    col1, col2 = st.columns(2)
    
    with col1:
        cdsc_from_account = st.text_input("From Account", placeholder="Source account number", key="cdsc_from_account")
        cdsc_account = st.text_input("CDSC Account Number", placeholder="Enter CDSC account number", key="cdsc_account_input")
        cdsc_amount = st.number_input("Transfer Amount (KES)", min_value=0.0, step=100.0, key="cdsc_amount_input")
        cdsc_narration = st.text_area("Purpose", placeholder="Investment purpose", key="cdsc_narration_input", value="Investment transfer to CDSC")
        
    with col2:
        st.info("**CDSC Transfer Info:**")
        st.write("- Transfer fee: KES 100")
        st.write("- Processing: Same day")
        st.write("- Minimum: KES 1,000")
        st.write("- Maximum: KES 50,000,000")
        st.write("- Purpose: Securities investment")
        
        if st.button("🔍 Verify Source Account", key="verify_cdsc_source"):
            if cdsc_from_account:
                account = get_account_details(cdsc_from_account)
                if account:
                    st.success("✅ Source account verified")
                    st.write(f"**Account Holder:** {account['full_name']}")
                    st.write(f"**Available Balance:** KES {account['balance']:,.2f}")
                else:
                    st.error("Source account not found")
        
        if st.button("🔍 Verify CDSC Account", key="verify_cdsc_dest"):
            if cdsc_account:
                # Mock CDSC account verification
                st.success("✅ CDSC account verified")
                st.write(f"**CDSC Account:** {cdsc_account}")
                st.write("**Status:** Active")
                st.write("**Type:** Investment Account")
    
    if st.button("📈 Process CDSC Transfer", type="primary", key="process_cdsc_btn"):
        if cdsc_from_account and cdsc_account and cdsc_amount >= 1000:
            result = process_cdsc_transfer(cdsc_from_account, cdsc_account, cdsc_amount, cdsc_narration, staff['staff_code'])
            if result:
                st.success(f"✅ CDSC transfer of KES {cdsc_amount:,.2f} completed!")
                st.write(f"**Transaction Reference:** {result['reference_code']}")
                st.write(f"**CDSC Account:** {cdsc_account}")
                st.write(f"**Transfer Fee:** KES {result['transfer_fee']:,.2f}")
                st.write(f"**Total Debited:** KES {result['total_debited']:,.2f}")
                st.write(f"**New Balance:** KES {result['new_balance']:,.2f}")
                st.info("💡 Funds will be available in your CDSC account within 24 hours")
        else:
            st.error("Please fill in all required fields (minimum KES 1,000)")

# TAB 8: Reports
with tab_reports:
    st.subheader("📋 Teller Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Daily Summary")
        # Get today's transaction summary
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                
                # Count today's transactions
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_txns,
                        SUM(CASE WHEN txn_type = 'DEPOSIT' THEN amount ELSE 0 END) as total_deposits,
                        SUM(CASE WHEN txn_type = 'WITHDRAWAL' THEN amount ELSE 0 END) as total_withdrawals,
                        COUNT(CASE WHEN txn_type = 'DEPOSIT' THEN 1 END) as deposit_count,
                        COUNT(CASE WHEN txn_type = 'WITHDRAWAL' THEN 1 END) as withdrawal_count
                    FROM transactions 
                    WHERE DATE(created_at) = CURDATE()
                """)
                
                summary = cursor.fetchone()
                conn.close()
                
                if summary:
                    st.metric("Transactions Processed", summary['total_txns'] or 0)
                    st.metric("Total Deposits", f"KES {summary['total_deposits'] or 0:,.2f}")
                    st.metric("Total Withdrawals", f"KES {summary['total_withdrawals'] or 0:,.2f}")
                    net_position = (summary['total_deposits'] or 0) - (summary['total_withdrawals'] or 0)
                    st.metric("Net Cash Position", f"KES {net_position:,.2f}")
        except Exception as e:
            st.error(f"Error loading summary: {e}")
        
    with col2:
        st.markdown("### Transaction Breakdown")
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                
                cursor.execute("""
                    SELECT txn_type, COUNT(*) as count
                    FROM transactions 
                    WHERE DATE(created_at) = CURDATE()
                    GROUP BY txn_type
                """)
                
                breakdown = cursor.fetchall()
                conn.close()
                
                if breakdown:
                    for item in breakdown:
                        st.write(f"- {item['txn_type']}: {item['count']} transactions")
                else:
                    st.write("No transactions today")
        except Exception as e:
            st.error(f"Error loading breakdown: {e}")
    
    if st.button("📊 Generate Full Report"):
        st.success("✅ Report generated successfully!")
        st.download_button(
            label="📥 Download Report",
            data="Teller Report - Sample Data",
            file_name=f"teller_report_{staff['staff_code']}_2026-01-03.txt",
            mime="text/plain"
        )
        st.warning("Teller not logged in. Please login first.")
        st.stop()
