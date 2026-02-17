"""
Conversation lifecycle management for the Chat API.

Manages the full lifecycle of a customer conversation: creation, message
appending, idle timeout enforcement, turn counting, end conditions, and
metering. This is the bridge between the Chat API endpoints and the
underlying Cosmos DB ConversationDocument + ConversationMeter.

Lifecycle states:
    ACTIVE      → accepting messages, pipeline processes each turn
    COMPLETED   → customer ended, max turns reached, or idle timeout
    ESCALATED   → human agent takeover
    TIMED_OUT   → idle timeout (30 min inactivity)
    ERROR       → pipeline failure

Architecture references:
    - UI-UX-ARCHITECTURE-DECISIONS.md §3: Chat API Specification
    - Decision #24: Billable conversation definition
    - Decision #71-72: ConversationMeter
    - ConversationRepository: append_message, end_conversation, find_active

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from src.chat.models import (
    ChatMessage,
    ConversationStartRequest,
    ConversationStartResponse,
    ConversationStateResponse,
    EndConversationRequest,
    EndConversationResponse,
    MessageRole,
    SendMessageRequest,
    SendMessageResponse,
    VisitorIdentity,
)
from src.multi_tenant.conversation_meter import (
    IDLE_TIMEOUT_SECONDS,
    MAX_TURNS,
    NON_BILLABLE_PREFIXES,
    ConversationEndReason,
    ConversationMeter,
)
from src.multi_tenant.cosmos_schema import (
    TIER_DEFAULTS,
    ConversationDocument,
    ConversationStatus,
    TenantTier,
)
from src.multi_tenant.gdpr_services import PiiScrubber
from src.multi_tenant.repository import (
    ConversationRepository,
    DocumentNotFoundError,
    TeamMemberRepository,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class ConversationNotFoundError(Exception):
    """Raised when a conversation does not exist or belongs to another tenant."""

    def __init__(self, conversation_id: str, tenant_id: str) -> None:
        self.conversation_id = conversation_id
        self.tenant_id = tenant_id
        super().__init__(
            f"Conversation not found: {conversation_id} (tenant={tenant_id})"
        )


class ConversationNotActiveError(Exception):
    """Raised when an operation requires an active conversation."""

    def __init__(self, conversation_id: str, status: str) -> None:
        self.conversation_id = conversation_id
        self.status = status
        super().__init__(
            f"Conversation {conversation_id} is not active (status={status})"
        )


class TurnLimitReachedError(Exception):
    """Raised when a conversation has reached the maximum turn count."""

    def __init__(self, conversation_id: str, turn_count: int) -> None:
        self.conversation_id = conversation_id
        self.turn_count = turn_count
        super().__init__(
            f"Conversation {conversation_id} reached max turns ({turn_count})"
        )


class TrialLimitReachedError(Exception):
    """Raised when a trial tenant has exhausted their conversation allowance."""

    def __init__(self, tenant_id: str, limit: int) -> None:
        self.tenant_id = tenant_id
        self.limit = limit
        super().__init__(
            f"Trial tenant {tenant_id} has used all {limit} conversations"
        )


# ---------------------------------------------------------------------------
# ConversationSession — lifecycle manager
# ---------------------------------------------------------------------------


class ConversationSession:
    """Manages the lifecycle of customer conversations.

    This service is the single entry point for conversation state changes.
    It coordinates between:
        - ConversationRepository (Cosmos DB persistence)
        - ConversationMeter (billing / metering)
        - Chat API endpoints (HTTP request/response translation)

    Thread-safety: each instance is stateless — all state lives in Cosmos DB.
    Multiple concurrent requests for the same conversation are safe because
    ConversationRepository uses atomic Cosmos DB patch operations.
    """

    def __init__(
        self,
        conversation_repo: ConversationRepository,
        conversation_meter: ConversationMeter | None = None,
        team_repo: TeamMemberRepository | None = None,
    ) -> None:
        self._repo = conversation_repo
        self._meter = conversation_meter
        self._team_repo = team_repo
        self._pii_scrubber: PiiScrubber | None = None

    def set_pii_scrubber(self, enabled: bool) -> None:
        """Enable or disable PII scrubbing on stored message content.

        When enabled, customer and AI message content is scrubbed for
        email addresses and phone numbers before persisting to Cosmos DB.
        The live response delivered to the customer is NOT affected —
        only the stored transcript.

        Called by the pipeline at the start of each conversation turn,
        based on the tenant's ``pii_scrubbing`` config value.
        """
        self._pii_scrubber = PiiScrubber() if enabled else None

    # -------------------------------------------------------------------
    # Create conversation
    # -------------------------------------------------------------------

    async def start_conversation(
        self,
        tenant_id: str,
        request: ConversationStartRequest,
        *,
        tier: TenantTier | None = None,
    ) -> ConversationStartResponse:
        """Start a new conversation.

        Creates a ConversationDocument in Cosmos DB with ACTIVE status.
        If the request includes an initial_message, it is appended as
        the first customer message.

        Args:
            tenant_id: Authenticated tenant identifier.
            request: Conversation start parameters.
            tier: Tenant tier (for billing context).

        Returns:
            ConversationStartResponse with assigned IDs and stream URLs.

        Raises:
            TrialLimitReachedError: If the tenant is on the trial tier
                and has used all included conversations.
        """
        # Trial cap enforcement — block new conversations when trial
        # allowance is exhausted (WI #119). Trial tenants have no packs
        # and no overage billing, so this is a hard stop.
        if tier == TenantTier.TRIAL and self._meter:
            try:
                defaults = TIER_DEFAULTS.get(TenantTier.TRIAL.value, {})
                trial_limit = defaults.get("included_conversations", 50)
                dashboard = await self._meter.get_usage_dashboard(
                    tenant_id, tier,
                )
                if dashboard.total_conversations >= trial_limit:
                    raise TrialLimitReachedError(tenant_id, trial_limit)
            except TrialLimitReachedError:
                raise
            except Exception:
                # Non-fatal — don't block conversations on meter errors
                logger.debug("Trial cap check failed for %s, allowing", tenant_id)

        conversation_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        # Resolve customer_id from visitor identity if provided
        customer_id = _resolve_customer_id(request.visitor)

        # Determine billability from conversation_id prefix
        is_billable = not conversation_id.startswith(NON_BILLABLE_PREFIXES)

        # Build initial messages list
        messages: list[dict[str, Any]] = []
        message_count = 0
        turn_count = 0

        if request.initial_message:
            msg_id = str(uuid.uuid4())
            messages.append({
                "role": MessageRole.CUSTOMER.value,
                "content": request.initial_message,
                "timestamp": now,
                "message_id": msg_id,
            })
            message_count = 1

        doc = ConversationDocument(
            id=conversation_id,
            tenant_id=tenant_id,
            conversation_id=conversation_id,
            status=ConversationStatus.ACTIVE,
            customer_id=customer_id,
            is_billable=is_billable,
            message_count=message_count,
            turn_count=turn_count,
            agents_invoked=[],
            messages=messages,
            started_at=now,
            last_activity_at=now,
        )

        await self._repo.create(tenant_id, doc)

        logger.info(
            "Conversation started: %s (tenant=%s, customer=%s)",
            conversation_id,
            tenant_id,
            customer_id or "anonymous",
        )

        return ConversationStartResponse(
            conversation_id=conversation_id,
            stream_url=f"/api/chat/stream/{conversation_id}",
            ws_url=f"/ws/chat/{conversation_id}",
            created_at=now,
        )

    # -------------------------------------------------------------------
    # Append customer message
    # -------------------------------------------------------------------

    async def add_customer_message(
        self,
        tenant_id: str,
        request: SendMessageRequest,
    ) -> SendMessageResponse:
        """Append a customer message to an active conversation.

        Validates that the conversation is active and under the turn limit,
        then atomically appends the message via Cosmos DB patch.

        Args:
            tenant_id: Authenticated tenant identifier.
            request: Message content and conversation_id.

        Returns:
            SendMessageResponse with the assigned message_id and turn count.

        Raises:
            ConversationNotFoundError: Conversation does not exist for this tenant.
            ConversationNotActiveError: Conversation is not in ACTIVE status.
            TurnLimitReachedError: Conversation has reached MAX_TURNS.
        """
        doc = await self._get_active_conversation(tenant_id, request.conversation_id)

        turn_count = doc.get("turn_count", 0)
        if turn_count >= MAX_TURNS:
            raise TurnLimitReachedError(request.conversation_id, turn_count)

        now = datetime.now(timezone.utc).isoformat()
        message_id = str(uuid.uuid4())

        # PII scrubbing: redact emails/phones from stored transcript
        stored_content = request.content
        if self._pii_scrubber:
            stored_content = self._pii_scrubber.scrub_text(stored_content)

        message_dict: dict[str, Any] = {
            "role": MessageRole.CUSTOMER.value,
            "content": stored_content,
            "timestamp": now,
            "message_id": message_id,
        }
        if request.metadata:
            message_dict["metadata"] = request.metadata

        await self._repo.append_message(
            tenant_id=tenant_id,
            conversation_id=request.conversation_id,
            message=message_dict,
        )

        # message_count was atomically incremented by append_message;
        # turn_count increments when the AI responds (in add_ai_message).
        new_message_count = doc.get("message_count", 0) + 1

        logger.debug(
            "Customer message appended: conv=%s msg=%s (#%d)",
            request.conversation_id,
            message_id,
            new_message_count,
        )

        return SendMessageResponse(
            message_id=message_id,
            conversation_id=request.conversation_id,
            turn_count=turn_count,
            accepted=True,
        )

    # -------------------------------------------------------------------
    # Append AI response
    # -------------------------------------------------------------------

    async def add_ai_message(
        self,
        tenant_id: str,
        conversation_id: str,
        content: str,
        *,
        agents_invoked: list[str] | None = None,
        model_used: str | None = None,
        critic_passed: bool | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Append an AI-generated response to the conversation.

        Called by the pipeline orchestrator after the full response is
        generated and (optionally) validated by the Critic. Atomically
        appends the message, increments turn_count, and updates pipeline
        trace fields.

        Args:
            tenant_id: Tenant identifier.
            conversation_id: Target conversation.
            content: AI response text.
            agents_invoked: Pipeline agents that participated.
            model_used: Primary model used for generation.
            critic_passed: Whether the Critic approved the response.
            metadata: Optional metadata (latency, tokens, etc.).

        Returns:
            The assigned message_id.
        """
        now = datetime.now(timezone.utc).isoformat()
        message_id = str(uuid.uuid4())

        # PII scrubbing: redact emails/phones from stored AI response
        stored_content = content
        if self._pii_scrubber:
            stored_content = self._pii_scrubber.scrub_text(stored_content)

        message_dict: dict[str, Any] = {
            "role": MessageRole.AI.value,
            "content": stored_content,
            "timestamp": now,
            "message_id": message_id,
        }
        if metadata:
            message_dict["metadata"] = metadata

        # Build patch operations: append message + increment turn + update trace
        operations: list[dict[str, Any]] = [
            {"op": "add", "path": "/messages/-", "value": message_dict},
            {"op": "incr", "path": "/message_count", "value": 1},
            {"op": "incr", "path": "/turn_count", "value": 1},
            {"op": "set", "path": "/last_activity_at", "value": now},
        ]

        if agents_invoked is not None:
            operations.append(
                {"op": "set", "path": "/agents_invoked", "value": agents_invoked}
            )
        if model_used is not None:
            operations.append(
                {"op": "set", "path": "/model_used", "value": model_used}
            )
        if critic_passed is not None:
            operations.append(
                {"op": "set", "path": "/critic_passed", "value": critic_passed}
            )

        await self._repo.patch(
            tenant_id=tenant_id,
            document_id=conversation_id,
            operations=operations,
        )

        logger.debug(
            "AI message appended: conv=%s msg=%s critic=%s",
            conversation_id,
            message_id,
            critic_passed,
        )

        return message_id

    # -------------------------------------------------------------------
    # End conversation
    # -------------------------------------------------------------------

    async def end_conversation(
        self,
        tenant_id: str,
        conversation_id: str,
        request: EndConversationRequest | None = None,
        *,
        reason: ConversationEndReason = ConversationEndReason.CUSTOMER_ENDED,
    ) -> EndConversationResponse:
        """End an active conversation.

        Sets the conversation status based on the end reason, then
        meters the conversation for billing (if billable).

        Args:
            tenant_id: Tenant identifier.
            conversation_id: Conversation to end.
            request: Optional end request with feedback.
            reason: Why the conversation is ending.

        Returns:
            EndConversationResponse with final state.

        Raises:
            ConversationNotFoundError: Conversation not found.
            ConversationNotActiveError: Already ended.
        """
        doc = await self._get_active_conversation(tenant_id, conversation_id)

        # Map end reason to conversation status
        status = _end_reason_to_status(reason)
        await self._repo.end_conversation(tenant_id, conversation_id, status)

        # Store feedback if provided
        if request and (request.feedback_rating or request.feedback_text):
            feedback_ops: list[dict[str, Any]] = []
            if request.feedback_rating is not None:
                feedback_ops.append(
                    {"op": "set", "path": "/feedback_rating", "value": request.feedback_rating}
                )
            if request.feedback_text is not None:
                feedback_ops.append(
                    {"op": "set", "path": "/feedback_text", "value": request.feedback_text}
                )
            if request.reason is not None:
                feedback_ops.append(
                    {"op": "set", "path": "/end_reason", "value": request.reason}
                )
            if feedback_ops:
                await self._repo.patch(tenant_id, conversation_id, feedback_ops)

        # Meter the conversation for billing
        is_billable = doc.get("is_billable", True)
        if is_billable and self._meter:
            try:
                await self._meter.meter_conversation(
                    tenant_id=tenant_id,
                    conversation_id=conversation_id,
                )
            except Exception:
                logger.exception(
                    "Failed to meter conversation %s (tenant=%s) — "
                    "billing reconciliation will catch this",
                    conversation_id,
                    tenant_id,
                )

        # Calculate duration
        duration_seconds = _calculate_duration(
            doc.get("started_at", ""),
            datetime.now(timezone.utc).isoformat(),
        )

        logger.info(
            "Conversation ended: %s reason=%s status=%s billable=%s",
            conversation_id,
            reason.value,
            status.value,
            is_billable,
        )

        return EndConversationResponse(
            conversation_id=conversation_id,
            status=status.value,
            turn_count=doc.get("turn_count", 0),
            duration_seconds=duration_seconds,
            is_billable=is_billable,
        )

    # -------------------------------------------------------------------
    # Get conversation state
    # -------------------------------------------------------------------

    async def get_conversation(
        self,
        tenant_id: str,
        conversation_id: str,
    ) -> ConversationStateResponse:
        """Get the current state of a conversation.

        Args:
            tenant_id: Tenant identifier.
            conversation_id: Conversation to retrieve.

        Returns:
            ConversationStateResponse with full message history.

        Raises:
            ConversationNotFoundError: Conversation not found.
        """
        doc = await self._get_conversation(tenant_id, conversation_id)

        messages = [
            ChatMessage(
                role=MessageRole(m["role"]),
                content=m["content"],
                timestamp=m.get("timestamp", ""),
                message_id=m.get("message_id"),
                metadata=m.get("metadata"),
            )
            for m in doc.get("messages", [])
        ]

        return ConversationStateResponse(
            conversation_id=conversation_id,
            status=doc.get("status", ConversationStatus.ACTIVE.value),
            turn_count=doc.get("turn_count", 0),
            message_count=doc.get("message_count", 0),
            messages=messages,
            is_escalated=doc.get("status") == ConversationStatus.ESCALATED.value,
            created_at=doc.get("started_at", ""),
            last_activity_at=doc.get("last_activity_at", ""),
        )

    # -------------------------------------------------------------------
    # Idle timeout check
    # -------------------------------------------------------------------

    async def check_idle_timeout(
        self,
        tenant_id: str,
        conversation_id: str,
    ) -> ConversationEndReason | None:
        """Check if an active conversation should be ended due to inactivity.

        Delegates to ConversationMeter.should_end_conversation() for the
        idle timeout and max turns checks.

        Returns:
            The end reason if the conversation should end, or None if active.
        """
        doc = await self._get_conversation(tenant_id, conversation_id)

        if doc.get("status") != ConversationStatus.ACTIVE.value:
            return None

        return ConversationMeter.should_end_conversation(
            last_activity_at=doc.get("last_activity_at", ""),
            turn_count=doc.get("turn_count", 0),
        )

    # -------------------------------------------------------------------
    # Escalation — agent routing
    # -------------------------------------------------------------------

    async def find_best_agent_for_category(
        self,
        tenant_id: str,
        category: str,
    ) -> str | None:
        """Find an active escalation_agent who handles the given category.

        Selects the agent with the fewest unresolved escalations who is
        still below their ``max_concurrent_conversations`` cap.  Falls
        back to agents handling ``general_inquiry`` if no exact match.

        Returns the member's document ID, or ``None`` if no suitable
        agent is available.
        """
        if not self._team_repo:
            logger.debug("No team_repo configured — cannot auto-assign")
            return None

        members = await self._team_repo.list_members(tenant_id)

        # Filter to active escalation agents who handle this category
        candidates = [
            m for m in members
            if m.get("role") == "escalation_agent"
            and m.get("is_active", True)
            and category in (m.get("escalation_categories") or [])
        ]

        # Fallback: try general_inquiry agents
        if not candidates and category != "general_inquiry":
            candidates = [
                m for m in members
                if m.get("role") == "escalation_agent"
                and m.get("is_active", True)
                and "general_inquiry" in (m.get("escalation_categories") or [])
            ]

        if not candidates:
            return None

        # Score each candidate by current workload
        best_id: str | None = None
        best_count = float("inf")

        for member in candidates:
            member_id = member["id"]
            cap = member.get("max_concurrent_conversations", 5)

            count = await self._repo.count_filtered(
                tenant_id,
                status=ConversationStatus.ESCALATED,
                assigned_to=member_id,
            )

            if count >= cap:
                continue  # at capacity

            if count < best_count:
                best_count = count
                best_id = member_id

        return best_id

    # -------------------------------------------------------------------
    # Escalation — conversation state
    # -------------------------------------------------------------------

    async def escalate_conversation(
        self,
        tenant_id: str,
        conversation_id: str,
        *,
        escalation_reason: str | None = None,
        escalation_category: str | None = None,
        assigned_to: str | None = None,
    ) -> None:
        """Escalate a conversation to a human agent.

        Sets the conversation status to ESCALATED and appends a system
        message recording the escalation event.  Optionally sets the
        escalation category and assigns the conversation to a specific
        team member.

        Args:
            tenant_id: Tenant identifier.
            conversation_id: Conversation to escalate.
            escalation_reason: Optional reason from the Escalation agent.
            escalation_category: Optional category (from ESCALATION_CATEGORIES).
            assigned_to: Optional human agent ID for auto-assignment.
        """
        doc = await self._get_active_conversation(tenant_id, conversation_id)

        now = datetime.now(timezone.utc).isoformat()
        system_msg: dict[str, Any] = {
            "role": MessageRole.SYSTEM.value,
            "content": "Conversation escalated to a human agent.",
            "timestamp": now,
            "message_id": str(uuid.uuid4()),
        }
        if escalation_reason:
            metadata: dict[str, Any] = {"escalation_reason": escalation_reason}
            if escalation_category:
                metadata["escalation_category"] = escalation_category
            if assigned_to:
                metadata["assigned_to"] = assigned_to
            system_msg["metadata"] = metadata

        operations: list[dict[str, Any]] = [
            {"op": "set", "path": "/status", "value": ConversationStatus.ESCALATED.value},
            {"op": "add", "path": "/messages/-", "value": system_msg},
            {"op": "incr", "path": "/message_count", "value": 1},
            {"op": "set", "path": "/last_activity_at", "value": now},
        ]
        if escalation_category:
            operations.append(
                {"op": "set", "path": "/escalation_category", "value": escalation_category}
            )
        if assigned_to:
            operations.append(
                {"op": "set", "path": "/assigned_to", "value": assigned_to}
            )

        await self._repo.patch(tenant_id, conversation_id, operations)

        logger.info(
            "Conversation escalated: %s (tenant=%s, reason=%s, category=%s, assigned=%s)",
            conversation_id,
            tenant_id,
            escalation_reason or "not specified",
            escalation_category or "none",
            assigned_to or "unassigned",
        )

    # -------------------------------------------------------------------
    # Resume from existing active conversation
    # -------------------------------------------------------------------

    async def find_active_conversation(
        self,
        tenant_id: str,
        customer_id: str,
    ) -> ConversationStateResponse | None:
        """Find an existing active conversation for a customer.

        Used when a returning customer opens the widget — if they have
        an active conversation, resume it instead of starting a new one.

        Returns:
            The active conversation state, or None if no active conversation.
        """
        doc = await self._repo.find_active(tenant_id, customer_id)
        if doc is None:
            return None

        return await self.get_conversation(tenant_id, doc["conversation_id"])

    # -------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------

    async def _get_conversation(
        self,
        tenant_id: str,
        conversation_id: str,
    ) -> dict[str, Any]:
        """Read a conversation document, raising domain exceptions."""
        try:
            return await self._repo.read(tenant_id, conversation_id)
        except DocumentNotFoundError:
            raise ConversationNotFoundError(conversation_id, tenant_id) from None

    async def _get_active_conversation(
        self,
        tenant_id: str,
        conversation_id: str,
    ) -> dict[str, Any]:
        """Read a conversation and verify it is ACTIVE."""
        doc = await self._get_conversation(tenant_id, conversation_id)
        status = doc.get("status", "")
        if status != ConversationStatus.ACTIVE.value:
            raise ConversationNotActiveError(conversation_id, status)
        return doc


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_session: ConversationSession | None = None


def get_conversation_session() -> ConversationSession:
    """Get or create the module-level ConversationSession singleton.

    Returns a session with default-constructed dependencies. For testing,
    use ConversationSession() directly with injected mocks.
    """
    global _session
    if _session is None:
        _session = ConversationSession(
            conversation_repo=ConversationRepository(),
        )
    return _session


def configure_conversation_session(
    conversation_repo: ConversationRepository,
    conversation_meter: ConversationMeter | None = None,
    team_repo: TeamMemberRepository | None = None,
) -> ConversationSession:
    """Configure the module-level singleton with explicit dependencies.

    Called during app startup (main.py) after Cosmos DB and metering
    services are initialized.
    """
    global _session
    _session = ConversationSession(
        conversation_repo=conversation_repo,
        conversation_meter=conversation_meter,
        team_repo=team_repo,
    )
    return _session


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _resolve_customer_id(visitor: VisitorIdentity | None) -> str | None:
    """Extract customer_id from visitor identity, if available."""
    if visitor is None:
        return None
    return visitor.customer_id or visitor.email or None


def _end_reason_to_status(reason: ConversationEndReason) -> ConversationStatus:
    """Map a ConversationEndReason to the appropriate ConversationStatus."""
    mapping = {
        ConversationEndReason.CUSTOMER_ENDED: ConversationStatus.RESOLVED,
        ConversationEndReason.IDLE_TIMEOUT: ConversationStatus.TIMED_OUT,
        ConversationEndReason.ESCALATED: ConversationStatus.ESCALATED,
        ConversationEndReason.MAX_TURNS: ConversationStatus.RESOLVED,
        ConversationEndReason.ERROR: ConversationStatus.ERROR,
    }
    return mapping.get(reason, ConversationStatus.RESOLVED)


def _calculate_duration(started_at: str, ended_at: str) -> int | None:
    """Calculate conversation duration in seconds from ISO 8601 timestamps."""
    if not started_at or not ended_at:
        return None
    try:
        start = datetime.fromisoformat(started_at)
        end = datetime.fromisoformat(ended_at)
        return max(0, int((end - start).total_seconds()))
    except (ValueError, TypeError):
        return None
