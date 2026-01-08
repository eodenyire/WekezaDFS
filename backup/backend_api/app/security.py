from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import hashlib

# --- CONFIGURATION (In prod, these go in .env) ---
SECRET_KEY = "wekeza_super_secret_key_2026" # Change this!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Use a simpler password context to avoid bcrypt version issues
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except:
    # Fallback to simple hashing if bcrypt has issues
    pwd_context = None

def verify_password(plain_password, hashed_password):
    if pwd_context:
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except:
            pass
    
    # Fallback: simple SHA256 comparison for testing
    simple_hash = hashlib.sha256(plain_password.encode()).hexdigest()
    return simple_hash == hashed_password

def get_password_hash(password):
    if pwd_context:
        try:
            return pwd_context.hash(password)
        except:
            pass
    
    # Fallback: simple SHA256 for testing
    return hashlib.sha256(password.encode()).hexdigest()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt