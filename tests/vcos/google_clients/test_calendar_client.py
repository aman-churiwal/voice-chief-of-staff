from unittest.mock import MagicMock

from vcos.google_clients.calendar_client import (
    create_event,
    list_events,
    update_event,
)


def test_list_events_returns_items_from_api_response():
    service = MagicMock()
    service.events.return_value.list.return_value.execute.return_value = {
        "items": [
            {"id": "evt1", "summary": "Standup", "start": {"dateTime": "2026-07-22T09:00:00Z"}},
            {"id": "evt2", "summary": "1:1 with Sam", "start": {"dateTime": "2026-07-22T15:00:00Z"}},
        ]
    }

    result = list_events(service, calendar_id="primary", max_results=10)

    assert result == [
        {"id": "evt1", "summary": "Standup", "start": {"dateTime": "2026-07-22T09:00:00Z"}},
        {"id": "evt2", "summary": "1:1 with Sam", "start": {"dateTime": "2026-07-22T15:00:00Z"}},
    ]
    service.events.return_value.list.assert_called_once_with(
        calendarId="primary",
        timeMin=None,
        timeMax=None,
        maxResults=10,
        singleEvents=True,
        orderBy="startTime",
    )


def test_list_events_returns_empty_list_when_no_items():
    service = MagicMock()
    service.events.return_value.list.return_value.execute.return_value = {}

    result = list_events(service)

    assert result == []


def test_create_event_calls_insert_with_correct_body():
    service = MagicMock()
    service.events.return_value.insert.return_value.execute.return_value = {
        "id": "new-evt-1",
        "summary": "Reschedule with Sam"
    }

    result = create_event(
        service,
        calendar_id="primary",
        summary="Reschedule with Sam",
        start_iso="2026-07-23T15:00:00Z",
        end_iso="2026-07-23T15:30:00Z",
        attendee_emails=["sam@example.com"],
    )

    service.events.return_value.insert.assert_called_once_with(
        calendarId="primary",
        body={
            "summary": "Reschedule with Sam",
            "start": {"dateTime": "2026-07-23T15:00:00Z"},
            "end": {"dateTime": "2026-07-23T15:30:00Z"},
            "attendees": [{"email": "sam@example.com"}],
        },
    )
    assert result == {"id": "new-evt-1", "summary": "Reschedule with Sam"}


def test_update_event_calls_patch_with_updates():
    service = MagicMock()
    service.events.return_value.patch.return_value.execute.return_value = {
        "id": "evt1",
        "summary": "Standup (moved)",
    }

    result = update_event(
        service,
        calendar_id="primary",
        event_id="evt1",
        updates={"summary": "Standup (moved)"},
    )

    service.events.return_value.patch.assert_called_once_with(
        calendarId="primary", eventId="evt1", body={"summary": "Standup (moved)"}
    )
    assert result == {"id": "evt1", "summary": "Standup (moved)"}