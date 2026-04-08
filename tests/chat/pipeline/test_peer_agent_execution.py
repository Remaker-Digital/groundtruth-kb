"""Slice 0a: S230 peer-agent routing execution-level regression tests.

Tests drive _handle_peer_agent() through success, denied, and error paths,
asserting actual dispatch kwargs, emitted event sequences, metadata persistence,
and fallback behavior.

Test plan ref: COMPREHENSIVE-TEST-PLAN-S245-S255.md Slice 0a

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import pytest
from dataclasses import dataclass, field
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch


# ---------------------------------------------------------------------------
# Lightweight stub for DispatchResult (avoids full plugin import)
# ---------------------------------------------------------------------------

@dataclass
class FakeDispatchResult:
    result: dict[str, Any] | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _collect_events(async_gen) -> list[dict]:
    """Drain an async generator into a list of SSE event dicts."""
    events = []
    async for event in async_gen:
        events.append(event)
    return events


def _make_orchestrator():
    """Create a minimal ChatPipeline-like orchestrator with mocked dependencies."""
    from src.chat.pipeline.orchestrator import ChatPipeline

    mock_session = MagicMock()
    mock_session.add_ai_message = AsyncMock(return_value="msg-001")
    mock_session.update_conversation_metadata = AsyncMock()
    mock_session.get_conversation = AsyncMock(return_value=MagicMock(turn_count=3))

    orch = ChatPipeline.__new__(ChatPipeline)
    orch._session = mock_session
    orch._background_tasks = set()

    def create_bg(coro, name=""):
        import asyncio
        task = asyncio.ensure_future(coro)
        orch._background_tasks.add(task)
        task.add_done_callback(orch._background_tasks.discard)

    orch._create_background_task = create_bg
    orch._fire_analytics = AsyncMock()

    return orch


def _make_budget():
    """Create a PipelineTimeoutBudget mock."""
    budget = MagicMock()
    budget.elapsed_ms = 150.0
    budget.stages = []

    async def execute_with_budget(agent_id, coro):
        result = await coro
        budget.stages.append(MagicMock(stage=agent_id, elapsed_ms=100.0, succeeded=True))
        return result

    budget.execute_with_budget = execute_with_budget
    return budget


def _make_trace():
    """Create a DecisionTraceBuilder mock."""
    trace = MagicMock()
    trace.add_stage = MagicMock()
    return trace


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestPeerAgentExecution:
    """Execution-level tests for _handle_peer_agent in the orchestrator."""

    @pytest.mark.asyncio
    async def test_success_path_emits_correct_event_sequence(self):
        """Happy path: dispatch succeeds, events emitted in correct order."""
        orch = _make_orchestrator()
        budget = _make_budget()
        trace = _make_trace()

        success_result = FakeDispatchResult(
            result={"response": "I found your order #12345.", "model": "gpt-4o"},
        )

        with patch("src.agents.plugins.dispatch.PluginDispatcher") as MockDispatcher, \
             patch("src.agents.plugins.events.emit_invocation"):
            MockDispatcher.return_value.dispatch_with_binding = AsyncMock(return_value=success_result)

            events = await _collect_events(
                orch._handle_peer_agent(
                    tenant_id="t-001",
                    conversation_id="conv-001",
                    customer_message="Where is my order?",
                    agent_id="orders-agent",
                    skill_id="track_order",
                    budget=budget,
                    trace=trace,
                    trace_id="trace-001",
                )
            )

        # Verify event sequence: started -> completed -> token -> validated -> done
        event_strs = [str(e) for e in events]
        assert "started" in event_strs[0], "First event should be a stage event (started)"
        assert any("I found your order" in s for s in event_strs), \
            "Should emit a token event with the response"

        # Session received the response
        orch._session.add_ai_message.assert_called_once()
        call_kwargs = orch._session.add_ai_message.call_args
        assert call_kwargs.kwargs.get("content") == "I found your order #12345." or \
               (call_kwargs.args and "I found your order #12345." in str(call_kwargs))

        # Pipeline trace persisted
        orch._session.update_conversation_metadata.assert_called_once()

    @pytest.mark.asyncio
    async def test_denied_result_dispatches_then_returns_fallback(self):
        """Denied path: dispatch IS called, denied result produces fallback."""
        orch = _make_orchestrator()
        budget = _make_budget()
        trace = _make_trace()

        denied_result = FakeDispatchResult(
            error="denied: tier-gate blocked",
            metadata={"policy_verdict": "denied"},
        )

        with patch("src.agents.plugins.dispatch.PluginDispatcher") as MockDispatcher, \
             patch("src.agents.plugins.events.emit_invocation") as mock_emit:
            MockDispatcher.return_value.dispatch_with_binding = AsyncMock(return_value=denied_result)

            await _collect_events(
                orch._handle_peer_agent(
                    tenant_id="t-001",
                    conversation_id="conv-001",
                    customer_message="Help me",
                    agent_id="premium-agent",
                    skill_id=None,
                    budget=budget,
                    trace=trace,
                )
            )

        # Dispatch WAS called (not skipped)
        MockDispatcher.return_value.dispatch_with_binding.assert_called_once()

        # emit_invocation called with result_class="denied"
        mock_emit.assert_called()
        emit_kwargs = mock_emit.call_args.kwargs if mock_emit.call_args.kwargs else {}
        assert emit_kwargs.get("result_class") == "denied"

        # Fallback message in response
        orch._session.add_ai_message.assert_called_once()
        content_arg = orch._session.add_ai_message.call_args.kwargs.get(
            "content", str(orch._session.add_ai_message.call_args)
        )
        assert "wasn't able to connect" in content_arg

    @pytest.mark.asyncio
    async def test_dispatch_error_emits_fallback_and_error_event(self):
        """Error path: dispatch raises, fallback message emitted."""
        orch = _make_orchestrator()
        budget = _make_budget()
        trace = _make_trace()

        with patch("src.agents.plugins.dispatch.PluginDispatcher") as MockDispatcher, \
             patch("src.agents.plugins.events.emit_invocation"):
            MockDispatcher.return_value.dispatch_with_binding = AsyncMock(
                side_effect=RuntimeError("Connection refused")
            )

            events = await _collect_events(
                orch._handle_peer_agent(
                    tenant_id="t-001",
                    conversation_id="conv-001",
                    customer_message="Help",
                    agent_id="broken-agent",
                    skill_id=None,
                    budget=budget,
                    trace=trace,
                )
            )

        # Fallback message in events
        event_content = " ".join(str(e) for e in events)
        assert "encountered an issue" in event_content or "try again" in event_content

    @pytest.mark.asyncio
    async def test_pipeline_trace_contains_peer_metadata(self):
        """Pipeline trace persisted with route_target, agent_id, latency."""
        orch = _make_orchestrator()
        budget = _make_budget()
        trace = _make_trace()

        success_result = FakeDispatchResult(
            result={"response": "Done.", "model": "gpt-4o-mini"},
        )

        with patch("src.agents.plugins.dispatch.PluginDispatcher") as MockDispatcher, \
             patch("src.agents.plugins.events.emit_invocation"):
            MockDispatcher.return_value.dispatch_with_binding = AsyncMock(return_value=success_result)

            await _collect_events(
                orch._handle_peer_agent(
                    tenant_id="t-001",
                    conversation_id="conv-001",
                    customer_message="Check order",
                    agent_id="orders-agent",
                    skill_id="track",
                    budget=budget,
                    trace=trace,
                    trace_id="trace-002",
                )
            )

        # Verify pipeline_trace metadata
        orch._session.update_conversation_metadata.assert_called_once()
        meta_call = orch._session.update_conversation_metadata.call_args
        metadata = meta_call.kwargs.get("metadata", {})
        peer_trace = metadata.get("pipeline_trace", {})
        assert peer_trace.get("route_target") == "peer_agent"
        assert peer_trace.get("route_agent_id") == "orders-agent"
        assert "total_latency_ms" in peer_trace

    @pytest.mark.asyncio
    async def test_agents_invoked_includes_peer_agent(self):
        """agents_invoked list passed to add_ai_message includes the peer agent."""
        orch = _make_orchestrator()
        budget = _make_budget()
        trace = _make_trace()

        success_result = FakeDispatchResult(
            result={"response": "Here's your info.", "model": "gpt-4o"},
        )

        with patch("src.agents.plugins.dispatch.PluginDispatcher") as MockDispatcher, \
             patch("src.agents.plugins.events.emit_invocation"):
            MockDispatcher.return_value.dispatch_with_binding = AsyncMock(return_value=success_result)

            await _collect_events(
                orch._handle_peer_agent(
                    tenant_id="t-001",
                    conversation_id="conv-001",
                    customer_message="Info please",
                    agent_id="info-agent",
                    skill_id=None,
                    budget=budget,
                    trace=trace,
                )
            )

        call_kwargs = orch._session.add_ai_message.call_args.kwargs
        agents = call_kwargs.get("agents_invoked", [])
        assert "info-agent" in agents

    @pytest.mark.asyncio
    async def test_budget_timeout_raises_pipeline_timeout(self):
        """Budget timeout during dispatch raises PipelineTimeoutError."""
        from src.multi_tenant.pipeline_resilience import PipelineTimeoutError

        orch = _make_orchestrator()
        trace = _make_trace()

        # Create a budget that raises on execute_with_budget
        budget = MagicMock()
        budget.elapsed_ms = 5000.0
        budget.stages = []

        async def timeout_execute(agent_id, coro):
            raise PipelineTimeoutError(agent_id, budget_ms=5000, elapsed_ms=5100.0)

        budget.execute_with_budget = timeout_execute

        with patch("src.agents.plugins.dispatch.PluginDispatcher"), \
             patch("src.agents.plugins.events.emit_invocation"):
            with pytest.raises(PipelineTimeoutError):
                await _collect_events(
                    orch._handle_peer_agent(
                        tenant_id="t-001",
                        conversation_id="conv-001",
                        customer_message="Help",
                        agent_id="slow-agent",
                        skill_id=None,
                        budget=budget,
                        trace=trace,
                    )
                )
