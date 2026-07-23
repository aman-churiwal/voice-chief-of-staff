"""ADK Root Agent: the top-level orchestrator. Routes calendar requests to
calendar_agent and email requests to email_agent. Has no tools of its own in
this phase, so every action goes through a sub-agent's propose-not-execute
tools.
"""
from google.adk.agents import Agent

from vcos.agents.calendar_agent import calendar_agent
from vcos.agents.email_agent import email_agent

root_agent = Agent(
    name="root_agent",
    model="gemini-flash-latest",
    description=(
      "Main coordinator for a personal productivity assistant. Routes "
      "calendar requests to calendar_agent and email requests to "
      "email_agent."
    ),
    instruction=(
        "You are the root coordinator of a personal productivity assistant. "
        "You have two specialists: "
        "1. 'calendar_agent' - handles anything about the user's calendar: "
        "checking what's scheduled, proposing new events or reschedules. "
        "2. 'email_agent' - handles anything about the user's email: "
        "searching the inbox, reading threads, proposing emails to send. "
        "Delegate every calendar-related request to calendar_agent and "
        "every email-related request to email_agent. If a request touches "
        "both (e.g. 'reschedule with Sam and email him'), delegate each "
        "part to the appropriate specialist in turn. Never claim an action "
        "was completed if a specialist only proposed it - tell the user "
        "what was proposed and that it's awaiting confirmation."
    ),
    tools=[],
    sub_agents=[calendar_agent, email_agent],
)