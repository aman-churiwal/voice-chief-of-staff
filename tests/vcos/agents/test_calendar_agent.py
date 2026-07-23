from unittest.mock import MagicMock, patch

from vcos.agents.calendar_agent import (
    calendar_agent,
    check_calendar,
    propose_calendar_change,
)


def test_check_calendar_calls_list_events_with_real_service():
    fake_service = MagicMock()
    with patch(
        "vcos.agents.calendar_agent.build_calendar_service", return_value=fake_service
    ), patch(
        "vcos.agents.calendar_agent.list_events",
        return_value=[{"id": "evt1", "summary": "Standup"}],
    ) as mock_list_events:
        result = check_calendar(time_min="2026-07-22T00:00:00Z")

    mock_list_events.assert_called_once_with(
        fake_service, time_min="2026-07-22T00:00:00Z", time_max=None
    )
    assert result == [{"id": "evt1", "summary": "Standup"}]


def test_propose_calendar_change_never_calls_create_event():
    with patch("vcos.agents.calendar_agent.create_event") as mock_create_event, patch(
        "vcos.agents.calendar_agent.build_calendar_service"
    ) as mock_build_service:
        result = propose_calendar_change(
            summary="Reschedule with Sam",
            start_iso="2026-07-23T15:00:00Z",
            end_iso="2026-07-23T15:30:00Z",
            attendee_emails=["sam@example.com"],
        )

    mock_create_event.assert_not_called()
    mock_build_service.assert_not_called()
    assert result == {
        "action": "create_event",
        "status": "proposed",
        "summary": "Reschedule with Sam",
        "start_iso": "2026-07-23T15:00:00Z",
        "end_iso": "2026-07-23T15:30:00Z",
        "attendee_emails": ["sam@example.com"]
    }


def test_calendar_agent_is_configured_with_both_tools():
    tool_names = {tool.__name__ for tool in calendar_agent.tools}
    assert tool_names == {"check_calendar", "propose_calendar_change"}
    assert calendar_agent.name == "calendar_agent"
    assert "calendar" in calendar_agent.description.lower()