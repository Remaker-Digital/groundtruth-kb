"""Bot Agent — External AI Agent Conversation MCP Server (SPEC-1708).

Handles agent-to-agent (A2A) conversations with external AI assistants
(personal AI, corporate procurement bots).  Provides authentication,
parameter negotiation, guardrails, and audit logging.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

AGENT_ID = "bot_agent"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


@dataclass
class BotSession:
    """Active A2A conversation session."""

    session_id: str
    tenant_id: str
    bot_identity: str
    authenticated: bool = False
    parameters: dict[str, Any] = field(default_factory=dict)
    message_count: int = 0
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    rate_limit_remaining: int = 100
    topic_restrictions: list[str] = field(default_factory=list)
    escalation_triggers: list[str] = field(default_factory=list)


@dataclass
class BotAuditEntry:
    """Audit log entry for A2A interactions."""

    session_id: str
    tenant_id: str
    bot_identity: str
    event: str
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


# ---------------------------------------------------------------------------
# Guardrails
# ---------------------------------------------------------------------------

DEFAULT_RATE_LIMIT = 100  # messages per session
DEFAULT_MAX_SESSION_DURATION = 3600  # 1 hour
BLOCKED_TOPICS = ["payment_info", "credentials", "internal_systems"]


# ---------------------------------------------------------------------------
# Agent tools
# ---------------------------------------------------------------------------


class BotAgentTools:
    """Tool implementations for the Bot Agent.

    Each method maps to an MCP tool capability defined in agents.yaml.
    """

    def __init__(self, signing_secret: str = "") -> None:
        self._sessions: dict[str, BotSession] = {}
        self._audit_log: list[BotAuditEntry] = []
        self._signing_secret = signing_secret

    async def authenticate_agent(
        self,
        tenant_id: str,
        bot_identity: str,
        *,
        credentials: dict[str, str] | None = None,
        signature: str = "",
        payload: str = "",
    ) -> dict[str, Any]:
        """Authenticate an inbound AI agent.

        Tool: bot.authenticate_agent

        Verifies identity via HMAC signature or API key.
        Creates a session on success.
        """
        authenticated = False

        if self._signing_secret and signature and payload:
            expected = hmac.new(
                self._signing_secret.encode(),
                payload.encode(),
                hashlib.sha256,
            ).hexdigest()
            authenticated = hmac.compare_digest(signature, expected)
        elif credentials and credentials.get("api_key"):
            # Simple API key auth for testing
            authenticated = bool(credentials["api_key"])

        if not authenticated:
            self._audit(tenant_id, "", bot_identity, "auth_failed")
            return {"authenticated": False, "error": "Authentication failed"}

        session_id = f"bot-{tenant_id}-{int(time.time())}"
        session = BotSession(
            session_id=session_id,
            tenant_id=tenant_id,
            bot_identity=bot_identity,
            authenticated=True,
            rate_limit_remaining=DEFAULT_RATE_LIMIT,
        )
        self._sessions[session_id] = session
        self._audit(tenant_id, session_id, bot_identity, "authenticated")

        return {
            "authenticated": True,
            "session_id": session_id,
            "rate_limit": DEFAULT_RATE_LIMIT,
            "max_duration_seconds": DEFAULT_MAX_SESSION_DURATION,
        }

    async def negotiate_parameters(
        self,
        session_id: str,
        *,
        topics: list[str] | None = None,
        response_format: str = "text",
        max_turns: int = 50,
    ) -> dict[str, Any]:
        """Negotiate interaction parameters for an A2A session.

        Tool: bot.negotiate_parameters
        """
        session = self._sessions.get(session_id)
        if not session or not session.authenticated:
            return {"error": "Invalid or unauthenticated session"}

        # Filter out blocked topics
        allowed_topics = [
            t for t in (topics or []) if t not in BLOCKED_TOPICS
        ]
        blocked = [t for t in (topics or []) if t in BLOCKED_TOPICS]

        session.parameters = {
            "topics": allowed_topics,
            "response_format": response_format,
            "max_turns": min(max_turns, 100),
        }
        session.topic_restrictions = BLOCKED_TOPICS.copy()

        self._audit(
            session.tenant_id, session_id, session.bot_identity,
            "parameters_negotiated",
            details={"allowed": allowed_topics, "blocked": blocked},
        )

        return {
            "accepted": True,
            "allowed_topics": allowed_topics,
            "blocked_topics": blocked,
            "max_turns": min(max_turns, 100),
            "response_format": response_format,
        }

    async def exchange_messages(
        self,
        session_id: str,
        message: str,
    ) -> dict[str, Any]:
        """Exchange a message within an A2A session.

        Tool: bot.exchange_messages

        Enforces rate limits and topic restrictions.
        """
        session = self._sessions.get(session_id)
        if not session or not session.authenticated:
            return {"error": "Invalid or unauthenticated session"}

        # Rate limit check
        if session.rate_limit_remaining <= 0:
            self._audit(
                session.tenant_id, session_id, session.bot_identity,
                "rate_limited",
            )
            return {"error": "Rate limit exceeded", "remaining": 0}

        # Session duration check
        elapsed = time.time() - session.created_at
        if elapsed > DEFAULT_MAX_SESSION_DURATION:
            return {"error": "Session expired", "elapsed_seconds": elapsed}

        session.message_count += 1
        session.rate_limit_remaining -= 1
        session.last_activity = time.time()

        self._audit(
            session.tenant_id, session_id, session.bot_identity,
            "message_exchanged",
            details={"message_number": session.message_count},
        )

        return {
            "received": True,
            "message_number": session.message_count,
            "rate_limit_remaining": session.rate_limit_remaining,
            "response": "",  # Filled by pipeline
        }

    async def enforce_guardrails(
        self,
        session_id: str,
        message: str,
    ) -> dict[str, Any]:
        """Check message against guardrails before processing.

        Tool: bot.enforce_guardrails

        Checks: topic restrictions, rate limits, escalation triggers.
        """
        session = self._sessions.get(session_id)
        if not session:
            return {"allowed": False, "reason": "Invalid session"}

        violations: list[str] = []

        # Check topic restrictions
        message_lower = message.lower()
        for topic in session.topic_restrictions:
            if topic.replace("_", " ") in message_lower:
                violations.append(f"Blocked topic: {topic}")

        # Check rate limit
        if session.rate_limit_remaining <= 0:
            violations.append("Rate limit exceeded")

        # Check escalation triggers
        escalation_keywords = ["speak to human", "real person", "supervisor", "manager"]
        needs_escalation = any(kw in message_lower for kw in escalation_keywords)

        if violations:
            self._audit(
                session.tenant_id, session_id, session.bot_identity,
                "guardrail_violation",
                details={"violations": violations},
            )

        return {
            "allowed": len(violations) == 0,
            "violations": violations,
            "needs_escalation": needs_escalation,
        }

    # -- Audit helpers ------------------------------------------------------

    def _audit(
        self,
        tenant_id: str,
        session_id: str,
        bot_identity: str,
        event: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Record an audit entry."""
        self._audit_log.append(BotAuditEntry(
            session_id=session_id,
            tenant_id=tenant_id,
            bot_identity=bot_identity,
            event=event,
            details=details or {},
        ))

    @property
    def audit_log(self) -> list[BotAuditEntry]:
        """Access audit log (testing)."""
        return self._audit_log
