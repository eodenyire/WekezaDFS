# services/api_client.py
import requests
import json

"""
API Client Module
-----------------
Centralized HTTP client for communicating with the backend Core Banking system.
Handles GET, POST, PUT, DELETE requests with error handling.
"""

# -----------------------------
# GET Request
# -----------------------------
def get_request(url: str, params: dict = None, headers: dict = None):
    """
    Perform a GET request to the backend API.
    
    Args:
        url (str): Full URL of the API endpoint
        params (dict): Query parameters
        headers (dict): HTTP headers
    
    Returns:
        requests.Response: Response object
    """
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        # Wrap request errors in a Response-like object
        return _mock_error_response(str(e))


# -----------------------------
# POST Request
# -----------------------------
def post_request(url: str, payload: dict, headers: dict = None):
    """
    Perform a POST request to the backend API.
    
    Args:
        url (str): Full URL of the API endpoint
        payload (dict): JSON payload
        headers (dict): HTTP headers
    
    Returns:
        requests.Response: Response object
    """
    if headers is None:
        headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=10)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        return _mock_error_response(str(e))


# -----------------------------
# PUT Request
# -----------------------------
def put_request(url: str, payload: dict, headers: dict = None):
    """
    Perform a PUT request to update data in the backend API.
    """
    if headers is None:
        headers = {"Content-Type": "application/json"}
    try:
        response = requests.put(url, data=json.dumps(payload), headers=headers, timeout=10)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        return _mock_error_response(str(e))


# -----------------------------
# DELETE Request
# -----------------------------
def delete_request(url: str, params: dict = None, headers: dict = None):
    """
    Perform a DELETE request to remove data from the backend API.
    """
    try:
        response = requests.delete(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        return _mock_error_response(str(e))


# -----------------------------
# Helper: Mock Error Response
# -----------------------------
def _mock_error_response(error_msg: str):
    """
    Return a mock response object for error handling in Streamlit UI.
    """
    class MockResponse:
        def __init__(self, message):
            self.status_code = 500
            self._message = message
        def json(self):
            return {"detail": self._message}
    return MockResponse(error_msg)
