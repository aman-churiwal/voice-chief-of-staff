"""Run this once by hand to grant vcos access to your Google Calendar/Gmail.

Usage:
    python scripts/authorize_google.py

Opens a browser window for Google's OAuth consent screen, then writes the resulting
token to GOOGLE_TOKEN_PATH (default: credentials/token.json).
"""
import os

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
]

def main() -> None:
    credentials_path = os.environ.get(
        "GOOGLE_CREDENTIALS_PATH", "credentials/client_secret.json"
    )
    token_path = os.environ.get("GOOGLE_TOKEN_PATH", "credentials/token.json")

    if not os.path.exists(credentials_path):
        raise FileNotFoundError(
            f"No OAuth client secret found at {credentials_path}. "
            "Download it from the Google Cloud Console (APIs & Services > "
            "Credentials) and place it there."
        )

    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
    creds = flow.run_local_server(port=0)  #type: ignore[attr-defined]

    with open(token_path, "w") as f:
        f.write(creds.to_json())

    print(f"Authorization complete. Token saved to {token_path}")


if __name__ == "__main__":
    main()