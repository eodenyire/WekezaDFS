# branch_management/services/api_client.py
import requests
import logging

# -----------------------------
# Configure Logger
# -----------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# -----------------------------
# API Client Functions
# -----------------------------
def get_request(url: str, params: dict = None, headers: dict = None, timeout: int = 10):
    """
    Send a GET request to the backend API.

    Args:
        url (str): Full API URL
        params (dict): Query parameters
        headers (dict): Optional HTTP headers
        timeout (int): Request timeout in seconds

    Returns:
        Response: requests.Response object
    """
    try:
        response = requests.get(url, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
        return response
    except requests.exceptions.RequestException as err:
        logger.error(f"Request error: {err}")
        raise


def post_request(url: str, payload: dict, headers: dict = None, timeout: int = 10):
    """
    Send a POST request to the backend API.

    Args:
        url (str): Full API URL
        payload (dict): JSON payload
        headers (dict): Optional HTTP headers
        timeout (int): Request timeout in seconds

    Returns:
        Response: requests.Response object
    """
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
        return response
    except requests.exceptions.RequestException as err:
        logger.error(f"Request error: {err}")
        raise


def put_request(url: str, payload: dict, headers: dict = None, timeout: int = 10):
    """
    Send a PUT request to the backend API.

    Args:
        url (str): Full API URL
        payload (dict): JSON payload
        headers (dict): Optional HTTP headers
        timeout (int): Request timeout in seconds

    Returns:
        Response: requests.Response object
    """
    try:
        response = requests.put(url, json=payload, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
        return response
    except requests.exceptions.RequestException as err:
        logger.error(f"Request error: {err}")
        raise


def delete_request(url: str, params: dict = None, headers: dict = None, timeout: int = 10):
