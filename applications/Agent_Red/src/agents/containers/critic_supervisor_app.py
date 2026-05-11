# Agent Red — Critic/Supervisor Container Entry Point
#
# Run: uvicorn src.agents.containers.critic_supervisor_app:app --port 8086
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

from __future__ import annotations

import os

from src.agents.containers.agent_app import create_agent_app
from src.agents.critic_supervisor import CriticSupervisorAgent


async def _configure(agent: CriticSupervisorAgent) -> None:
    """Inject Azure OpenAI client."""
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


app = create_agent_app(CriticSupervisorAgent, configure_fn=_configure)
