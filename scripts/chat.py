"""Interactive text REPL for the Voice Chief of Staff root agent.

Usage:
    python scripts/chat.py

Requires GOOGLE_API_KEY set in the environment and Google
OAuth already authorized via scripts/authorize_google.py.

Try:
    - "What's on my calendar today?"
    - "Reschedule my 3pm to tomorrow at the same time"
    - "Do I have any unread email from Sam?"
    - "Draft a reply to Aman saying I can do 4pm tomorrow"
"""
import asyncio

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from vcos.agents.root_agent import root_agent

APP_NAME = "vcos_chat"
USER_ID = "local_user"
SESSION_ID = "local_session"


async def main() -> None:
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    runner = Runner(
        agent=root_agent, app_name=APP_NAME, session_service=session_service
    )

    print("Voice Chief of Staff (text mode). Type 'quit' to exit.\n")
    while True:
        query = input("You: ").strip()
        if query.lower() in ("quit", "exit"):
            break

        content = types.Content(role="user" ,parts=[types.Part(text=query)])
        final_response = "(no response)"
        async for event in runner.run_async(
            user_id=USER_ID, session_id=SESSION_ID, new_message=content
        ):
            if event.is_final_response() and event.content and event.content.parts:
                final_response = event.content.parts[0].text

        print(f"Assistant: {final_response}\n")


if __name__ == "__main__":
    asyncio.run(main())