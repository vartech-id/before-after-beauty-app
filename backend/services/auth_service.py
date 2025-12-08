import os
from typing import Optional

from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from backend.config import CLIENT_SECRETS_FILE, SCOPES, TOKEN_FILE, API_BASE_URL

CREDENTIALS: Credentials | None = None
DRIVE_SERVICE = None


def save_credentials(creds: Credentials):
    """Persist credentials (including refresh token) to disk."""
    print(f"Token berhasil disimpan ke {TOKEN_FILE}")
    with open(TOKEN_FILE, "w") as token:
        token.write(creds.to_json())


def load_credentials() -> Optional[Credentials]:
    """Load credentials from disk if they exist."""
    if os.path.exists(TOKEN_FILE):
        print(f"Memuat kredensial dari {TOKEN_FILE}")
        with open(TOKEN_FILE, "r") as token:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            if creds.refresh_token:
                return creds
    return None


def create_flow() -> InstalledAppFlow:
    """Create an OAuth flow with a fixed redirect URI for the local FastAPI app."""
    redirect_uri = f"{API_BASE_URL.rstrip('/')}/api/oauth2callback"
    return InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES, redirect_uri=redirect_uri
    )


def refresh_or_authorize_credentials():
    """Ensure credentials are available and refreshed before using the Drive API."""
    global CREDENTIALS, DRIVE_SERVICE

    creds = load_credentials()
    if not creds:
        CREDENTIALS = None
        DRIVE_SERVICE = None
        return

    if creds.expired and creds.refresh_token:
        print("Access Token kedaluwarsa, mencoba refresh...")
        try:
            creds.refresh(GoogleAuthRequest())
            save_credentials(creds)
            print("Refresh Token berhasil.")
        except Exception as e:
            print(f"ERROR: Gagal merefresh token: {e}")
            return

    CREDENTIALS = creds
    DRIVE_SERVICE = build("drive", "v3", credentials=CREDENTIALS)


def get_drive_service():
    """Return an initialized Drive service, refreshing credentials if needed."""
    if not DRIVE_SERVICE:
        refresh_or_authorize_credentials()
    return DRIVE_SERVICE


def is_authorized() -> bool:
    return CREDENTIALS is not None and CREDENTIALS.valid


def handle_callback(authorization_response: str):
    """Handle OAuth callback, exchange code for tokens, and persist them."""
    flow = create_flow()
    flow.fetch_token(authorization_response=authorization_response)
    creds = flow.credentials
    save_credentials(creds)
    refresh_or_authorize_credentials()


def get_credentials() -> Optional[Credentials]:
    return CREDENTIALS
