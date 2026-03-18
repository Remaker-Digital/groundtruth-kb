"""Tests for Bidirectional Sync Manager (SPEC-1768).

Tests cover: echo marker store (set/check/remove), echo prevention
flow, cancel on send failure, convenience handle_inbound, stats,
marker expiry behavior.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import time

import pytest

from src.integrations.sync_manager import (
    ECHO_MARKER_TTL_SECONDS,
    BidirectionalSyncManager,
    EchoMarkerStore,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def echo_store() -> EchoMarkerStore:
    return EchoMarkerStore()


@pytest.fixture
def sync_manager() -> BidirectionalSyncManager:
    return BidirectionalSyncManager()


# ===================================================================
# EchoMarkerStore
# ===================================================================


class TestEchoMarkerStore:
    """SPEC-1768: Redis-backed echo marker store (in-memory fallback)."""

    @pytest.mark.asyncio
    async def test_set_and_check(self, echo_store: EchoMarkerStore) -> None:
        """Set marker, then check returns True (echo detected)."""
        await echo_store.set_marker("t-1", "zendesk", "ticket-1", "reply")
        is_echo = await echo_store.check_marker("t-1", "zendesk", "ticket-1", "reply")
        assert is_echo is True

    @pytest.mark.asyncio
    async def test_check_without_set(self, echo_store: EchoMarkerStore) -> None:
        """Check without set returns False (not an echo)."""
        is_echo = await echo_store.check_marker("t-1", "zendesk", "ticket-1", "reply")
        assert is_echo is False

    @pytest.mark.asyncio
    async def test_check_consumes_marker(self, echo_store: EchoMarkerStore) -> None:
        """Checking a marker consumes it (one-time use)."""
        await echo_store.set_marker("t-1", "zendesk", "ticket-1", "reply")
        await echo_store.check_marker("t-1", "zendesk", "ticket-1", "reply")
        # Second check should return False
        is_echo = await echo_store.check_marker("t-1", "zendesk", "ticket-1", "reply")
        assert is_echo is False

    @pytest.mark.asyncio
    async def test_different_actions_independent(self, echo_store: EchoMarkerStore) -> None:
        """Different actions on same resource are independent markers."""
        await echo_store.set_marker("t-1", "zendesk", "ticket-1", "reply")
        is_echo = await echo_store.check_marker("t-1", "zendesk", "ticket-1", "status_change")
        assert is_echo is False

    @pytest.mark.asyncio
    async def test_different_resources_independent(self, echo_store: EchoMarkerStore) -> None:
        """Different resources are independent markers."""
        await echo_store.set_marker("t-1", "zendesk", "ticket-1", "reply")
        is_echo = await echo_store.check_marker("t-1", "zendesk", "ticket-2", "reply")
        assert is_echo is False

    @pytest.mark.asyncio
    async def test_different_tenants_independent(self, echo_store: EchoMarkerStore) -> None:
        """Different tenants are independent markers."""
        await echo_store.set_marker("t-1", "zendesk", "ticket-1", "reply")
        is_echo = await echo_store.check_marker("t-2", "zendesk", "ticket-1", "reply")
        assert is_echo is False

    @pytest.mark.asyncio
    async def test_remove_marker(self, echo_store: EchoMarkerStore) -> None:
        """Remove clears the marker."""
        await echo_store.set_marker("t-1", "zendesk", "ticket-1", "reply")
        removed = await echo_store.remove_marker("t-1", "zendesk", "ticket-1", "reply")
        assert removed is True
        # Now check should return False
        is_echo = await echo_store.check_marker("t-1", "zendesk", "ticket-1", "reply")
        assert is_echo is False

    @pytest.mark.asyncio
    async def test_remove_nonexistent(self, echo_store: EchoMarkerStore) -> None:
        """Removing a nonexistent marker returns False."""
        removed = await echo_store.remove_marker("t-1", "zendesk", "ticket-1", "reply")
        assert removed is False

    @pytest.mark.asyncio
    async def test_expired_marker_not_echo(self, echo_store: EchoMarkerStore) -> None:
        """Expired marker is not detected as echo."""
        await echo_store.set_marker("t-1", "zendesk", "ticket-1", "reply")
        # Manually expire the marker
        key = echo_store._build_key("t-1", "zendesk", "ticket-1", "reply")
        echo_store._memory[key] = time.time() - 1  # Already expired
        is_echo = await echo_store.check_marker("t-1", "zendesk", "ticket-1", "reply")
        assert is_echo is False

    @pytest.mark.asyncio
    async def test_clear(self, echo_store: EchoMarkerStore) -> None:
        """Clear removes all markers."""
        await echo_store.set_marker("t-1", "zendesk", "ticket-1", "reply")
        echo_store.clear()
        is_echo = await echo_store.check_marker("t-1", "zendesk", "ticket-1", "reply")
        assert is_echo is False


# ===================================================================
# BidirectionalSyncManager
# ===================================================================


class TestBidirectionalSyncManager:
    """SPEC-1768: Full echo prevention workflow."""

    @pytest.mark.asyncio
    async def test_outbound_then_inbound_echo(self, sync_manager: BidirectionalSyncManager) -> None:
        """Outbound record → inbound check = echo detected."""
        await sync_manager.record_outbound("t-1", "zendesk", "ticket-1", "reply")
        is_echo = await sync_manager.is_echo("t-1", "zendesk", "ticket-1", "reply")
        assert is_echo is True

    @pytest.mark.asyncio
    async def test_inbound_without_outbound_not_echo(self, sync_manager: BidirectionalSyncManager) -> None:
        """Inbound without prior outbound = not an echo."""
        is_echo = await sync_manager.is_echo("t-1", "zendesk", "ticket-1", "reply")
        assert is_echo is False

    @pytest.mark.asyncio
    async def test_cancel_outbound_prevents_false_echo(self, sync_manager: BidirectionalSyncManager) -> None:
        """Cancelling outbound prevents false echo detection."""
        await sync_manager.record_outbound("t-1", "zendesk", "ticket-1", "reply")
        await sync_manager.cancel_outbound("t-1", "zendesk", "ticket-1", "reply")
        is_echo = await sync_manager.is_echo("t-1", "zendesk", "ticket-1", "reply")
        assert is_echo is False

    @pytest.mark.asyncio
    async def test_cancel_nonexistent_outbound(self, sync_manager: BidirectionalSyncManager) -> None:
        """Cancelling a nonexistent outbound returns False."""
        result = await sync_manager.cancel_outbound("t-1", "zendesk", "ticket-1", "reply")
        assert result is False

    @pytest.mark.asyncio
    async def test_handle_inbound_skips_echo(self, sync_manager: BidirectionalSyncManager) -> None:
        """handle_inbound convenience method skips echoes."""
        handler_called = False

        async def handler() -> str:
            nonlocal handler_called
            handler_called = True
            return "processed"

        await sync_manager.record_outbound("t-1", "zendesk", "ticket-1", "reply")
        result = await sync_manager.handle_inbound(
            "t-1", "zendesk", "ticket-1", "reply", handler
        )
        assert result is None
        assert handler_called is False

    @pytest.mark.asyncio
    async def test_handle_inbound_processes_non_echo(self, sync_manager: BidirectionalSyncManager) -> None:
        """handle_inbound processes non-echo events."""
        async def handler() -> str:
            return "processed"

        result = await sync_manager.handle_inbound(
            "t-1", "zendesk", "ticket-1", "reply", handler
        )
        assert result == "processed"

    @pytest.mark.asyncio
    async def test_stats(self, sync_manager: BidirectionalSyncManager) -> None:
        """Stats track outbound, inbound, and echoes."""
        await sync_manager.record_outbound("t-1", "zendesk", "ticket-1", "reply")
        await sync_manager.is_echo("t-1", "zendesk", "ticket-1", "reply")  # echo
        await sync_manager.is_echo("t-1", "zendesk", "ticket-2", "reply")  # not echo

        stats = sync_manager.stats
        assert stats["outbound_operations"] == 1
        assert stats["inbound_events"] == 2
        assert stats["echoes_prevented"] == 1

    @pytest.mark.asyncio
    async def test_multiple_outbound_same_resource(self, sync_manager: BidirectionalSyncManager) -> None:
        """Multiple outbound operations on same resource handled correctly."""
        await sync_manager.record_outbound("t-1", "zendesk", "ticket-1", "reply")
        # First inbound consumes the echo marker
        assert await sync_manager.is_echo("t-1", "zendesk", "ticket-1", "reply") is True
        # Second inbound is NOT an echo (marker consumed)
        assert await sync_manager.is_echo("t-1", "zendesk", "ticket-1", "reply") is False
