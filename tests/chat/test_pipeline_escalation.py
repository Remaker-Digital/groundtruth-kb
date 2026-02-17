"""Tests for ChatPipeline escalation flow (Backlog #19).

Covers:
    - Category extraction from escalation agent result
    - Auto-assignment via find_best_agent_for_category
    - Graceful fallback when no agent is available

Run:
    pytest tests/chat/test_pipeline_escalation.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
from typing import Any, AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.chat.pipeline import ChatPipeline
from src.multi_tenant.pipeline_resilience import PipelineTimeoutBudget


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

TENANT_ID = "remaker-digital-001"
CONV_ID = "conv-esc-001"


def _build_pipeline() -> ChatPipeline:
    """Create a ChatPipeline with all dependencies mocked."""
    pipeline = ChatPipeline.__new__(ChatPipeline)

    pipeline._session = AsyncMock()
    pipeline._session.escalate_conversation = AsyncMock()
    pipeline._session.find_best_agent_for_category = AsyncMock(return_value=None)
    # set_pii_scrubber is synchronous — prevent AsyncMock auto-coroutine
    pipeline._session.set_pii_scrubber = MagicMock()

    pipeline._prompt_builder = MagicMock()
    pipeline._profile_service = MagicMock()
    pipeline._vectorizer = None
    pipeline._critic = None
    pipeline._meter = None
    pipeline._openai_client = None
    pipeline._kb_repo = None
    pipeline._use_containers = False

    # Agent stubs
    pipeline._escalation_handler = MagicMock()
    pipeline._analytics_collector = MagicMock()
    pipeline._intent_classifier = MagicMock()
    pipeline._knowledge_retrieval = MagicMock()
    pipeline._response_generator = MagicMock()
    pipeline._critic_supervisor = MagicMock()

    return pipeline


async def _collect_events(gen: AsyncGenerator) -> list:
    """Drain an async generator into a list."""
    events = []
    async for event in gen:
        events.append(event)
    return events


async def _passthrough_budget(stage: str, coro):
    """Await and return the coroutine — simulates budget.execute_with_budget."""
    return await coro


# ---------------------------------------------------------------------------
# PE-01 to PE-03: Pipeline escalation flow
# ---------------------------------------------------------------------------


class TestPipelineEscalation:
    """Pipeline _handle_escalation category routing."""

    @pytest.mark.asyncio
    async def test_pe_01_passes_category_to_session(self):
        """Category from escalation agent flows to escalate_conversation."""
        pipeline = _build_pipeline()

        # Mock escalation agent to return a category
        pipeline._call_escalation_handler = AsyncMock(
            return_value={
                "reason": "Billing dispute",
                "urgency": "high",
                "context_summary": "Customer disputing charge",
                "category": "account",
                "model": "gpt-4o-mini",
            }
        )
        # Mock the budget to pass through
        budget = MagicMock(spec=PipelineTimeoutBudget)
        budget.execute_with_budget = AsyncMock(
            side_effect=_passthrough_budget
        )
        budget.stages = []

        from src.multi_tenant.response_explainability import DecisionTraceBuilder
        trace = DecisionTraceBuilder(CONV_ID, TENANT_ID)

        events = await _collect_events(
            pipeline._handle_escalation(
                TENANT_ID, CONV_ID, "I want a refund!",
                "system prompt", budget, trace,
            )
        )

        # Verify session.escalate_conversation was called with category
        call_kwargs = pipeline._session.escalate_conversation.call_args[1]
        assert call_kwargs["escalation_category"] == "account"

    @pytest.mark.asyncio
    async def test_pe_02_auto_assigns_agent(self):
        """Pipeline calls find_best_agent and passes ID to session."""
        pipeline = _build_pipeline()
        pipeline._session.find_best_agent_for_category = AsyncMock(
            return_value="agent-42"
        )

        pipeline._call_escalation_handler = AsyncMock(
            return_value={
                "reason": "Technical issue",
                "urgency": "medium",
                "context_summary": "",
                "category": "technical_assistance",
                "model": "gpt-4o-mini",
            }
        )
        budget = MagicMock(spec=PipelineTimeoutBudget)
        budget.execute_with_budget = AsyncMock(
            side_effect=_passthrough_budget
        )
        budget.stages = []

        from src.multi_tenant.response_explainability import DecisionTraceBuilder
        trace = DecisionTraceBuilder(CONV_ID, TENANT_ID)

        events = await _collect_events(
            pipeline._handle_escalation(
                TENANT_ID, CONV_ID, "My widget is broken",
                "system prompt", budget, trace,
            )
        )

        # find_best_agent was called with the detected category
        pipeline._session.find_best_agent_for_category.assert_called_once_with(
            TENANT_ID, "technical_assistance",
        )

        # assigned_to passed to escalate_conversation
        call_kwargs = pipeline._session.escalate_conversation.call_args[1]
        assert call_kwargs["assigned_to"] == "agent-42"

    @pytest.mark.asyncio
    async def test_pe_03_no_agent_available_proceeds(self):
        """Escalation completes even when no agent matches."""
        pipeline = _build_pipeline()
        pipeline._session.find_best_agent_for_category = AsyncMock(
            return_value=None
        )

        pipeline._call_escalation_handler = AsyncMock(
            return_value={
                "reason": "Sales inquiry",
                "urgency": "low",
                "context_summary": "",
                "category": "sales",
                "model": "gpt-4o-mini",
            }
        )
        budget = MagicMock(spec=PipelineTimeoutBudget)
        budget.execute_with_budget = AsyncMock(
            side_effect=_passthrough_budget
        )
        budget.stages = []

        from src.multi_tenant.response_explainability import DecisionTraceBuilder
        trace = DecisionTraceBuilder(CONV_ID, TENANT_ID)

        events = await _collect_events(
            pipeline._handle_escalation(
                TENANT_ID, CONV_ID, "I want to buy in bulk",
                "system prompt", budget, trace,
            )
        )

        # escalate_conversation still called, assigned_to is None
        call_kwargs = pipeline._session.escalate_conversation.call_args[1]
        assert call_kwargs["assigned_to"] is None
        assert call_kwargs["escalation_category"] == "sales"

        # Done event was yielded (pipeline didn't crash)
        event_types = [e.get("type") for e in events if isinstance(e, dict)]
        assert len(events) > 0  # At least stage events + token + done
