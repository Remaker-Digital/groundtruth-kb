# Agent Red — Co-Pilot Container Entry Point
#
# Run: uvicorn src.agents.containers.co_pilot_app:app --port 8087
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

from __future__ import annotations

import os

from src.agents.co_pilot import CoPilotAgent
from src.agents.containers.agent_app import create_agent_app


async def _configure(agent: CoPilotAgent) -> None:
    """Inject Azure OpenAI client and admin documentation repository."""
    try:
        from openai import AsyncAzureOpenAI

        endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
        api_key = os.environ.get("AZURE_OPENAI_API_KEY", "")
        if endpoint and api_key:
            client = AsyncAzureOpenAI(
                azure_endpoint=endpoint,
                api_key=api_key,
                api_version="2024-10-21",
            )
            agent.configure(client)
    except ImportError:
        pass


app = create_agent_app(CoPilotAgent, configure_fn=_configure)
