"""
Agent Portal - Web interface for agency banking operations
Replaces the traditional branch teller interface with agent-focused UI
"""

import streamlit as st
import sys
import os
from datetime import datetime, timedelta
import json
from decimal import Decimal

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agents'))

from agency_gateway import AgencyGateway
from agent_management import AgentManager

# Initialize components
gateway = AgencyGateway()
agent_manager = AgentManager()

# Page configuration
st.set_page_config(
    page_title="Wekeza Agency Banking",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for agency banking theme
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .agent-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2a5298;
        margin-bottom: 1rem;
    }
    .transaction-success {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .transaction-error {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def authenticate_agent():
    """Handle agent authentication"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.markdown('<div class="main-header"><h1>🏪 Wekeza Agency Banking</h1><p>Secure Agent Portal</p></div>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                st.subheader("Agent Login")
                agent_id = st.text_input("Agent ID", placeholder="AG20240101ABCDEF")
                device_id = st.text_input("Device ID", placeholder="POS001 or MOBILE001")
                pin = st.text_input("PIN", type="password", placeholder="Enter your 4-digit PIN")
                
                # Optional location (for geo-fencing)
                with st.expander("📍 Location Verification (Optional)"):
                    col_lat, col_lng = st.columns(2)
                    with col_lat:
                        latitude = st.number_input("Latitude", value=0.0, format="%.6f")
                    with col_lng:
                        longitude = st.number_input("Longitude", value=0.0, format="%.6f")
                
                submitted = st.form_submit_button("🔐 Login", type="primary", use_container_width=True)
                
                if submitted:
                    if agent_id and device_id and pin:
                        location = None
                        if latitude != 0.0 and longitude != 0.0:
                            location = {"lat": latitude, "lng": longitude}
                        
                        # Authenticate with gateway
                        auth_result = gateway.authenticate_agent(
                            agent_id=agent_id,
                            device_id=device_id,
                            pin=pin,
                            location=location
                        )
                        
                        if auth_result['success']:
                            st.session_state.authenticated = True
                            st.session_state.session_token = auth_result['session_token']
                            st.session_state.agent_info = auth_result['agent_info']
                            st.session_state.device_id = device_id
                            st.success("✅ Authentication successful!")
                            st.rerun()
                        else:
                            st.error(f"❌ Authentication failed: {auth_result['error']}")
                    else:
                        st.error("Please fill in all required fields")
        
        return False
    
    return True

def show_agent_dashboard():
    """Display agent dashboard with key metrics"""
    agent_info = st.session_state.agent_info
    
    # Header
    st.markdown(f"""
    <div class="main-header">
        <h1>🏪 {agent_info['agent_name']}</h1>
        <p>Agent ID: {agent_info['agent_id']} | Type: {agent_info['agent_type']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Agent metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>💰 Float Balance</h3>
            <h2>KES {agent_info['float_balance']:,.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📊 Daily Limit</h3>
            <h2>KES {agent_info['daily_limit']:,.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>💳 Transaction Limit</h3>
            <h2>KES {agent_info['transaction_limit']:,.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Get today's performance
        performance = agent_manager.get_agent_performance(agent_info['agent_id'], 1)
        today_transactions = performance.get('summary', {}).get('total_transactions', 0) if performance['success'] else 0
        
        st.markdown(f"""
        <div class="metric-card">
            <h3>📈 Today's Transactions</h3>
            <h2>{today_transactions}</h2>
        </div>
        """, unsafe_allow_html=True)

def process_cash_in():
    """Handle cash in (deposit) transactions"""
    st.subheader("💰 Cash In (Customer Deposit)")
    
    with st.form("cash_in_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            customer_account = st.text_input("Customer Account Number", placeholder="ACC1000001")
            amount = st.number_input("Deposit Amount (KES)", min_value=100.0, step=100.0)
            narration = st.text_area("Narration", value="Cash deposit via agent", placeholder="Transaction description")
        
        with col2:
            st.info("**Cash In Process:**")
            st.write("1. Customer gives cash to agent")
            st.write("2. Agent credits customer account")
            st.write("3. Agent float is debited")
            st.write("4. Commission is earned")
            
            st.warning("**Requirements:**")
            st.write("- Sufficient agent float balance")
            st.write("- Valid customer account")
            st.write("- Minimum KES 100")
        
        submitted = st.form_submit_button("💰 Process Cash In", type="primary")
        
        if submitted:
            if customer_account and amount >= 100:
                # Prepare transaction data
                txn_data = {
                    'transaction_type': 'CASH_IN',
                    'customer_account': customer_account,
                    'amount': amount,
                    'narration': narration,
                    'device_id': st.session_state.device_id,
                    'ip_address': '127.0.0.1'  # In real implementation, get actual IP
                }
                
                # Process transaction
                result = gateway.process_transaction(
                    st.session_state.session_token,
                    txn_data
                )
                
                if result['success']:
                    st.markdown(f"""
                    <div class="transaction-success">
                        <h4>✅ Cash In Successful!</h4>
                        <p><strong>Transaction Reference:</strong> {result['transaction_ref']}</p>
                        <p><strong>Customer Balance:</strong> KES {result['customer_balance']:,.2f}</p>
                        <p><strong>Your Float Balance:</strong> KES {result['agent_balance']:,.2f}</p>
                        <p><strong>Commission Earned:</strong> KES {result['commission']:,.2f}</p>
                        <p><strong>Time:</strong> {result['timestamp']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Update session agent info
                    st.session_state.agent_info['float_balance'] = result['agent_balance']
                    
                else:
                    st.markdown(f"""
                    <div class="transaction-error">
                        <h4>❌ Transaction Failed</h4>
                        <p>{result['error']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("Please enter valid account number and amount (minimum KES 100)")

def process_cash_out():
    """Handle cash out (withdrawal) transactions"""
    st.subheader("💸 Cash Out (Customer Withdrawal)")
    
    with st.form("cash_out_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            customer_account = st.text_input("Customer Account Number", placeholder="ACC1000001")
            amount = st.number_input("Withdrawal Amount (KES)", min_value=100.0, step=100.0)
            narration = st.text_area("Narration", value="Cash withdrawal via agent", placeholder="Transaction description")
        
        with col2:
            st.info("**Cash Out Process:**")
            st.write("1. Customer requests cash withdrawal")
            st.write("2. Agent debits customer account")
            st.write("3. Agent gives cash to customer")
            st.write("4. Agent float is credited")
            
            st.warning("**Requirements:**")
            st.write("- Sufficient customer balance")
            st.write("- Within daily withdrawal limits")
            st.write("- Agent has physical cash")
        
        submitted = st.form_submit_button("💸 Process Cash Out", type="primary")
        
        if submitted:
            if customer_account and amount >= 100:
                # Prepare transaction data
                txn_data = {
                    'transaction_type': 'CASH_OUT',
                    'customer_account': customer_account,
                    'amount': amount,
                    'narration': narration,
                    'device_id': st.session_state.device_id,
                    'ip_address': '127.0.0.1'
                }
                
                # Process transaction
                result = gateway.process_transaction(
                    st.session_state.session_token,
                    txn_data
                )
                
                if result['success']:
                    st.markdown(f"""
                    <div class="transaction-success">
                        <h4>✅ Cash Out Successful!</h4>
                        <p><strong>Transaction Reference:</strong> {result['transaction_ref']}</p>
                        <p><strong>Customer Balance:</strong> KES {result['customer_balance']:,.2f}</p>
                        <p><strong>Your Float Balance:</strong> KES {result['agent_balance']:,.2f}</p>
                        <p><strong>Commission Earned:</strong> KES {result['commission']:,.2f}</p>
                        <p><strong>Time:</strong> {result['timestamp']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Update session agent info
                    st.session_state.agent_info['float_balance'] = result['agent_balance']
                    
                else:
                    st.markdown(f"""
                    <div class="transaction-error">
                        <h4>❌ Transaction Failed</h4>
                        <p>{result['error']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("Please enter valid account number and amount (minimum KES 100)")

def process_balance_inquiry():
    """Handle balance inquiry"""
    st.subheader("📊 Balance Inquiry")
    
    with st.form("balance_inquiry_form"):
        customer_account = st.text_input("Customer Account Number", placeholder="ACC1000001")
        submitted = st.form_submit_button("🔍 Check Balance", type="primary")
        
        if submitted:
            if customer_account:
                # Prepare transaction data
                txn_data = {
                    'transaction_type': 'BALANCE_INQUIRY',
                    'customer_account': customer_account,
                    'device_id': st.session_state.device_id,
                    'ip_address': '127.0.0.1'
                }
                
                # Process transaction
                result = gateway.process_transaction(
                    st.session_state.session_token,
                    txn_data
                )
                
                if result['success']:
                    st.success("✅ Balance inquiry successful!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"**Account Holder:** {result['account_holder']}")
                        st.info(f"**Account Status:** {result['account_status']}")
                    with col2:
                        st.metric("Available Balance", f"KES {result['balance']:,.2f}")
                    
                    st.caption(f"Transaction Reference: {result['transaction_ref']}")
                    
                else:
                    st.error(f"❌ Balance inquiry failed: {result['error']}")
            else:
                st.error("Please enter customer account number")

def show_agent_performance():
    """Display agent performance metrics"""
    st.subheader("📈 Performance Dashboard")
    
    # Performance period selector
    period_options = {
        "Today": 1,
        "Last 7 Days": 7,
        "Last 30 Days": 30,
        "Last 90 Days": 90
    }
    
    selected_period = st.selectbox("Select Period", list(period_options.keys()))
    period_days = period_options[selected_period]
    
    # Get performance data
    performance = agent_manager.get_agent_performance(
        st.session_state.agent_info['agent_id'], 
        period_days
    )
    
    if performance['success']:
        summary = performance['summary']
        breakdown = performance['transaction_breakdown']
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Transactions", summary['total_transactions'])
        with col2:
            st.metric("Total Volume", f"KES {summary['total_volume']:,.2f}")
        with col3:
            st.metric("Commission Earned", f"KES {summary['total_commission']:,.2f}")
        with col4:
            st.metric("Current Float", f"KES {summary['current_float']:,.2f}")
        
        # Transaction breakdown
        if breakdown:
            st.subheader("Transaction Breakdown")
            
            for txn_type, stats in breakdown.items():
                with st.expander(f"{txn_type.replace('_', ' ').title()}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Count", stats['count'])
                    with col2:
                        st.metric("Volume", f"KES {stats['volume']:,.2f}")
        
    else:
        st.error(f"Failed to load performance data: {performance['error']}")

def main():
    """Main application function"""
    
    # Authentication check
    if not authenticate_agent():
        return
    
    # Sidebar navigation
    st.sidebar.title("🏪 Agency Banking")
    st.sidebar.markdown(f"**Agent:** {st.session_state.agent_info['agent_name']}")
    st.sidebar.markdown(f"**Float:** KES {st.session_state.agent_info['float_balance']:,.2f}")
    
    # Navigation menu
    menu_options = [
        "🏠 Dashboard",
        "💰 Cash In",
        "💸 Cash Out", 
        "📊 Balance Inquiry",
        "📈 Performance",
        "🔧 Settings"
    ]
    
    selected_menu = st.sidebar.selectbox("Select Service", menu_options)
    
    # Logout button
    if st.sidebar.button("🚪 Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    # Route to appropriate function
    if selected_menu == "🏠 Dashboard":
        show_agent_dashboard()
        
        # Quick actions
        st.subheader("Quick Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💰 Cash In", use_container_width=True):
                st.session_state.selected_menu = "💰 Cash In"
                st.rerun()
        
        with col2:
            if st.button("💸 Cash Out", use_container_width=True):
                st.session_state.selected_menu = "💸 Cash Out"
                st.rerun()
        
        with col3:
            if st.button("📊 Balance Inquiry", use_container_width=True):
                st.session_state.selected_menu = "📊 Balance Inquiry"
                st.rerun()
    
    elif selected_menu == "💰 Cash In":
        process_cash_in()
    
    elif selected_menu == "💸 Cash Out":
        process_cash_out()
    
    elif selected_menu == "📊 Balance Inquiry":
        process_balance_inquiry()
    
    elif selected_menu == "📈 Performance":
        show_agent_performance()
    
    elif selected_menu == "🔧 Settings":
        st.subheader("⚙️ Agent Settings")
        st.info("Settings functionality coming soon...")
        
        # Show agent details
        agent_info = st.session_state.agent_info
        st.json({
            "Agent ID": agent_info['agent_id'],
            "Agent Name": agent_info['agent_name'],
            "Agent Type": agent_info['agent_type'],
            "Daily Limit": f"KES {agent_info['daily_limit']:,.2f}",
            "Transaction Limit": f"KES {agent_info['transaction_limit']:,.2f}",
            "Float Balance": f"KES {agent_info['float_balance']:,.2f}"
        })

if __name__ == "__main__":
    main()