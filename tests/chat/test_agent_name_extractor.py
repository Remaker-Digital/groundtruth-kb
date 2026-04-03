"""Tests for NL agent name extraction (SPEC-1864).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.chat.pipeline.agent_name_extractor import (
    build_agent_name_index,
    extract_agent_name,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_agent(agent_id: str, display_name: str, kind: str = "peer"):
    """Create a mock PluginAgentDefinition."""
    agent = MagicMock()
    agent.agent_id = agent_id
    agent.display_name = display_name
    agent.agent_kind = kind
    return agent


@pytest.fixture()
def mock_registry():
    """Registry with 3 peer agents and 1 core agent."""
    reg = MagicMock()
    reg.list_agents.return_value = [
        _make_agent("sales", "Sales Agent", "peer"),
        _make_agent("campaigns", "Campaign Agent", "peer"),
        _make_agent("bot_agent", "Bot Agent", "peer"),
        _make_agent("intent-classifier", "Intent Classifier", "core"),
    ]
    return reg


# ---------------------------------------------------------------------------
# Index tests
# ---------------------------------------------------------------------------


class TestBuildAgentNameIndex:
    """Verify the name index only includes PEER agents."""

    def test_includes_peer_agents(self, mock_registry):
        index = build_agent_name_index(mock_registry)
        assert "sales" in index
        assert "campaigns" in index
        assert "bot_agent" in index

    def test_excludes_core_agents(self, mock_registry):
        index = build_agent_name_index(mock_registry)
        assert "intent-classifier" not in index
        assert "intent classifier" not in index

    def test_includes_display_names(self, mock_registry):
        index = build_agent_name_index(mock_registry)
        assert "sales agent" in index
        assert "campaign agent" in index

    def test_includes_first_word(self, mock_registry):
        index = build_agent_name_index(mock_registry)
        assert "campaign" in index  # first word of "Campaign Agent"

    def test_includes_underscore_variants(self, mock_registry):
        index = build_agent_name_index(mock_registry)
        assert "bot agent" in index  # bot_agent → "bot agent"


# ---------------------------------------------------------------------------
# Extraction tests
# ---------------------------------------------------------------------------


class TestExtractAgentName:
    """Verify NL extraction from messages."""

    def test_transfer_to_sales(self, mock_registry):
        assert extract_agent_name("transfer to sales", mock_registry) == "sales"

    def test_talk_to_campaign_agent(self, mock_registry):
        assert extract_agent_name("talk to Campaign Agent", mock_registry) == "campaigns"

    def test_escalate_to_bot(self, mock_registry):
        result = extract_agent_name("escalate to bot", mock_registry)
        assert result == "bot_agent"

    def test_connect_me_with_sales(self, mock_registry):
        assert extract_agent_name("can you connect me with sales?", mock_registry) == "sales"

    def test_no_match_returns_none(self, mock_registry):
        assert extract_agent_name("just say hello", mock_registry) is None

    def test_empty_message_returns_none(self, mock_registry):
        assert extract_agent_name("", mock_registry) is None

    def test_none_message_returns_none(self, mock_registry):
        assert extract_agent_name(None, mock_registry) is None

    def test_case_insensitive(self, mock_registry):
        assert extract_agent_name("TRANSFER TO SALES", mock_registry) == "sales"

    def test_no_core_agents_matched(self, mock_registry):
        """Core agents should never be extracted."""
        assert extract_agent_name("transfer to intent classifier", mock_registry) is None

    def test_send_me_to_campaigns(self, mock_registry):
        assert extract_agent_name("send me to campaigns", mock_registry) == "campaigns"

    def test_let_the_sales_handle(self, mock_registry):
        assert extract_agent_name("let the sales handle this", mock_registry) == "sales"
