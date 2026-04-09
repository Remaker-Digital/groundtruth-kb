# Agent Red Customer Experience — Base Agent Protocol Implementation
#
# Abstract base class for all 6 Agent Red pipeline agents. Extends the
# AGNTCY SDK's BaseAgentProtocol with Agent Red conventions:
#   - JSON payload serialization (Message.payload is always UTF-8 JSON bytes)
#   - Tenant context propagation via message headers
#   - Structured error responses
#   - Health check support
#
# Subclasses implement process() with domain-specific logic extracted from
# the monolithic pipeline.py. The handle_message() wrapper handles
# serialization, error handling, and observability.
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

from __future__ import annotations

import json
import logging
import time
from abc import abstractmethod
from typing import Any

# AGNTCY SDK imports — wrapped in try/except per project lesson.
# The SDK's BaseAgentProtocol was renamed/removed in 0.5.x; provide a
# local ABC stub so the agent hierarchy works regardless of SDK version.
try:
    from agntcy_app_sdk.semantic.base import BaseAgentProtocol
except ImportError:
    from abc import ABC

    class BaseAgentProtocol(ABC):  # type: ignore[no-redef]
        """Local stub when agntcy_app_sdk.semantic.base.BaseAgentProtocol is unavailable."""
        pass

try:
    from agntcy_app_sdk.semantic.message import Message
except ImportError:

    class Message:  # type: ignore[no-redef]
        """Local stub for Message when agntcy_app_sdk is unavailable."""

        def __init__(self, **kwargs: Any) -> None:
            for k, v in kwargs.items():
                setattr(self, k, v)

try:
    from agntcy_app_sdk.transport.base import BaseTransport
except ImportError:
    BaseTransport = None  # type: ignore[assignment,misc]

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Message helpers
# ---------------------------------------------------------------------------


def make_request(
    agent_type: str,
    payload: dict[str, Any],
    *,
    tenant_id: str | None = None,
    conversation_id: str | None = None,
    reply_to: str | None = None,
) -> Message:
    """Build an A2A request Message with JSON payload.

    Args:
        agent_type: Target agent identifier (e.g., "intent-classifier").
        payload: JSON-serializable dict to send as the message body.
        tenant_id: Optional tenant ID propagated via headers.
        conversation_id: Optional conversation ID propagated via headers.
        reply_to: Optional correlation ID for request-response pairing.

    Returns:
        Message ready for transport.
    """
    headers: dict[str, str] = {"agent-type": agent_type}
    if tenant_id:
        headers["x-tenant-id"] = tenant_id
    if conversation_id:
        headers["x-conversation-id"] = conversation_id

    return Message(
        type="A2ARequest",
        payload=json.dumps(payload).encode("utf-8"),
        reply_to=reply_to,
        route_path=f"/agents/{agent_type}/process",
        method="POST",
        headers=headers,
    )


def make_response(
    agent_type: str,
    payload: dict[str, Any],
    *,
    reply_to: str | None = None,
    status_code: int = 200,
) -> Message:
    """Build an A2A response Message with JSON payload.

    Args:
        agent_type: Responding agent identifier.
        payload: JSON-serializable result dict.
        reply_to: Correlation ID from the original request.
        status_code: HTTP-like status code (200=OK, 500=error).

    Returns:
        Response Message ready for transport.
    """
    return Message(
        type="A2AResponse",
        payload=json.dumps(payload).encode("utf-8"),
        reply_to=reply_to,
        route_path=f"/agents/{agent_type}/process",
        method="POST",
        headers={"agent-type": agent_type},
        status_code=status_code,
    )


def make_error_response(
    agent_type: str,
    error: str,
    code: str = "agent_error",
    *,
    reply_to: str | None = None,
) -> Message:
    """Build an A2A error response Message.

    Args:
        agent_type: Responding agent identifier.
        error: Human-readable error message.
        code: Machine-readable error code.
        reply_to: Correlation ID from the original request.

    Returns:
        Error response Message with status_code=500.
    """
    return make_response(
        agent_type,
        {"error": error, "code": code},
        reply_to=reply_to,
        status_code=500,
    )


def parse_payload(message: Message) -> dict[str, Any]:
    """Extract the JSON payload from a Message.

    Args:
        message: Incoming Message with JSON bytes payload.

    Returns:
        Parsed dict from the payload.

    Raises:
        ValueError: If payload is not valid JSON.
    """
    raw = message.payload
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"Invalid JSON payload: {exc}") from exc


# ---------------------------------------------------------------------------
# Base agent
# ---------------------------------------------------------------------------


class AgentRedBaseAgent(BaseAgentProtocol):
    """Abstract base for Agent Red pipeline agents.

    Subclasses MUST implement:
        - agent_type: class attribute or property (str, e.g., "intent-classifier")
        - process(payload, headers) → dict: domain logic

    The base class provides:
        - handle_message(): SDK-compatible entry point with error handling
        - type(): returns "A2A"
        - setup(): no-op (override if async init needed)
        - create_client(): delegates to factory (not typically called on agent side)
        - create_agent_topic(): returns topic from agent_type
        - bind_server(): stores FastAPI/Starlette app reference
    """

    agent_type: str = ""  # Override in subclass

    def __init__(self) -> None:
        self._server: Any = None
        self._configured: bool = False

    # -- BaseAgentProtocol required methods --

    def type(self) -> str:
        """Protocol type identifier."""
        return "A2A"

    async def setup(self, *args: Any, **kwargs: Any) -> None:
        """Initialize agent state. Override in subclass if async init needed."""
        self._configured = True
        logger.info("Agent %s setup complete", self.agent_type)

    def create_client(
        self,
        url: str | None = None,
        topic: str | None = None,
        transport: BaseTransport | None = None,
        **kwargs: Any,
    ) -> Any:
        """Create A2A client. Typically called by the orchestrator, not the agent."""
        # Agents don't usually create their own clients; the orchestrator does.
        # This satisfies the ABC contract.
        raise NotImplementedError(
            f"Agent {self.agent_type} does not create clients. "
            "Use AgntcyFactory.create_client() from the orchestrator."
        )

    def create_agent_topic(self, *args: Any, **kwargs: Any) -> str:
        """Return the NATS/SLIM topic for this agent."""
        return self.agent_type

    def bind_server(self, server: Any) -> None:
        """Bind this agent to a FastAPI/Starlette server instance."""
        self._server = server

    async def handle_message(self, message: Message) -> Message:
        """SDK entry point: receive Message, run domain logic, return Message.

        This method:
        1. Parses the JSON payload from the incoming Message
        2. Extracts tenant/conversation context from headers
        3. Calls self.process() with the parsed payload
        4. Wraps the result in a response Message
        5. Catches and wraps any exceptions as error responses

        Subclasses should NOT override this method — override process() instead.
        """
        start_time = time.monotonic()
        reply_to = getattr(message, "reply_to", None)
        headers = getattr(message, "headers", None) or {}

        try:
            payload = parse_payload(message)
        except ValueError as exc:
            logger.warning(
                "Agent %s: invalid payload: %s", self.agent_type, exc,
            )
            return make_error_response(
                self.agent_type,
                str(exc),
                code="invalid_payload",
                reply_to=reply_to,
            )

        try:
            result = await self.process(payload, headers)
            elapsed_ms = (time.monotonic() - start_time) * 1000

            # Inject standard metadata
            result.setdefault("_agent", self.agent_type)
            result.setdefault("_latency_ms", round(elapsed_ms, 1))

            return make_response(
                self.agent_type,
                result,
                reply_to=reply_to,
                status_code=200,
            )

        except Exception as exc:
            elapsed_ms = (time.monotonic() - start_time) * 1000
            logger.exception(
                "Agent %s: process() failed after %.1fms: %s",
                self.agent_type,
                elapsed_ms,
                exc,
            )
            return make_error_response(
                self.agent_type,
                f"Agent processing error: {type(exc).__name__}: {str(exc)[:500]}",
                code="processing_error",
                reply_to=reply_to,
            )

    # -- Domain logic (subclass implements) --

    @abstractmethod
    async def process(
        self,
        payload: dict[str, Any],
        headers: dict[str, str],
    ) -> dict[str, Any]:
        """Process a request payload and return a result dict.

        This is the domain-specific logic extracted from pipeline.py.
        Each agent subclass implements this method.

        Args:
            payload: Parsed JSON request body.
            headers: Message headers (contains x-tenant-id, x-conversation-id, etc.)

        Returns:
            Result dict to be JSON-serialized in the response Message.

        Raises:
            Any exception — caught by handle_message() and wrapped in error response.
        """
        ...

    # -- Health check --

    def health(self) -> dict[str, Any]:
        """Return agent health status for container health probes."""
        return {
            "agent": self.agent_type,
            "protocol": self.type(),
            "configured": self._configured,
            "status": "healthy" if self._configured else "not_configured",
        }
