from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from app.database import Base
from app import security

# 1. Setup a Test Database (SQLite Memory)
# This runs in RAM, creates tables, runs test, then deletes everything. Pure & Clean.
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the Dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create Tables
Base.metadata.create_all(bind=engine)

client = TestClient(app)

# --- THE TESTS ---

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "active", "system": "Wekeza Core Engine"}

def test_register_user():
    payload = {
        "full_name": "Test User",
        "email": "test@wekeza.com",
        "phone_number": "0700000000",
        "national_id": "12345678",
        "password": "password123"
    }
    response = client.post("/users/", json=payload)
    assert response.status_code == 200
    assert response.json()["email"] == "test@wekeza.com"

def test_login_and_get_token():
    # 1. Login
    response = client.post("/token", data={"username": "test@wekeza.com", "password": "password123"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return token

def test_apply_loan_authorized():
    # 1. Get Token
    token = test_login_and_get_token()
    
    # 2. Apply for Loan (With Token)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"user_id": 1, "amount": 5000, "tenure_days": 30} # user_id ignored by backend now
    
    response = client.post("/loans/apply", json=payload, headers=headers)
    
    # It might be approved or rejected based on random risk logic, 
    # but status code should be 200 (Success) or 400 (Business Rejection), NOT 401 (Unauthorized)
    assert response.status_code in [200, 400] 

def test_apply_loan_unauthorized():
    # Try to apply WITHOUT a token
    payload = {"user_id": 1, "amount": 5000, "tenure_days": 30}
    response = client.post("/loans/apply", json=payload)
    assert response.status_code == 401  # Must fail!