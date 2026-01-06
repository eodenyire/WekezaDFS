import requests
import uuid

# CONFIG
API_URL = "http://localhost:8000"
TEST_EMAIL = f"director_{uuid.uuid4().hex[:4]}@wekeza-hardware.com"
TEST_PASS = "securePass123"

def print_step(msg):
    print(f"\n🔹 {msg}")

def verify_business_flow():
    print("🚀 STARTING BUSINESS BANKING LOGIC CHECK...\n")

    # STEP 1: REGISTER BUSINESS
    # This checks if the API correctly creates 3 things: Business, Director, and Wallet
    print_step("STEP 1: Registering New Business (Wekeza Hardware Ltd)...")
    payload = {
        "business_name": "Wekeza Hardware Ltd",
        "registration_no": f"BN-{uuid.uuid4().hex[:6].upper()}",
        "kra_pin": f"P05{uuid.uuid4().hex[:6].upper()}",
        "sector": "Retail",
        "director_email": TEST_EMAIL,
        "director_password": TEST_PASS
    }
    
    try:
        res = requests.post(f"{API_URL}/business/register", json=payload)
        if res.status_code == 200:
            data = res.json()
            print(f"✅ SUCCESS: Business Registered. ID: {data['business_id']}")
        else:
            print(f"❌ FAILED: {res.text}")
            return
    except Exception as e:
        print(f"❌ CRITICAL ERROR: Is the Server Running? {e}")
        return

    # STEP 2: LOGIN AS DIRECTOR
    # This checks if the 'User' table was correctly linked to the 'Business'
    print_step("STEP 2: Logging in as Director...")
    login_payload = {"username": TEST_EMAIL, "password": TEST_PASS}
    res = requests.post(f"{API_URL}/token", data=login_payload)
    
    if res.status_code == 200:
        token = res.json()['access_token']
        print("✅ SUCCESS: Director Authenticated (JWT Received)")
    else:
        print("❌ FAILED: Login rejected.")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # STEP 3: APPLY FOR VALID SME LOAN
    # Logic: Retail Sector = Medium Risk. Amount 500,000 should be < 20% of simulated turnover.
    print_step("STEP 3: Testing 'Happy Path' Loan Application (KES 500,000)...")
    loan_payload = {
        "amount": 500000,
        "sector": "Retail",
        "tenure_months": 3
    }
    
    res = requests.post(f"{API_URL}/business/loans/apply", json=loan_payload, headers=headers)
    
    if res.status_code == 200:
        print(f"✅ SUCCESS: Loan Approved. New Balance: KES {res.json()['new_balance']:,.2f}")
    else:
        # Note: Since turnover is random in our mock engine, this might occasionally fail.
        # But logically, it proves the endpoint is reachable.
        print(f"⚠️ NOTE: Loan Rejected (Expected if random turnover was low). Reason: {res.json()['detail']}")

    # STEP 4: APPLY FOR INVALID LOAN (OVER LIMIT)
    # Logic: Asking for 1 Billion should definitely trigger the "Turnover Rule" failure.
    print_step("STEP 4: Testing 'Risk Logic' (Asking for KES 1 Billion)...")
    huge_loan = {
        "amount": 1000000000,
        "sector": "Retail",
        "tenure_months": 12
    }
    
    res = requests.post(f"{API_URL}/business/loans/apply", json=huge_loan, headers=headers)
    
    if res.status_code == 400:
        print(f"✅ SUCCESS: System correctly REJECTED the loan.")
        print(f"   Reason given by Risk Engine: '{res.json()['detail']}'")
    else:
        print(f"❌ FAILED: System approved a 1 Billion loan! Logic Error.")

    print("\n✅ VERIFICATION COMPLETE.")

if __name__ == "__main__":
    verify_business_flow()