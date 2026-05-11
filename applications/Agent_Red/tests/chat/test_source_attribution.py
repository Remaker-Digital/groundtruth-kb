"""Source attribution tests (B1, SPEC-1870).

Tests for structured source data in validated_event and widget rendering.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json

from src.chat.models import validated_event


class TestValidatedEventSources:
    """B1: validated_event carries optional structured sources (SPEC-1870)."""

    def test_sources_included_when_provided(self):
        """validated_event includes sources array in SSE data."""
        sources = [
            {"title": "Return Policy", "url": "https://example.com/returns"},
            {"title": "FAQ"},
        ]
        event = validated_event("conv-1", "msg-1", sources=sources)
        data = json.loads(event.to_sse().split("data: ")[1].split("\n")[0])
        assert "sources" in data
        assert len(data["sources"]) == 2
        assert data["sources"][0]["title"] == "Return Policy"
        assert data["sources"][0]["url"] == "https://example.com/returns"
        assert data["sources"][1]["title"] == "FAQ"
        assert "url" not in data["sources"][1]

    def test_sources_omitted_when_none(self):
        """validated_event omits sources key when not provided (backward compat)."""
        event = validated_event("conv-1", "msg-1")
        data = json.loads(event.to_sse().split("data: ")[1].split("\n")[0])
        assert "sources" not in data
        assert data["critic_passed"] is True

    def test_sources_omitted_when_empty_list(self):
        """validated_event omits sources key for empty list."""
        event = validated_event("conv-1", "msg-1", sources=[])
        data = json.loads(event.to_sse().split("data: ")[1].split("\n")[0])
        assert "sources" not in data

    def test_standard_fields_preserved_with_sources(self):
        """Standard validated_event fields are present alongside sources."""
        sources = [{"title": "Help Center"}]
        event = validated_event("conv-1", "msg-1", sources=sources)
        data = json.loads(event.to_sse().split("data: ")[1].split("\n")[0])
        assert data["conversation_id"] == "conv-1"
        assert data["message_id"] == "msg-1"
        assert data["critic_passed"] is True
        assert data["sources"] == [{"title": "Help Center"}]
