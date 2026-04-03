"""Slice 4: S253 Phase 1 — SSE fan-out/replay routing behavioral tests.

Tests SSEConnectionManager state methods AND routing decision integration
that event_generator() depends on.

Test plan ref: COMPREHENSIVE-TEST-PLAN-S245-S255.md Slice 4

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import pytest

from src.chat.sse_manager import SSEConnectionManager, EventBuffer


@pytest.fixture
def sse_mgr():
    """Create a fresh SSEConnectionManager for each test."""
    return SSEConnectionManager()


# ── is_producer_active ────────────────────────────────────────────

class TestProducerActiveRouting:
    """Tests for fan-out routing condition."""

    def test_no_active_producer_returns_false(self, sse_mgr):
        assert sse_mgr.is_producer_active("conv-1", "msg-1") is False

    def test_active_producer_matching_message_returns_true(self, sse_mgr):
        sse_mgr._active_producers["conv-1"] = "msg-1"
        assert sse_mgr.is_producer_active("conv-1", "msg-1") is True

    def test_active_producer_different_message_returns_false(self, sse_mgr):
        sse_mgr._active_producers["conv-1"] = "msg-old"
        assert sse_mgr.is_producer_active("conv-1", "msg-new") is False


# ── is_message_completed ──────────────────────────────────────────

class TestCompletedMessageRouting:
    """Tests for replay-only routing condition."""

    def test_no_completed_message_returns_false(self, sse_mgr):
        assert sse_mgr.is_message_completed("conv-1", "msg-1") is False

    def test_completed_message_matching_returns_true(self, sse_mgr):
        sse_mgr._completed_messages["conv-1"] = "msg-1"
        assert sse_mgr.is_message_completed("conv-1", "msg-1") is True

    def test_completed_different_id_returns_false(self, sse_mgr):
        sse_mgr._completed_messages["conv-1"] = "msg-old"
        assert sse_mgr.is_message_completed("conv-1", "msg-new") is False


# ── Replay events ─────────────────────────────────────────────────

class TestReplayEvents:
    """Tests for event buffer replay."""

    def test_no_buffer_returns_empty(self, sse_mgr):
        assert sse_mgr.get_replay_events("conv-1", 0) == []

    def test_replay_from_last_event_id(self, sse_mgr):
        buf = EventBuffer()
        buf.append("event: token\ndata: hello\n\n")  # seq=1
        buf.append("event: token\ndata: world\n\n")  # seq=2
        buf.append("event: done\ndata: {}\n\n")       # seq=3
        sse_mgr._buffers["conv-1"] = buf

        events = sse_mgr.get_replay_events("conv-1", 1)
        assert len(events) == 2  # seq=2 and seq=3

    def test_replay_from_zero_returns_all(self, sse_mgr):
        buf = EventBuffer()
        buf.append("event: token\ndata: a\n\n")  # seq=1
        buf.append("event: done\ndata: {}\n\n")  # seq=2
        sse_mgr._buffers["conv-1"] = buf

        events = sse_mgr.get_replay_events("conv-1", 0)
        assert len(events) == 2


# ── Routing decision tree integration ─────────────────────────────

class TestRoutingDecisionTree:
    """Integration tests for the three-branch routing decision."""

    def test_fan_out_takes_priority_over_completed(self, sse_mgr):
        """When both active and completed, fan-out should win (checked first)."""
        sse_mgr._active_producers["conv-1"] = "msg-1"
        sse_mgr._completed_messages["conv-1"] = "msg-1"

        # Simulate event_generator() priority: check producer first
        msg_id = "msg-1"
        if sse_mgr.is_producer_active("conv-1", msg_id):
            branch = "fan_out"
        elif sse_mgr.is_message_completed("conv-1", msg_id):
            branch = "replay_only"
        else:
            branch = "pipeline"

        assert branch == "fan_out"

    def test_completed_takes_priority_over_pipeline(self, sse_mgr):
        """When completed but no active producer, replay-only wins."""
        sse_mgr._completed_messages["conv-1"] = "msg-1"

        msg_id = "msg-1"
        if sse_mgr.is_producer_active("conv-1", msg_id):
            branch = "fan_out"
        elif sse_mgr.is_message_completed("conv-1", msg_id):
            branch = "replay_only"
        else:
            branch = "pipeline"

        assert branch == "replay_only"

    def test_pipeline_fallback_when_neither(self, sse_mgr):
        """Neither active nor completed -> pipeline fallback."""
        msg_id = "msg-1"
        if sse_mgr.is_producer_active("conv-1", msg_id):
            branch = "fan_out"
        elif sse_mgr.is_message_completed("conv-1", msg_id):
            branch = "replay_only"
        else:
            branch = "pipeline"

        assert branch == "pipeline"

    def test_no_message_id_goes_to_pipeline(self, sse_mgr):
        """None message_id skips both checks -> pipeline."""
        sse_mgr._active_producers["conv-1"] = "msg-1"
        sse_mgr._completed_messages["conv-1"] = "msg-1"

        msg_id = None
        if msg_id and sse_mgr.is_producer_active("conv-1", msg_id):
            branch = "fan_out"
        elif msg_id and sse_mgr.is_message_completed("conv-1", msg_id):
            branch = "replay_only"
        else:
            branch = "pipeline"

        assert branch == "pipeline"
