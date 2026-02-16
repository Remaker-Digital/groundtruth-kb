# Agent Red — Analytics Collector Container Entry Point
#
# Run: uvicorn src.agents.containers.analytics_collector_app:app --port 8085
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

from __future__ import annotations

from src.agents.containers.agent_app import create_agent_app
from src.agents.analytics_collector import AnalyticsCollectorAgent

app = create_agent_app(AnalyticsCollectorAgent)
