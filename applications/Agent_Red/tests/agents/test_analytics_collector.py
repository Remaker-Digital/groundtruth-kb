"""Tests for AnalyticsCollectorAgent.

Verifies:
    - Successful analytics collection
    - Event count matches stages count
    - Handles empty stages
    - Handles missing payload fields
    - Fire-and-forget semantics (no external deps)

Run:
    pytest tests/agents/test_analytics_collector.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import pytest

from src.agents.analytics_collector import AnalyticsCollectorAgent


# ---------------------------------------------------------------------------
# AC-01 to AC-05: Normal collection
# ---------------------------------------------------------------------------


class TestAnalyticsCollection:
    """AnalyticsCollectorAgent normal operation."""

    @pytest.mark.asyncio
    async def test_ac_01_collects_pipeline_analytics(self):
        """Collects analytics event and returns event count."""
        agent = AnalyticsCollectorAgent()

        stages = [
            {"stage": "intent_classifier", "elapsed_ms": 120.5, "succeeded": True},
            {"stage": "knowledge_retrieval", "elapsed_ms": 250.3, "succeeded": True},
            {"stage": "response_generator", "elapsed_ms": 890.1, "succeeded": True},
            {"stage": "critic_supervisor", "elapsed_ms": 180.0, "succeeded": True},
        ]

        result = await agent.process(
            {
                "tenant_id": "t-001",
                "conversation_id": "c-001",
                "intent": "product_question",
                "stages": stages,
                "total_latency_ms": 1441.0,
            },
            {},
        )

        assert result["collected"] is True
        assert result["event_count"] == 4

    @pytest.mark.asyncio
    async def test_ac_02_empty_stages(self):
        """Handles empty stages list."""
        agent = AnalyticsCollectorAgent()

        result = await agent.process(
            {
                "tenant_id": "t-001",
                "conversation_id": "c-001",
                "intent": "greeting",
                "stages": [],
                "total_latency_ms": 50.0,
            },
            {},
        )

        assert result["collected"] is True
        assert result["event_count"] == 0

    @pytest.mark.asyncio
    async def test_ac_03_missing_fields_uses_defaults(self):
        """Missing payload fields use 'unknown' defaults."""
        agent = AnalyticsCollectorAgent()

        result = await agent.process({}, {})

        assert result["collected"] is True
        assert result["event_count"] == 0

    @pytest.mark.asyncio
    async def test_ac_04_single_stage(self):
        """Single stage event."""
        agent = AnalyticsCollectorAgent()

        result = await agent.process(
            {
                "tenant_id": "t-001",
                "conversation_id": "c-001",
                "intent": "escalation",
                "stages": [
                    {"stage": "escalation_handler", "elapsed_ms": 95.0, "succeeded": True},
                ],
                "total_latency_ms": 95.0,
            },
            {},
        )

        assert result["collected"] is True
        assert result["event_count"] == 1

    @pytest.mark.asyncio
    async def test_ac_05_failed_stage_recorded(self):
        """Stages with succeeded=False are still counted."""
        agent = AnalyticsCollectorAgent()

        stages = [
            {"stage": "intent_classifier", "elapsed_ms": 100, "succeeded": True},
            {"stage": "knowledge_retrieval", "elapsed_ms": 500, "succeeded": False},
        ]

        result = await agent.process(
            {
                "tenant_id": "t-001",
                "conversation_id": "c-001",
                "stages": stages,
            },
            {},
        )

        assert result["event_count"] == 2


# ---------------------------------------------------------------------------
# AC-06 to AC-08: Agent identity and lifecycle
# ---------------------------------------------------------------------------


class TestAnalyticsIdentity:
    """Agent identity and lifecycle."""

    def test_ac_06_agent_type(self):
        """Agent type is 'analytics-collector'."""
        agent = AnalyticsCollectorAgent()
        assert agent.agent_type == "analytics-collector"
        assert agent.create_agent_topic() == "analytics-collector"

    def test_ac_07_no_configure_needed(self):
        """Analytics collector has no external dependencies to configure."""
        agent = AnalyticsCollectorAgent()
        # Should work without any configure() call
        assert agent.agent_type == "analytics-collector"

    @pytest.mark.asyncio
    async def test_ac_08_handle_message_integration(self):
        """Full handle_message() round-trip via A2A protocol."""
        from src.agents.base import make_request, parse_payload

        agent = AnalyticsCollectorAgent()

        req = make_request(
            "analytics-collector",
            {
                "tenant_id": "t-001",
                "conversation_id": "c-001",
                "intent": "product_question",
                "stages": [{"stage": "test", "elapsed_ms": 50, "succeeded": True}],
                "total_latency_ms": 50,
            },
        )

        msg = await agent.handle_message(req)
        result = parse_payload(msg)

        assert result["collected"] is True
        assert result["event_count"] == 1
        assert result["_agent"] == "analytics-collector"
        assert "_latency_ms" in result
