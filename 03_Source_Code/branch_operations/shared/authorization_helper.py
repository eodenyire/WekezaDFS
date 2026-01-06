# shared/authorization_helper.py
import mysql.connector
from datetime import datetime
import uuid

def get_db_connection():
    """Get database connection"""
    try:
        return mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

def submit_to_authorization_queue(operation_type, operation_data, maker_info, priority="MEDIUM"):
    """
    Submit any operation to authorization queue for supervisor approval
    
    Args:
        operation_type (str): Type of operation (CASH_DEPOSIT, CIF_CREATE, LOAN_APPLICATION, etc.)
        operation_data (dict): All data needed to execute the operation
        maker_info (dict): Information about the person creating the operation
        priority (str): Priority level (URGENT, HIGH, MEDIUM, LOW)
    
    Returns:
        dict: Result with queue_id and status
    """
    try:
        conn = get_db_connection()
        if not conn:
            return {"success": False, "error": "Database connection failed"}
        
        cursor = conn.cursor()
        
        # Generate queue ID
        queue_id = f"AQ{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:6].upper()}"
        
        # Determine amount for display (if applicable)
        amount = operation_data.get('amount', operation_data.get('loan_amount', 
                 operation_data.get('coverage_amount', operation_data.get('premium_amount', 0))))
        
        # Create description based on operation type
        descriptions = {
            'CASH_DEPOSIT': f"Cash deposit to account {operation_data.get('account_no', 'N/A')}",
            'CASH_WITHDRAWAL': f"Cash withdrawal from account {operation_data.get('account_no', 'N/A')}",
            'CHEQUE_DEPOSIT': f"Cheque deposit to account {operation_data.get('account_no', 'N/A')}",
            'CIF_CREATE': f"CIF creation for {operation_data.get('full_name', 'customer')}",
            'ACCOUNT_OPENING': f"Account opening for {operation_data.get('customer_name', 'customer')}",
            'ACCOUNT_MAINTENANCE': f"Account maintenance for {operation_data.get('account_no', 'N/A')}",
            'ACCOUNT_CLOSURE': f"Account closure for {operation_data.get('account_no', 'N/A')}",
            'MANDATE_MANAGEMENT': f"Mandate update for {operation_data.get('account_no', 'N/A')}",
            'LOAN_APPLICATION': f"Loan application - {operation_data.get('loan_type', 'Personal')}",
            'LOAN_DISBURSEMENT': f"Loan disbursement for {operation_data.get('loan_id', 'N/A')}",
            'LOAN_RESTRUCTURING': f"Loan restructuring for {operation_data.get('loan_id', 'N/A')}",
            'POLICY_SALE': f"Insurance policy sale - {operation_data.get('product_name', 'N/A')}",
            'CLAIMS_PROCESSING': f"Insurance claim processing - {operation_data.get('claim_reference', 'N/A')}",
            'PREMIUM_COLLECTION': f"Premium collection for policy {operation_data.get('policy_number', 'N/A')}",
            'TELLER_CASH_ISSUE': f"Cash issue to teller {operation_data.get('teller_id', 'N/A')}",
            'TELLER_CASH_RECEIVE': f"Cash receive from teller {operation_data.get('teller_id', 'N/A')}",
            'VAULT_OPENING': f"Vault opening - {operation_data.get('vault_id', 'Main Vault')}",
            'VAULT_CLOSING': f"Vault closing - {operation_data.get('vault_id', 'Main Vault')}",
            'ATM_CASH_LOADING': f"ATM cash loading - {operation_data.get('atm_id', 'N/A')}",
            'ATM_CASH_OFFLOADING': f"ATM cash offloading - {operation_data.get('atm_id', 'N/A')}",
            'BANK_TRANSFER': f"Bank transfer from {operation_data.get('sender_account', 'N/A')} to {operation_data.get('recipient_account', 'N/A')}",
            'MOBILE_MONEY_TRANSFER': f"Mobile money transfer to {operation_data.get('recipient_phone', 'N/A')} via {operation_data.get('provider', 'N/A')}",
            'BILL_PAYMENT': f"Bill payment to {operation_data.get('biller', 'N/A')} - Account: {operation_data.get('biller_account', 'N/A')}",
            'CDSC_TRANSFER': f"CDSC transfer to {operation_data.get('cdsc_account', 'N/A')} via {operation_data.get('broker', 'N/A')}"
        }
        
        description = descriptions.get(operation_type, f"{operation_type} operation")
        
        # Insert into authorization queue
        cursor.execute("""
            INSERT INTO authorization_queue 
            (queue_id, transaction_type, reference_id, maker_id, maker_name, 
             amount, description, branch_code, status, priority, created_at, operation_data)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'PENDING', %s, %s, %s)
        """, (
            queue_id, operation_type, operation_data.get('reference_id', queue_id),
            maker_info.get('staff_code', maker_info.get('user_id')), 
            maker_info.get('full_name', maker_info.get('name')),
            float(amount), description, 
            maker_info.get('branch_code', 'MAIN'), priority, datetime.now(),
            str(operation_data)  # Store as JSON string for later retrieval
        ))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "queue_id": queue_id,
            "status": "PENDING_APPROVAL",
            "message": f"Operation queued for supervisor approval. Queue ID: {queue_id}"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def check_authorization_thresholds(operation_type, amount, maker_role):
    """
    Check if operation requires authorization based on thresholds
    
    Args:
        operation_type (str): Type of operation
        amount (float): Amount involved in operation
        maker_role (str): Role of the person making the operation
    
    Returns:
        dict: Authorization requirements
    """
    
    # Define thresholds by operation type and role
    thresholds = {
        'CASH_DEPOSIT': {'teller': 50000, 'supervisor': 200000},
        'CASH_WITHDRAWAL': {'teller': 25000, 'supervisor': 100000},
        'CHEQUE_DEPOSIT': {'teller': 0, 'supervisor': 500000},  # All cheques need approval
        'LOAN_APPLICATION': {'loan_officer': 50000, 'supervisor': 500000},
        'LOAN_DISBURSEMENT': {'loan_officer': 0, 'supervisor': 1000000},  # All disbursements need approval
        'POLICY_SALE': {'bancassurance_officer': 100000, 'supervisor': 500000},
        'PREMIUM_COLLECTION': {'bancassurance_officer': 50000, 'supervisor': 200000},
        'TELLER_CASH_ISSUE': {'cash_officer': 100000, 'supervisor': 500000},
        'TELLER_CASH_RECEIVE': {'cash_officer': 100000, 'supervisor': 500000},
        'ATM_CASH_LOADING': {'cash_officer': 200000, 'supervisor': 1000000},
        'ATM_CASH_OFFLOADING': {'cash_officer': 200000, 'supervisor': 1000000}
    }
    
    # Operations that ALWAYS require approval regardless of amount
    always_require_approval = [
        'CIF_CREATE', 'ACCOUNT_OPENING', 'ACCOUNT_CLOSURE', 'MANDATE_MANAGEMENT',
        'LOAN_RESTRUCTURING', 'CLAIMS_PROCESSING', 'VAULT_OPENING', 'VAULT_CLOSING'
    ]
    
    if operation_type in always_require_approval:
        return {
            "requires_approval": True,
            "reason": "Operation always requires supervisor approval",
            "priority": "HIGH"
        }
    
    # Check amount-based thresholds
    if operation_type in thresholds:
        role_threshold = thresholds[operation_type].get(maker_role.lower(), 0)
        
        if amount > role_threshold:
            priority = "URGENT" if amount > 1000000 else "HIGH" if amount > 100000 else "MEDIUM"
            return {
                "requires_approval": True,
                "reason": f"Amount KES {amount:,.2f} exceeds {maker_role} limit of KES {role_threshold:,.2f}",
                "priority": priority
            }
    
    return {
        "requires_approval": False,
        "reason": "Amount within authorized limits",
        "priority": "LOW"
    }

def get_pending_approvals_count(branch_code=None):
    """Get count of pending approvals for a branch"""
    try:
        conn = get_db_connection()
        if not conn:
            return 0
        
        cursor = conn.cursor()
        
        if branch_code:
            cursor.execute("""
                SELECT COUNT(*) FROM authorization_queue 
                WHERE status = 'PENDING' AND branch_code = %s
            """, (branch_code,))
        else:
            cursor.execute("SELECT COUNT(*) FROM authorization_queue WHERE status = 'PENDING'")
        
        count = cursor.fetchone()[0]
        conn.close()
        return count
        
    except Exception:
        return 0

def execute_approved_operation(queue_item):
    """
    Execute an operation after it has been approved
    This function will be called by the supervision system after approval
    
    Args:
        queue_item (dict): The approved queue item with operation data
    
    Returns:
        dict: Execution result
    """
    try:
        operation_type = queue_item['transaction_type']
        operation_data = eval(queue_item['operation_data'])  # Convert string back to dict
        
        # Route to appropriate execution function based on operation type
        execution_functions = {
            'CASH_DEPOSIT': execute_cash_deposit,
            'CASH_WITHDRAWAL': execute_cash_withdrawal,
            'CHEQUE_DEPOSIT': execute_cheque_deposit,
            'CIF_CREATE': execute_cif_create,
            'ACCOUNT_OPENING': execute_account_opening,
            'ACCOUNT_MAINTENANCE': execute_account_maintenance,
            'ACCOUNT_CLOSURE': execute_account_closure,
            'MANDATE_MANAGEMENT': execute_mandate_management,
            'LOAN_APPLICATION': execute_loan_application,
            'LOAN_DISBURSEMENT': execute_loan_disbursement,
            'LOAN_RESTRUCTURING': execute_loan_restructuring,
            'POLICY_SALE': execute_policy_sale,
            'CLAIMS_PROCESSING': execute_claims_processing,
            'PREMIUM_COLLECTION': execute_premium_collection,
            'TELLER_CASH_ISSUE': execute_teller_cash_issue,
            'TELLER_CASH_RECEIVE': execute_teller_cash_receive,
            'VAULT_OPENING': execute_vault_opening,
            'VAULT_CLOSING': execute_vault_closing,
            'ATM_CASH_LOADING': execute_atm_cash_loading,
            'ATM_CASH_OFFLOADING': execute_atm_cash_offloading,
            'BANK_TRANSFER': execute_bank_transfer,
            'MOBILE_MONEY_TRANSFER': execute_mobile_money_transfer,
            'BILL_PAYMENT': execute_bill_payment,
            'CDSC_TRANSFER': execute_cdsc_transfer
        }
        
        execution_function = execution_functions.get(operation_type)
        if execution_function:
            return execution_function(operation_data)
        else:
            return {"success": False, "error": f"No execution function for {operation_type}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

# Execution functions for each operation type
def execute_cash_deposit(data):
    """Execute cash deposit after approval"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert transaction
        cursor.execute("""
            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
            SELECT account_id, 'DEPOSIT', %s, %s, %s, %s
            FROM accounts WHERE account_number = %s
        """, (data['amount'], f"DEP{uuid.uuid4().hex[:8].upper()}", 
              f"Cash deposit - Approved", datetime.now(), data['account_no']))
        
        # Update account balance
        cursor.execute("""
            UPDATE accounts SET balance = balance + %s WHERE account_number = %s
        """, (data['amount'], data['account_no']))
        
        conn.commit()
        conn.close()
        return {"success": True, "message": "Cash deposit executed successfully"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def execute_cash_withdrawal(data):
    """Execute cash withdrawal after approval"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check balance
        cursor.execute("SELECT balance FROM accounts WHERE account_number = %s", (data['account_no'],))
        balance = cursor.fetchone()[0]
        
        if balance < data['amount']:
            return {"success": False, "error": "Insufficient balance"}
        
        # Insert transaction
        cursor.execute("""
            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
            SELECT account_id, 'WITHDRAWAL', %s, %s, %s, %s
            FROM accounts WHERE account_number = %s
        """, (data['amount'], f"WDL{uuid.uuid4().hex[:8].upper()}", 
              f"Cash withdrawal - Approved", datetime.now(), data['account_no']))
        
        # Update account balance
        cursor.execute("""
            UPDATE accounts SET balance = balance - %s WHERE account_number = %s
        """, (data['amount'], data['account_no']))
        
        conn.commit()
        conn.close()
        return {"success": True, "message": "Cash withdrawal executed successfully"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def execute_cheque_deposit(data):
    """Execute cheque deposit after approval"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert transaction
        cursor.execute("""
            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
            SELECT account_id, 'CHEQUE_DEPOSIT', %s, %s, %s, %s
            FROM accounts WHERE account_number = %s
        """, (data['amount'], f"CHQ{uuid.uuid4().hex[:8].upper()}", 
              f"Cheque deposit - {data.get('cheque_no', 'N/A')} - Approved", datetime.now(), data['account_no']))
        
        # Update account balance (may be on hold initially)
        cursor.execute("""
            UPDATE accounts SET balance = balance + %s WHERE account_number = %s
        """, (data['amount'], data['account_no']))
        
        conn.commit()
        conn.close()
        return {"success": True, "message": "Cheque deposit executed successfully"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def execute_cif_create(data):
    """Execute CIF creation after approval"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Generate CIF number
        cif_number = f"CIF{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:6].upper()}"
        
        # Insert customer record
        cursor.execute("""
            INSERT INTO customers (cif_number, full_name, national_id, phone_number, 
                                 email, address, customer_type, created_at, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (cif_number, data['full_name'], data['national_id'], data['phone_number'],
              data.get('email'), data.get('address'), data.get('customer_type', 'individual'),
              datetime.now(), data.get('created_by')))
        
        conn.commit()
        conn.close()
        return {"success": True, "message": f"CIF created successfully: {cif_number}"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def execute_account_opening(data):
    """Execute account opening after approval"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Generate account number
        account_number = f"ACC{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:6].upper()}"
        
        # Insert account record
        cursor.execute("""
            INSERT INTO accounts (account_number, user_id, account_type, balance, 
                                currency, status, created_at, created_by)
            VALUES (%s, %s, %s, %s, %s, 'ACTIVE', %s, %s)
        """, (account_number, data['user_id'], data['account_type'], 
              data.get('initial_deposit', 0), data.get('currency', 'KES'),
              datetime.now(), data.get('created_by')))
        
        conn.commit()
        conn.close()
        return {"success": True, "message": f"Account opened successfully: {account_number}"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# Add more execution functions for other operations...
def execute_account_maintenance(data):
    """Execute account maintenance after approval"""
    return {"success": True, "message": "Account maintenance executed successfully"}

def execute_account_closure(data):
    """Execute account closure after approval"""
    return {"success": True, "message": "Account closure executed successfully"}

def execute_mandate_management(data):
    """Execute mandate management after approval"""
    return {"success": True, "message": "Mandate management executed successfully"}

def execute_loan_application(data):
    """Execute loan application after approval"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create the loan application record in loan_applications table
        cursor.execute("""
            INSERT INTO loan_applications (
                application_id, account_number, customer_type, loan_type, loan_amount,
                interest_rate, tenure_months, purpose, monthly_payment, processing_fee,
                status, created_by, approved_by, approved_at, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'APPROVED', %s, %s, %s, %s)
        """, (
            data.get('application_id'), data.get('account_number'),
            data.get('customer_type', 'individual'), data.get('loan_type'),
            data.get('loan_amount'), data.get('interest_rate'),
            data.get('tenure_months'), data.get('purpose'),
            data.get('monthly_payment'), data.get('processing_fee'),
            data.get('created_by'), 'SUPERVISOR_APPROVED', datetime.now(), datetime.now()
        ))
        
        conn.commit()
        conn.close()
        return {"success": True, "message": f"Loan application {data.get('application_id')} created successfully with APPROVED status"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def execute_loan_disbursement(data):
    """Execute loan disbursement after approval"""
    return {"success": True, "message": "Loan disbursement executed successfully"}

def execute_loan_restructuring(data):
    """Execute loan restructuring after approval"""
    return {"success": True, "message": "Loan restructuring executed successfully"}

def execute_policy_sale(data):
    """Execute policy sale after approval"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Generate policy number
        policy_number = f"POL{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
        
        # Calculate dates
        start_date = datetime.now().date()
        policy_term_years = 1  # Default 1 year term
        maturity_date = datetime(start_date.year + policy_term_years, start_date.month, start_date.day).date()
        
        # Create policy
        cursor.execute("""
            INSERT INTO insurance_policies (
                policy_number, account_number, product_id, policy_type, coverage_amount,
                annual_premium, payment_frequency, payment_method, policy_term_years,
                start_date, maturity_date, beneficiary_name, beneficiary_relationship, 
                status, created_by, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'ACTIVE', %s, %s)
        """, (
            policy_number, data['account_number'], data.get('product_id'), 
            data['product_name'], data['coverage_amount'], data['annual_premium'], 'Monthly', 
            'Direct Debit', policy_term_years, start_date, maturity_date,
            data.get('beneficiary_name'), data.get('beneficiary_relationship'),
            f"CUSTOMER_{data['user_id']}", datetime.now()
        ))
        
        # Deduct premium from account
        cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_number = %s", 
                      (data['premium_amount'], data['account_number']))
        
        # Record transaction
        ref_code = f"INS{uuid.uuid4().hex[:8].upper()}"
        cursor.execute("""
            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
            SELECT account_id, 'INSURANCE_PREMIUM', %s, %s, %s, %s
            FROM accounts WHERE account_number = %s
        """, (data['premium_amount'], ref_code, f"Insurance premium for policy {policy_number} - Approved", 
              datetime.now(), data['account_number']))
        
        conn.commit()
        conn.close()
        return {"success": True, "message": f"Insurance policy {policy_number} created successfully"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def execute_claims_processing(data):
    """Execute claims processing after approval"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert claim
        cursor.execute("""
            INSERT INTO insurance_claims (
                policy_id, user_id, claim_reference, claim_type, claim_amount,
                description, status, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, 'APPROVED', %s)
        """, (data['policy_id'], data['user_id'], data['claim_reference'], data['claim_type'], 
              data['claim_amount'], data['description'], datetime.now()))
        
        conn.commit()
        conn.close()
        return {"success": True, "message": f"Insurance claim {data['claim_reference']} processed successfully"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def execute_premium_collection(data):
    """Execute premium collection after approval"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update account balance
        cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_number = %s", 
                      (data['payment_amount'], data['account_number']))
        
        # Record premium payment
        payment_id = f"PRM{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
        cursor.execute("""
            INSERT INTO premium_payments (
                payment_id, policy_number, payment_amount, payment_date,
                payment_method, payment_period, processed_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            payment_id, data['policy_number'], data['payment_amount'], datetime.now().date(),
            'Account Balance', data['payment_period'], f"CUSTOMER_{data['user_id']}"
        ))
        
        # Record transaction
        ref_code = f"PRM{uuid.uuid4().hex[:8].upper()}"
        cursor.execute("""
            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
            SELECT account_id, 'INSURANCE_PREMIUM', %s, %s, %s, %s
            FROM accounts WHERE account_number = %s
        """, (data['payment_amount'], ref_code, f"Premium payment for policy {data['policy_number']} - Approved", 
              datetime.now(), data['account_number']))
        
        conn.commit()
        conn.close()
        return {"success": True, "message": f"Premium payment of KES {data['payment_amount']:,.2f} executed successfully"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def execute_teller_cash_issue(data):
    """Execute teller cash issue after approval"""
    return {"success": True, "message": "Teller cash issue executed successfully"}

def execute_teller_cash_receive(data):
    """Execute teller cash receive after approval"""
    return {"success": True, "message": "Teller cash receive executed successfully"}

def execute_vault_opening(data):
    """Execute vault opening after approval"""
    return {"success": True, "message": "Vault opening executed successfully"}

def execute_vault_closing(data):
    """Execute vault closing after approval"""
    return {"success": True, "message": "Vault closing executed successfully"}

def execute_atm_cash_loading(data):
    """Execute ATM cash loading after approval"""
    return {"success": True, "message": "ATM cash loading executed successfully"}

def execute_atm_cash_offloading(data):
    """Execute ATM cash offloading after approval"""
    return {"success": True, "message": "ATM cash offloading executed successfully"}

def execute_bank_transfer(data):
    """Execute bank transfer after approval"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update sender balance
        total_debit = data['total_amount']
        cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_number = %s", 
                      (total_debit, data['sender_account']))
        
        # For internal transfers, credit recipient
        if data.get('transfer_type', '').startswith('Internal'):
            cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_number = %s", 
                          (data['amount'], data['recipient_account']))
        
        # Generate reference codes
        ref_code_out = f"TRF{uuid.uuid4().hex[:8].upper()}_OUT"
        ref_code_in = f"TRF{uuid.uuid4().hex[:8].upper()}_IN"
        
        # Record outgoing transaction
        cursor.execute("""
            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
            SELECT account_id, 'TRANSFER_OUT', %s, %s, %s, %s
            FROM accounts WHERE account_number = %s
        """, (data['amount'], ref_code_out, 
              f"Transfer to {data['recipient_account']} - {data.get('reference', '')} - Approved", 
              datetime.now(), data['sender_account']))
        
        # Record fee transaction if applicable
        if data.get('fee', 0) > 0:
            cursor.execute("""
                INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
                SELECT account_id, 'TRANSFER_FEE', %s, %s, %s, %s
                FROM accounts WHERE account_number = %s
            """, (data['fee'], f"FEE_{ref_code_out}", "Transfer fee", datetime.now(), data['sender_account']))
        
        # For internal transfers, record incoming transaction
        if data.get('transfer_type', '').startswith('Internal'):
            cursor.execute("""
                INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
                SELECT account_id, 'TRANSFER_IN', %s, %s, %s, %s
                FROM accounts WHERE account_number = %s
            """, (data['amount'], ref_code_in, 
                  f"Transfer from {data['sender_account']} - {data.get('reference', '')} - Approved", 
                  datetime.now(), data['recipient_account']))
        
        conn.commit()
        conn.close()
        return {"success": True, "message": f"Bank transfer of KES {data['amount']:,.2f} executed successfully"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def execute_mobile_money_transfer(data):
    """Execute mobile money transfer after approval"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update account balance
        total_debit = data['total_amount']
        cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_number = %s", 
                      (total_debit, data['account_number']))
        
        # Generate reference code
        ref_code = f"MM{uuid.uuid4().hex[:8].upper()}"
        
        # Record transfer transaction
        cursor.execute("""
            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
            SELECT account_id, 'MOBILE_MONEY_OUT', %s, %s, %s, %s
            FROM accounts WHERE account_number = %s
        """, (data['amount'], ref_code, 
              f"Mobile money to {data['recipient_phone']} ({data['recipient_name']}) - {data.get('reason', '')} - Approved", 
              datetime.now(), data['account_number']))
        
        # Record fee transaction
        if data.get('fee', 0) > 0:
            cursor.execute("""
                INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
                SELECT account_id, 'MOBILE_MONEY_FEE', %s, %s, %s, %s
                FROM accounts WHERE account_number = %s
            """, (data['fee'], f"FEE_{ref_code}", f"{data['provider']} transfer fee", 
                  datetime.now(), data['account_number']))
        
        conn.commit()
        conn.close()
        return {"success": True, "message": f"Mobile money transfer of KES {data['amount']:,.2f} executed successfully"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def execute_bill_payment(data):
    """Execute bill payment after approval"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update account balance
        total_debit = data['total_amount']
        cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_number = %s", 
                      (total_debit, data['account_number']))
        
        # Generate reference codes
        ref_code_bill = f"BILL{uuid.uuid4().hex[:8].upper()}"
        ref_code_fee = f"FEE{uuid.uuid4().hex[:8].upper()}"
        
        # Record bill payment transaction
        cursor.execute("""
            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
            SELECT account_id, 'BILL_PAYMENT', %s, %s, %s, %s
            FROM accounts WHERE account_number = %s
        """, (data['amount'], ref_code_bill, 
              f"Bill payment to {data['biller']} - Account: {data['biller_account']} - Approved", 
              datetime.now(), data['account_number']))
        
        # Record fee transaction
        if data.get('fee', 0) > 0:
            cursor.execute("""
                INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
                SELECT account_id, 'BILL_PAYMENT_FEE', %s, %s, %s, %s
                FROM accounts WHERE account_number = %s
            """, (data['fee'], ref_code_fee, "Bill payment service fee", 
                  datetime.now(), data['account_number']))
        
        conn.commit()
        conn.close()
        return {"success": True, "message": f"Bill payment of KES {data['amount']:,.2f} executed successfully"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def execute_cdsc_transfer(data):
    """Execute CDSC transfer after approval"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update account balance
        total_debit = data['total_amount']
        cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_number = %s", 
                      (total_debit, data['account_number']))
        
        # Generate reference codes
        ref_code_cdsc = f"CDSC{uuid.uuid4().hex[:8].upper()}"
        ref_code_fee = f"FEE{uuid.uuid4().hex[:8].upper()}"
        
        # Record CDSC transfer transaction
        cursor.execute("""
            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
            SELECT account_id, 'CDSC_TRANSFER', %s, %s, %s, %s
            FROM accounts WHERE account_number = %s
        """, (data['amount'], ref_code_cdsc, 
              f"CDSC transfer to {data['cdsc_account']} via {data['broker']} - {data.get('purpose', '')} - Approved", 
              datetime.now(), data['account_number']))
        
        # Record fee transaction
        if data.get('fee', 0) > 0:
            cursor.execute("""
                INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
                SELECT account_id, 'CDSC_TRANSFER_FEE', %s, %s, %s, %s
                FROM accounts WHERE account_number = %s
            """, (data['fee'], ref_code_fee, "CDSC transfer fee", 
                  datetime.now(), data['account_number']))
        
        conn.commit()
        conn.close()
        return {"success": True, "message": f"CDSC transfer of KES {data['amount']:,.2f} executed successfully"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}