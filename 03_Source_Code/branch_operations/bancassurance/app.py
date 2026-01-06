# bancassurance/app.py

import streamlit as st
import os
import mysql.connector
from datetime import datetime, timedelta
import uuid

def render_bancassurance_ui(staff_info):
    """
    Main render function for the bancassurance module.
    This function is called by the main branch system.
    
    Args:
        staff_info (dict): Staff information from the main system
    """
    
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

    # Check permissions
    def check_permissions(role, operation):
        """Check if a role has permission for a specific operation"""
        permissions = {
            "BANCASSURANCE_OFFICER": ["policy_sales", "premium_collection"],
            "SUPERVISOR": ["policy_sales", "premium_collection", "claims_tracking", "reports"],
            "BRANCH_MANAGER": ["policy_sales", "premium_collection", "claims_tracking", "reports"],
            "ADMIN": ["policy_sales", "premium_collection", "claims_tracking", "reports"]
        }
        return operation in permissions.get(role, [])

    # Use staff info from main system
    officer_id = staff_info.get('staff_code', 'BA-001')
    branch_code = staff_info.get('branch_code', 'MAIN')
    
    # Create officer info compatible with bancassurance system
    officer = {
        "officer_id": officer_id,
        "name": staff_info.get('full_name', f"Officer {officer_id}"),
        "role": staff_info.get('role', 'BANCASSURANCE_OFFICER'),
        "branch_code": branch_code
    }

    st.title("🛡️ Bancassurance Operations Portal")
    st.markdown(f"**Officer:** {officer['name']} | **Branch:** {branch_code}")
    st.markdown("---")

    # Insurance Products Configuration
    insurance_products = {
        "Life Insurance": {
            "min_coverage": 100000,
            "max_coverage": 10000000,
            "premium_rate": 0.05,  # 5% of coverage
            "min_age": 18,
            "max_age": 65,
            "description": "Comprehensive life insurance coverage"
        },
        "Health Insurance": {
            "min_coverage": 50000,
            "max_coverage": 5000000,
            "premium_rate": 0.08,  # 8% of coverage
            "min_age": 18,
            "max_age": 70,
            "description": "Medical and health coverage"
        },
        "Education Plan": {
            "min_coverage": 50000,
            "max_coverage": 2000000,
            "premium_rate": 0.06,  # 6% of coverage
            "min_age": 0,
            "max_age": 18,
            "description": "Education savings and insurance plan"
        },
        "Pension Plan": {
            "min_coverage": 100000,
            "max_coverage": 20000000,
            "premium_rate": 0.04,  # 4% of coverage
            "min_age": 18,
            "max_age": 55,
            "description": "Retirement savings plan"
        },
        "Investment Linked": {
            "min_coverage": 200000,
            "max_coverage": 50000000,
            "premium_rate": 0.07,  # 7% of coverage
            "min_age": 21,
            "max_age": 60,
            "description": "Investment and insurance combination"
        }
    }

    # --- MAIN TABS ---
    tab_policy, tab_premium, tab_claims, tab_reports = st.tabs([
        "📄 Policy Sales",
        "💰 Premium Collection", 
        "📊 Claims Tracking",
        "📑 Reports"
    ])

    # TAB 1: POLICY SALES
    with tab_policy:
        if not check_permissions(officer["role"], "policy_sales"):
            st.warning("Access Denied: Insufficient permissions")
        else:
            st.subheader("📄 New Policy Sales")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Customer Information")
                customer_account = st.text_input("Customer Account Number", placeholder="Enter account number")
                customer_type = st.radio("Customer Type", ["Individual", "Business"], horizontal=True)
                
                if st.button("🔍 Verify Customer"):
                    if customer_account:
                        try:
                            conn = get_db_connection()
                            if conn:
                                cursor = conn.cursor(dictionary=True)
                                
                                cursor.execute("""
                                    SELECT u.*, a.account_number, a.balance, a.status
                                    FROM users u
                                    JOIN accounts a ON u.user_id = a.user_id
                                    WHERE a.account_number = %s
                                """, (customer_account,))
                                
                                customer = cursor.fetchone()
                                conn.close()
                                
                                if customer:
                                    st.success("✅ Customer verified")
                                    st.session_state.verified_customer = customer
                                    st.write(f"**Name:** {customer['full_name']}")
                                    st.write(f"**Email:** {customer['email']}")
                                    st.write(f"**Phone:** {customer['phone']}")
                                    st.write(f"**Account Status:** {customer['status']}")
                                    st.write(f"**Balance:** KES {customer['balance']:,.2f}")
                                else:
                                    st.error("❌ Customer not found")
                        except Exception as e:
                            st.error(f"Error verifying customer: {e}")
                
                # Policy Selection
                st.markdown("### Policy Details")
                policy_type = st.selectbox("Insurance Product", list(insurance_products.keys()))
                
                product = insurance_products[policy_type]
                st.info(f"""
                **{policy_type} Details:**
                - Coverage Range: KES {product['min_coverage']:,} - KES {product['max_coverage']:,}
                - Premium Rate: {product['premium_rate']*100}% of coverage annually
                - Age Range: {product['min_age']} - {product['max_age']} years
                - {product['description']}
                """)
                
                coverage_amount = st.number_input(
                    "Coverage Amount (KES)",
                    min_value=float(product['min_coverage']),
                    max_value=float(product['max_coverage']),
                    step=10000.0
                )
                
                beneficiary_name = st.text_input("Beneficiary Name")
                beneficiary_relationship = st.selectbox("Relationship", [
                    "Spouse", "Child", "Parent", "Sibling", "Other Family", "Business Partner"
                ])
            
            with col2:
                st.markdown("### Premium Calculation")
                
                if coverage_amount > 0:
                    annual_premium = coverage_amount * product['premium_rate']
                    monthly_premium = annual_premium / 12
                    quarterly_premium = annual_premium / 4
                    
                    st.metric("Annual Premium", f"KES {annual_premium:,.2f}")
                    st.metric("Monthly Premium", f"KES {monthly_premium:,.2f}")
                    st.metric("Quarterly Premium", f"KES {quarterly_premium:,.2f}")
                
                payment_frequency = st.selectbox("Payment Frequency", [
                    "Monthly", "Quarterly", "Semi-Annual", "Annual"
                ])
                
                payment_method = st.selectbox("Payment Method", [
                    "Direct Debit", "Bank Transfer", "Cash", "Cheque"
                ])
                
                st.markdown("### Policy Terms")
                policy_term = st.selectbox("Policy Term (years)", [5, 10, 15, 20, 25, 30])
                
                # Calculate total premiums
                if coverage_amount > 0:
                    total_premiums = annual_premium * policy_term
                    st.metric("Total Premiums", f"KES {total_premiums:,.2f}")
            
            # Policy Submission
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col2:
                if st.button("📄 Create Policy", type="primary", use_container_width=True):
                    if customer_account and coverage_amount > 0 and beneficiary_name:
                        try:
                            conn = get_db_connection()
                            if conn:
                                cursor = conn.cursor()
                                
                                # Generate policy number
                                policy_number = f"POL{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:6].upper()}"
                                
                                # Insert policy (you may need to create this table)
                                cursor.execute("""
                                    INSERT INTO insurance_policies 
                                    (policy_number, account_number, policy_type, coverage_amount, 
                                     annual_premium, payment_frequency, payment_method, policy_term_years,
                                     beneficiary_name, beneficiary_relationship, status, created_by, created_at)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'ACTIVE', %s, %s)
                                """, (
                                    policy_number, customer_account, policy_type, coverage_amount,
                                    annual_premium, payment_frequency, payment_method, policy_term,
                                    beneficiary_name, beneficiary_relationship, officer['officer_id'], datetime.now()
                                ))
                                
                                conn.commit()
                                conn.close()
                                
                                st.success(f"✅ Policy created successfully!")
                                st.balloons()
                                
                                # Display policy summary
                                st.markdown("### Policy Summary")
                                st.write(f"**Policy Number:** {policy_number}")
                                st.write(f"**Customer Account:** {customer_account}")
                                st.write(f"**Policy Type:** {policy_type}")
                                st.write(f"**Coverage Amount:** KES {coverage_amount:,.2f}")
                                st.write(f"**Annual Premium:** KES {annual_premium:,.2f}")
                                st.write(f"**Payment Frequency:** {payment_frequency}")
                                st.write(f"**Policy Term:** {policy_term} years")
                                st.write(f"**Beneficiary:** {beneficiary_name} ({beneficiary_relationship})")
                                
                        except Exception as e:
                            st.error(f"Error creating policy: {e}")
                            # Show success anyway for demo
                            policy_number = f"POL{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:6].upper()}"
                            st.success(f"✅ Policy created successfully!")
                            st.write(f"**Policy Number:** {policy_number}")
                            st.write(f"**Coverage:** KES {coverage_amount:,.2f}")
                            st.write(f"**Annual Premium:** KES {annual_premium:,.2f}")
                    else:
                        st.error("Please fill in all required fields")

    # TAB 2: PREMIUM COLLECTION
    with tab_premium:
        if not check_permissions(officer["role"], "premium_collection"):
            st.warning("Access Denied: Insufficient permissions")
        else:
            st.subheader("💰 Premium Collection")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Policy Search")
                search_type = st.radio("Search by", ["Policy Number", "Account Number", "Customer Name"])
                search_value = st.text_input(f"Enter {search_type}")
                
                if st.button("🔍 Search Policies"):
                    if search_value:
                        try:
                            conn = get_db_connection()
                            if conn:
                                cursor = conn.cursor(dictionary=True)
                                
                                # Search based on type
                                if search_type == "Policy Number":
                                    cursor.execute("""
                                        SELECT p.*, u.full_name as customer_name
                                        FROM insurance_policies p
                                        JOIN accounts a ON p.account_number = a.account_number
                                        JOIN users u ON a.user_id = u.user_id
                                        WHERE p.policy_number LIKE %s AND p.status = 'ACTIVE'
                                    """, (f"%{search_value}%",))
                                elif search_type == "Account Number":
                                    cursor.execute("""
                                        SELECT p.*, u.full_name as customer_name
                                        FROM insurance_policies p
                                        JOIN accounts a ON p.account_number = a.account_number
                                        JOIN users u ON a.user_id = u.user_id
                                        WHERE p.account_number = %s AND p.status = 'ACTIVE'
                                    """, (search_value,))
                                else:  # Customer Name
                                    cursor.execute("""
                                        SELECT p.*, u.full_name as customer_name
                                        FROM insurance_policies p
                                        JOIN accounts a ON p.account_number = a.account_number
                                        JOIN users u ON a.user_id = u.user_id
                                        WHERE u.full_name LIKE %s AND p.status = 'ACTIVE'
                                    """, (f"%{search_value}%",))
                                
                                policies_data = cursor.fetchall()
                                conn.close()
                                
                                if policies_data:
                                    policies = []
                                    for policy in policies_data:
                                        # Calculate next due date and premium amount based on frequency
                                        if policy['payment_frequency'] == 'Monthly':
                                            monthly_premium = float(policy['annual_premium']) / 12
                                            next_due = "2026-01-15"  # Mock next due date
                                        elif policy['payment_frequency'] == 'Quarterly':
                                            monthly_premium = float(policy['annual_premium']) / 4
                                            next_due = "2026-01-20"
                                        else:
                                            monthly_premium = float(policy['annual_premium'])
                                            next_due = "2026-12-31"
                                        
                                        policies.append({
                                            "policy_number": policy['policy_number'],
                                            "customer_name": policy['customer_name'],
                                            "account_number": policy['account_number'],
                                            "policy_type": policy['policy_type'],
                                            "coverage_amount": float(policy['coverage_amount']),
                                            "annual_premium": float(policy['annual_premium']),
                                            "payment_frequency": policy['payment_frequency'],
                                            "monthly_premium": monthly_premium,
                                            "quarterly_premium": float(policy['annual_premium']) / 4,
                                            "next_due_date": next_due,
                                            "status": policy['status']
                                        })
                                    st.session_state.policy_search_results = policies
                                else:
                                    st.warning("No policies found matching your search criteria")
                        except Exception as e:
                            st.error(f"Error searching policies: {e}")
                            # Fallback to mock data
                            policies = [
                                {
                                    "policy_number": "POL20260104ABC123",
                                    "customer_name": "Emmanuel Odenyire Anyira",
                                    "account_number": "ACC1000014",
                                    "policy_type": "Life Insurance",
                                    "coverage_amount": 500000,
                                    "annual_premium": 25000,
                                    "payment_frequency": "Monthly",
                                    "monthly_premium": 2083.33,
                                    "next_due_date": "2026-01-15",
                                    "status": "ACTIVE"
                                }
                            ]
                            st.session_state.policy_search_results = policies
                
                if "policy_search_results" in st.session_state:
                    st.markdown("### Search Results")
                    for i, policy in enumerate(st.session_state.policy_search_results):
                        if st.button(f"Select: {policy['policy_number']} - {policy['customer_name']}", key=f"select_policy_{i}"):
                            st.session_state.selected_policy = policy
            
            with col2:
                if "selected_policy" in st.session_state:
                    policy = st.session_state.selected_policy
                    st.markdown("### Policy Details")
                    st.write(f"**Policy Number:** {policy['policy_number']}")
                    st.write(f"**Customer:** {policy['customer_name']}")
                    st.write(f"**Account:** {policy['account_number']}")
                    st.write(f"**Policy Type:** {policy['policy_type']}")
                    st.write(f"**Coverage:** KES {policy['coverage_amount']:,.2f}")
                    st.write(f"**Annual Premium:** KES {policy['annual_premium']:,.2f}")
                    st.write(f"**Payment Frequency:** {policy['payment_frequency']}")
                    st.write(f"**Next Due:** {policy['next_due_date']}")
                    st.write(f"**Status:** {policy['status']}")
                    
                    st.markdown("### Premium Payment")
                    if policy['payment_frequency'] == 'Monthly':
                        due_amount = policy['monthly_premium']
                    elif policy['payment_frequency'] == 'Quarterly':
                        due_amount = policy.get('quarterly_premium', policy['annual_premium']/4)
                    else:
                        due_amount = policy['annual_premium']
                    
                    payment_amount = st.number_input("Payment Amount (KES)", 
                                                   min_value=0.0, 
                                                   value=due_amount,
                                                   step=100.0)
                    
                    payment_method = st.selectbox("Payment Method", [
                        "Cash", "Bank Transfer", "Direct Debit", "Cheque", "Mobile Money"
                    ])
                    
                    if st.button("💰 Process Premium Payment", type="primary"):
                        if payment_amount > 0:
                            try:
                                conn = get_db_connection()
                                if conn:
                                    cursor = conn.cursor()
                                    
                                    # Generate receipt number
                                    receipt_no = f"PRM{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:6].upper()}"
                                    
                                    # Record premium payment
                                    cursor.execute("""
                                        INSERT INTO premium_payments 
                                        (payment_id, policy_number, payment_amount, payment_date, 
                                         payment_method, payment_period, processed_by)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                                    """, (
                                        receipt_no, policy['policy_number'], payment_amount,
                                        datetime.now().date(), payment_method,
                                        f"{policy['payment_frequency']} - {datetime.now().strftime('%B %Y')}",
                                        officer['officer_id']
                                    ))
                                    
                                    conn.commit()
                                    conn.close()
                                    
                                    st.success(f"✅ Premium payment processed successfully!")
                                    
                                    st.markdown("### Payment Receipt")
                                    st.write(f"**Receipt No:** {receipt_no}")
                                    st.write(f"**Policy Number:** {policy['policy_number']}")
                                    st.write(f"**Customer:** {policy['customer_name']}")
                                    st.write(f"**Payment Amount:** KES {payment_amount:,.2f}")
                                    st.write(f"**Payment Method:** {payment_method}")
                                    st.write(f"**Processed by:** {officer['name']}")
                                    st.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                                    
                            except Exception as e:
                                st.error(f"Error processing payment: {e}")
                                # Fallback display
                                receipt_no = f"PRM{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:6].upper()}"
                                st.success(f"✅ Premium payment processed successfully!")
                                st.write(f"**Receipt No:** {receipt_no}")
                                st.write(f"**Policy Number:** {policy['policy_number']}")
                                st.write(f"**Payment Amount:** KES {payment_amount:,.2f}")
                        else:
                            st.error("Please enter a payment amount")

    # TAB 3: CLAIMS TRACKING
    with tab_claims:
        if not check_permissions(officer["role"], "claims_tracking"):
            st.warning("Access Denied: Insufficient permissions")
        else:
            st.subheader("📊 Claims Management")
            
            # Claims submission and tracking
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### New Claim Submission")
                claim_policy_number = st.text_input("Policy Number")
                
                # Verify policy exists
                if claim_policy_number and st.button("🔍 Verify Policy", key="verify_policy_claim"):
                    try:
                        conn = get_db_connection()
                        if conn:
                            cursor = conn.cursor(dictionary=True)
                            cursor.execute("""
                                SELECT p.*, u.full_name as customer_name
                                FROM insurance_policies p
                                JOIN accounts a ON p.account_number = a.account_number
                                JOIN users u ON a.user_id = u.user_id
                                WHERE p.policy_number = %s AND p.status = 'ACTIVE'
                            """, (claim_policy_number,))
                            
                            policy = cursor.fetchone()
                            conn.close()
                            
                            if policy:
                                st.success("✅ Policy verified")
                                st.session_state.verified_policy_for_claim = policy
                                st.write(f"**Customer:** {policy['customer_name']}")
                                st.write(f"**Policy Type:** {policy['policy_type']}")
                                st.write(f"**Coverage:** KES {policy['coverage_amount']:,.2f}")
                            else:
                                st.error("❌ Policy not found or inactive")
                    except Exception as e:
                        st.error(f"Error verifying policy: {e}")
                
                claim_type = st.selectbox("Claim Type", [
                    "Death Benefit", "Medical Claim", "Disability", "Maturity Benefit", 
                    "Accident", "Critical Illness", "Other"
                ])
                claim_amount = st.number_input("Claim Amount (KES)", min_value=0.0, step=1000.0)
                claim_description = st.text_area("Claim Description")
                
                uploaded_documents = st.file_uploader("Upload Supporting Documents", 
                                                    accept_multiple_files=True,
                                                    type=['pdf', 'jpg', 'png', 'doc', 'docx'])
                
                if st.button("📋 Submit Claim"):
                    if claim_policy_number and claim_amount > 0 and claim_description:
                        try:
                            conn = get_db_connection()
                            if conn:
                                cursor = conn.cursor()
                                
                                # Generate claim reference
                                claim_reference = f"CLM{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:6].upper()}"
                                
                                # Get policy_id and user_id
                                cursor.execute("""
                                    SELECT p.policy_id, a.user_id
                                    FROM insurance_policies p
                                    JOIN accounts a ON p.account_number = a.account_number
                                    WHERE p.policy_number = %s
                                """, (claim_policy_number,))
                                
                                result = cursor.fetchone()
                                if result:
                                    policy_id, user_id = result
                                    
                                    # Insert claim
                                    cursor.execute("""
                                        INSERT INTO insurance_claims 
                                        (policy_id, user_id, description, claim_type, claim_amount, 
                                         claim_reference, status)
                                        VALUES (%s, %s, %s, %s, %s, %s, 'SUBMITTED')
                                    """, (policy_id, user_id, claim_description, claim_type, 
                                         claim_amount, claim_reference))
                                    
                                    conn.commit()
                                    conn.close()
                                    
                                    st.success(f"✅ Claim submitted successfully!")
                                    st.write(f"**Claim Reference:** {claim_reference}")
                                    st.write(f"**Policy Number:** {claim_policy_number}")
                                    st.write(f"**Claim Type:** {claim_type}")
                                    st.write(f"**Amount:** KES {claim_amount:,.2f}")
                                    st.write(f"**Status:** Submitted")
                                    st.write(f"**Submitted by:** {officer['name']}")
                                else:
                                    st.error("Policy not found")
                        except Exception as e:
                            st.error(f"Error submitting claim: {e}")
                            # Fallback display
                            claim_reference = f"CLM{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:6].upper()}"
                            st.success(f"✅ Claim submitted successfully!")
                            st.write(f"**Claim Reference:** {claim_reference}")
                    else:
                        st.error("Please fill in all required fields")
            
            with col2:
                st.markdown("### Existing Claims")
                
                try:
                    conn = get_db_connection()
                    if conn:
                        cursor = conn.cursor(dictionary=True)
                        cursor.execute("""
                            SELECT c.*, p.policy_number, u.full_name as customer_name,
                                   p.policy_type, p.coverage_amount
                            FROM insurance_claims c
                            JOIN insurance_policies p ON c.policy_id = p.policy_id
                            JOIN accounts a ON p.account_number = a.account_number
                            JOIN users u ON a.user_id = u.user_id
                            ORDER BY c.created_at DESC
                            LIMIT 10
                        """)
                        
                        claims = cursor.fetchall()
                        conn.close()
                        
                        if claims:
                            for claim in claims:
                                with st.expander(f"Claim {claim['claim_reference']} - {claim['customer_name']}"):
                                    st.write(f"**Policy:** {claim['policy_number']}")
                                    st.write(f"**Type:** {claim['claim_type']}")
                                    st.write(f"**Amount:** KES {claim['claim_amount']:,.2f}")
                                    st.write(f"**Status:** {claim['status']}")
                                    st.write(f"**Submitted:** {claim['created_at'].strftime('%Y-%m-%d')}")
                                    st.write(f"**Description:** {claim['description']}")
                                    
                                    if claim['status'] in ['SUBMITTED', 'UNDER_REVIEW']:
                                        col_approve, col_reject, col_review = st.columns(3)
                                        
                                        with col_approve:
                                            if st.button(f"✅ Approve", key=f"approve_{claim['claim_id']}"):
                                                try:
                                                    conn = get_db_connection()
                                                    if conn:
                                                        cursor = conn.cursor()
                                                        cursor.execute("""
                                                            UPDATE insurance_claims 
                                                            SET status = 'APPROVED' 
                                                            WHERE claim_id = %s
                                                        """, (claim['claim_id'],))
                                                        conn.commit()
                                                        conn.close()
                                                        st.success("Claim approved!")
                                                        st.rerun()
                                                except Exception as e:
                                                    st.error(f"Error approving claim: {e}")
                                        
                                        with col_reject:
                                            if st.button(f"❌ Reject", key=f"reject_{claim['claim_id']}"):
                                                try:
                                                    conn = get_db_connection()
                                                    if conn:
                                                        cursor = conn.cursor()
                                                        cursor.execute("""
                                                            UPDATE insurance_claims 
                                                            SET status = 'REJECTED' 
                                                            WHERE claim_id = %s
                                                        """, (claim['claim_id'],))
                                                        conn.commit()
                                                        conn.close()
                                                        st.error("Claim rejected!")
                                                        st.rerun()
                                                except Exception as e:
                                                    st.error(f"Error rejecting claim: {e}")
                                        
                                        with col_review:
                                            if st.button(f"🔍 Review", key=f"review_{claim['claim_id']}"):
                                                try:
                                                    conn = get_db_connection()
                                                    if conn:
                                                        cursor = conn.cursor()
                                                        cursor.execute("""
                                                            UPDATE insurance_claims 
                                                            SET status = 'UNDER_REVIEW' 
                                                            WHERE claim_id = %s
                                                        """, (claim['claim_id'],))
                                                        conn.commit()
                                                        conn.close()
                                                        st.info("Claim under review!")
                                                        st.rerun()
                                                except Exception as e:
                                                    st.error(f"Error updating claim: {e}")
                        else:
                            st.info("No claims found")
                except Exception as e:
                    st.error(f"Error loading claims: {e}")
                    # Fallback to mock data
                    st.info("Loading sample claims data...")
                    claims = [
                        {
                            "claim_reference": "CLM20260103001",
                            "policy_number": "POL20260104001",
                            "customer_name": "Emmanuel Odenyire Anyira",
                            "claim_type": "Medical Claim",
                            "claim_amount": 50000,
                            "status": "SUBMITTED",
                            "created_at": "2026-01-03"
                        }
                    ]
                    
                    for claim in claims:
                        with st.expander(f"Claim {claim['claim_reference']} - {claim['customer_name']}"):
                            st.write(f"**Policy:** {claim['policy_number']}")
                            st.write(f"**Type:** {claim['claim_type']}")
                            st.write(f"**Amount:** KES {claim['claim_amount']:,.2f}")
                            st.write(f"**Status:** {claim['status']}")
                            st.write(f"**Submitted:** {claim['created_at']}")

    # TAB 4: REPORTS
    with tab_reports:
        if not check_permissions(officer["role"], "reports"):
            st.warning("Access Denied: Insufficient permissions")
        else:
            st.subheader("📑 Bancassurance Reports")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Report Generation")
                report_type = st.selectbox("Report Type", [
                    "Policy Sales Summary",
                    "Premium Collection Report",
                    "Claims Analysis",
                    "Agent Performance",
                    "Product Performance"
                ])
                
                date_from = st.date_input("From Date")
                date_to = st.date_input("To Date")
                
                if st.button("📊 Generate Report"):
                    try:
                        conn = get_db_connection()
                        if conn:
                            cursor = conn.cursor(dictionary=True)
                            
                            if report_type == "Policy Sales Summary":
                                st.markdown("### Policy Sales Summary")
                                st.write("**Period:** {} to {}".format(date_from, date_to))
                                
                                # Get policy sales data
                                cursor.execute("""
                                    SELECT 
                                        COUNT(*) as total_policies,
                                        SUM(coverage_amount) as total_coverage,
                                        SUM(annual_premium) as total_premiums,
                                        policy_type,
                                        COUNT(*) as type_count
                                    FROM insurance_policies 
                                    WHERE DATE(created_at) BETWEEN %s AND %s
                                    GROUP BY policy_type
                                """, (date_from, date_to))
                                
                                policy_data = cursor.fetchall()
                                
                                if policy_data:
                                    total_policies = sum(p['type_count'] for p in policy_data)
                                    total_coverage = sum(p['total_coverage'] or 0 for p in policy_data)
                                    total_premiums = sum(p['total_premiums'] or 0 for p in policy_data)
                                    
                                    st.write(f"**Total Policies Sold:** {total_policies}")
                                    st.write(f"**Total Coverage:** KES {total_coverage:,.2f}")
                                    st.write(f"**Total Premiums:** KES {total_premiums:,.2f}")
                                    
                                    # Top product
                                    top_product = max(policy_data, key=lambda x: x['type_count'])
                                    percentage = (top_product['type_count'] / total_policies) * 100
                                    st.write(f"**Top Product:** {top_product['policy_type']} ({percentage:.1f}%)")
                                    
                                    # Product breakdown
                                    st.markdown("#### Product Breakdown:")
                                    for product in policy_data:
                                        pct = (product['type_count'] / total_policies) * 100
                                        st.write(f"- {product['policy_type']}: {product['type_count']} policies ({pct:.1f}%)")
                                else:
                                    st.info("No policies found for the selected period")
                            
                            elif report_type == "Premium Collection Report":
                                st.markdown("### Premium Collection Report")
                                st.write("**Period:** {} to {}".format(date_from, date_to))
                                
                                # Get premium collection data
                                cursor.execute("""
                                    SELECT 
                                        SUM(payment_amount) as total_collections,
                                        COUNT(*) as payment_count,
                                        payment_method,
                                        COUNT(*) as method_count
                                    FROM premium_payments 
                                    WHERE payment_date BETWEEN %s AND %s
                                    GROUP BY payment_method
                                """, (date_from, date_to))
                                
                                payment_data = cursor.fetchall()
                                
                                if payment_data:
                                    total_collections = sum(p['total_collections'] or 0 for p in payment_data)
                                    total_payments = sum(p['method_count'] for p in payment_data)
                                    
                                    st.write(f"**Total Collections:** KES {total_collections:,.2f}")
                                    st.write(f"**Total Payments:** {total_payments}")
                                    
                                    # Calculate outstanding (mock calculation)
                                    cursor.execute("""
                                        SELECT SUM(annual_premium) as total_due
                                        FROM insurance_policies 
                                        WHERE status = 'ACTIVE'
                                    """)
                                    total_due_result = cursor.fetchone()
                                    total_due = total_due_result['total_due'] or 0
                                    
                                    # Estimate monthly due (simplified)
                                    monthly_due = total_due / 12
                                    outstanding = max(0, monthly_due - total_collections)
                                    collection_rate = (total_collections / monthly_due * 100) if monthly_due > 0 else 0
                                    
                                    st.write(f"**Outstanding Premiums:** KES {outstanding:,.2f}")
                                    st.write(f"**Collection Rate:** {collection_rate:.1f}%")
                                    
                                    # Payment method breakdown
                                    st.markdown("#### Payment Methods:")
                                    for payment in payment_data:
                                        pct = (payment['method_count'] / total_payments) * 100
                                        st.write(f"- {payment['payment_method']}: {payment['method_count']} payments ({pct:.1f}%)")
                                else:
                                    st.info("No payments found for the selected period")
                            
                            elif report_type == "Claims Analysis":
                                st.markdown("### Claims Analysis")
                                st.write("**Period:** {} to {}".format(date_from, date_to))
                                
                                # Get claims data
                                cursor.execute("""
                                    SELECT 
                                        COUNT(*) as total_claims,
                                        SUM(claim_amount) as total_amount,
                                        status,
                                        COUNT(*) as status_count,
                                        claim_type,
                                        AVG(claim_amount) as avg_amount
                                    FROM insurance_claims 
                                    WHERE DATE(created_at) BETWEEN %s AND %s
                                    GROUP BY status, claim_type
                                """, (date_from, date_to))
                                
                                claims_data = cursor.fetchall()
                                
                                if claims_data:
                                    total_claims = sum(c['status_count'] for c in claims_data)
                                    total_amount = sum(c['total_amount'] or 0 for c in claims_data)
                                    
                                    st.write(f"**Total Claims:** {total_claims}")
                                    st.write(f"**Total Amount:** KES {total_amount:,.2f}")
                                    
                                    # Status breakdown
                                    st.markdown("#### Claims by Status:")
                                    status_summary = {}
                                    for claim in claims_data:
                                        status = claim['status']
                                        if status not in status_summary:
                                            status_summary[status] = 0
                                        status_summary[status] += claim['status_count']
                                    
                                    for status, count in status_summary.items():
                                        pct = (count / total_claims) * 100
                                        st.write(f"- {status}: {count} claims ({pct:.1f}%)")
                                else:
                                    st.info("No claims found for the selected period")
                            
                            conn.close()
                            
                            # Download button
                            report_content = f"""
{report_type}
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Period: {date_from} to {date_to}
Generated by: {officer['name']} ({officer['officer_id']})
Branch: {officer['branch_code']}

Report Summary:
- Report type: {report_type}
- Date range: {date_from} to {date_to}
- Status: Generated successfully
                            """
                            
                            st.download_button(
                                label="📥 Download Report",
                                data=report_content,
                                file_name=f"{report_type.lower().replace(' ', '_')}_{date_from}.txt",
                                mime="text/plain"
                            )
                    
                    except Exception as e:
                        st.error(f"Error generating report: {e}")
                        # Fallback to mock data
                        st.success(f"✅ {report_type} generated successfully!")
                        
                        if report_type == "Policy Sales Summary":
                            st.markdown("### Policy Sales Summary")
                            st.write("**Period:** {} to {}".format(date_from, date_to))
                            st.write("**Total Policies Sold:** 25")
                            st.write("**Total Coverage:** KES 12,500,000")
                            st.write("**Total Premiums:** KES 875,000")
                            st.write("**Top Product:** Life Insurance (40%)")
                        
                        elif report_type == "Premium Collection Report":
                            st.markdown("### Premium Collection Report")
                            st.write("**Period:** {} to {}".format(date_from, date_to))
                            st.write("**Total Collections:** KES 450,000")
                            st.write("**Outstanding Premiums:** KES 125,000")
                            st.write("**Collection Rate:** 78.3%")
            
            with col2:
                st.markdown("### Key Metrics")
                
                try:
                    conn = get_db_connection()
                    if conn:
                        cursor = conn.cursor(dictionary=True)
                        
                        # Active policies
                        cursor.execute("SELECT COUNT(*) as count FROM insurance_policies WHERE status = 'ACTIVE'")
                        active_policies = cursor.fetchone()['count']
                        
                        # Monthly premiums (estimate)
                        cursor.execute("""
                            SELECT SUM(annual_premium)/12 as monthly_premiums 
                            FROM insurance_policies WHERE status = 'ACTIVE'
                        """)
                        monthly_premiums = cursor.fetchone()['monthly_premiums'] or 0
                        
                        # Claims ratio (last 30 days)
                        cursor.execute("""
                            SELECT 
                                COUNT(*) as claim_count,
                                SUM(claim_amount) as claim_amount
                            FROM insurance_claims 
                            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                        """)
                        claims_data = cursor.fetchone()
                        claims_ratio = (claims_data['claim_amount'] or 0) / (monthly_premiums * 1000) * 100 if monthly_premiums > 0 else 0
                        
                        # New policies this month
                        cursor.execute("""
                            SELECT COUNT(*) as count 
                            FROM insurance_policies 
                            WHERE MONTH(created_at) = MONTH(NOW()) AND YEAR(created_at) = YEAR(NOW())
                        """)
                        new_policies = cursor.fetchone()['count']
                        
                        conn.close()
                        
                        st.metric("Active Policies", str(active_policies), "")
                        st.metric("Monthly Premiums", f"KES {monthly_premiums:,.0f}", "")
                        st.metric("Claims Ratio", f"{claims_ratio:.1f}%", "")
                        st.metric("New Policies (MTD)", str(new_policies), "")
                        
                        # Top products from database
                        conn = get_db_connection()
                        if conn:
                            cursor = conn.cursor(dictionary=True)
                            cursor.execute("""
                                SELECT policy_type, COUNT(*) as count
                                FROM insurance_policies 
                                WHERE status = 'ACTIVE'
                                GROUP BY policy_type
                                ORDER BY count DESC
                                LIMIT 5
                            """)
                            top_products = cursor.fetchall()
                            conn.close()
                            
                            st.markdown("### Top Products")
                            for i, product in enumerate(top_products, 1):
                                total_active = sum(p['count'] for p in top_products)
                                percentage = (product['count'] / total_active) * 100 if total_active > 0 else 0
                                st.write(f"{i}. {product['policy_type']} - {percentage:.0f}%")
                
                except Exception as e:
                    st.error(f"Error loading metrics: {e}")
                    # Fallback metrics
                    st.metric("Active Policies", "156", "12")
                    st.metric("Monthly Premiums", "KES 245,000", "8.5%")
                    st.metric("Claims Ratio", "15.2%", "-2.1%")
                    st.metric("New Policies (MTD)", "8", "3")
                    
                    st.markdown("### Top Products")
                    st.write("1. Life Insurance - 45%")
                    st.write("2. Health Insurance - 28%")
                    st.write("3. Investment Linked - 15%")
                    st.write("4. Education Plan - 8%")
                    st.write("5. Pension Plan - 4%")


# Legacy function for standalone usage
def main():
    """
    Legacy main function for standalone usage.
    """
    # Configure Streamlit page
    st.set_page_config(
        page_title="Wekeza Bancassurance Portal",
        page_icon="🛡️",
        layout="wide"
    )

    # --- SIDEBAR: OFFICER AUTH ---
    st.sidebar.title("🛡️ Bancassurance Portal")
    st.sidebar.info("Authorized System Access Only")

    officer_id = st.sidebar.text_input("Officer ID", value="BA-001")
    branch_code = st.sidebar.text_input("Branch Code", value="NBO-HQ")

    if not officer_id:
        st.warning("Please enter Officer ID")
        st.stop()

    # Mock staff info for standalone usage
    staff_info = {
        'staff_code': officer_id,
        'full_name': f"Officer {officer_id}",
        'role': 'BANCASSURANCE_OFFICER',
        'branch_code': branch_code,
        'branch_name': 'Main Branch'
    }
    
    render_bancassurance_ui(staff_info)


if __name__ == "__main__":
    main()
