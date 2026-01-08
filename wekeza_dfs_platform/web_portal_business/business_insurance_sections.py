import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime, timedelta
import uuid

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

def render_insurance_section(user_data):
    """Render the business insurance section"""
    st.subheader("🛡️ Business Insurance & Risk Management")
    
    # Insurance tabs
    ins_tab1, ins_tab2, ins_tab3, ins_tab4, ins_tab5 = st.tabs([
        "🛡️ Business Insurance Plans", "📋 My Policies", "💰 Premium Payments", "📞 File Claims", "🧮 Risk Calculator"
    ])
    
    with ins_tab1:
        render_business_insurance_plans_section(user_data)
    
    with ins_tab2:
        render_my_business_policies_section(user_data)
    
    with ins_tab3:
        render_premium_payments_section(user_data)
    
    with ins_tab4:
        render_business_claims_section(user_data)
    
    with ins_tab5:
        render_business_risk_calculator_section(user_data)

def render_business_insurance_plans_section(user_data):
    """Render business insurance plans section"""
    st.markdown("### 🛡️ Business Insurance Plans")
    
    # Business insurance categories
    insurance_categories = {
        "Property Insurance": [
            {
                "name": "Commercial Property Insurance",
                "description": "Covers business premises, equipment, and inventory",
                "coverage": "Up to KES 100M",
                "premium": "0.5-2% of sum insured annually",
                "features": ["Fire & Perils", "Theft & Burglary", "Business Interruption", "Equipment Breakdown"]
            }
        ],
        "Liability Insurance": [
            {
                "name": "Public Liability Insurance", 
                "description": "Protection against third-party injury or property damage claims",
                "coverage": "KES 5M - 100M",
                "premium": "KES 15,000 - 150,000 annually",
                "features": ["Bodily Injury", "Property Damage", "Legal Costs", "Court Awards"]
            }
        ]
    }
    
    # Display insurance categories
    for category, products in insurance_categories.items():
        st.markdown(f"#### {category}")
        
        for product in products:
            with st.expander(f"🛡️ {product['name']} - {product['coverage']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Description:** {product['description']}")
                    st.write(f"**Coverage Limit:** {product['coverage']}")
                    st.write(f"**Premium Range:** {product['premium']}")
                    
                    st.markdown("**Key Features:**")
                    for feature in product['features']:
                        st.write(f"• {feature}")
                
                with col2:
                    st.markdown("**Get a Quote**")
                    
                    with st.form(f"quote_{product['name'].replace(' ', '_')}"):
                        sum_insured = st.number_input("Coverage Amount (KES)", min_value=1000000.0, step=100000.0)
                        estimated_premium = sum_insured * 0.015  # 1.5% rate
                        
                        st.metric("Estimated Annual Premium", f"KES {estimated_premium:,.2f}")
                        
                        if st.form_submit_button("📋 Get Detailed Quote"):
                            get_business_insurance_quote(user_data, product, sum_insured, estimated_premium)

def get_business_insurance_quote(user_data, product, sum_insured, premium):
    """Get detailed business insurance quote"""
    try:
        quote_ref = f"BQ{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
        
        st.success("✅ Quote generated successfully!")
        st.info(f"📋 Quote Reference: {quote_ref}")
        st.info(f"🛡️ Product: {product['name']}")
        st.info(f"💰 Sum Insured: KES {sum_insured:,.2f}")
        st.info(f"💵 Annual Premium: KES {premium:,.2f}")
        
    except Exception as e:
        st.error(f"❌ Quote generation failed: {e}")

def render_my_business_policies_section(user_data):
    """Render my business policies section"""
    st.markdown("### 📋 My Business Insurance Policies")
    
    # Mock business policies
    business_policies = [
        {
            "policy_number": "BIZ001234",
            "product_name": "Commercial Property Insurance",
            "cover_amount": 5000000,
            "premium_paid": 75000,
            "status": "ACTIVE",
            "start_date": "2025-01-01",
            "end_date": "2025-12-31"
        }
    ]
    
    if business_policies:
        for policy in business_policies:
            status_color = "🟢" if policy['status'] == 'ACTIVE' else "🔴"
            
            with st.expander(f"{status_color} {policy['product_name']} - {policy['policy_number']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write("**Policy Information**")
                    st.write(f"Policy Number: {policy['policy_number']}")
                    st.write(f"Product: {policy['product_name']}")
                    st.write(f"Status: {policy['status']}")
                
                with col2:
                    st.write("**Coverage Details**")
                    st.write(f"Coverage: KES {policy['cover_amount']:,.2f}")
                    st.write(f"Premium: KES {policy['premium_paid']:,.2f}")
                
                with col3:
                    st.write("**Policy Period**")
                    st.write(f"Start: {policy['start_date']}")
                    st.write(f"End: {policy['end_date']}")
                    
                    if st.button(f"📞 File Claim", key=f"claim_{policy['policy_number']}"):
                        st.success("Claim form opened!")
    else:
        st.info("📋 No business insurance policies found")

def render_premium_payments_section(user_data):
    """Render premium payments section"""
    st.markdown("### 💰 Premium Payments")
    st.info("Premium payment features coming soon...")

def render_business_claims_section(user_data):
    """Render business claims section"""
    st.markdown("### 📞 File Business Claims")
    st.info("Claims filing features coming soon...")

def render_business_risk_calculator_section(user_data):
    """Render business risk calculator section"""
    st.markdown("### 🧮 Business Risk Calculator")
    st.info("Risk calculator features coming soon...")