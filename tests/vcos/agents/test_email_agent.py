from unittest.mock import MagicMock, patch

from pygments.lexers import q

from vcos.agents.email_agent import (
    check_email,
    email_agent,
    propose_email_send,
    read_email_thread,
)


def test_check_email_calls_list_threads_with_real_service():
    fake_service = MagicMock()
    with patch(
        "vcos.agents.email_agent.build_gmail_service", return_value=fake_service
    ), patch(
        "vcos.agents.email_agent.list_threads",
        return_value=[{"id": "t1", "snippet": "Re: Q3 numbers"}],
    ) as mock_list_threads:
        result = check_email(query="is:unread")

    mock_list_threads.assert_called_once_with(fake_service, query="is:unread")
    assert result == [{"id": "t1", "snippet": "Re: Q3 numbers"}]


def test_read_email_thread_calls_get_thread_with_real_service():
    fake_service = MagicMock()
    with patch(
        "vcos.agents.email_agent.build_gmail_service", return_value=fake_service
    ), patch(
        "vcos.agents.email_agent.get_thread",
        return_value={"id": "t1", "messages": []},
    ) as mock_get_thread:
        result = read_email_thread(thread_id="t1")

    mock_get_thread.assert_called_once_with(fake_service, thread_id="t1")
    assert result == {"id": "t1", "messages": []}


def test_propose_email_send_never_calls_create_draft():
    with patch("vcos.agents.email_agent.create_draft") as mock_create_draft, patch(
        "vcos.agents.email_agent.build_gmail_service"
    ) as mock_build_service:
        result = propose_email_send(
            to="sam@example.com",
            subject="Rescheduling our 1:1",
            body="Hi Sam, can we move our 1:1 to 4pm tomorrow?",
        )

    mock_create_draft.assert_not_called()
    mock_build_service.assert_not_called()
    assert result == {
        "action": "send_email",
        "status": "proposed",
        "to": "sam@example.com",
        "subject": "Rescheduling our 1:1",
        "body": "Hi Sam, can we move our 1:1 to 4pm tomorrow?",
    }


def test_email_agent_is_configured_with_all_three_tools():
    tool_names = {tool.__name__ for tool in email_agent.tools}
    assert tool_names == {"check_email", "propose_email_send", "read_email_thread"}
    assert email_agent.name == "email_agent"
    assert "email" in email_agent.description.lower()