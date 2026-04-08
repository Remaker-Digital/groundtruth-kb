"""Tests for Transcript Persistence module (SPEC-1868).

Tests the pure logic of save/load/clear with TTL, without requiring
browser storage APIs. Uses a mock storage backend.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import time



# ---------------------------------------------------------------------------
# Since transcript.ts is TypeScript, we test the equivalent Python logic.
# These tests validate the contract that the TypeScript module must follow.
# ---------------------------------------------------------------------------


WIDGET_KEY = "pk_live_abc123def456"
EXPECTED_STORAGE_KEY = "__agentred_abc123def456_conv"


class MockStorage:
    """In-memory mock for localStorage/sessionStorage."""

    def __init__(self) -> None:
        self._data: dict[str, str] = {}

    def setItem(self, key: str, value: str) -> None:
        self._data[key] = value

    def getItem(self, key: str) -> str | None:
        return self._data.get(key)

    def removeItem(self, key: str) -> None:
        self._data.pop(key, None)


def make_key(widget_key: str) -> str:
    """Mirror the TypeScript makeKey function."""
    prefix = widget_key.replace("pk_live_", "")[:12]
    return f"__agentred_{prefix}_conv"


def save_transcript(storage: MockStorage, widget_key: str, conversation_id: str) -> None:
    """Mirror the TypeScript saveTranscript function."""
    data = {"conversationId": conversation_id, "savedAt": int(time.time() * 1000)}
    storage.setItem(make_key(widget_key), json.dumps(data))


def load_transcript(storage: MockStorage, widget_key: str, ttl_hours: int) -> str | None:
    """Mirror the TypeScript loadTranscript function."""
    raw = storage.getItem(make_key(widget_key))
    if not raw:
        return None
    data = json.loads(raw)
    ttl_ms = ttl_hours * 60 * 60 * 1000
    now = int(time.time() * 1000)
    if now - data["savedAt"] > ttl_ms:
        storage.removeItem(make_key(widget_key))
        return None
    return data.get("conversationId")


def clear_transcript(storage: MockStorage, widget_key: str) -> None:
    """Mirror the TypeScript clearTranscript function."""
    storage.removeItem(make_key(widget_key))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestMakeKey:
    def test_key_format(self) -> None:
        assert make_key(WIDGET_KEY) == EXPECTED_STORAGE_KEY

    def test_key_strips_prefix(self) -> None:
        key = make_key("pk_live_xyz789")
        assert key == "__agentred_xyz789_conv"

    def test_key_truncates_long_keys(self) -> None:
        key = make_key("pk_live_abcdefghijklmnop")
        assert key == "__agentred_abcdefghijkl_conv"


class TestSaveLoad:
    def test_save_and_load(self) -> None:
        storage = MockStorage()
        save_transcript(storage, WIDGET_KEY, "conv-001")
        result = load_transcript(storage, WIDGET_KEY, ttl_hours=24)
        assert result == "conv-001"

    def test_load_empty_storage(self) -> None:
        storage = MockStorage()
        result = load_transcript(storage, WIDGET_KEY, ttl_hours=24)
        assert result is None

    def test_load_expired(self) -> None:
        storage = MockStorage()
        # Manually write an expired entry (savedAt = 48 hours ago)
        key = make_key(WIDGET_KEY)
        expired_ms = int(time.time() * 1000) - (48 * 60 * 60 * 1000)
        storage.setItem(key, json.dumps({"conversationId": "conv-old", "savedAt": expired_ms}))

        result = load_transcript(storage, WIDGET_KEY, ttl_hours=24)
        assert result is None
        # Expired entry should be cleaned up
        assert storage.getItem(key) is None

    def test_load_not_expired(self) -> None:
        storage = MockStorage()
        # Entry saved 1 hour ago, TTL is 24 hours
        key = make_key(WIDGET_KEY)
        recent_ms = int(time.time() * 1000) - (1 * 60 * 60 * 1000)
        storage.setItem(key, json.dumps({"conversationId": "conv-recent", "savedAt": recent_ms}))

        result = load_transcript(storage, WIDGET_KEY, ttl_hours=24)
        assert result == "conv-recent"


class TestClear:
    def test_clear_removes_entry(self) -> None:
        storage = MockStorage()
        save_transcript(storage, WIDGET_KEY, "conv-001")
        clear_transcript(storage, WIDGET_KEY)
        result = load_transcript(storage, WIDGET_KEY, ttl_hours=24)
        assert result is None

    def test_clear_on_empty_is_safe(self) -> None:
        storage = MockStorage()
        clear_transcript(storage, WIDGET_KEY)  # Should not raise


class TestMultipleTenants:
    def test_different_keys_dont_collide(self) -> None:
        storage = MockStorage()
        save_transcript(storage, "pk_live_tenant_aaa", "conv-aaa")
        save_transcript(storage, "pk_live_tenant_bbb", "conv-bbb")

        assert load_transcript(storage, "pk_live_tenant_aaa", 24) == "conv-aaa"
        assert load_transcript(storage, "pk_live_tenant_bbb", 24) == "conv-bbb"
