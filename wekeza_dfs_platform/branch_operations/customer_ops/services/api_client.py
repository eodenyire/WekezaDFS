import os
import requests

# -----------------------------------------------------------------------------
# Base Backend URL
# -----------------------------------------------------------------------------
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api")

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
def get_request(endpoint: str, params: dict = None, headers: dict = None) -> dict:
    """
    Perform a GET request to the backend API
    """
    url = f"{API_URL}{endpoint}"
    try:
        res = requests.get(url, params=params, headers=headers)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"GET request failed: {e}")

def post_request(endpoint: str, payload: dict, headers: dict = None) -> dict:
    """
    Perform a POST request to the backend API
    """
    url = f"{API_URL}{endpoint}"
    try:
        res = requests.post(url, json=payload, headers=headers)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"POST request failed: {e}")

def put_request(endpoint: str, payload: dict, headers: dict = None) -> dict:
    """
    Perform a PUT request to the backend API
    """
    url = f"{API_URL}{endpoint}"
    try:
        res = requests.put(url, json=payload, headers=headers)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"PUT request failed: {e}")
