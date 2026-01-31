"""
NATS tenant isolation — topic namespace, subscription authorization, lifecycle.

Implements Decisions #3 (tenant-scoped NATS topics), #14 (per-tenant queue
depth), and Work Items #15-17, #26. Ensures the 6-agent conversation pipeline
routes messages exclusively within tenant-scoped topic namespaces, preventing
cross-tenant message access at the transport layer.

Topic namespace (Decision #3):
    Pattern: {tenant_id}.{agent}
    Examples:
        t-abc123.intent-classifier
        t-abc123.knowledge-retrieval
        t-abc123.response-generator
        t-abc123.escalation-handler
        t-abc123.analytics-collector
        t-abc123.critic-supervisor

    JetStream streams:
        Each tenant gets a dedicated JetStream stream capturing all their
        agent topics via wildcard subject: {tenant_id}.>
        Stream name: tenant-{tenant_id}

Subscription authorization:
    - TenantNATSManager.subscribe() validates that the requesting tenant_id
      matches the topic's tenant prefix before allowing subscription.
    - No client can subscribe to topics outside their tenant namespace.
    - Platform-wide topics (e.g., platform.health) require explicit admin auth.

Lifecycle:
    - provision_tenant_topics()  — Creates JetStream stream on tenant creation
    - deprovision_tenant_topics() — Purges and deletes stream on tenant deletion
    - Automatic stream configuration per tier (queue depth limits from TIER_DEFAULTS)

Architecture references:
    - Decision #3: Tenant-scoped NATS topics ({tenant_id}.{agent})
    - Decision #14: Per-tenant concurrency limits + queue depth
    - Decision #15: Circuit breakers on NATS (3 failures / 10s)
    - Master Plan Review Section 4: Topic-Based Routing
    - AGNTCY upstream: Topic naming (intent-classifier, knowledge-retrieval, etc.)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import nats
from nats.aio.client import Client as NATSClient
from nats.aio.msg import Msg
from nats.errors import (
    BadSubscriptionError,
    ConnectionClosedError,
    NoRespondersError,
    TimeoutError as NATSTimeoutError,
)
from nats.js.api import (
    ConsumerConfig,
    DeliverPolicy,
    RetentionPolicy,
    StorageType,
    StreamConfig,
)
from nats.js.client import JetStreamContext
from nats.js.errors import NotFoundError as JetStreamNotFoundError

from src.multi_tenant.cosmos_schema import TIER_DEFAULTS, TenantTier

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# NATS server URL (production: NATS JetStream at 10.0.1.5:4222)
NATS_URL = os.environ.get("NATS_URL", "nats://10.0.1.5:4222")

# Agent topic suffixes — matching AGNTCY upstream topic-based routing
AGENT_TOPICS = (
    "intent-classifier",
    "knowledge-retrieval",
    "response-generator",
    "escalation-handler",
    "analytics-collector",
    "critic-supervisor",
)

# Platform-wide topics (not tenant-scoped)
PLATFORM_TOPICS = (
    "platform.health",
    "platform.config-reload",
    "platform.metrics",
)

# JetStream stream naming
STREAM_PREFIX = "tenant-"

# Stream retention: WorkQueue ensures each message is consumed once
DEFAULT_RETENTION = RetentionPolicy.WORK_QUEUE

# Storage: file-based for durability (survives NATS restart)
DEFAULT_STORAGE = StorageType.FILE

# Message TTL — messages older than this are discarded (prevents stale
# messages accumulating if a consumer is temporarily offline)
MESSAGE_MAX_AGE_SECONDS = 300  # 5 minutes

# Maximum message size (256 KB — generous for JSON payloads)
MAX_MSG_SIZE = 256 * 1024

# Circuit breaker thresholds (Decision #15 — NATS: 3 failures / 10s)
CIRCUIT_BREAKER_FAILURE_THRESHOLD = 3
CIRCUIT_BREAKER_WINDOW_SECONDS = 10
CIRCUIT_BREAKER_RECOVERY_SECONDS = 5

# Connection settings
CONNECT_TIMEOUT_SECONDS = 5
RECONNECT_TIME_WAIT_SECONDS = 1
MAX_RECONNECT_ATTEMPTS = 10
DRAIN_TIMEOUT_SECONDS = 10


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def tenant_topic(tenant_id: str, agent: str) -> str:
    """Build a tenant-scoped topic name.

    Args:
        tenant_id: Tenant identifier.
        agent: Agent topic suffix (e.g., "intent-classifier").

    Returns:
        Fully qualified topic: "{tenant_id}.{agent}"
    """
    return f"{tenant_id}.{agent}"


def tenant_wildcard(tenant_id: str) -> str:
    """Build a wildcard subject matching all topics for a tenant.

    Returns:
        "{tenant_id}.>" (NATS wildcard for all sub-subjects)
    """
    return f"{tenant_id}.>"


def stream_name(tenant_id: str) -> str:
    """Build the JetStream stream name for a tenant.

    Returns:
        "tenant-{tenant_id}"
    """
    return f"{STREAM_PREFIX}{tenant_id}"


def _extract_tenant_from_subject(subject: str) -> str | None:
    """Extract the tenant_id prefix from a NATS subject.

    Args:
        subject: NATS subject (e.g., "t-abc123.intent-classifier").

    Returns:
        The tenant_id portion, or None if the subject doesn't
        follow the tenant-scoped pattern.
    """
    if "." not in subject:
        return None
    return subject.split(".", 1)[0]


# ---------------------------------------------------------------------------
# Circuit breaker (adapted from critic_policy.py for NATS)
# ---------------------------------------------------------------------------


class NATSCircuitBreaker:
    """Circuit breaker for NATS connectivity (Decision #15).

    NATS thresholds: 3 failures / 10s window, 5s recovery.

    State machine:
        CLOSED    → (3 failures in 10s)    → OPEN
        OPEN      → (5s elapsed)           → HALF_OPEN
        HALF_OPEN → (next call succeeds)   → CLOSED
        HALF_OPEN → (next call fails)      → OPEN
    """

    class State(str, Enum):
        CLOSED = "closed"
        OPEN = "open"
        HALF_OPEN = "half_open"

    def __init__(
        self,
        failure_threshold: int = CIRCUIT_BREAKER_FAILURE_THRESHOLD,
        window_seconds: float = CIRCUIT_BREAKER_WINDOW_SECONDS,
        recovery_seconds: float = CIRCUIT_BREAKER_RECOVERY_SECONDS,
    ) -> None:
        self._failure_threshold = failure_threshold
        self._window_seconds = window_seconds
        self._recovery_seconds = recovery_seconds
        self._state = self.State.CLOSED
        self._failures: list[float] = []
        self._opened_at: float | None = None

    @property
    def state(self) -> State:
        if self._state == self.State.OPEN:
            if (
                self._opened_at is not None
                and time.monotonic() - self._opened_at >= self._recovery_seconds
            ):
                self._state = self.State.HALF_OPEN
        return self._state

    @property
    def is_open(self) -> bool:
        return self.state == self.State.OPEN

    def record_success(self) -> None:
        self._state = self.State.CLOSED
        self._failures.clear()
        self._opened_at = None

    def record_failure(self) -> None:
        now = time.monotonic()
        self._failures.append(now)
        cutoff = now - self._window_seconds
        self._failures = [t for t in self._failures if t > cutoff]
        if len(self._failures) >= self._failure_threshold:
            self._state = self.State.OPEN
            self._opened_at = now
            logger.warning(
                "NATS circuit breaker OPENED: %d failures in %.0fs window",
                len(self._failures), self._window_seconds,
            )

    def reset(self) -> None:
        self._state = self.State.CLOSED
        self._failures.clear()
        self._opened_at = None


# ---------------------------------------------------------------------------
# Authorization error
# ---------------------------------------------------------------------------


class NATSAuthorizationError(Exception):
    """Raised when a tenant attempts to access a topic outside their namespace."""

    def __init__(self, tenant_id: str, subject: str) -> None:
        self.tenant_id = tenant_id
        self.subject = subject
        super().__init__(
            f"Tenant {tenant_id} is not authorized to access subject '{subject}'."
        )


# ---------------------------------------------------------------------------
# Health status
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class NATSHealthStatus:
    """Health status of the NATS connection and tenant streams."""

    connected: bool
    server_url: str
    circuit_breaker_state: str
    active_streams: int
    last_check_at: str
    details: dict[str, Any]


# ---------------------------------------------------------------------------
# TenantNATSManager — core isolation service
# ---------------------------------------------------------------------------


class TenantNATSManager:
    """Manages tenant-scoped NATS topic namespaces and subscriptions.

    This is the enforcement point for NATS tenant isolation (Decision #3).
    All agent message publishing and subscribing must go through this
    manager, which validates tenant authorization before allowing access
    to any subject.

    Lifecycle:
        1. Call connect() on application startup.
        2. Call provision_tenant_topics() when a new tenant is created.
        3. Use publish() / subscribe() for tenant-scoped messaging.
        4. Call deprovision_tenant_topics() on tenant deletion.
        5. Call close() on application shutdown.

    Usage:
        manager = TenantNATSManager()
        await manager.connect()

        # Provision on tenant creation
        await manager.provision_tenant_topics("t-abc123", TenantTier.STARTER)

        # Publish a message (validates tenant authorization)
        await manager.publish(
            tenant_id="t-abc123",
            agent="intent-classifier",
            data=b'{"message": "hello"}',
        )

        # Subscribe to a tenant's agent topic
        sub = await manager.subscribe(
            tenant_id="t-abc123",
            agent="intent-classifier",
            callback=handle_message,
        )

        # Cleanup on tenant deletion
        await manager.deprovision_tenant_topics("t-abc123")

        # Shutdown
        await manager.close()
    """

    def __init__(
        self,
        nats_url: str = NATS_URL,
    ) -> None:
        self._nats_url = nats_url
        self._nc: NATSClient | None = None
        self._js: JetStreamContext | None = None
        self._circuit_breaker = NATSCircuitBreaker()

        # Track active subscriptions per tenant for cleanup
        # {tenant_id: {agent: subscription}}
        self._subscriptions: dict[str, dict[str, Any]] = {}

        # Track provisioned streams
        self._provisioned_streams: set[str] = set()

    # -------------------------------------------------------------------
    # Connection lifecycle
    # -------------------------------------------------------------------

    async def connect(self) -> None:
        """Connect to the NATS server and initialize JetStream context.

        Should be called once during application startup (e.g., in a
        FastAPI lifespan handler).

        Raises:
            Exception: If the connection cannot be established.
        """
        if self._nc is not None and self._nc.is_connected:
            logger.debug("NATS already connected")
            return

        try:
            self._nc = await nats.connect(
                servers=[self._nats_url],
                connect_timeout=CONNECT_TIMEOUT_SECONDS,
                reconnect_time_wait=RECONNECT_TIME_WAIT_SECONDS,
                max_reconnect_attempts=MAX_RECONNECT_ATTEMPTS,
                error_cb=self._error_callback,
                disconnected_cb=self._disconnected_callback,
                reconnected_cb=self._reconnected_callback,
                closed_cb=self._closed_callback,
            )
            self._js = self._nc.jetstream()
            self._circuit_breaker.record_success()

            logger.info(
                "NATS connected: url=%s client_id=%s",
                self._nats_url, self._nc.client_id,
            )
        except Exception:
            self._circuit_breaker.record_failure()
            logger.exception("Failed to connect to NATS: url=%s", self._nats_url)
            raise

    async def close(self) -> None:
        """Drain subscriptions and close the NATS connection.

        Should be called during application shutdown.
        """
        if self._nc is None or self._nc.is_closed:
            return

        try:
            # Drain ensures in-flight messages are processed before closing
            await self._nc.drain()
            logger.info("NATS connection drained and closed")
        except Exception:
            logger.exception("Error closing NATS connection")
            # Force close if drain fails
            if self._nc and not self._nc.is_closed:
                await self._nc.close()

        self._nc = None
        self._js = None
        self._subscriptions.clear()
        self._provisioned_streams.clear()

    @property
    def is_connected(self) -> bool:
        """Whether the NATS client is currently connected."""
        return self._nc is not None and self._nc.is_connected

    # -------------------------------------------------------------------
    # NATS event callbacks
    # -------------------------------------------------------------------

    async def _error_callback(self, exc: Exception) -> None:
        logger.error("NATS error: %s", exc)
        self._circuit_breaker.record_failure()

    async def _disconnected_callback(self) -> None:
        logger.warning("NATS disconnected")
        self._circuit_breaker.record_failure()

    async def _reconnected_callback(self) -> None:
        logger.info("NATS reconnected")
        self._circuit_breaker.record_success()

    async def _closed_callback(self) -> None:
        logger.info("NATS connection closed")

    # -------------------------------------------------------------------
    # Tenant topic provisioning (Work Item #16)
    # -------------------------------------------------------------------

    async def provision_tenant_topics(
        self,
        tenant_id: str,
        tier: TenantTier,
    ) -> dict[str, Any]:
        """Provision NATS JetStream stream for a new tenant.

        Creates a JetStream stream capturing all messages for the tenant's
        topic namespace ({tenant_id}.>). Stream configuration is tier-aware:
        queue depth limits come from TIER_DEFAULTS.

        Called by the provisioning service when a new tenant is created
        (after Cosmos DB records are written).

        Args:
            tenant_id: Tenant identifier.
            tier: Subscription tier (determines queue depth limits).

        Returns:
            Dict with stream info: {stream_name, subjects, max_msgs, created}.

        Raises:
            ConnectionClosedError: If NATS is not connected.
            NATSCircuitBreaker open: Returns error dict without attempting.
        """
        self._require_connected()

        if self._circuit_breaker.is_open:
            logger.error(
                "NATS circuit breaker OPEN — cannot provision tenant: %s",
                tenant_id,
            )
            return {
                "error": "nats_circuit_breaker_open",
                "tenant_id": tenant_id,
            }

        # Get tier-specific queue depth
        tier_config = TIER_DEFAULTS.get(tier.value, {})
        max_msgs = tier_config.get("queue_depth", 5)

        sname = stream_name(tenant_id)
        subjects = [tenant_wildcard(tenant_id)]

        config = StreamConfig(
            name=sname,
            subjects=subjects,
            retention=DEFAULT_RETENTION,
            storage=DEFAULT_STORAGE,
            max_age=MESSAGE_MAX_AGE_SECONDS,
            max_msgs_per_subject=max_msgs,
            max_msg_size=MAX_MSG_SIZE,
            # Discard old messages when limits are reached (back-pressure)
            discard=nats.js.api.DiscardPolicy.OLD,
            # No replicas at launch (single NATS cluster); revisit at
            # Option C DR upgrade (50+ tenants, work item #62)
            num_replicas=1,
        )

        try:
            info = await self._js.add_stream(config)
            self._provisioned_streams.add(sname)
            self._circuit_breaker.record_success()

            logger.info(
                "Tenant NATS stream provisioned: stream=%s subjects=%s "
                "max_msgs_per_subject=%d tier=%s",
                sname, subjects, max_msgs, tier.value,
            )

            return {
                "stream_name": sname,
                "subjects": subjects,
                "max_msgs_per_subject": max_msgs,
                "tier": tier.value,
                "created": True,
            }

        except Exception as exc:
            self._circuit_breaker.record_failure()
            logger.exception(
                "Failed to provision NATS stream: tenant=%s stream=%s",
                tenant_id, sname,
            )
            return {
                "error": str(exc),
                "tenant_id": tenant_id,
                "stream_name": sname,
            }

    async def update_tenant_stream(
        self,
        tenant_id: str,
        tier: TenantTier,
    ) -> dict[str, Any]:
        """Update a tenant's JetStream stream after a tier change.

        When a tenant upgrades or downgrades, their queue depth limits
        change per TIER_DEFAULTS. This updates the stream configuration
        without disrupting active subscriptions.

        Args:
            tenant_id: Tenant identifier.
            tier: New subscription tier.

        Returns:
            Dict with updated stream info.
        """
        self._require_connected()

        tier_config = TIER_DEFAULTS.get(tier.value, {})
        max_msgs = tier_config.get("queue_depth", 5)

        sname = stream_name(tenant_id)

        try:
            # Fetch current config and update
            info = await self._js.find_stream_name_by_subject(
                tenant_wildcard(tenant_id),
            )
            stream_info = await self._js.stream_info(sname)

            config = stream_info.config
            config.max_msgs_per_subject = max_msgs

            updated = await self._js.update_stream(config)
            self._circuit_breaker.record_success()

            logger.info(
                "Tenant NATS stream updated: stream=%s max_msgs_per_subject=%d tier=%s",
                sname, max_msgs, tier.value,
            )

            return {
                "stream_name": sname,
                "max_msgs_per_subject": max_msgs,
                "tier": tier.value,
                "updated": True,
            }

        except JetStreamNotFoundError:
            # Stream doesn't exist — provision it
            logger.warning(
                "Stream not found for update, provisioning: tenant=%s", tenant_id,
            )
            return await self.provision_tenant_topics(tenant_id, tier)

        except Exception as exc:
            self._circuit_breaker.record_failure()
            logger.exception(
                "Failed to update NATS stream: tenant=%s stream=%s",
                tenant_id, sname,
            )
            return {"error": str(exc), "tenant_id": tenant_id}

    async def deprovision_tenant_topics(
        self,
        tenant_id: str,
    ) -> dict[str, Any]:
        """Remove a tenant's NATS JetStream stream and all messages.

        Called during tenant deletion (after grace period expires).
        Purges all messages first, then deletes the stream entirely.

        Args:
            tenant_id: Tenant identifier.

        Returns:
            Dict with deletion result.
        """
        self._require_connected()

        sname = stream_name(tenant_id)

        # Unsubscribe all active subscriptions for this tenant
        await self._cleanup_tenant_subscriptions(tenant_id)

        try:
            # Purge all messages from the stream
            await self._js.purge_stream(sname)
            logger.info("Tenant NATS stream purged: stream=%s", sname)

            # Delete the stream
            await self._js.delete_stream(sname)
            self._provisioned_streams.discard(sname)
            self._circuit_breaker.record_success()

            logger.info(
                "Tenant NATS stream deleted: stream=%s tenant=%s",
                sname, tenant_id,
            )

            return {
                "stream_name": sname,
                "tenant_id": tenant_id,
                "deleted": True,
            }

        except JetStreamNotFoundError:
            logger.info(
                "Tenant NATS stream already absent: stream=%s tenant=%s",
                sname, tenant_id,
            )
            return {
                "stream_name": sname,
                "tenant_id": tenant_id,
                "deleted": True,
                "already_absent": True,
            }

        except Exception as exc:
            self._circuit_breaker.record_failure()
            logger.exception(
                "Failed to deprovision NATS stream: tenant=%s stream=%s",
                tenant_id, sname,
            )
            return {"error": str(exc), "tenant_id": tenant_id}

    # -------------------------------------------------------------------
    # Subscription authorization (Work Items #17, #26)
    # -------------------------------------------------------------------

    def authorize_subject(self, tenant_id: str, subject: str) -> None:
        """Validate that a tenant is authorized to access a NATS subject.

        This is the enforcement point for cross-tenant isolation at the
        transport layer. Every publish() and subscribe() call goes through
        this check.

        Authorization rules:
            1. Tenant-scoped subjects must start with the tenant's ID prefix.
            2. Platform-wide subjects require explicit allowlisting.
            3. Wildcard subscriptions are restricted to the tenant's namespace.

        Args:
            tenant_id: The authenticated tenant making the request.
            subject: The NATS subject being accessed.

        Raises:
            NATSAuthorizationError: If the tenant is not authorized.
        """
        # Platform-wide topics — reject from tenant context
        # (only internal services can use platform topics)
        if subject.startswith("platform."):
            raise NATSAuthorizationError(tenant_id, subject)

        # Tenant-scoped subjects must start with the tenant's own prefix
        subject_tenant = _extract_tenant_from_subject(subject)
        if subject_tenant != tenant_id:
            logger.warning(
                "NATS authorization denied: tenant=%s attempted subject=%s "
                "(subject belongs to tenant=%s)",
                tenant_id, subject, subject_tenant,
            )
            raise NATSAuthorizationError(tenant_id, subject)

    # -------------------------------------------------------------------
    # Publishing (tenant-scoped)
    # -------------------------------------------------------------------

    async def publish(
        self,
        tenant_id: str,
        agent: str,
        data: bytes,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Publish a message to a tenant-scoped agent topic.

        Validates tenant authorization before publishing. The message is
        published to the JetStream stream for the tenant, ensuring
        durability and exactly-once delivery semantics.

        Args:
            tenant_id: Tenant identifier (must match authenticated context).
            agent: Agent topic suffix (e.g., "intent-classifier").
            data: Message payload (JSON bytes).
            headers: Optional NATS headers for correlation ID propagation
                (Decision #12: conversation_id + tenant_id + trace_id).

        Raises:
            NATSAuthorizationError: If tenant is not authorized for this topic.
            ConnectionClosedError: If NATS is not connected.
        """
        self._require_connected()
        subject = tenant_topic(tenant_id, agent)

        # Authorization check — tenant can only publish to their own namespace
        self.authorize_subject(tenant_id, subject)

        if self._circuit_breaker.is_open:
            raise ConnectionClosedError(
                "NATS circuit breaker is open — publish rejected"
            )

        try:
            ack = await self._js.publish(
                subject,
                data,
                headers=headers,
            )
            self._circuit_breaker.record_success()

            logger.debug(
                "NATS publish: subject=%s stream=%s seq=%d tenant=%s",
                subject, ack.stream, ack.seq, tenant_id,
            )

        except NATSTimeoutError:
            self._circuit_breaker.record_failure()
            logger.error(
                "NATS publish timeout: subject=%s tenant=%s", subject, tenant_id,
            )
            raise

        except Exception:
            self._circuit_breaker.record_failure()
            logger.exception(
                "NATS publish error: subject=%s tenant=%s", subject, tenant_id,
            )
            raise

    async def subscribe(
        self,
        tenant_id: str,
        agent: str,
        callback: Any,
        durable_name: str | None = None,
    ) -> Any:
        """Subscribe to a tenant-scoped agent topic.

        Validates tenant authorization before creating the subscription.
        Uses JetStream push-based subscription with durable consumer for
        reliable message delivery.

        Args:
            tenant_id: Tenant identifier (must match authenticated context).
            agent: Agent topic suffix (e.g., "intent-classifier").
            callback: Async message handler: async (msg: Msg) -> None.
            durable_name: Optional durable consumer name for persistence
                across restarts. If None, a default name is generated.

        Returns:
            The NATS subscription object (for later unsubscribe).

        Raises:
            NATSAuthorizationError: If tenant is not authorized for this topic.
            ConnectionClosedError: If NATS is not connected.
        """
        self._require_connected()
        subject = tenant_topic(tenant_id, agent)

        # Authorization check
        self.authorize_subject(tenant_id, subject)

        if self._circuit_breaker.is_open:
            raise ConnectionClosedError(
                "NATS circuit breaker is open — subscribe rejected"
            )

        if durable_name is None:
            durable_name = f"{tenant_id}-{agent}"

        try:
            sub = await self._js.subscribe(
                subject,
                cb=callback,
                durable=durable_name,
                stream=stream_name(tenant_id),
                config=ConsumerConfig(
                    durable_name=durable_name,
                    deliver_policy=DeliverPolicy.NEW,
                ),
            )

            # Track subscription for cleanup
            if tenant_id not in self._subscriptions:
                self._subscriptions[tenant_id] = {}
            self._subscriptions[tenant_id][agent] = sub

            self._circuit_breaker.record_success()

            logger.info(
                "NATS subscribe: subject=%s durable=%s tenant=%s",
                subject, durable_name, tenant_id,
            )

            return sub

        except Exception:
            self._circuit_breaker.record_failure()
            logger.exception(
                "NATS subscribe error: subject=%s tenant=%s", subject, tenant_id,
            )
            raise

    async def unsubscribe(
        self,
        tenant_id: str,
        agent: str,
    ) -> None:
        """Unsubscribe from a tenant-scoped agent topic.

        Args:
            tenant_id: Tenant identifier.
            agent: Agent topic suffix.
        """
        tenant_subs = self._subscriptions.get(tenant_id, {})
        sub = tenant_subs.pop(agent, None)

        if sub is None:
            logger.debug(
                "No active subscription to unsubscribe: tenant=%s agent=%s",
                tenant_id, agent,
            )
            return

        try:
            await sub.unsubscribe()
            logger.info(
                "NATS unsubscribe: tenant=%s agent=%s", tenant_id, agent,
            )
        except Exception:
            logger.exception(
                "Error unsubscribing: tenant=%s agent=%s", tenant_id, agent,
            )

    async def _cleanup_tenant_subscriptions(self, tenant_id: str) -> None:
        """Unsubscribe all active subscriptions for a tenant."""
        tenant_subs = self._subscriptions.pop(tenant_id, {})
        for agent, sub in tenant_subs.items():
            try:
                await sub.unsubscribe()
                logger.debug(
                    "Cleaned up subscription: tenant=%s agent=%s",
                    tenant_id, agent,
                )
            except Exception:
                logger.exception(
                    "Error cleaning up subscription: tenant=%s agent=%s",
                    tenant_id, agent,
                )

    # -------------------------------------------------------------------
    # Pipeline message helpers
    # -------------------------------------------------------------------

    def build_correlation_headers(
        self,
        tenant_id: str,
        conversation_id: str,
        trace_id: str | None = None,
    ) -> dict[str, str]:
        """Build NATS message headers for correlation ID propagation.

        Decision #12 requires conversation_id + tenant_id + trace_id
        propagated across all agents via NATS message headers.

        Args:
            tenant_id: Tenant identifier.
            conversation_id: Conversation thread identifier.
            trace_id: Optional OpenTelemetry trace ID.

        Returns:
            Dict of NATS headers ready for publish().
        """
        headers = {
            "X-Tenant-Id": tenant_id,
            "X-Conversation-Id": conversation_id,
        }
        if trace_id:
            headers["X-Trace-Id"] = trace_id
        return headers

    @staticmethod
    def extract_correlation_headers(msg: Msg) -> dict[str, str | None]:
        """Extract correlation IDs from a received NATS message.

        Args:
            msg: The received NATS message.

        Returns:
            Dict with tenant_id, conversation_id, and trace_id (may be None).
        """
        headers = msg.headers or {}
        return {
            "tenant_id": headers.get("X-Tenant-Id"),
            "conversation_id": headers.get("X-Conversation-Id"),
            "trace_id": headers.get("X-Trace-Id"),
        }

    # -------------------------------------------------------------------
    # Health monitoring
    # -------------------------------------------------------------------

    async def check_health(self) -> NATSHealthStatus:
        """Check NATS connection health and stream status.

        Used by the /ready endpoint and monitoring systems.

        Returns:
            NATSHealthStatus with connection and stream details.
        """
        now = datetime.now(timezone.utc).isoformat()

        if not self.is_connected:
            return NATSHealthStatus(
                connected=False,
                server_url=self._nats_url,
                circuit_breaker_state=self._circuit_breaker.state.value,
                active_streams=0,
                last_check_at=now,
                details={"error": "not_connected"},
            )

        details: dict[str, Any] = {
            "client_id": self._nc.client_id if self._nc else None,
            "active_subscriptions": sum(
                len(subs) for subs in self._subscriptions.values()
            ),
            "provisioned_streams": len(self._provisioned_streams),
        }

        # Count active streams
        active_streams = 0
        try:
            # List streams to count active ones
            streams = await self._js.streams_info()
            tenant_streams = [
                s for s in streams
                if s.config.name.startswith(STREAM_PREFIX)
            ]
            active_streams = len(tenant_streams)
            details["total_tenant_streams"] = active_streams
            self._circuit_breaker.record_success()
        except Exception as exc:
            details["stream_list_error"] = str(exc)
            self._circuit_breaker.record_failure()

        return NATSHealthStatus(
            connected=True,
            server_url=self._nats_url,
            circuit_breaker_state=self._circuit_breaker.state.value,
            active_streams=active_streams,
            last_check_at=now,
            details=details,
        )

    # -------------------------------------------------------------------
    # Stream inspection (operational)
    # -------------------------------------------------------------------

    async def get_tenant_stream_info(
        self,
        tenant_id: str,
    ) -> dict[str, Any] | None:
        """Get JetStream stream info for a specific tenant.

        Useful for monitoring, debugging, and the usage dashboard
        (Work Item #73).

        Args:
            tenant_id: Tenant identifier.

        Returns:
            Stream info dict, or None if the stream doesn't exist.
        """
        self._require_connected()

        sname = stream_name(tenant_id)
        try:
            info = await self._js.stream_info(sname)
            return {
                "stream_name": info.config.name,
                "subjects": info.config.subjects,
                "max_msgs_per_subject": info.config.max_msgs_per_subject,
                "messages": info.state.messages,
                "bytes": info.state.bytes,
                "consumer_count": info.state.consumer_count,
                "first_seq": info.state.first_seq,
                "last_seq": info.state.last_seq,
            }
        except JetStreamNotFoundError:
            return None
        except Exception:
            logger.exception(
                "Error fetching stream info: tenant=%s stream=%s",
                tenant_id, sname,
            )
            return None

    # -------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------

    def _require_connected(self) -> None:
        """Assert that the NATS client is connected.

        Raises:
            ConnectionClosedError: If not connected.
        """
        if not self.is_connected:
            raise ConnectionClosedError(
                "NATS client is not connected. Call connect() first."
            )

    # -------------------------------------------------------------------
    # Circuit breaker management
    # -------------------------------------------------------------------

    def get_circuit_breaker_state(self) -> str:
        """Get the current NATS circuit breaker state."""
        return self._circuit_breaker.state.value

    def reset_circuit_breaker(self) -> None:
        """Force-reset the NATS circuit breaker to CLOSED.

        Admin operation only — call after manually verifying NATS recovery.
        """
        self._circuit_breaker.reset()
        logger.info("NATS circuit breaker manually reset to CLOSED")


# ---------------------------------------------------------------------------
# Module-level singleton
#
# The TenantNATSManager is a singleton: one connection per application
# process, shared across all request handlers. Initialized via connect()
# during FastAPI startup, closed via close() during shutdown.
# ---------------------------------------------------------------------------

_manager: TenantNATSManager | None = None


def get_nats_manager() -> TenantNATSManager:
    """Get the module-level TenantNATSManager singleton.

    Returns the existing instance or creates a new (unconnected) one.
    Call connect() before using publish/subscribe operations.
    """
    global _manager
    if _manager is None:
        _manager = TenantNATSManager()
    return _manager


async def init_nats_manager(nats_url: str | None = None) -> TenantNATSManager:
    """Initialize and connect the module-level TenantNATSManager.

    Convenience function for FastAPI startup:
        @app.on_event("startup")
        async def startup():
            await init_nats_manager()

    Args:
        nats_url: NATS server URL. Defaults to NATS_URL env var.

    Returns:
        The connected TenantNATSManager singleton.
    """
    global _manager
    if _manager is None:
        _manager = TenantNATSManager(nats_url=nats_url or NATS_URL)
    await _manager.connect()
    return _manager


async def close_nats_manager() -> None:
    """Close the module-level TenantNATSManager.

    Convenience function for FastAPI shutdown:
        @app.on_event("shutdown")
        async def shutdown():
            await close_nats_manager()
    """
    global _manager
    if _manager is not None:
        await _manager.close()
        _manager = None
