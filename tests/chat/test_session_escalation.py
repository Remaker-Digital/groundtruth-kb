"""Tests for ConversationSession escalation routing (Backlog #19).

Covers:
    - escalate_conversation() with category and assigned_to
    - find_best_agent_for_category() load-balanced routing
    - Concurrency cap enforcement
    - Fallback to general_inquiry agents

Run:
    pytest tests/chat/test_session_escalation.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.chat.session import ConversationSession
from src.multi_tenant.cosmos_schema import ConversationStatus


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

TENANT_ID = "remaker-digital-001"
CONV_ID = "conv-001"


def _make_session(
    *,
    team_members: list[dict[str, Any]] | None = None,
    count_by_assigned: dict[str, int] | None = None,
) -> ConversationSession:
    """Build a ConversationSession with mocked repos."""
    conv_repo = AsyncMock()
    team_repo = AsyncMock()

    # Default: conversation exists and is active
    conv_repo.read.return_value = {
        "id": CONV_ID,
        "tenant_id": TENANT_ID,
        "status": ConversationStatus.ACTIVE.value,
        "messages": [],
        "message_count": 3,
    }
    conv_repo.patch.return_value = None
    conv_repo.append_message_with_metadata.return_value = {
        "id": CONV_ID,
        "messages": [],
    }

    # count_filtered returns workload counts per agent
    counts = count_by_assigned or {}
    conv_repo.count_filtered = AsyncMock(
        side_effect=lambda tid, **kw: counts.get(kw.get("assigned_to", ""), 0)
    )

    # list_members returns team members
    team_repo.list_members.return_value = team_members or []

    return ConversationSession(
        conversation_repo=conv_repo,
        team_repo=team_repo,
    )


def _make_agent_member(
    member_id: str,
    categories: list[str],
    *,
    max_concurrent: int = 5,
    is_active: bool = True,
) -> dict[str, Any]:
    """Build a mock team member dict for an escalation agent."""
    return {
        "id": member_id,
        "tenant_id": TENANT_ID,
        "email": f"{member_id}@example.com",
        "display_name": member_id.replace("-", " ").title(),
        "role": "escalation_agent",
        "is_active": is_active,
        "escalation_categories": categories,
        "max_concurrent_conversations": max_concurrent,
    }


# ---------------------------------------------------------------------------
# SE-01 to SE-02: escalate_conversation with category + assigned_to
# ---------------------------------------------------------------------------


class TestEscalateConversation:
    """Escalation with category and assignment fields."""

    @pytest.mark.asyncio
    async def test_se_01_sets_category_and_assigned_to(self):
        """Both escalation_category and assigned_to are patched on the conversation."""
        session = _make_session()

        await session.escalate_conversation(
            TENANT_ID,
            CONV_ID,
            escalation_reason="Billing issue",
            escalation_category="account",
            assigned_to="agent-42",
        )

        # Verify append_message_with_metadata was called (SPEC-1843)
        call = session._repo.append_message_with_metadata.call_args
        assert call is not None
        metadata_updates = call.kwargs.get("metadata_updates") or call[1].get("metadata_updates", {})
        assert metadata_updates.get("escalation_category") == "account"
        assert metadata_updates.get("assigned_to") == "agent-42"
        assert metadata_updates.get("status") == ConversationStatus.ESCALATED.value

    @pytest.mark.asyncio
    async def test_se_02_without_category_omits_field(self):
        """Backward compat: no category/assigned_to fields when not provided."""
        session = _make_session()

        await session.escalate_conversation(
            TENANT_ID,
            CONV_ID,
            escalation_reason="General request",
        )

        call = session._repo.append_message_with_metadata.call_args
        metadata_updates = call.kwargs.get("metadata_updates") or call[1].get("metadata_updates", {})
        assert "escalation_category" not in metadata_updates
        assert "assigned_to" not in metadata_updates


# ---------------------------------------------------------------------------
# SE-03 to SE-05: find_best_agent_for_category
# ---------------------------------------------------------------------------


class TestFindBestAgent:
    """Auto-assignment routing logic."""

    @pytest.mark.asyncio
    async def test_se_03_returns_first_matching_agent(self):
        """Returns the first matching agent for the category (WI-3030: no workload balancing)."""
        session = _make_session(
            team_members=[
                _make_agent_member("agent-a", ["support"]),
                _make_agent_member("agent-b", ["support"]),
            ],
            count_by_assigned={"agent-a": 3, "agent-b": 1},
        )

        result = await session.find_best_agent_for_category(TENANT_ID, "support")
        assert result == "agent-a"  # first match, no workload balancing

    @pytest.mark.asyncio
    async def test_se_04_returns_first_match_regardless_of_load(self):
        """Concurrency caps removed for async email-bridge model (WI-3030)."""
        session = _make_session(
            team_members=[
                _make_agent_member("agent-a", ["support"], max_concurrent=2),
                _make_agent_member("agent-b", ["support"], max_concurrent=5),
            ],
            count_by_assigned={"agent-a": 2, "agent-b": 1},
        )

        result = await session.find_best_agent_for_category(TENANT_ID, "support")
        assert result == "agent-a"  # no cap enforcement in async model

    @pytest.mark.asyncio
    async def test_se_05_returns_none_when_no_match(self):
        """Returns None when no agents handle the requested category."""
        session = _make_session(
            team_members=[
                _make_agent_member("agent-a", ["sales"]),
            ],
            count_by_assigned={},
        )

        result = await session.find_best_agent_for_category(TENANT_ID, "technical_assistance")
        assert result is None

    @pytest.mark.asyncio
    async def test_se_06_falls_back_to_general_inquiry(self):
        """Falls back to general_inquiry agents when no category match."""
        session = _make_session(
            team_members=[
                _make_agent_member("agent-a", ["sales"]),
                _make_agent_member("agent-b", ["general_inquiry"]),
            ],
            count_by_assigned={"agent-b": 0},
        )

        result = await session.find_best_agent_for_category(TENANT_ID, "technical_assistance")
        assert result == "agent-b"

    @pytest.mark.asyncio
    async def test_se_07_no_team_repo_returns_none(self):
        """Returns None when team_repo is not configured."""
        session = ConversationSession(
            conversation_repo=AsyncMock(),
            team_repo=None,
        )

        result = await session.find_best_agent_for_category(TENANT_ID, "support")
        assert result is None
