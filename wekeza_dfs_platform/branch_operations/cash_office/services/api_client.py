"""
Centralized API Client for Cash Office
Handles all backend interactions (GET and POST requests)
"""

import requests
import os

# Base API URL (from environment variable or default localhost)
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


# --- Generic GET Request ---
def get_request(endpoint, params=None, headers=None):
    """
    Sends a GET request to the backend API.
    - endpoint: API endpoint string, e.g., '/cash-office/reconciliation'
    - params: dictionary of query parameters
    - headers: optional headers dictionary
    Returns: dict response from backend
    """
    url = f"{API_URL}{endpoint}"
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        return {"status": "error", "detail": f"HTTP error: {http_err}"}
    except requests.exceptions.ConnectionError as conn_err:
        return {"status": "error", "detail": f"Connection error: {conn_err}"}
    except Exception as e:
        return {"status": "error", "detail": f"Unexpected error: {e}"}


# --- Generic POST Request ---
def post_request(endpoint, payload=None, headers=None):
    """
    Sends a POST request to the backend API.
    - endpoint: API endpoint string, e.g., '/cash-office/vault/open'
    - payload: dictionary of JSON data to send
    - headers: optional headers dictionary
    Returns: dict response from backend
    """
    url = f"{API_URL}{endpoint}"
    headers = headers or {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        return {"status": "error", "detail": f"HTTP error: {http_err}"}
    except requests.exceptions.ConnectionError as conn_err:
        return {"status": "error", "detail": f"Connection error: {conn_err}"}
    except Exception as e:
        return {"status": "error", "detail": f"Unexpected error: {e}"}
