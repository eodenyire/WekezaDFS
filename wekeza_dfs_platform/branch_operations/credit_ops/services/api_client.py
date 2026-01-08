import os
import requests

# -----------------------------------------------------------------------------
# BACKEND API CONFIGURATION
# -----------------------------------------------------------------------------
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# -----------------------------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def get_request(endpoint: str, params: dict = None):
    """
    Send GET request to backend.
    """
    url = f"{API_URL}{endpoint}"
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise Exception(f"GET request failed: {e}")

def post_request(endpoint: str, data: dict):
    """
    Send POST request to backend.
    """
    url = f"{API_URL}{endpoint}"
    try:
        response = requests.post(url, json=data, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise Exception(f"POST request failed: {e}")

def put_request(endpoint: str, data: dict):
    """
    Send PUT request to backend.
    """
    url = f"{API_URL}{endpoint}"
    try:
        response = requests.put(url, json=data, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise Exception(f"PUT request failed: {e}")

def delete_request(endpoint: str, data: dict = None):
    """
    Send DELETE request to backend.
    """
    url = f"{API_URL}{endpoint}"
    try:
        response = requests.delete(url, json=data, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise Exception(f"DELETE request failed: {e}")
