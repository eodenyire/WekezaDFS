import streamlit as st
from datetime import datetime
from common import show_cash_receipt, get_cash_officer_info
from services.api_client import post_request, get_request

# --- Cash Reconciliation UI ---
def reconcile_cash_ui(officer_info):
    st.subheader("📊 End-of-Day Cash Reconciliation")

    st.info("Compare vault, teller, and ATM balances with the core banking ledger. Highlight discrepancies for review.")

    # Select date for reconciliation
    reconciliation_date = st.date_input("Select Date for Reconciliation", datetime.today())

    # Fetch summary data from backend
    if st.button("Fetch Reconciliation Data"):
        try:
            response = get_request(
                f"/cash-office/reconciliation?branch_code={officer_info['branch_code']}&date={reconciliation_date}"
            )
            if response.get("status") == "success":
                data = response.get("data", {})
                st.success("✅ Reconciliation data fetched successfully.")

                # Display Vault Summary
                st.subheader("🏦 Vault Summary")
                st.write(data.get("vault", "No vault data available."))

                # Display Teller Summary
                st.subheader("💵 Teller Summary")
                st.write(data.get("tellers", "No teller data available."))

                # Display ATM Summary
                st.subheader("🏧 ATM Summary")
                st.write(data.get("atms", "No ATM data available."))

                # Display Discrepancies
                st.subheader("⚠️ Discrepancies")
                discrepancies = data.get("discrepancies", [])
                if discrepancies:
                    for item in discrepancies:
                        st.warning(f"{item['type']} discrepancy: Expected {item['expected']}, Found {item['actual']}")
                else:
                    st.success("No discrepancies found. All balances match!")

                # Optionally, generate digital reconciliation report
                if st.button("Generate Reconciliation Receipt"):
                    show_cash_receipt(
                        "End-of-Day Cash Reconciliation",
                        {
                            "Branch": officer_info["branch_code"],
                            "Date": str(reconciliation_date),
                            "Vault Balance": data.get("vault_balance"),
                            "Total Teller Cash": data.get("teller_total"),
                            "Total ATM Cash": data.get("atm_total"),
                            "Discrepancies": discrepancies,
                            "Processed By": officer_info["officer_id"],
                            "Timestamp": datetime.now().isoformat()
                        }
                    )

            else:
                st.error(f"Failed to fetch reconciliation data: {response.get('detail')}")

        except Exception as e:
            st.error(f"System Error: Could not connect to Core Banking. {e}")
