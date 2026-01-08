import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime, timedelta
import uuid

st.set_page_config(page_title="Wekeza Corporate", layout="wide", page_icon="🏢")

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

if 'biz_user_data' not in st.session_state: 
    st.session_state['biz_user_data'] = None

def login_register_screen():
    st.title("🏢 Corporate Banking")
    
    tab1, tab2, tab3 = st.tabs(["Login", "Register Business", "Admin"])
    
    with tab1:
        st.subheader("Director Login")
        email = st.text_input("Director Email", key="biz_login_email")
        password = st.text_input("Password", type="password", key="biz_login_password")
        
        if st.button("Login", key="biz_login_btn"):
            if email and password:
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor(dictionary=True)
                    
                    # Check user credentials (must be business user)
                    cursor.execute("""
                        SELECT user_id, full_name, email, business_id 
                        FROM users 
                        WHERE email = %s AND password_hash = %s AND is_active = 1 AND business_id IS NOT NULL
                    """, (email, password))
                    
                    user = cursor.fetchone()
                    conn.close()
                    
                    if user:
                        st.session_state['biz_user_data'] = user
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials or not a business account")
                        
                except Exception as e:
                    st.error(f"Login failed: {e}")
    
    with tab2:
        st.subheader("Register New Business")
        
        with st.form("register_business_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                biz_name = st.text_input("Business Name *")
                reg_no = st.text_input("Registration Number *")
                kra_pin = st.text_input("KRA PIN *")
                sector = st.selectbox("Sector", ["Technology", "Agriculture", "Retail", "Manufacturing", "Services"])
            
            with col2:
                dir_name = st.text_input("Director Name *")
                dir_email = st.text_input("Director Email *")
                dir_password = st.text_input("Director Password *", type="password")
                dir_confirm = st.text_input("Confirm Password *", type="password")
            
            submitted = st.form_submit_button("Register Business", type="primary")
            
            if submitted and all([biz_name, reg_no, kra_pin, dir_name, dir_email, dir_password]):
                if dir_password != dir_confirm:
                    st.error("Passwords don't match!")
                else:
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        
                        # Check if business already exists
                        cursor.execute("SELECT registration_no FROM businesses WHERE registration_no = %s", (reg_no,))
                        if cursor.fetchone():
                            st.error("Business already registered! Please visit a branch for assistance.")
                        else:
                            # Create business
                            cursor.execute("""
                                INSERT INTO businesses (business_name, registration_no, kra_pin, sector, created_at)
                                VALUES (%s, %s, %s, %s, %s)
                            """, (biz_name, reg_no, kra_pin, sector, datetime.now()))
                            
                            business_id = cursor.lastrowid
                            
                            # Create director user
                            cursor.execute("""
                                INSERT INTO users (full_name, email, phone_number, national_id, password_hash, kyc_tier, is_active, business_id, created_at)
                                VALUES (%s, %s, %s, %s, %s, %s, 1, %s, %s)
                            """, (dir_name, dir_email, '0700000000', f"DIR{reg_no}", dir_password, 'TIER_3', business_id, datetime.now()))
                            
                            # Create business account
                            account_number = f"BIZ{1000000 + business_id}"
                            cursor.execute("""
                                INSERT INTO accounts (business_id, account_number, balance, currency, status, created_at)
                                VALUES (%s, %s, 50000.00, 'KES', 'ACTIVE', %s)
                            """, (business_id, account_number, datetime.now()))
                            
                            conn.commit()
                            conn.close()
                            
                            st.success(f"✅ Business registered successfully!")
                            st.info(f"🏢 Business: {biz_name}")
                            st.info(f"🏦 Account: {account_number}")
                            st.info(f"💰 Initial Balance: KES 50,000")
                            st.info(f"🔑 Director login: {dir_email}")
                            
                    except Exception as e:
                        st.error(f"Registration failed: {e}")
    
    with tab3:
        st.subheader("Admin Access")
        admin_user = st.text_input("Username", value="admin", key="biz_admin_user")
        admin_pass = st.text_input("Password", type="password", value="admin", key="biz_admin_pass")
        
        if st.button("Admin Login", key="biz_admin_btn"):
            if admin_user == "admin" and admin_pass == "admin":
                st.session_state['biz_user_data'] = {
                    'user_id': 0,
                    'full_name': 'Administrator',
                    'email': 'admin',
                    'is_admin': True
                }
                st.success("Admin login successful!")
                st.rerun()
            else:
                st.error("Invalid admin credentials")

def dashboard():
    user_data = st.session_state['biz_user_data']
    
    # Admin dashboard
    if user_data.get('is_admin'):
        st.title("🔧 Admin Quick Access")
        st.info("For full admin features, visit: http://localhost:8503")
        
        if st.button("Logout"): 
            st.session_state['biz_user_data'] = None
            st.rerun()
        return
    
    # Business dashboard
    st.sidebar.title("🏢 Corporate Banking")
    st.sidebar.success("KYC Verified")
    
    user_id = user_data['user_id']
    business_id = user_data['business_id']
    
    # Fetch business account data
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get business account
        cursor.execute("""
            SELECT a.account_number, a.balance, a.status, b.business_name
            FROM accounts a
            JOIN businesses b ON a.business_id = b.business_id
            WHERE a.business_id = %s
        """, (business_id,))
        
        account_data = cursor.fetchone()
        conn.close()
        
        if not account_data:
            st.error("Business account not found")
            return
            
    except Exception as e:
        st.error(f"Database error: {e}")
        return
    
    st.title("Corporate Command Center")
    
    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Operating Account", f"KES {account_data['balance']:,.2f}")
    c2.metric("Account Status", account_data['status'])
    c3.metric("Director", user_data['full_name'])

    # BIMS Tabs
    tab_borrow, tab_insure, tab_move, tab_admin = st.tabs(["📉 SME Finance", "🛡️ Insure", "💸 Bulk Payments", "⚙️ Admin"])

    with tab_borrow:
        st.subheader("Working Capital Request")
        st.info("SME loan features coming soon...")

    with tab_insure:
        st.subheader("🛡️ Business Insurance")
        
        # Get available insurance products suitable for businesses
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT * FROM insurance_products WHERE is_active = 1 ORDER BY product_id")
            insurance_products = cursor.fetchall()
            
            # Get business's existing policies
            cursor.execute("""
                SELECT up.*, ip.product_name, ip.product_code, ip.description
                FROM user_policies up
                JOIN insurance_products ip ON up.product_id = ip.product_id
                WHERE up.business_id = %s
                ORDER BY up.created_at DESC
            """, (business_id,))
            
            business_policies = cursor.fetchall()
            conn.close()
            
        except Exception as e:
            st.error(f"Error fetching insurance data: {e}")
            insurance_products = []
            business_policies = []
        
        # Business insurance tabs
        biz_ins_tab1, biz_ins_tab2, biz_ins_tab3 = st.tabs(["Business Plans", "Our Policies", "Premium Calculator"])
        
        with biz_ins_tab1:
            st.markdown("### 🏢 Business Insurance Plans")
            
            if insurance_products:
                for product in insurance_products:
                    # Show business-relevant insurance
                    if product['product_code'] in ['CLP-001', 'DAP-001', 'HMC-001']:  # Credit Life, Device Protection, Health for employees
                        with st.expander(f"🛡️ {product['product_name']} - KES {product['premium_amount']}/month"):
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                st.write(f"**Product Code:** {product['product_code']}")
                                st.write(f"**Description:** {product['description']}")
                                st.write(f"**Coverage Amount:** KES {float(product['cover_amount']):,.2f}")
                                st.write(f"**Premium:** KES {float(product['premium_amount'])}/month")
                                
                                # Check if business already has this policy
                                has_policy = any(p['product_id'] == product['product_id'] and p['status'] == 'ACTIVE' 
                                               for p in business_policies)
                                
                                if has_policy:
                                    st.success("✅ Your business already has this policy")
                                else:
                                    # Business-specific purchase form
                                    with st.form(f"biz_purchase_{product['product_id']}"):
                                        st.markdown("**Business Coverage Options:**")
                                        
                                        # For businesses, offer higher coverage tiers
                                        if product['product_code'] == 'CLP-001':  # Credit Life for business loans
                                            coverage_options = [
                                                (float(product['cover_amount']), "Standard Business Coverage"),
                                                (float(product['cover_amount']) * 2, "Enhanced Business Coverage"),
                                                (float(product['cover_amount']) * 5, "Enterprise Coverage")
                                            ]
                                        elif product['product_code'] == 'HMC-001':  # Group health for employees
                                            num_employees = st.number_input("Number of Employees", min_value=1, max_value=100, value=5)
                                            coverage_options = [
                                                (float(product['cover_amount']) * num_employees * 0.5, f"Basic Group Health ({num_employees} employees)"),
                                                (float(product['cover_amount']) * num_employees, f"Standard Group Health ({num_employees} employees)"),
                                                (float(product['cover_amount']) * num_employees * 1.5, f"Premium Group Health ({num_employees} employees)")
                                            ]
                                        else:  # Device protection for business assets
                                            coverage_options = [
                                                (float(product['cover_amount']) * 2, "Business Assets Coverage"),
                                                (float(product['cover_amount']) * 5, "Extended Business Assets"),
                                                (float(product['cover_amount']) * 10, "Comprehensive Business Protection")
                                            ]
                                        
                                        selected_coverage = st.selectbox(
                                            "Coverage Level",
                                            coverage_options,
                                            format_func=lambda x: f"{x[1]} - KES {x[0]:,.2f}",
                                            key=f"biz_coverage_{product['product_id']}"
                                        )
                                        
                                        # Calculate business premium
                                        coverage_multiplier = selected_coverage[0] / float(product['cover_amount'])
                                        adjusted_premium = float(product['premium_amount']) * coverage_multiplier
                                        
                                        # Business-specific options
                                        auto_renew = st.checkbox("Enable Auto-Renewal", value=True, key=f"biz_auto_{product['product_id']}")
                                        
                                        st.info(f"💰 Monthly Premium: KES {adjusted_premium:.2f}")
                                        
                                        submitted = st.form_submit_button("Purchase Business Policy", type="primary")
                                        
                                        if submitted:
                                            purchase_business_insurance_policy(
                                                business_id, product['product_id'], selected_coverage[0], 
                                                adjusted_premium, auto_renew
                                            )
                            
                            with col2:
                                # Business-specific benefits
                                st.markdown("**Business Benefits:**")
                                if product['product_code'] == 'CLP-001':
                                    st.write("• Business loan protection")
                                    st.write("• Key person insurance")
                                    st.write("• Business continuity")
                                    st.write("• Creditor protection")
                                elif product['product_code'] == 'HMC-001':
                                    st.write("• Employee health coverage")
                                    st.write("• Group medical benefits")
                                    st.write("• Workplace wellness")
                                    st.write("• Productivity protection")
                                elif product['product_code'] == 'DAP-001':
                                    st.write("• Business equipment cover")
                                    st.write("• IT infrastructure protection")
                                    st.write("• Business interruption")
                                    st.write("• Cyber security coverage")
            else:
                st.info("No business insurance products available at the moment.")
        
        with biz_ins_tab2:
            st.markdown("### 📋 Our Business Policies")
            
            if business_policies:
                # Business policy summary
                active_policies = [p for p in business_policies if p['status'] == 'ACTIVE']
                total_coverage = sum(float(p['cover_amount']) for p in active_policies)
                total_premiums = sum(float(p['premium_paid']) for p in active_policies)
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Active Policies", len(active_policies))
                col2.metric("Total Coverage", f"KES {total_coverage:,.2f}")
                col3.metric("Monthly Premiums", f"KES {total_premiums:,.2f}")
                
                st.markdown("---")
                
                # Display business policies
                for policy in business_policies:
                    status_color = "🟢" if policy['status'] == 'ACTIVE' else "🔴" if policy['status'] == 'EXPIRED' else "🟡"
                    
                    with st.expander(f"{status_color} {policy['product_name']} - {policy['policy_number']}"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write("**Policy Details**")
                            st.write(f"Policy Number: {policy['policy_number']}")
                            st.write(f"Product: {policy['product_name']}")
                            st.write(f"Status: {policy['status']}")
                            st.write(f"Coverage: KES {policy['cover_amount']:,.2f}")
                        
                        with col2:
                            st.write("**Dates & Payments**")
                            if policy['start_date']:
                                st.write(f"Start Date: {policy['start_date']}")
                            if policy['end_date']:
                                st.write(f"End Date: {policy['end_date']}")
                            st.write(f"Premium Paid: KES {policy['premium_paid']:,.2f}")
                            st.write(f"Auto-Renew: {'Yes' if policy['auto_renew'] else 'No'}")
                        
                        with col3:
                            st.write("**Actions**")
                            if policy['status'] == 'ACTIVE':
                                if st.button(f"File Business Claim", key=f"biz_claim_{policy['policy_id']}"):
                                    st.session_state[f'biz_claim_policy_{policy["policy_id"]}'] = True
                                
                                if st.button(f"Cancel Policy", key=f"biz_cancel_{policy['policy_id']}"):
                                    cancel_business_insurance_policy(policy['policy_id'])
                                
                                # Business claim form
                                if st.session_state.get(f'biz_claim_policy_{policy["policy_id"]}', False):
                                    with st.form(f"biz_claim_form_{policy['policy_id']}"):
                                        st.markdown("**File Business Insurance Claim**")
                                        claim_type = st.selectbox("Business Claim Type", [
                                            "Business Interruption", "Equipment Damage", "Cyber Attack",
                                            "Employee Injury", "Key Person Loss", "Professional Liability",
                                            "Property Damage", "Business Theft"
                                        ])
                                        claim_amount = st.number_input("Claim Amount (KES)", min_value=1000.0, max_value=float(policy['cover_amount']))
                                        claim_description = st.text_area("Business Incident Description")
                                        
                                        if st.form_submit_button("Submit Business Claim"):
                                            file_business_insurance_claim(business_id, policy['policy_id'], claim_type, claim_amount, claim_description)
                                            st.session_state[f'biz_claim_policy_{policy["policy_id"]}'] = False
                                            st.rerun()
                            else:
                                st.info(f"Policy is {policy['status']}")
            else:
                st.info("📝 No business insurance policies found. Purchase your first business policy above!")
        
        with biz_ins_tab3:
            st.markdown("### 🧮 Business Insurance Calculator")
            st.write("Calculate insurance needs for your business")
            
            calc_col1, calc_col2 = st.columns(2)
            
            with calc_col1:
                st.markdown("**Business Risk Assessment**")
                
                # Business-specific calculations
                annual_revenue = st.number_input("Annual Revenue (KES)", min_value=0.0, value=5000000.0)
                num_employees = st.number_input("Number of Employees", min_value=1, max_value=1000, value=10)
                business_assets = st.number_input("Business Assets Value (KES)", min_value=0.0, value=2000000.0)
                outstanding_loans = st.number_input("Outstanding Business Loans (KES)", min_value=0.0, value=1000000.0)
                
                # Calculate recommended business coverage
                revenue_protection = annual_revenue * 0.25  # 3 months revenue protection
                employee_coverage = num_employees * 1000000  # 1M per employee
                asset_protection = business_assets * 1.2  # 120% of asset value
                loan_protection = outstanding_loans * 1.1  # 110% of loan amount
                
                st.markdown("**Recommended Business Coverage:**")
                st.write(f"• Business Interruption: KES {revenue_protection:,.2f}")
                st.write(f"• Employee Group Health: KES {employee_coverage:,.2f}")
                st.write(f"• Asset Protection: KES {asset_protection:,.2f}")
                st.write(f"• Loan Protection: KES {loan_protection:,.2f}")
            
            with calc_col2:
                st.markdown("**Premium Estimates**")
                
                if insurance_products:
                    # Business premium calculations
                    total_monthly_premium = 0
                    
                    for product in insurance_products:
                        if product['product_code'] in ['CLP-001', 'DAP-001', 'HMC-001']:
                            if product['product_code'] == 'CLP-001':
                                business_multiplier = outstanding_loans / 1000000  # Scale with loan amount
                            elif product['product_code'] == 'HMC-001':
                                business_multiplier = num_employees  # Scale with employees
                            else:
                                business_multiplier = business_assets / 1000000  # Scale with assets
                            
                            estimated_premium = float(product['premium_amount']) * max(1, business_multiplier)
                            total_monthly_premium += estimated_premium
                            
                            st.write(f"**{product['product_name']}**")
                            st.write(f"Monthly: KES {estimated_premium:,.2f}")
                            st.write(f"Annual: KES {estimated_premium * 12:,.2f}")
                            st.write("---")
                    
                    st.metric("Total Monthly Premium", f"KES {total_monthly_premium:,.2f}")
                    st.metric("Total Annual Premium", f"KES {total_monthly_premium * 12:,.2f}")
                    
                    # Affordability check
                    if annual_revenue > 0:
                        premium_percentage = (total_monthly_premium * 12 / annual_revenue) * 100
                        if premium_percentage <= 2:
                            st.success(f"✅ Affordable ({premium_percentage:.1f}% of revenue)")
                        elif premium_percentage <= 5:
                            st.warning(f"⚠️ Moderate ({premium_percentage:.1f}% of revenue)")
                        else:
                            st.error(f"❌ High cost ({premium_percentage:.1f}% of revenue)")

def purchase_business_insurance_policy(business_id, product_id, coverage_amount, premium_amount, auto_renew):
    """Purchase a business insurance policy"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check business account balance
        cursor.execute("SELECT balance FROM accounts WHERE business_id = %s", (business_id,))
        account = cursor.fetchone()
        
        if not account or account['balance'] < premium_amount:
            st.error(f"Insufficient balance! Required: KES {premium_amount:.2f}, Available: KES {account['balance']:.2f}")
            return
        
        # Generate policy number
        policy_number = f"BIZ{uuid.uuid4().hex[:8].upper()}"
        
        # Calculate dates
        start_date = datetime.now().date()
        end_date = datetime(start_date.year + 1, start_date.month, start_date.day).date()
        
        # Create business policy
        cursor.execute("""
            INSERT INTO user_policies (business_id, product_id, policy_number, start_date, end_date, 
                                     status, auto_renew, premium_paid, cover_amount, created_at)
            VALUES (%s, %s, %s, %s, %s, 'ACTIVE', %s, %s, %s, %s)
        """, (business_id, product_id, policy_number, start_date, end_date, 
              auto_renew, premium_amount, coverage_amount, datetime.now()))
        
        policy_id = cursor.lastrowid
        
        # Deduct premium from business account
        cursor.execute("UPDATE accounts SET balance = balance - %s WHERE business_id = %s", 
                      (premium_amount, business_id))
        
        # Record transaction
        ref_code = f"BINS{uuid.uuid4().hex[:8].upper()}"
        cursor.execute("""
            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
            SELECT account_id, 'INSURANCE_PREMIUM', %s, %s, %s, %s
            FROM accounts WHERE business_id = %s
        """, (premium_amount, ref_code, f"Business insurance premium for policy {policy_number}", datetime.now(), business_id))
        
        conn.commit()
        conn.close()
        
        st.success(f"🎉 Business insurance policy purchased successfully!")
        st.info(f"📋 Policy Number: {policy_number}")
        st.info(f"💰 Premium Paid: KES {premium_amount:.2f}")
        st.info(f"🛡️ Coverage: KES {coverage_amount:,.2f}")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Business policy purchase failed: {e}")

def cancel_business_insurance_policy(policy_id):
    """Cancel a business insurance policy"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE user_policies SET status = 'CANCELLED' WHERE policy_id = %s", (policy_id,))
        conn.commit()
        conn.close()
        
        st.success("✅ Business policy cancelled successfully!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Business policy cancellation failed: {e}")

def file_business_insurance_claim(business_id, policy_id, claim_type, claim_amount, description):
    """File a business insurance claim"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Generate claim reference
        claim_ref = f"BCLM{uuid.uuid4().hex[:8].upper()}"
        
        # Insert business claim
        cursor.execute("""
            INSERT INTO insurance_claims (policy_id, user_id, claim_reference, claim_type, claim_amount, 
                                        description, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, 'SUBMITTED', %s)
        """, (policy_id, business_id, claim_ref, claim_type, claim_amount, description, datetime.now()))
        
        conn.commit()
        conn.close()
        
        st.success(f"✅ Business insurance claim filed successfully!")
        st.info(f"📋 Claim Reference: {claim_ref}")
        st.info("🔄 Your business claim is under review. You will be contacted within 48 hours.")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Business claim filing failed: {e}")

    with tab_move:
        st.subheader("Bulk Transfers (Payroll/Suppliers)")
        st.info("Bulk payment features coming soon...")

    with tab_admin:
        st.subheader("Director Management")
        st.info("Director management features coming soon...")
    
    if st.sidebar.button("Logout"):
        st.session_state['biz_user_data'] = None
        st.rerun()

if st.session_state['biz_user_data']: 
    dashboard()
else: 
    login_register_screen()