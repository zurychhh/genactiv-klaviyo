"""
Google Ads OAuth Authentication - cohnen's approach integrated into tool calls
"""

import os
import json
import requests
import logging
from typing import Dict, Any

# Google Auth libraries
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger(__name__)

# Constants
SCOPES = ['https://www.googleapis.com/auth/adwords']
API_VERSION = "v23"

# Environment variables
GOOGLE_ADS_OAUTH_CONFIG_PATH = os.environ.get("GOOGLE_ADS_OAUTH_CONFIG_PATH")
GOOGLE_ADS_DEVELOPER_TOKEN = os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN")

def format_customer_id(customer_id: str) -> str:
    """Format customer ID to ensure it's 10 digits without dashes."""
    customer_id = str(customer_id)
    customer_id = customer_id.replace('\"', '').replace('"', '')
    customer_id = ''.join(char for char in customer_id if char.isascii() and char.isdigit())
    return customer_id.zfill(10)

def get_oauth_credentials():
    """Get and refresh OAuth user credentials using cohnen's approach."""
    if not GOOGLE_ADS_OAUTH_CONFIG_PATH:
        raise ValueError(
            "GOOGLE_ADS_OAUTH_CONFIG_PATH environment variable not set. "
            "Please set it to point to your OAuth credentials JSON file."
        )
    
    if not os.path.exists(GOOGLE_ADS_OAUTH_CONFIG_PATH):
        raise FileNotFoundError(f"OAuth config file not found: {GOOGLE_ADS_OAUTH_CONFIG_PATH}")
    
    creds = None
    
    # Path to store the token (same directory as OAuth config)
    config_dir = os.path.dirname(os.path.abspath(GOOGLE_ADS_OAUTH_CONFIG_PATH))
    token_path = os.path.join(config_dir, 'google_ads_token.json')
    
    # Load existing token if it exists
    if os.path.exists(token_path):
        try:
            logger.info(f"Loading existing OAuth token from {token_path}")
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except Exception as e:
            logger.warning(f"Error loading existing token: {e}")
            creds = None
    
    # Check if credentials are valid
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                logger.info("Refreshing expired OAuth token")
                creds.refresh(Request())
                logger.info("Token successfully refreshed")
            except RefreshError as e:
                logger.warning(f"Token refresh failed: {e}, will get new token")
                creds = None
            except Exception as e:
                logger.error(f"Unexpected error refreshing token: {e}")
                raise
        
        # Need new credentials - MCP servers can't do interactive OAuth
        if not creds:
            # Check for pre-generated token in the server directory
            server_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            alt_token_path = os.path.join(server_dir, 'google_ads_token.json')

            if os.path.exists(alt_token_path):
                try:
                    logger.info(f"Loading token from server directory: {alt_token_path}")
                    creds = Credentials.from_authorized_user_file(alt_token_path, SCOPES)

                    # Try to refresh if expired
                    if creds and creds.expired and creds.refresh_token:
                        creds.refresh(Request())
                        logger.info("Token refreshed successfully")
                except Exception as e:
                    logger.error(f"Failed to load/refresh token: {e}")
                    creds = None

            if not creds:
                error_msg = (
                    "No valid OAuth token found. Please run the token generator script:\n"
                    "  cd google-ads-mcp && python generate_refresh_token.py\n"
                    "Then restart Claude Code."
                )
                logger.error(error_msg)
                raise ValueError(error_msg)
        
        # Save the credentials
        if creds:
            try:
                logger.info(f"Saving credentials to {token_path}")
                os.makedirs(os.path.dirname(token_path), exist_ok=True)
                with open(token_path, 'w') as f:
                    f.write(creds.to_json())
                logger.info("Credentials saved successfully")
            except Exception as e:
                logger.warning(f"Could not save credentials: {e}")
    
    return creds

def get_headers_with_auto_token() -> Dict[str, str]:
    """Get API headers with automatically managed token - integrated OAuth."""
    if not GOOGLE_ADS_DEVELOPER_TOKEN:
        raise ValueError("GOOGLE_ADS_DEVELOPER_TOKEN environment variable not set")
    
    # This will automatically trigger OAuth flow if needed
    creds = get_oauth_credentials()
    
    headers = {
        'Authorization': f'Bearer {creds.token}',
        'Developer-Token': GOOGLE_ADS_DEVELOPER_TOKEN.strip('"').strip("'"),
        'Content-Type': 'application/json'
    }
    
    return headers

def execute_gaql(customer_id: str, query: str, manager_id: str = "") -> Dict[str, Any]:
    """Execute GAQL using the non-streaming search endpoint."""
    # This will automatically trigger OAuth if needed
    headers = get_headers_with_auto_token()
    
    formatted_customer_id = format_customer_id(customer_id)
    url = f"https://googleads.googleapis.com/{API_VERSION}/customers/{formatted_customer_id}/googleAds:search"
    
    if manager_id:
        headers['login-customer-id'] = format_customer_id(manager_id)

    payload = {'query': query}
    resp = requests.post(url, headers=headers, json=payload)
    
    if not resp.ok:
        raise Exception(f"Error executing GAQL: {resp.status_code} {resp.reason} - {resp.text}")
    
    data = resp.json()
    results = data.get('results', [])
    return {
        'results': results,
        'query': query,
        'totalRows': len(results),
    }