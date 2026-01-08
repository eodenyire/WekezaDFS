# bancassurance/services/api_client.py

import requests
import os
import time

# --- CONFIG ---
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")  # Core banking / Bancassurance backend URL
RETRY_COUNT = 3
RETRY_DELAY = 2  # seconds

# --- HEADERS / AUTH ---
def get_headers():
    """
    Returns standard headers for API requests.
    Include authorization if required.
    """
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        # "Authorization": f"Bearer {os.getenv('API_TOKEN')}"  # Uncomment if token-based auth
    }

# --- HELPER FUNCTIONS ---
def get_request(endpoint, params=None):
    """
    Send a GET request to the backend with retry logic.
    
    Args:
        endpoint (str): API endpoint, e.g., "/bancassurance/policy-sale"
        params (dict): Query parameters
    Returns:
        dict: JSON response from backend
    """
    url = f"{API_URL}{endpoint}"
    for attempt in range(RETRY_COUNT):
        try:
            response = requests.get(url, headers=get_headers(), params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if attempt < RETRY_COUNT - 1:
                time.sleep(RETRY_DELAY)
                continue
            raise e

def post_request(endpoint, payload):
    """
    Send a POST request to the backend with retry logic.
    
    Args:
        endpoint (str): API endpoint
        payload (dict): Data to send in the body
    Returns:
        dict: JSON response from backend
    """
    url = f"{API_URL}{endpoint}"
    for attempt in range(RETRY_COUNT):
        try:
            response = requests.post(url, headers=get_headers(), json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if attempt < RETRY_COUNT - 1:
                time.sleep(RETRY_DELAY)
                continue
            raise e

def put_request(endpoint, payload):
    """
    Send a PUT request to the backend with retry logic.
    
    Args:
        endpoint (str): API endpoint
        payload (dict): Data to update
    Returns:
        dict: JSON response from backend
    """
    url = f"{API_URL}{endpoint}"
    for attempt in range(RETRY_COUNT):
        try:
            response = requests.put(url, headers=get_headers(), json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if attempt < RETRY_COUNT - 1:
                time.sleep(RETRY_DELAY)
                continue
            raise e
