# shared/api_client.py

import requests
import os
import time
from shared.auth import decode_token

# --- CONFIGURATION ---
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")  # Core banking backend URL
RETRY_COUNT = 3
RETRY_DELAY = 2  # seconds
TIMEOUT = 10     # seconds


# --- HEADERS ---
def get_headers(token=None):
    """
    Return standard headers for API requests.
    
    Args:
        token (str): JWT token (optional)
    """
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


# --- HELPER FUNCTIONS ---
def get_request(endpoint, params=None, token=None):
    """
    Send a GET request to the backend with retry logic.
    
    Args:
        endpoint (str): API endpoint
        params (dict): Query parameters
        token (str): JWT token for authorization
    Returns:
        dict: JSON response
    """
    url = f"{API_URL}{endpoint}"
    for attempt in range(RETRY_COUNT):
        try:
            response = requests.get(url, headers=get_headers(token), params=params, timeout=TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if attempt < RETRY_COUNT - 1:
                time.sleep(RETRY_DELAY)
                continue
            raise e


def post_request(endpoint, payload, token=None):
    """
    Send a POST request to the backend with retry logic.
    
    Args:
        endpoint (str): API endpoint
        payload (dict): Data to send
        token (str): JWT token for authorization
    Returns:
        dict: JSON response
    """
    url = f"{API_URL}{endpoint}"
    for attempt in range(RETRY_COUNT):
        try:
            response = requests.post(url, json=payload, headers=get_headers(token), timeout=TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if attempt < RETRY_COUNT - 1:
                time.sleep(RETRY_DELAY)
                continue
            raise e


def put_request(endpoint, payload, token=None):
    """
    Send a PUT request to the backend with retry logic.
    
    Args:
        endpoint (str): API endpoint
        payload (dict): Data to update
        token (str): JWT token for authorization
    Returns:
        dict: JSON response
    """
    url = f"{API_URL}{endpoint}"
    for attempt in range(RETRY_COUNT):
        try:
            response = requests.put(url, json=payload, headers=get_headers(token), timeout=TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if attempt < RETRY_COUNT - 1:
                time.sleep(RETRY_DELAY)
                continue
            raise e
