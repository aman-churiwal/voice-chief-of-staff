"""ADK Calendar Agent: reads real calendar data, proposes (never executes)
calendar changes. Delegated to by the root agent for calendar-related requests.
"""
import os

from google.adk.agents import Agent
from googleapiclient.discovery import build

from vcos.google_clients.auth import get_credentials
from vcos.google_clients.calendar_client import create_event, list_events

CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar"]


def build_calendar_service():
    """Builds an authenticated Google Calendar API v3 service object."""
    creds = get_credentials(
        scopes=CALENDAR_SCOPES,
        credentials_path=os.environ.get(
            "GOOGLE_CREDENTIALS_PATH", "credentials/client_secret.json"
        ),
        token_path=os.environ.get("GOOGLE_TOKEN_PATH", "credentials/token.json"),
    )
    return build("calendar", "v3", credentials=creds)


def check_calendar(
    time_min: str | None = None, time_max: str | None = None
) -> list[dict]:
    """Reads upcoming events from the user's primary calendar.

    Args:
        time_min: RFC3339 timestamp; only events starting after this are returned.
            Use this to answer questions like "What's on my calendar today?"
        time_max: RFC3339 timestamp; only events starting before this are returned.

    Returns:
        A list of event dicts, each with 'id', 'summary', 'start', 'end'.
    """
    service = build_calendar_service()
    return list_events(service, time_min=time_min, time_max=time_max)


def propose_calendar_change(
    summary: str,
    start_iso: str,
    end_iso: str,
    attendee_emails: list[str] | None = None,
) -> dict:
    """Proposes creating or changing a calendar event. Does NOT create it.

    This tool never touches the real calendar. It returns a structured
    proposal describing the intended change, for a human (or later, the
    Temporal task layer) to confirm and execute.

    Args:
        summary: Event title.
        start_iso: RFC3339 start timestamp, e.g. "2026-07-23T15:00:00Z".
        end_iso: RFC3339 end timestamp.
        attendee_emails: Optional list of attendee email addresses to invite.

    Returns:
        A dict describing the proposed action: {"action": "create_event",
        "status": "proposed", "summary": ..., "start_iso": ..., "end_iso": ...,
        "attendee_emails": ...}
    """
    return {
        "action": "create_event",
        "status": "proposed",
        "summary": summary,
        "start_iso": start_iso,
        "end_iso": end_iso,
        "attendee_emails": attendee_emails,
    }


calendar_agent = Agent(
    name="calendar_agent",
    model="gemini-flash-latest",
    description=(
        "Handles calendar-related requests: checking what's on the "
        "calendar, and proposing new events or reschedules. Never sends "
        "invites or creates events itself - always proposes first."
    ),
    instruction=(
      "You are the Calendar Agent. For questions about what's already "  
      "scheduled, use 'check_calendar'. For requests to create, move, or "
      "cancel an event, use 'propose_calendar_change' to describe the "
      "intended change - do not claim the event has been created, since "
      "this tool only proposes changes for later confirmation."
    ),
    tools=[check_calendar, propose_calendar_change],
)