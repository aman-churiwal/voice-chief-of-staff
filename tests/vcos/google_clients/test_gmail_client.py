import base64
from unittest.mock import MagicMock

from vcos.google_clients.gmail_client import create_draft, get_thread, list_threads


def test_list_threads_returns_items_from_api_response():
    service = MagicMock()
    service.users.return_value.threads.return_value.list.return_value.execute.return_value = {
        "threads": [{"id": "t1", "snippet": "Re: Q3 numbers"}]
    }

    result = list_threads(service, query="from:sam@example.com", max_results=5)

    assert result == [{"id": "t1", "snippet": "Re: Q3 numbers"}]
    service.users.return_value.threads.return_value.list.assert_called_once_with(
        userId="me", q="from:sam@example.com", maxResults=5
    )


def test_list_threads_returns_empty_list_when_no_threads():
    service = MagicMock()
    service.users.return_value.threads.return_value.list.return_value.execute.return_value = {}

    result = list_threads(service)

    assert result == []


def test_get_thread_returns_full_thread():
    service = MagicMock()
    service.users.return_value.threads.return_value.get.return_value.execute.return_value = {
        "id": "t1",
        "messages": [{"id": "m1", "snippet": "Can we push to 4pm?"}],
    }

    result = get_thread(service, thread_id="t1")

    service.users.return_value.threads.return_value.get.assert_called_once_with(
        userId="me", id="t1", format="full"
    )
    assert result == {
        "id": "t1",
        "messages": [{"id": "m1", "snippet": "Can we push to 4pm?"}],
    }


def test_create_draft_encodes_message_and_calls_drafts_create():
    service = MagicMock()
    service.users.return_value.drafts.return_value.create.return_value.execute.return_value = {
        "id": "draft1",
        "message": {"id": "m2"},
    }

    result = create_draft(
        service,
        to="sam@example.com",
        subject="Rescheduling our 1:1",
        body="Hi Sam, can we move our 1:1 to 4pm tomorrow?",
    )

    assert result == {"id": "draft1", "message": {"id": "m2"}}
    service.users.return_value.drafts.return_value.create.assert_called_once()
    call_kwargs = service.users.return_value.drafts.return_value.create.call_args.kwargs
    assert call_kwargs["userId"] == "me"
    raw = call_kwargs["body"]["message"]["raw"]
    decoded = base64.urlsafe_b64decode(raw.encode("utf-8")).decode("utf-8")
    assert "To: sam@example.com" in decoded
    assert "Subject: Rescheduling our 1:1" in decoded
    assert "Hi Sam, can we move our 1:1 to 4pm tomorrow?" in decoded