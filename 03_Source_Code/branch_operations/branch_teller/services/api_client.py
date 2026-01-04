import requests
import streamlit as st
from app import get_logged_in_teller

# -----------------------------------------------------------------------------
# API BASE URL
# -----------------------------------------------------------------------------
API_URL = st.secrets.get("API_URL", "http://127.0.0.1:8000/api")

# -----------------------------------------------------------------------------
# EXCEPTIONS
# -----------------------------------------------------------------------------
class APIClientError(Exception):
    """Custom exception for API client errors."""
    pass

# -----------------------------------------------------------------------------
# INTERNAL: Build Headers
# -----------------------------------------------------------------------------
def _build_headers():
    """
    Build request headers with JWT token from the logged-in teller.
    """
    teller = get_logged_in_teller()
    if not teller or "token" not in teller:
        raise APIClientError("Teller not logged in or missing token.")
    return {
        "Authorization": f"Bearer {teller['token']}",
        "Content-Type": "application/json"
    }

# -----------------------------------------------------------------------------
# GET REQUEST
# -----------------------------------------------------------------------------
def get_request(endpoint: str, params: dict = None, timeout: int = 15) -> dict:
    """
    Send a GET request to the backend.
    """
    url = f"{API_URL}{endpoint}"
    headers = _build_headers()
    try:
        response = requests.get(url, headers=headers, params=params, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.HTTPError as http_err:
        raise APIClientError(f"HTTP error: {http_err} - {response.text}")
    except requests.exceptions.RequestException as req_err:
        raise APIClientError(f"Request error: {req_err}")
    except ValueError as json_err:
        raise APIClientError(f"Invalid JSON response: {json_err}")

# -----------------------------------------------------------------------------
# POST REQUEST
# -----------------------------------------------------------------------------
def post_request(endpoint: str, payload: dict, timeout: int = 15) -> dict:
    """
    Send a POST request to the backend.
    """
    url = f"{API_URL}{endpoint}"
    headers = _build_headers()
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.HTTPError as http_err:
        raise APIClientError(f"HTTP error: {http_err} - {response.text}")
    except requests.exceptions.RequestException as req_err:
        raise APIClientError(f"Request error: {req_err}")
    except ValueError as json_err:
        raise APIClientError(f"Invalid JSON response: {json_err}")

# -----------------------------------------------------------------------------
# PUT REQUEST
# -----------------------------------------------------------------------------
def put_request(endpoint: str, payload: dict, timeout: int = 15) -> dict:
    """
    Send a PUT request to the backend.
    """
    url = f"{API_URL}{endpoint}"
    headers = _build_headers()
    try:
        response = requests.put(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.HTTPError as http_err:
        raise APIClientError(f"HTTP error: {http_err} - {response.text}")
    except requests.exceptions.RequestException as req_err:
        raise APIClientError(f"Request error: {req_err}")
    except ValueError as json_err:
        raise APIClientError(f"Invalid JSON response: {json_err}")

# -----------------------------------------------------------------------------
# DELETE REQUEST
# -----------------------------------------------------------------------------
def delete_request(endpoint: str, params: dict = None, timeout: int = 15) -> dict:
    """
    Send a DELETE request to the backend.
    """
    url = f"{API_URL}{endpoint}"
    headers = _build_headers()
    try:
        response = requests.delete(url, headers=headers, params=params, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.HTTPError as http_err:
        raise APIClientError(f"HTTP error: {http_err} - {response.text}")
    except requests.exceptions.RequestException as req_err:
        raise APIClientError(f"Request error: {req_err}")
    except ValueError as json_err:
        raise APIClientError(f"Invalid JSON response: {json_err}")

# -----------------------------------------------------------------------------
# OPTIONAL: RETRY LOGIC
# -----------------------------------------------------------------------------
def retry_request(method, endpoint, payload=None, params=None, retries=3):
    """
    Retry API request on failure up to `retries` times.
    Method: 'GET', 'POST', 'PUT', 'DELETE'
    """
    for attempt in range(retries):
        try:
            if method.upper() == "GET":
                return get_request(endpoint, params=params)
            elif method.upper() == "POST":
                return post_request(endpoint, payload=payload)
            elif method.upper() == "PUT":
                return put_request(endpoint, payload=payload)
            elif method.upper() == "DELETE":
                return delete_request(endpoint, params=params)
            else:
                raise ValueError("Invalid HTTP method.")
        except APIClientError as e:
            if attempt < retries - 1:
                continue  # retry
            else:
                raise
