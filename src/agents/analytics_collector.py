# Agent Red Customer Experience — Analytics Collector Agent
#
# Receives span/metric data from all pipeline agents and persists it.
# Fire-and-forget: failures never block the pipeline.
#
# Extracted from pipeline.py _fire_analytics().
#
# Input payload:
#   {"tenant_id": str, "conversation_id": str, "intent": str,
#    "stages": [{"stage": str, "elapsed_ms": float, "succeeded": bool}],
#    "total_latency_ms": float}
#
# Output payload:
#   {"collected": bool, "event_count": int}
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

from __future__ import annotations

import logging
from typing import Any

from src.agents.base import AgentRedBaseAgent

logger = logging.getLogger(__name__)


class AnalyticsCollectorAgent(AgentRedBaseAgent):
    """Collect pipeline analytics events.

    Receives stage-level metrics from the pipeline orchestrator and logs
    them. In production, this agent will persist to a time-series store
    or forward to Azure Monitor.
    """

    agent_type = "analytics-collector"

    async def process(
        self,
        payload: dict[str, Any],
        headers: dict[str, str],
    ) -> dict[str, Any]:
        """Collect analytics event.

        Args:
            payload: Analytics event data with stages and latency.
            headers: A2A headers.

        Returns:
            {"collected": bool, "event_count": int}
        """
        tenant_id = payload.get("tenant_id", "unknown")
        conversation_id = payload.get("conversation_id", "unknown")
        intent = payload.get("intent", "unknown")
        stages = payload.get("stages", [])
        total_latency_ms = payload.get("total_latency_ms", 0)

        logger.info(
            "Analytics: tenant=%s conv=%s intent=%s stages=%d latency=%.0fms",
            tenant_id,
            conversation_id,
            intent,
            len(stages),
            total_latency_ms,
        )

        # Log per-stage metrics
        for stage in stages:
            logger.debug(
                "  Stage %s: %.0fms success=%s",
                stage.get("stage", "?"),
                stage.get("elapsed_ms", 0),
                stage.get("succeeded", True),
            )

        return {
            "collected": True,
            "event_count": len(stages),
        }
