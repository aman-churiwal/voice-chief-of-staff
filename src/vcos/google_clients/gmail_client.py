"""Thin wrapper functions around the Gmail v1 API.

Every function takes a pre-built `service` object (from
googleapiclient.discovery.build("gmail", "v1", credentials=...)) so this
module has no knowledge of authentication. Functions return plain dicts/lists
only - no googleapiclient objects leak out.
"""
import base64
from email.mime.text import MIMEText


def list_threads(
    service, query: str | None = None, max_results: int = 10
) -> list[dict]:
    """List Gmail threads matching an optional search query.

    Args:
        service: An authenticated Gmail API service object.
        query: Gmail search syntax, e.g. "from:sam@example.com is:unread".
            If None, returns the most recent threads across the mailbox.
        max_results: Maximum number of threads to return.

    Returns:
        A list of thread summary dicts (each has at least 'id', 'snippet').
    """
    response = (
        service.users()
        .threads()
        .list(userId="me", q=query, maxResults=max_results)
        .execute()
    )
    return response.get("threads", [])


def get_thread(service, thread_id: str) -> dict:
    """Fetches a full Gmail thread, including all messages in it.

    Args:
        service: An authenticated Gmail API service object.
        thread_id: The Gmail thread ID to fetch.

    Returns:
        The full thread dict, including a `messages` list.
    """
    return (
        service.users()
        .threads()
        .get(userId="me", id=thread_id, format="full")
        .execute()
    )


def create_draft(
    service, to: str, subject: str, body: str, thread_id: str | None = None
) -> dict:
    """Creates a Gmail draft. Does NOT send it.

    Args:
        service: An authenticated Gmail API service object.
        to: Recipient email address.
        subject: Email subject line.
        body: Plain-text email body.
        thread_id: Optional Gmail thread ID to attach this draft to, for
            replying within an existing conversation.

    Returns:
        The created draft dict as returned by the Gmail API.
    """
    messages = MIMEText(body)
    messages["To"] = to
    messages["Subject"] = subject
    raw = base64.urlsafe_b64encode(messages.as_bytes()).decode("utf-8")

    draft_body = {"message": {"raw": raw}}
    if thread_id:
        draft_body["message"]["threadId"] = thread_id

    return service.users().drafts().create(userId="me", body=draft_body).execute()