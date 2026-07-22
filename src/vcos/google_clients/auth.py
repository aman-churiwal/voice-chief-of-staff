"""Loads and refreshes Google OAuth credentials for Calendar/Gmail access.

This module NEVER launches an interactive browser consent flow - that only
happens in scripts/authorize_google.py, run once by hand. This module just
loads the token that the script produced, refreshing it if it expired.
"""
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

def get_credentials(
    scopes: list[str], credentials_path: str, token_path: str,
) -> Credentials:
    """Loads Google OAuth credentials from token_path, refreshing if expired.

    Args:
        scopes: OAuth scopes the returned credentials must be valid for.
        credentials_path: Path to the OAuth client secret JSON (used only to
            confirm the app's client config exists; not read for the token).
        token_path: Path to the token.json file produced by
            scripts/authorize_google.py.

    Returns:
        A valid google.oauth2.credentials.Credentials object.

    Raises:
        FileNotFoundError: If token_path doesn't exist - the caller must run
            `python scripts/authorize_google.py` first to create it.
    """
    if not os.path.exists(token_path):
        raise FileNotFoundError(
            f"No token found at {token_path}. Run "
            "`python scripts/authorize_google.py` first to authorize this app."
        )

    creds = Credentials.from_authorized_user_file(token_path, scopes)

    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_path, "w") as f:
                f.write(creds.to_json())
        else:
            raise FileNotFoundError(
                f"Token at {token_path} is invalid and cannot be refreshed. "
                "Run `python scripts/authorize_google.py` again."
            )

    return creds