"""SSE error handling tests — WI #131.

Tests for:
    - _classify_openai_error() error classification
    - Enhanced error_event() with recoverable, tokens_sent, stage fields
    - Mid-stream error handling in pipeline execute()
    - Outer except block enhanced error events

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.chat.models import (
    StreamEvent,
    StreamEventType,
    error_event,
)
from src.chat.pipeline import _classify_openai_error


# ---------------------------------------------------------------------------
# _classify_openai_error tests
# ---------------------------------------------------------------------------


class TestClassifyOpenaiError:
    """Tests for _classify_openai_error() — Azure OpenAI exception classifier."""

    def test_rate_limit_by_type_name(self) -> None:
        """RateLimitError class name maps to rate_limited."""
        exc = type("RateLimitError", (Exception,), {})("Too many requests")
        code, msg, recoverable = _classify_openai_error(exc)
        assert code == "rate_limited"
        assert recoverable is True

    def test_rate_limit_by_status_429(self) -> None:
        """Exception mentioning 429 maps to rate_limited."""
        exc = Exception("Error code: 429 - Rate limit exceeded")
        code, msg, recoverable = _classify_openai_error(exc)
        assert code == "rate_limited"
        assert recoverable is True

    def test_content_filter_triggered(self) -> None:
        """Content filter exception maps to content_filtered (non-recoverable)."""
        exc = Exception("content_filter triggered for this prompt")
        code, msg, recoverable = _classify_openai_error(exc)
        assert code == "content_filtered"
        assert recoverable is False

    def test_content_filter_camelcase(self) -> None:
        """ContentFilter variation also detected."""
        exc = Exception("ContentFilter policy violation")
        code, msg, recoverable = _classify_openai_error(exc)
        assert code == "content_filtered"
        assert recoverable is False

    def test_model_overloaded_503(self) -> None:
        """503 status maps to model_overloaded."""
        exc = Exception("Error code: 503 - Service Unavailable")
        code, msg, recoverable = _classify_openai_error(exc)
        assert code == "model_overloaded"
        assert recoverable is True

    def test_model_overloaded_by_message(self) -> None:
        """Exception mentioning 'overloaded' maps to model_overloaded."""
        exc = Exception("The model is currently overloaded")
        code, msg, recoverable = _classify_openai_error(exc)
        assert code == "model_overloaded"
        assert recoverable is True

    def test_model_server_error(self) -> None:
        """Exception mentioning 'server_error' maps to model_overloaded."""
        exc = Exception("server_error in processing request")
        code, msg, recoverable = _classify_openai_error(exc)
        assert code == "model_overloaded"
        assert recoverable is True

    def test_timeout_by_type_name(self) -> None:
        """TimeoutError class maps to generation_timeout."""
        exc = TimeoutError("Request timed out")
        code, msg, recoverable = _classify_openai_error(exc)
        assert code == "generation_timeout"
        assert recoverable is True

    def test_timeout_by_message(self) -> None:
        """Exception mentioning timeout maps to generation_timeout."""
        exc = Exception("Connection timeout after 30s")
        code, msg, recoverable = _classify_openai_error(exc)
        assert code == "generation_timeout"
        assert recoverable is True

    def test_auth_error_401(self) -> None:
        """401 auth error maps to ai_configuration_error (non-recoverable)."""
        exc = Exception("Error code: 401 - Unauthorized")
        code, msg, recoverable = _classify_openai_error(exc)
        assert code == "ai_configuration_error"
        assert recoverable is False

    def test_auth_error_403(self) -> None:
        """403 auth error maps to ai_configuration_error."""
        exc = Exception("Error code: 403 - Forbidden")
        code, msg, recoverable = _classify_openai_error(exc)
        assert code == "ai_configuration_error"
        assert recoverable is False

    def test_auth_error_by_type(self) -> None:
        """AuthenticationError class maps to ai_configuration_error."""
        exc = type("AuthenticationError", (Exception,), {})("Invalid API key")
        code, msg, recoverable = _classify_openai_error(exc)
        assert code == "ai_configuration_error"
        assert recoverable is False

    def test_connection_error_by_type(self) -> None:
        """ConnectionError class maps to ai_connection_error."""
        exc = ConnectionError("Connection refused")
        code, msg, recoverable = _classify_openai_error(exc)
        assert code == "ai_connection_error"
        assert recoverable is True

    def test_connection_error_by_message(self) -> None:
        """Exception mentioning connection maps to ai_connection_error."""
        exc = Exception("Failed to establish a new connection")
        code, msg, recoverable = _classify_openai_error(exc)
        assert code == "ai_connection_error"
        assert recoverable is True

    def test_generic_fallback(self) -> None:
        """Unknown exception maps to generation_error (recoverable)."""
        exc = ValueError("Something unexpected happened")
        code, msg, recoverable = _classify_openai_error(exc)
        assert code == "generation_error"
        assert recoverable is True

    def test_all_return_human_readable_message(self) -> None:
        """All error codes return non-empty human-readable messages."""
        test_cases = [
            type("RateLimitError", (Exception,), {})(""),
            Exception("content_filter blocked"),
            Exception("503"),
            TimeoutError(""),
            Exception("401 Unauthorized"),
            ConnectionError(""),
            ValueError("generic"),
        ]
        for exc in test_cases:
            _, msg, _ = _classify_openai_error(exc)
            assert len(msg) > 10, f"Message too short for {type(exc).__name__}: {msg}"


# ---------------------------------------------------------------------------
# Enhanced error_event() model tests
# ---------------------------------------------------------------------------


class TestEnhancedErrorEvent:
    """Tests for the enhanced error_event() factory function."""

    def test_basic_error_event(self) -> None:
        """Basic error event with just message and code."""
        event = error_event("Something failed", code="test_error")
        assert event.event == StreamEventType.ERROR
        assert event.data["message"] == "Something failed"
        assert event.data["code"] == "test_error"
        assert event.data["recoverable"] is True  # default
        assert "tokens_sent" not in event.data
        assert "stage" not in event.data

    def test_error_event_with_recoverable_false(self) -> None:
        """Non-recoverable error event."""
        event = error_event("Config error", code="config", recoverable=False)
        assert event.data["recoverable"] is False

    def test_error_event_with_tokens_sent(self) -> None:
        """Error event tracking partial response tokens."""
        event = error_event("Mid-stream fail", tokens_sent=42)
        assert event.data["tokens_sent"] == 42

    def test_error_event_with_stage(self) -> None:
        """Error event with pipeline stage attribution."""
        event = error_event("Stage failed", stage="response-generator")
        assert event.data["stage"] == "response-generator"

    def test_error_event_full_fields(self) -> None:
        """Error event with all enhanced fields."""
        event = error_event(
            "Rate limited during generation",
            code="rate_limited",
            recoverable=True,
            tokens_sent=15,
            stage="response-generator",
        )
        assert event.data == {
            "message": "Rate limited during generation",
            "code": "rate_limited",
            "recoverable": True,
            "tokens_sent": 15,
            "stage": "response-generator",
        }

    def test_error_event_tokens_sent_zero(self) -> None:
        """tokens_sent=0 means error before any tokens streamed."""
        event = error_event("Failed before streaming", tokens_sent=0)
        assert event.data["tokens_sent"] == 0

    def test_error_event_sse_serialization(self) -> None:
        """Enhanced error event serializes correctly to SSE format."""
        event = error_event(
            "test", code="test_code",
            recoverable=False, tokens_sent=5, stage="critic",
        )
        sse = event.to_sse()
        assert "event: error" in sse
        assert '"recoverable": false' in sse
        assert '"tokens_sent": 5' in sse
        assert '"stage": "critic"' in sse

    def test_error_event_default_code(self) -> None:
        """Default code is pipeline_error."""
        event = error_event("generic failure")
        assert event.data["code"] == "pipeline_error"

    def test_error_event_omits_none_tokens(self) -> None:
        """tokens_sent=None means field is omitted (not set to null)."""
        event = error_event("test", tokens_sent=None)
        assert "tokens_sent" not in event.data

    def test_error_event_omits_none_stage(self) -> None:
        """stage=None means field is omitted."""
        event = error_event("test", stage=None)
        assert "stage" not in event.data


# ---------------------------------------------------------------------------
# Pipeline mid-stream error handling integration tests
# ---------------------------------------------------------------------------


class TestPipelineMidStreamErrors:
    """Tests for pipeline execute() mid-stream error handling.

    These tests verify that errors during response generation emit
    properly classified error events with token tracking. Uses full
    ChatPipeline with all internal methods mocked to isolate the
    streaming error handling logic.
    """

    @pytest.fixture()
    def mock_session(self) -> AsyncMock:
        """Mock ConversationSession."""
        session = AsyncMock()
        session.get_conversation.return_value = MagicMock(
            turn_count=1,
            customer_id=None,
        )
        session.add_ai_message.return_value = "msg-001"
        # set_pii_scrubber is synchronous — prevent AsyncMock auto-coroutine
        session.set_pii_scrubber = MagicMock()
        return session

    @pytest.fixture()
    def mock_preferences(self) -> MagicMock:
        """Mock PreferencesDocument."""
        prefs = MagicMock()
        prefs.fine_tuning_enabled = False
        prefs.fine_tuning_active_model_id = None
        prefs.fine_tuning_ab_experiment_id = None
        return prefs

    @pytest.fixture()
    def mock_tenant(self) -> MagicMock:
        """Mock TenantDocument."""
        from src.multi_tenant.cosmos_schema import TenantTier
        tenant = MagicMock()
        tenant.tier = TenantTier.STARTER
        return tenant

    @pytest.fixture()
    def pipeline(self, mock_session: AsyncMock) -> Any:
        """Create a ChatPipeline with mocked dependencies."""
        from src.chat.pipeline import ChatPipeline
        from src.multi_tenant.system_prompt_builder import AgentRole

        mock_prompt_builder = MagicMock()
        mock_prompt_builder.build_all.return_value = {
            AgentRole.INTENT_CLASSIFIER: "prompt",
            AgentRole.KNOWLEDGE_RETRIEVAL: "prompt",
            AgentRole.RESPONSE_GENERATOR: "prompt",
            AgentRole.ESCALATION_HANDLER: "prompt",
            AgentRole.ANALYTICS_COLLECTOR: "prompt",
            AgentRole.CRITIC_SUPERVISOR: "prompt",
        }
        mock_prompt_builder.explain.return_value = {}
        mock_profile_service = AsyncMock()
        p = ChatPipeline(
            session=mock_session,
            prompt_builder=mock_prompt_builder,
            profile_service=mock_profile_service,
        )
        return p

    @pytest.fixture(autouse=True)
    def _patch_internals(self) -> Any:
        """Patch DecisionTraceBuilder and PipelineTimeoutBudget."""
        mock_trace = MagicMock()
        mock_trace.build.return_value = MagicMock()

        mock_budget = MagicMock()
        mock_budget.elapsed_ms = 500.0
        mock_budget.stages = []

        # execute_with_budget: run the coroutine directly
        async def run_coro(stage_name: str, coro: Any) -> Any:
            result = await coro
            mock_budget.stages.append(MagicMock(stage=stage_name, elapsed_ms=100.0))
            return result

        mock_budget.execute_with_budget = AsyncMock(side_effect=run_coro)

        with (
            patch(
                "src.chat.pipeline.DecisionTraceBuilder",
                return_value=mock_trace,
            ),
            patch(
                "src.chat.pipeline.PipelineTimeoutBudget",
                return_value=mock_budget,
            ),
        ):
            yield

    async def _collect_events(self, gen: Any) -> list[StreamEvent]:
        """Collect all events from an async generator."""
        events = []
        async for event in gen:
            events.append(event)
        return events

    @pytest.mark.asyncio
    async def test_rate_limit_mid_stream_emits_classified_error(
        self, pipeline: Any, mock_session: AsyncMock,
        mock_tenant: MagicMock, mock_preferences: MagicMock,
    ) -> None:
        """Rate limit during streaming emits rate_limited error with tokens_sent."""

        async def mock_stream(*args: Any, **kwargs: Any) -> Any:
            yield "Hello "
            yield "world"
            raise type("RateLimitError", (Exception,), {})("429 rate limit")

        with (
            patch.object(pipeline, "_call_intent_classifier", new_callable=AsyncMock, return_value={
                "intent": "general_inquiry", "confidence": 0.95,
            }),
            patch.object(pipeline, "_call_knowledge_retrieval", new_callable=AsyncMock, return_value={
                "context": "some context", "sources": [],
            }),
            patch.object(pipeline, "_call_response_generator_stream", side_effect=mock_stream),
            patch.object(pipeline, "_load_customer_profile", new_callable=AsyncMock, return_value=None),
            patch.object(pipeline, "_fire_analytics", new_callable=AsyncMock),
        ):
            events = await self._collect_events(
                pipeline.execute(
                    "t-001", "conv-001", "Hello?",
                    tenant=mock_tenant, preferences=mock_preferences,
                )
            )

        token_events = [e for e in events if e.event == StreamEventType.TOKEN]
        error_events = [e for e in events if e.event == StreamEventType.ERROR]
        done_events = [e for e in events if e.event == StreamEventType.DONE]

        assert len(token_events) == 2
        assert len(error_events) == 1
        assert len(done_events) == 1

        err = error_events[0]
        assert err.data["code"] == "rate_limited"
        assert err.data["recoverable"] is True
        assert err.data["tokens_sent"] == 2
        assert err.data["stage"] == "response-generator"

    @pytest.mark.asyncio
    async def test_content_filter_mid_stream_non_recoverable(
        self, pipeline: Any, mock_session: AsyncMock,
        mock_tenant: MagicMock, mock_preferences: MagicMock,
    ) -> None:
        """Content filter during streaming emits non-recoverable error."""

        async def mock_stream(*args: Any, **kwargs: Any) -> Any:
            yield "Starting "
            raise Exception("content_filter triggered")

        with (
            patch.object(pipeline, "_call_intent_classifier", new_callable=AsyncMock, return_value={
                "intent": "general_inquiry", "confidence": 0.95,
            }),
            patch.object(pipeline, "_call_knowledge_retrieval", new_callable=AsyncMock, return_value={
                "context": "", "sources": [],
            }),
            patch.object(pipeline, "_call_response_generator_stream", side_effect=mock_stream),
            patch.object(pipeline, "_load_customer_profile", new_callable=AsyncMock, return_value=None),
        ):
            events = await self._collect_events(
                pipeline.execute(
                    "t-001", "conv-001", "test",
                    tenant=mock_tenant, preferences=mock_preferences,
                )
            )

        error_events = [e for e in events if e.event == StreamEventType.ERROR]
        assert len(error_events) == 1
        assert error_events[0].data["code"] == "content_filtered"
        assert error_events[0].data["recoverable"] is False
        assert error_events[0].data["tokens_sent"] == 1

    @pytest.mark.asyncio
    async def test_error_before_any_tokens(
        self, pipeline: Any, mock_session: AsyncMock,
        mock_tenant: MagicMock, mock_preferences: MagicMock,
    ) -> None:
        """Error before any tokens yields tokens_sent=0."""

        async def mock_stream(*args: Any, **kwargs: Any) -> Any:
            raise ConnectionError("Connection refused")
            yield  # make it a generator  # noqa: E501

        with (
            patch.object(pipeline, "_call_intent_classifier", new_callable=AsyncMock, return_value={
                "intent": "general_inquiry", "confidence": 0.95,
            }),
            patch.object(pipeline, "_call_knowledge_retrieval", new_callable=AsyncMock, return_value={
                "context": "", "sources": [],
            }),
            patch.object(pipeline, "_call_response_generator_stream", side_effect=mock_stream),
            patch.object(pipeline, "_load_customer_profile", new_callable=AsyncMock, return_value=None),
        ):
            events = await self._collect_events(
                pipeline.execute(
                    "t-001", "conv-001", "test",
                    tenant=mock_tenant, preferences=mock_preferences,
                )
            )

        error_events = [e for e in events if e.event == StreamEventType.ERROR]
        assert len(error_events) == 1
        assert error_events[0].data["code"] == "ai_connection_error"
        assert error_events[0].data["tokens_sent"] == 0
        assert error_events[0].data["stage"] == "response-generator"


# ---------------------------------------------------------------------------
# Outer except block tests
# ---------------------------------------------------------------------------


class TestPipelineOuterErrorEvents:
    """Tests for outer except blocks having enhanced error_event fields."""

    def test_pipeline_timeout_has_stage(self) -> None:
        """PipelineTimeoutError error event includes stage field."""
        from src.multi_tenant.pipeline_resilience import PipelineTimeoutError

        exc = PipelineTimeoutError(stage="knowledge-retrieval", budget_ms=8000, elapsed_ms=8500)
        event = error_event(
            "Response took too long. Please try again.",
            code="pipeline_timeout",
            recoverable=True,
            stage=exc.stage,
        )
        assert event.data["stage"] == "knowledge-retrieval"
        assert event.data["recoverable"] is True
        assert event.data["code"] == "pipeline_timeout"

    def test_service_unavailable_has_stage(self) -> None:
        """ServiceUnavailableError error event includes service name as stage."""
        from src.multi_tenant.pipeline_resilience import ServiceUnavailableError

        exc = ServiceUnavailableError(service_name="azure-openai")
        event = error_event(
            "Service unavailable",
            code="service_unavailable",
            recoverable=True,
            stage=exc.service_name,
        )
        assert event.data["stage"] == "azure-openai"
        assert event.data["recoverable"] is True

    def test_internal_error_recoverable(self) -> None:
        """Generic internal errors are marked recoverable."""
        event = error_event(
            "An unexpected error occurred.",
            code="internal_error",
            recoverable=True,
        )
        assert event.data["recoverable"] is True
        assert "stage" not in event.data
