"""Bidirectional Sync Manager with Echo Prevention (SPEC-1768).

Prevents infinite loops in bidirectional sync by marking outbound
operations and filtering corresponding inbound webhooks.

Pattern (same as cache_invalidation.py _publish=False):
  1. Record outbound marker in Redis (30s TTL) BEFORE sending.
  2. On inbound, check for marker — if present, it's our own echo.
  3. Remove marker if outbound send fails (avoid false echo detection).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Callable, Coroutine

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ECHO_MARKER_TTL_SECONDS = 30
ECHO_MARKER_PREFIX = "sync:echo:"


# ---------------------------------------------------------------------------
# Echo Marker Store
# ---------------------------------------------------------------------------


class EchoMarkerStore:
    """Redis-backed echo marker store with in-memory fallback.

    Each marker is keyed by a composite of tenant_id, integration_id,
    and a resource identifier (e.g., ticket ID + action).
    """

    def __init__(self, redis_client: Any = None) -> None:
        self._redis = redis_client
        self._memory: dict[str, float] = {}  # key -> expiry timestamp

    def _build_key(
        self,
        tenant_id: str,
        integration_id: str,
        resource_id: str,
        action: str,
    ) -> str:
        return f"{ECHO_MARKER_PREFIX}{tenant_id}:{integration_id}:{resource_id}:{action}"

    async def set_marker(
        self,
        tenant_id: str,
        integration_id: str,
        resource_id: str,
        action: str,
    ) -> str:
        """Set an echo marker BEFORE sending an outbound operation.

        Returns the marker key.
        """
        key = self._build_key(tenant_id, integration_id, resource_id, action)

        if self._redis is not None:
            try:
                await self._redis.set(key, "1", ex=ECHO_MARKER_TTL_SECONDS)
                return key
            except Exception as exc:
                logger.warning("Redis echo marker set failed: %s", exc)

        # In-memory fallback
        self._memory[key] = time.time() + ECHO_MARKER_TTL_SECONDS
        return key

    async def check_marker(
        self,
        tenant_id: str,
        integration_id: str,
        resource_id: str,
        action: str,
    ) -> bool:
        """Check if an echo marker exists (indicating our own outbound).

        Returns True if the marker exists (this is an echo, skip it).
        """
        key = self._build_key(tenant_id, integration_id, resource_id, action)

        if self._redis is not None:
            try:
                result = await self._redis.get(key)
                if result is not None:
                    # Delete after checking (one-time use)
                    await self._redis.delete(key)
                    return True
                return False
            except Exception as exc:
                logger.warning("Redis echo marker check failed: %s", exc)

        # In-memory fallback
        expiry = self._memory.get(key)
        if expiry is not None:
            if time.time() < expiry:
                del self._memory[key]
                return True
            else:
                # Expired
                del self._memory[key]
                return False
        return False

    async def remove_marker(
        self,
        tenant_id: str,
        integration_id: str,
        resource_id: str,
        action: str,
    ) -> bool:
        """Remove a marker (call when outbound send fails).

        Returns True if the marker existed and was removed.
        """
        key = self._build_key(tenant_id, integration_id, resource_id, action)

        if self._redis is not None:
            try:
                result = await self._redis.delete(key)
                return result > 0
            except Exception as exc:
                logger.warning("Redis echo marker remove failed: %s", exc)

        # In-memory fallback
        existed = key in self._memory
        self._memory.pop(key, None)
        return existed

    def clear(self) -> None:
        """Clear in-memory store (testing)."""
        self._memory.clear()


# ---------------------------------------------------------------------------
# BidirectionalSyncManager
# ---------------------------------------------------------------------------

# Type for outbound send function
OutboundSendFn = Callable[..., Coroutine[Any, Any, Any]]


class BidirectionalSyncManager:
    """Manages bidirectional sync with echo prevention.

    Usage:
        manager = BidirectionalSyncManager()

        # Outbound: send a reply to Zendesk
        await manager.record_outbound("t-1", "zendesk", "ticket-123", "reply")
        try:
            await zendesk_client.create_reply(ticket_id="123", body="...")
        except Exception:
            await manager.cancel_outbound("t-1", "zendesk", "ticket-123", "reply")
            raise

        # Inbound: webhook arrives from Zendesk
        is_echo = await manager.is_echo("t-1", "zendesk", "ticket-123", "reply")
        if is_echo:
            return  # Skip — this is our own outbound bouncing back
        await process_inbound(event)
    """

    def __init__(
        self,
        echo_store: EchoMarkerStore | None = None,
    ) -> None:
        self._echo_store = echo_store or EchoMarkerStore()
        self._outbound_count: int = 0
        self._echo_count: int = 0
        self._inbound_count: int = 0

    async def record_outbound(
        self,
        tenant_id: str,
        integration_id: str,
        resource_id: str,
        action: str,
    ) -> str:
        """Record an outbound operation BEFORE sending.

        Must be called before the actual outbound API call.
        If the outbound fails, call cancel_outbound() to clean up.

        Args:
            tenant_id: Tenant identifier.
            integration_id: Integration identifier.
            resource_id: Resource being acted on (e.g., ticket ID).
            action: Action type (e.g., "reply", "status_change", "assign").

        Returns:
            The echo marker key.
        """
        self._outbound_count += 1
        key = await self._echo_store.set_marker(
            tenant_id, integration_id, resource_id, action
        )
        logger.debug(
            "Outbound recorded: tenant=%s integration=%s resource=%s action=%s",
            tenant_id,
            integration_id,
            resource_id,
            action,
        )
        return key

    async def cancel_outbound(
        self,
        tenant_id: str,
        integration_id: str,
        resource_id: str,
        action: str,
    ) -> bool:
        """Cancel an outbound marker (call when send fails).

        Prevents false echo detection for an operation that never
        actually completed.
        """
        removed = await self._echo_store.remove_marker(
            tenant_id, integration_id, resource_id, action
        )
        if removed:
            self._outbound_count -= 1
            logger.debug(
                "Outbound cancelled: tenant=%s integration=%s resource=%s action=%s",
                tenant_id,
                integration_id,
                resource_id,
                action,
            )
        return removed

    async def is_echo(
        self,
        tenant_id: str,
        integration_id: str,
        resource_id: str,
        action: str,
    ) -> bool:
        """Check if an inbound event is an echo of our own outbound.

        Call this when processing an inbound webhook. If True, the
        event should be skipped (it's our own operation bouncing back).

        Args:
            tenant_id: Tenant identifier.
            integration_id: Integration identifier.
            resource_id: Resource being acted on.
            action: Action type.

        Returns:
            True if this is an echo (skip processing).
        """
        self._inbound_count += 1
        is_echo = await self._echo_store.check_marker(
            tenant_id, integration_id, resource_id, action
        )
        if is_echo:
            self._echo_count += 1
            logger.debug(
                "Echo detected (skipping): tenant=%s integration=%s resource=%s action=%s",
                tenant_id,
                integration_id,
                resource_id,
                action,
            )
        return is_echo

    async def handle_inbound(
        self,
        tenant_id: str,
        integration_id: str,
        resource_id: str,
        action: str,
        handler: Callable[[], Coroutine[Any, Any, Any]],
    ) -> Any | None:
        """Convenience: check for echo and process if not.

        Args:
            tenant_id: Tenant identifier.
            integration_id: Integration identifier.
            resource_id: Resource identifier.
            action: Action type.
            handler: Async callable to invoke if not an echo.

        Returns:
            Handler result if processed, None if echo was detected.
        """
        if await self.is_echo(tenant_id, integration_id, resource_id, action):
            return None
        return await handler()

    # -- Stats --------------------------------------------------------------

    @property
    def stats(self) -> dict[str, int]:
        return {
            "outbound_operations": self._outbound_count,
            "inbound_events": self._inbound_count,
            "echoes_prevented": self._echo_count,
        }
