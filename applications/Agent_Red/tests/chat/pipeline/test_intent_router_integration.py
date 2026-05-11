"""IntentRouter integration tests (SPEC-1861).

Verify IntentRouter is wired into the orchestrator, trace builder
includes route decision, and peer agent handler has correct call
signatures for dispatch_with_binding and SSE helpers.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import inspect



class TestOrchestratorWiring:
    """Verify IntentRouter is wired into the live orchestrator."""

    def test_orchestrator_uses_intent_router(self):
        """execute() imports and calls IntentRouter.resolve()."""
        from src.chat.pipeline import orchestrator
        source = inspect.getsource(orchestrator)
        assert "IntentRouter" in source
        assert "router.resolve(" in source
        assert "RouteTarget.ESCALATION" in source
        assert "RouteTarget.CO_PILOT" in source
        assert "RouteTarget.PEER_AGENT" in source

    def test_hardcoded_escalation_check_removed(self):
        """The old 'if intent == ESCALATION_INTENT' pattern is gone."""
        from src.chat.pipeline import orchestrator
        source = inspect.getsource(orchestrator.ChatPipeline.execute)
        assert "if intent == ESCALATION_INTENT" not in source
        assert "route.target == RouteTarget.ESCALATION" in source

    def test_hardcoded_copilot_check_removed(self):
        """The old 'if team_member_role or intent == ADMIN_ASSISTANCE_INTENT' is gone."""
        from src.chat.pipeline import orchestrator
        source = inspect.getsource(orchestrator.ChatPipeline.execute)
        assert "if team_member_role or intent == ADMIN_ASSISTANCE_INTENT" not in source
        assert "route.target == RouteTarget.CO_PILOT" in source

    def test_overlay_store_wired(self):
        """execute() loads overlay store for IntentRouter (not None)."""
        from src.chat.pipeline import orchestrator
        source = inspect.getsource(orchestrator.ChatPipeline.execute)
        assert "_get_tenant_overlays" in source
        assert "overlay_store=None" not in source


class TestTraceIntegration:
    """Verify trace builder includes route decision."""

    def test_pipeline_trace_includes_route_fields(self):
        """pipeline_trace dict includes route_target and route_agent_id."""
        from src.chat.pipeline import orchestrator
        source = inspect.getsource(orchestrator)
        assert '"route_target"' in source
        assert '"route_agent_id"' in source

    def test_trace_builder_has_set_route_decision(self):
        """DecisionTraceBuilder has set_route_decision method."""
        from src.multi_tenant.response_explainability import DecisionTraceBuilder
        assert hasattr(DecisionTraceBuilder, "set_route_decision")

    def test_response_decision_trace_has_route_fields(self):
        """ResponseDecisionTrace dataclass has route_target field."""
        from src.multi_tenant.response_explainability import ResponseDecisionTrace
        trace = ResponseDecisionTrace()
        assert hasattr(trace, "route_target")
        assert hasattr(trace, "route_agent_id")
        assert hasattr(trace, "route_fallback_from")


class TestPeerAgentHandlerSignatures:
    """Verify _handle_peer_agent uses correct call signatures (Codex P1 fix)."""

    def test_dispatch_with_binding_has_agent_id_and_skill_id(self):
        """dispatch_with_binding() call includes agent_id and skill_id kwargs."""
        from src.chat.pipeline.orchestrator import ChatPipeline
        source = inspect.getsource(ChatPipeline._handle_peer_agent)
        assert "agent_id=agent_id" in source
        assert "skill_id=effective_skill" in source

    def test_validated_event_uses_conversation_id_and_message_id(self):
        """validated_event() uses (conversation_id, message_id) signature."""
        from src.chat.pipeline.orchestrator import ChatPipeline
        source = inspect.getsource(ChatPipeline._handle_peer_agent)
        assert "validated_event(conversation_id," in source

    def test_done_event_uses_conversation_id_and_turn_count(self):
        """done_event() uses (conversation_id, turn_count, ...) signature."""
        from src.chat.pipeline.orchestrator import ChatPipeline
        source = inspect.getsource(ChatPipeline._handle_peer_agent)
        assert "done_event(\n                conversation_id, 0," in source or "done_event(conversation_id, 0" in source

    def test_peer_handler_persists_pipeline_trace(self):
        """_handle_peer_agent persists pipeline_trace via metadata dict."""
        from src.chat.pipeline.orchestrator import ChatPipeline
        source = inspect.getsource(ChatPipeline._handle_peer_agent)
        assert "update_conversation_metadata" in source
        assert 'metadata={"pipeline_trace": peer_trace}' in source

    def test_peer_handler_done_event_uses_turn_count(self):
        """_handle_peer_agent retrieves turn_count via attribute access on ConversationStateResponse."""
        from src.chat.pipeline.orchestrator import ChatPipeline
        source = inspect.getsource(ChatPipeline._handle_peer_agent)
        # Must use attribute access (.turn_count) not dict access (.get("turn_count"))
        assert "conv.turn_count" in source
        assert 'conv.get("turn_count"' not in source

    def test_conversation_state_response_has_turn_count_attr(self):
        """ConversationStateResponse has turn_count as a Pydantic field."""
        from src.chat.models import ConversationStateResponse
        assert "turn_count" in ConversationStateResponse.model_fields

    def test_peer_handler_emits_invocation_events(self):
        """_handle_peer_agent emits invocation events for success/error/denial."""
        from src.chat.pipeline.orchestrator import ChatPipeline
        source = inspect.getsource(ChatPipeline._handle_peer_agent)
        assert "emit_invocation" in source
        assert 'result_class="success"' in source
        assert 'result_class="error"' in source

    def test_peer_handler_updates_agents_invoked(self):
        """_handle_peer_agent passes agent_id to agents_invoked."""
        from src.chat.pipeline.orchestrator import ChatPipeline
        source = inspect.getsource(ChatPipeline._handle_peer_agent)
        assert "agents_invoked=[agent_id]" in source


class TestDispatchSignatureContract:
    """Execution-level tests: verify call signatures compile correctly."""

    def test_dispatch_with_binding_accepts_all_required_kwargs(self):
        """dispatch_with_binding() signature accepts agent_id + skill_id."""
        from src.agents.plugins.dispatch import PluginDispatcher
        sig = inspect.signature(PluginDispatcher.dispatch_with_binding)
        params = sig.parameters
        assert "agent_id" in params
        assert "skill_id" in params
        assert "tenant_id" in params
        assert "conversation_id" in params

    def test_validated_event_signature(self):
        """validated_event() accepts (conversation_id, message_id)."""
        from src.chat.models import validated_event
        sig = inspect.signature(validated_event)
        params = list(sig.parameters.keys())
        assert params[0] == "conversation_id"
        assert params[1] == "message_id"

    def test_done_event_signature(self):
        """done_event() accepts (conversation_id, turn_count, ...)."""
        from src.chat.models import done_event
        sig = inspect.signature(done_event)
        params = list(sig.parameters.keys())
        assert params[0] == "conversation_id"
        assert params[1] == "turn_count"
