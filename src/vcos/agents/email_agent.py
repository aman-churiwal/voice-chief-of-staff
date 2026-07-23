"""ADK Email Agent: reads real Gmail data, proposes (never sends) emails.
Delegated to by the root agent for email-related requests.
"""
import os

from google.adk.agents import Agent
from googleapiclient.discovery import build

from vcos.google_clients.auth import get_credentials
from vcos.google_clients.gmail_client import list_threads, create_draft, get_thread

GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
]

def build_gmail_service():
    """Builds an authenticated Gmail API v1 service object."""
    creds = get_credentials(
        scopes=GMAIL_SCOPES,
        credentials_path=os.environ.get(
            "GOOGLE_CREDENTIALS_PATH", "credentials/client_secret.json"
        ),
        token_path=os.environ.get("GOOGLE_TOKEN_PATH", "credentials/token.json"),
    )
    return build("gmail", "v1", credentials=creds)


def check_email(query: str | None = None) -> list[dict]:
    """Searches the user's Gmail inbox for threads matching a query.

    Args:
        query: Gmail search syntax, e.g. "from:sam@example.com is:unread".
            If None, returns the most recent threads.

    Returns:
        A list of thread summary dicts, each with 'id' and 'snippet'.
    """
    service = build_gmail_service()
    return list_threads(service, query=query)


def read_email_thread(thread_id: str) -> dict:
    """Reads the full content of a specific Gmail thread.

    Args:
        thread_id: The Gmail thread ID to read, typically obtained from a
            prior `check_email` call.

    Returns:
        The full thread dict, including all messages in the conversation.
    """
    service = build_gmail_service()
    return get_thread(service, thread_id=thread_id)


def propose_email_send(to: str, subject: str, body: str) -> dict:
    """Proposes sending an email. Does NOT create a draft or send anything.

    This tool never touches the real mailbox. It returns a structured
    proposal describing the intended change, for a human (or later, the
    Temporal task layer) to confirm and send.

    Args:
        to: Recipient email address.
        subject: Email subject line.
        body: Plain-text email body.

    Returns:
        A dict describing the proposed action: {"action": "send_email",
        "status": "proposed", "to": ..., "subject": ..., "body": ...}.
    """
    return {
        "action": "send_email",
        "status": "proposed",
        "to": to,
        "subject": subject,
        "body": body,
    }


email_agent = Agent(
    name="email_agent",
    model="gemini-flash-latest",
    description=(
        "Handles email-related requests: searching the inbox, reading "
        "threads, and proposing emails to send. Never sends or drafts "
        "an email itself - always proposes first."
    ),
    instruction=(
        "You are the Email Agent. For questions about what's in the inbox, "
        "use 'check_email'. To read the full content of a specific thread, "
        "use 'read_email_thread'. For requests to send an email, use "
        "'propose_email_send' to describe the intended change - do not "
        "claim the email has been sent, since this tool only proposes "
        "messages for later confirmation."
    ),
    tools=[check_email, propose_email_send, read_email_thread],
)