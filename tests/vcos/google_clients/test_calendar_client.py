from unittest.mock import MagicMock

from vcos.google_clients.calendar_client import (
    create_event,
    list_events,
    update_event,
    create_event_idempotent,
    find_event_by_idempotency_key,
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


def test_find_event_by_idempotency_key_returns_match():
    service = MagicMock()
    service.events.return_value.list.return_value.execute.return_value = {
        "items": [{"id": "evt1", "summary": "Standup"}]
    }

    result = find_event_by_idempotency_key(service, "primary", "key-123")

    service.events.return_value.list.assert_called_once_with(
        calendarId="primary",
        privateExtendedProperty="vcos_idempotency_key=key-123",
        maxResults=1,
    )
    assert result == {"id": "evt1", "summary": "Standup"}


def test_find_event_by_idempotency_key_returns_none_when_no_match():
    service = MagicMock()
    service.events.return_value.list.return_value.execute.return_value = {"items": []}

    result = find_event_by_idempotency_key(service, "primary", "key-123")

    assert result is None


def test_create_event_idempotent_skip_insert_when_already_created():
    service = MagicMock()
    service.events.return_value.list.return_value.execute.return_value = {
        "items": [{"id": "evt-existing", "summary": "Standup"}]
    }

    result = create_event_idempotent(
        service,
        calendar_id="primary",
        summary="Standup",
        start_iso="2026-07-23T09:00:00Z",
        end_iso="2026-07-23T09:15:00Z",
        idempotency_key="key-123",
    )

    service.events.return_value.insert.assert_not_called()
    assert result == {"id": "evt-existing", "summary": "Standup"}


def test_create_event_idempotent_inserts_with_idempotency_key_when_new():
    service = MagicMock()
    service.events.return_value.list.return_value.execute.return_value = {"items": []}
    service.events.return_value.insert.return_value.execute.return_value = {
        "id": "evt-new",
        "summary": "Standup",
    }

    result = create_event_idempotent(
        service,
        calendar_id="primary",
        summary="Standup",
        start_iso="2026-07-23T09:00:00Z",
        end_iso="2026-07-23T09:15:00Z",
        idempotency_key="key-123",
        attendee_emails=["sam@example.com"]
    )

    service.events.return_value.insert.assert_called_once_with(
        calendarId="primary",
        body={
            "summary": "Standup",
            "start": {"dateTime": "2026-07-23T09:00:00Z"},
            "end": {"dateTime": "2026-07-23T09:15:00Z"},
            "privateExtendedProperties": {"private": {"vcos_idempotency_key": "key-123"}},
            "attendees": [{"email": "sam@example.com"}],
        },
    )
    assert result == {"id": "evt-new", "summary": "Standup"}