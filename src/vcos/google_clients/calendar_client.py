"""Thin wrapper functions around the Google Calendar v3 API.

Every function takes a pre-built `service` object (from
googleapiclient.discovery.build("calendar", "v3", credentials=...)) so this
module has no knowledge of authentication. Functions return plain dicts/lists
only - no googleapiclient objects leak out.
"""

from typing import Any

def list_events(
    service,
    calendar_id: str = "primary",
    time_min: str | None = None,
    time_max: str | None = None,
    max_results: int = 10,
) -> list[dict]:
    """List upcoming events on a calendar, ordered by start time.

    Args:
        service: An authenticated Calendar API service object.
        calendar_id: Calendar to query. Defaults to the user's primary calendar.
        time_min: RFC3339 timestamp; only events starting after this are returned.
        time_max: RFC3339 timestamp; only events starting before this are returned.
        max_results: Maximum number of events to return.

    Returns:
        A list of events dicts as returned by the Calendar API (each has at
        least 'id', 'summary', 'start', 'end' keys)
    """
    response = (
        service.events()
        .list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    return response.get("items", [])


def create_event(
    service,
    calendar_id: str,
    summary: str,
    start_iso: str,
    end_iso: str,
    attendee_emails: list[str] | None = None,
) -> dict:
    """Create a new calendar event.

    Args:
        service: An authenticated Calendar API service object.
        calendar_id: Calendar to create the event on.
        summary: Event title.
        start_iso: RFC3339 start timestamp, e.g. "2026-07-23T15:00:00Z".
        end_iso: RFC3339 end timestamp.
        attendee_emails: Optional list of attendee email addresses to invite.

    Returns:
        The created event dict as returned by the Calendar API.
    """
    body: dict[str, Any] = {
        "summary": summary,
        "start": {"dateTime": start_iso},
        "end": {"dateTime": end_iso},
    }
    if attendee_emails:
        body["attendees"] = [{"email": email} for email in attendee_emails]

    return service.events().insert(calendarId=calendar_id, body=body).execute()


def update_event(service, calendar_id: str, event_id: str, updates: dict) -> dict:
    """Applies a partial update to an existing calendar event.

    Args:
        service: An authenticated Calendar API service object.
        calendar_id: Calendar the event belongs to.
        event_id: ID of the event to update.
        updates: Dict of fields to change, e.g. {"summary": "New title"} or
            {"start": {"dateTime": "..."}, "end": {"dateTime": "..."}}.

    Returns:
        The updated event dict as returned by the Calendar API.
    """

    return (
        service.events()
        .patch(calendarId=calendar_id, eventId=event_id, body=updates)
        .execute()
    )


def find_event_by_idempotency_key(
    service, calendar_id: str, idempotency_key: str
) -> dict | None:
    """Look up an event previously created with a given idempotency key.

    Args:
        service: An authenticated Calendar API service object.
        calendar_id: Calendar to search.
        idempotency_key: The idempotency key passed to a prior
            create_event_idempotent call.

    Returns:
        The matching event dict if one exists, else None.
    """
    response = (
        service.events()
        .list(
            calendarId=calendar_id,
            privateExtendedProperty=f"vcos_idempotency_key={idempotency_key}",
            maxResults=1,
        )
        .execute()
    )
    items = response.get("items", [])
    return items[0] if items else None


def create_event_idempotent(
    service,
    calendar_id: str,
    summary: str,
    start_iso: str,
    end_iso: str,
    idempotency_key: str,
    attendee_emails: list[str] | None = None,
) -> dict:
    """Creates a calendar event, or returns the existing one if this
    idempotency_key was already used - safe to call repeatedly on retry.

    Args:
        service: An authenticated Calendar API service object.
        calendar_id: Calendar to create the event on.
        summary: Event title.
        start_iso: RFC3339 start timestamp.
        end_iso: RFC3339 end timestamp.
        idempotency_key: A caller-generated unique key (e.g. a UUID) that
            identifies this specific creation request across retries.
        attendee_emails: Optional list of attendee email addresses to invite.

    Returns:
        The created (or previously-created) event dict.
    """
    existing = find_event_by_idempotency_key(service, calendar_id, idempotency_key)
    if existing:
        return existing

    body = {
        "summary": summary,
        "start": {"dateTime": start_iso},
        "end": {"dateTime": end_iso},
        "privateExtendedProperties": {"private": {"vcos_idempotency_key": idempotency_key}},
    }
    if attendee_emails:
        body["attendees"] = [{"email": email} for email in attendee_emails]  #type: ignore[attr-defined]

    return service.events().insert(calendarId=calendar_id, body=body).execute()