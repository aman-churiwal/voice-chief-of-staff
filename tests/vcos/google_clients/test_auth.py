import json
from unittest.mock import MagicMock, patch

import pytest

from vcos.google_clients.auth import get_credentials

def test_get_credentials_loads_valid_existing_token(tmp_path):
    """If token.json exists and is valid, load it directly with no refresh/flow."""
    token_path = tmp_path / "token.json"
    token_path.write_text(json.dumps({
        "token": "fake-access-token",
        "refresh_token": "fake-refresh-token",
        "client_id": "fake-client-id",
        "client_secret": "fake-client-secret",
        "scopes": ["https://www.googleapis.com/auth/calendar"],
    }))
    credentials_path = tmp_path / "client_secret.json"
    credentials_path.write_text("{}")

    fake_creds = MagicMock(valid=True, expired=False)
    with patch(
        "vcos.google_clients.auth.Credentials.from_authorized_user_file",
        return_value=fake_creds,
    ) as mock_from_file:
        result = get_credentials(
            scopes=["https://www.googleapis.com/auth/calendar"],
            credentials_path=str(credentials_path),
            token_path=str(token_path),
        )

    mock_from_file.assert_called_once_with(
        str(token_path), ["https://www.googleapis.com/auth/calendar"]
    )
    assert result is fake_creds

def test_get_credentials_refreshes_expired_token(tmp_path):
    """If the token is expired but has a refresh_token, refresh it and re-save"""
    token_path = tmp_path / "token.json"
    token_path.write_text(json.dumps({"refresh_token": "fake-refresh-token"}))
    credentials_path = tmp_path / "client_secret.json"
    credentials_path.write_text("{}")

    fake_creds = MagicMock(valid=False, expired=True, refresh_token="fake-refresh-token")

    def fake_refresh(request):
        fake_creds.valid = True

    fake_creds.refresh.side_effect = fake_refresh
    fake_creds.to_json.return_value = '{"token": "refreshed"}'

    with patch(
        "vcos.google_clients.auth.Credentials.from_authorized_user_file",
        return_value=fake_creds,
    ):
        result = get_credentials(
            scopes=["https://www.googleapis.com/auth/calendar"],
            credentials_path=str(credentials_path),
            token_path=str(token_path),
        )

    fake_creds.refresh.assert_called_once()
    assert result is fake_creds
    assert token_path.read_text() == '{"token": "refreshed"}'

def test_get_credentials_raises_if_no_token_and_no_interactive_flow(tmp_path):
    """If token.json doesn't exist, get_credentials must not silently launch a
    browser flow (that belongs only in scripts/authorize_google.py) - it should
    raise a clear error telling the caller to run that script."""
    credentials_path = tmp_path / "client_secret.json"
    credentials_path.write_text("{}")
    missing_token_path = tmp_path / "token.json"

    with pytest.raises(FileNotFoundError, match="authorize_google.py"):
        get_credentials(
            scopes=["https://www.googleapis.com/auth/calendar"],
            credentials_path=str(credentials_path),
            token_path=str(missing_token_path),
        )