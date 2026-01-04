import streamlit as st
import sys
import os
import mysql.connector
from datetime import datetime

# Add the branch_operations directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import shared modules
from shared.auth import generate_token, decode_token
from shared.permissions import ROLE_PERMISSIONS

# Configure Streamlit page
st.set_page_config(
    page_title="Wekeza Branch Operations System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# Authentication functions
def authenticate_staff(staff_code, password, branch_code):
    """Authenticate staff against database - using plain text like other portals"""
    try:
        conn = get_db_connection()
        if not conn:
            st.error("Database connection failed")
            return None
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.*, b.branch_name, b.branch_code as branch_code_db
            FROM staff s 
            JOIN branches b ON s.branch_id = b.branch_id 
            WHERE s.staff_code = %s AND s.is_active = TRUE AND b.is_active = TRUE
        """, (staff_code,))
        
        staff = cursor.fetchone()
        conn.close()
        
        if not staff:
            st.error(f"Staff {staff_code} not found or inactive")
            return None
            
        # Debug info (remove in production)
        st.info(f"Found staff: {staff['full_name']} | Role: {staff['role']} | Branch: {staff['branch_code_db']}")
        
        # Verify password (plain text like customer/business portals)
        if staff['password_hash'] != password:
            st.error(f"Invalid password for {staff_code}")
            return None
            
        # Verify branch code
        if staff['branch_code_db'] != branch_code:
            st.error(f"Branch code mismatch. Expected: {staff['branch_code_db']}, Got: {branch_code}")
            return None
            
        return staff
        
    except Exception as e:
        st.error(f"Authentication error: {e}")
        return None

def get_role_modules(role):
    """Get allowed modules for a role"""
    role_module_mapping = {
        "TELLER": ["branch_teller"],
        "RELATIONSHIP_MANAGER": ["customer_ops"],
        "SUPERVISOR": ["supervision", "branch_teller", "customer_ops", "credit_ops", "bancassurance"],
        "BRANCH_MANAGER": ["branch_management", "supervision", "branch_teller", "customer_ops", "credit_ops", "cash_office", "bancassurance"],
        "ADMIN": ["branch_management", "supervision", "branch_teller", "customer_ops", "credit_ops", "cash_office", "bancassurance"]
    }
    return role_module_mapping.get(role, [])

def get_module_display_name(module):
    """Get display name for module"""
    display_names = {
        "branch_teller": "🏧 Teller Operations",
        "customer_ops": "👥 Customer Operations", 
        "credit_ops": "💳 Credit Operations",
        "cash_office": "💰 Cash Office",
        "bancassurance": "🛡️ Bancassurance",
        "supervision": "🛡️ Supervision",
        "branch_management": "🏢 Branch Management"
    }
    return display_names.get(module, module)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79, #2e7d32);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .module-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f4e79;
        margin: 0.5rem 0;
    }
    .status-active {
        color: #28a745;
        font-weight: bold;
    }
    .status-inactive {
        color: #dc3545;
        font-weight: bold;
    }
    .login-form {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🏦 Wekeza Branch Operations System</h1>
    <p>Comprehensive Core Banking Operations Platform</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'staff_info' not in st.session_state:
    st.session_state.staff_info = None

# Authentication section
if not st.session_state.authenticated:
    st.sidebar.title("🔐 Staff Login")
    st.sidebar.markdown("---")
    
    with st.sidebar.form("login_form"):
        staff_code = st.text_input("Staff Code", placeholder="e.g., STAFF001")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        branch_code = st.text_input("Branch Code", placeholder="e.g., BR001")
        login_button = st.form_submit_button("🔑 Login")
        
        if login_button:
            if not staff_code or not password or not branch_code:
                st.error("Please fill in all fields")
            else:
                staff = authenticate_staff(staff_code, password, branch_code)
                if staff:
                    st.session_state.authenticated = True
                    st.session_state.staff_info = staff
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials or inactive account")
    
    # Show login instructions
    st.markdown("""
    ### 🔐 Login Instructions
    
    Please enter your staff credentials to access the branch operations system.
    
    **Available Test Accounts:**
    - Staff Code: `TELLER001` | Password: `teller123` | Branch: `BR001`
    - Staff Code: `SUP001` | Password: `supervisor123` | Branch: `BR001`
    - Staff Code: `ADMIN001` | Password: `admin` | Branch: `HQ001`
    - Staff Code: `EG-74255` | Password: `password123` | Branch: `BR001`
    
    Contact your system administrator if you need assistance.
    """)
    st.stop()

# User is authenticated - show main interface
staff = st.session_state.staff_info
st.sidebar.title("🏦 Branch Operations")
st.sidebar.markdown("---")

# Display user info
st.sidebar.markdown(f"""
**👤 Staff:** {staff['full_name']}  
**🆔 Code:** {staff['staff_code']}  
**🏢 Role:** {staff['role']}  
**🏦 Branch:** {staff['branch_name']}
""")

# Logout button
if st.sidebar.button("🚪 Logout"):
    st.session_state.authenticated = False
    st.session_state.staff_info = None
    st.rerun()

st.sidebar.markdown("---")

# Get allowed modules for user's role
allowed_modules = get_role_modules(staff['role'])

if not allowed_modules:
    st.error(f"No modules available for role: {staff['role']}")
    st.stop()

# Module selection based on role
st.sidebar.subheader("📋 Available Modules")
module_options = [get_module_display_name(module) for module in allowed_modules]
selected_display = st.sidebar.radio("Choose Operation:", module_options)

# Get the actual module name from display name
selected_module = None
for module in allowed_modules:
    if get_module_display_name(module) == selected_display:
        selected_module = module
        break
# Main content area - Load selected module
st.markdown("---")

if selected_module:
    # Store staff info in session for modules to access
    st.session_state.current_staff = {
        'staff_code': staff['staff_code'],
        'full_name': staff['full_name'],
        'role': staff['role'],
        'branch_code': staff['branch_code_db'],
        'branch_name': staff['branch_name'],
        'staff_id': staff['staff_id'],
        'branch_id': staff['branch_id']
    }
    
    # Load the selected module
    if selected_module == "branch_teller":
        st.header("🏧 Teller Operations System")
        st.info("💸 Cash transactions and customer service operations")
        
        try:
            # Import and run the teller app
            import importlib.util
            spec = importlib.util.spec_from_file_location("teller_app", 
                os.path.join(os.path.dirname(__file__), "branch_teller", "app.py"))
            teller_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(teller_module)
        except Exception as e:
            st.error(f"Error loading Teller module: {e}")
            st.markdown("""
            ### Teller Operations Features:
            - **Cash Deposits**: Customer cash deposit processing
            - **Cash Withdrawals**: Account withdrawal transactions  
            - **Balance Enquiry**: Real-time account balance checks
            - **Mini Statements**: Transaction history printing
            - **Fund Transfers**: Internal and external transfers
            - **Bill Payments**: Utility and service bill processing
            """)
    
    elif selected_module == "customer_ops":
        st.header("👥 Customer Operations System")
        st.info("🔧 Complete customer lifecycle management and account services")
        
        try:
            from customer_ops.app import render_customer_ops_ui
            render_customer_ops_ui(st.session_state.current_staff)
        except Exception as e:
            st.error(f"Error loading Customer Operations module: {e}")
            st.markdown("""
            ### Customer Operations Features:
            - **CIF Creation**: Customer information file setup
            - **Account Opening**: New account creation and setup
            - **Account Maintenance**: Account updates and modifications
            - **Account Closure**: Account termination processing
            - **Mandate Management**: Signatory and authorization setup
            - **Customer Enquiries**: Account information and support
            """)
    
    elif selected_module == "credit_ops":
        st.header("💳 Credit Operations System")
        st.info("📋 Loan processing and credit risk management")
        
        try:
            from credit_ops.app import render_credit_ops_ui
            render_credit_ops_ui(st.session_state.current_staff)
        except Exception as e:
            st.error(f"Error loading Credit Operations module: {e}")
            st.markdown("""
            ### Credit Operations Features:
            - **Loan Origination**: New loan application processing
            - **Credit Assessment**: Risk evaluation and scoring
            - **Loan Approval**: Credit committee and approval workflows
            - **Disbursement**: Loan fund release and documentation
            - **Collections**: Overdue loan management and recovery
            - **Portfolio Management**: Loan portfolio monitoring
            """)
        except Exception as e:
            st.error(f"Error loading Credit Operations module: {e}")
            st.markdown("""
            ### Credit Operations Features:
            - **Loan Origination**: New loan application processing
            - **Credit Assessment**: Risk evaluation and scoring
            - **Loan Approval**: Credit committee and approval workflows
            - **Disbursement**: Loan fund release and documentation
            - **Collections**: Overdue loan management and recovery
            - **Portfolio Management**: Loan portfolio monitoring
            """)
    
    elif selected_module == "cash_office":
        st.header("💰 Cash Office System")
        st.info("🏛️ Branch cash management and vault operations")
        
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("cash_office_app", 
                os.path.join(os.path.dirname(__file__), "cash_office", "app.py"))
            cash_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cash_module)
        except Exception as e:
            st.error(f"Error loading Cash Office module: {e}")
            st.markdown("""
            ### Cash Office Features:
            - **Vault Management**: Cash inventory and security
            - **Teller Cash**: Cash allocation and reconciliation
            - **ATM Management**: ATM cash loading and monitoring
            - **Currency Exchange**: Foreign exchange operations
            - **Cash Ordering**: Head office cash requests
            - **Audit Trail**: Complete cash movement tracking
            """)
    
    elif selected_module == "bancassurance":
        st.header("🛡️ Bancassurance System")
        st.info("🏥 Insurance products and policy management")
        
        try:
            from bancassurance.app import render_bancassurance_ui
            render_bancassurance_ui(st.session_state.current_staff)
        except Exception as e:
            st.error(f"Error loading Bancassurance module: {e}")
            st.markdown("""
            ### Bancassurance Features:
            - **Product Catalog**: Available insurance products
            - **Policy Sales**: New policy origination and sales
            - **Premium Collection**: Insurance premium processing
            - **Claims Processing**: Insurance claim management
            - **Policy Servicing**: Policy updates and maintenance
            - **Commission Tracking**: Agent commission management
            """)
    
    elif selected_module == "supervision":
        st.header("🛡️ Supervision System")
        st.info("🔍 Compliance monitoring and audit management")
        
        try:
            from supervision.app import render_supervision_ui
            render_supervision_ui(st.session_state.current_staff)
        except Exception as e:
            st.error(f"Error loading Supervision module: {e}")
            st.markdown("""
            ### Supervision Features:
            - **Transaction Monitoring**: Real-time transaction oversight
            - **Compliance Checks**: Regulatory compliance monitoring
            - **Audit Management**: Internal and external audit support
            - **Risk Assessment**: Operational risk evaluation
            - **Exception Handling**: Transaction exception management
            - **Reporting**: Supervisory reports and analytics
            """)
    
    elif selected_module == "branch_management":
        st.header("🏢 Branch Management System")
        st.info("📊 Comprehensive branch performance monitoring and staff management")
        
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("branch_mgmt_app", 
                os.path.join(os.path.dirname(__file__), "branch_management", "app.py"))
            branch_mgmt_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(branch_mgmt_module)
        except Exception as e:
            st.error(f"Error loading Branch Management module: {e}")
            st.markdown("""
            ### Branch Management Features:
            - **Performance Dashboard**: Branch KPIs and metrics
            - **Staff Management**: Employee administration
            - **Cash Position**: Branch liquidity monitoring
            - **Transaction Reports**: Daily operational reports
            - **Compliance Monitoring**: Regulatory oversight
            - **Customer Analytics**: Customer behavior insights
            """)

# System status sidebar
with st.sidebar:
    st.markdown("---")
    st.markdown("### 📊 System Status")
    
    # Mock system status
    st.markdown("""
    **🟢 Core Banking:** Online  
    **🟢 Database:** Connected  
    **🟢 Network:** Stable  
    **🟡 Backup:** In Progress
    """)
    
    st.markdown("### 📈 Quick Stats")
    st.metric("Active Sessions", "24")
    st.metric("Today's Transactions", "1,247")
    st.metric("Branch Balance", "KES 2.4M")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <strong>Wekeza Bank DFS System</strong> | Branch Operations Platform<br>
    <small>Role-Based Access Control | Version 2.0 | 2026</small>
</div>
""", unsafe_allow_html=True)