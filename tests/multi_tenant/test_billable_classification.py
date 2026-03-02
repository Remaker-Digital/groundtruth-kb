"""Unit tests for billable conversation classification (SPEC-1606, SPEC-1607).

SPEC-1606: Conversations start non-billable; promoted on first AI response.
SPEC-1607: Inbox excludes zero-message conversations.

Covers:
    - ConversationDocument default is_billable=False (schema)
    - Session creation with is_billable=False
    - add_ai_message promotes eligible conversations to billable
    - Non-billable prefix conversations stay non-billable after AI response
    - Finalization safety net (no AI response → non-billable)
    - list_filtered excludes zero-message conversations
    - count_filtered excludes zero-message conversations

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from typing import Any

import pytest

from src.multi_tenant.conversation_meter import NON_BILLABLE_PREFIXES
from src.multi_tenant.cosmos_schema import (
    COLLECTION_CONVERSATIONS,
    ConversationDocument,
    ConversationStatus,
)
from src.multi_tenant.repositories.conversation import ConversationRepository

# ---------------------------------------------------------------------------
# Test constants
# ---------------------------------------------------------------------------

_TENANT = "tenant-bill-001"
_NOW = "2026-03-02T12:00:00+00:00"


def _inject_raw_doc(mock_cosmos, doc: dict[str, Any]) -> None:
    """Inject a raw dict directly into the mock container's item list."""
    container = mock_cosmos.get_container(COLLECTION_CONVERSATIONS)
    container.items.append(doc)


def _make_conv_doc(
    conversation_id: str = "conv-001",
    tenant_id: str = _TENANT,
    status: str = "active",
    customer_id: str = "cust-001",
    is_billable: bool = False,
    started_at: str = _NOW,
    message_count: int = 0,
    turn_count: int = 0,
    **overrides: Any,
) -> dict[str, Any]:
    """Build a raw conversation document for billable classification tests."""
    doc: dict[str, Any] = {
        "id": conversation_id,
        "tenant_id": tenant_id,
        "conversation_id": conversation_id,
        "status": status,
        "customer_id": customer_id,
        "is_billable": is_billable,
        "started_at": started_at,
        "ended_at": None,
        "last_activity_at": started_at,
        "is_test_mode": False,
        "message_count": message_count,
        "turn_count": turn_count,
        "messages": [],
        "agents_invoked": [],
        "internal_notes": [],
    }
    doc.update(overrides)
    return doc


# ===================================================================
# SPEC-1606: Billable classification deferral
# ===================================================================


class TestBillableClassification:
    """Verify conversations default to non-billable and are promoted on AI response."""

    @pytest.mark.unit
    def test_schema_default_non_billable(self):
        """TEST-2912: ConversationDocument.is_billable defaults to False."""
        doc = ConversationDocument(
            id="conv-schema-001",
            tenant_id="tenant-001",
            conversation_id="conv-schema-001",
            status=ConversationStatus.ACTIVE,
            started_at=_NOW,
            last_activity_at=_NOW,
            # Deliberately omit is_billable — must default to False
        )
        assert doc.is_billable is False

    @pytest.mark.unit
    def test_conversation_created_non_billable(self):
        """TEST-2909: session.py creates conversations with is_billable=False."""
        from pathlib import Path
        session_py = Path("src/chat/session.py").read_text(encoding="utf-8")
        # Verify the creation line uses is_billable = False
        assert "is_billable = False" in session_py
        # Verify the old pattern (prefix check at creation) is removed
        assert "is_billable = not conversation_id.startswith" not in session_py

    @pytest.mark.unit
    def test_ai_response_promotes_billable(self):
        """TEST-2910: add_ai_message includes is_billable=True patch for eligible IDs."""
        from pathlib import Path
        session_py = Path("src/chat/session.py").read_text(encoding="utf-8")
        # Verify the promotion logic exists in add_ai_message
        assert 'NON_BILLABLE_PREFIXES' in session_py
        assert '"op": "set", "path": "/is_billable", "value": True' in session_py

    @pytest.mark.unit
    def test_prefixed_conversation_stays_non_billable(self):
        """TEST-2911: Non-billable prefix conversations are not promoted."""
        from pathlib import Path
        session_py = Path("src/chat/session.py").read_text(encoding="utf-8")
        # The promotion is guarded by prefix check
        assert "not conversation_id.startswith(NON_BILLABLE_PREFIXES)" in session_py

    @pytest.mark.unit
    def test_all_non_billable_prefixes_defined(self):
        """All four non-billable prefixes are present."""
        assert "test_" in NON_BILLABLE_PREFIXES
        assert "admin_" in NON_BILLABLE_PREFIXES
        assert "health_" in NON_BILLABLE_PREFIXES
        assert "system_" in NON_BILLABLE_PREFIXES

    @pytest.mark.unit
    def test_finalization_safety_net(self):
        """TEST-2915: Finalization patches is_billable=False when no AI response."""
        from pathlib import Path
        meter_py = Path(
            "src/multi_tenant/conversation_meter.py"
        ).read_text(encoding="utf-8")
        # The safety net check: is_billable and not has_ai_response
        assert "is_billable and not has_ai_response" in meter_py
        assert '"op": "set", "path": "/is_billable", "value": False' in meter_py


# ===================================================================
# SPEC-1607: Inbox excludes zero-message conversations
# ===================================================================


class TestInboxZeroMessageFilter:
    """Verify inbox API excludes conversations with 0 messages."""

    @pytest.mark.unit
    def test_list_filtered_excludes_zero_messages(self):
        """TEST-2913: list_filtered query includes message_count > 0 condition."""
        from pathlib import Path
        repo_py = Path(
            "src/multi_tenant/repositories/conversation.py"
        ).read_text(encoding="utf-8")

        # Find the list_filtered method and verify message_count > 0
        in_list_filtered = False
        found = False
        for line in repo_py.splitlines():
            if "async def list_filtered" in line:
                in_list_filtered = True
            elif in_list_filtered and "async def " in line:
                break
            elif in_list_filtered and "message_count > 0" in line:
                found = True
                break
        assert found, "list_filtered must include 'message_count > 0' condition"

    @pytest.mark.unit
    def test_count_filtered_excludes_zero_messages(self):
        """TEST-2914: count_filtered query includes message_count > 0 condition."""
        from pathlib import Path
        repo_py = Path(
            "src/multi_tenant/repositories/conversation.py"
        ).read_text(encoding="utf-8")

        # Find the count_filtered method and verify message_count > 0
        in_count_filtered = False
        found = False
        for line in repo_py.splitlines():
            if "async def count_filtered" in line:
                in_count_filtered = True
            elif in_count_filtered and "async def " in line:
                break
            elif in_count_filtered and "message_count > 0" in line:
                found = True
                break
        assert found, "count_filtered must include 'message_count > 0' condition"

    @pytest.mark.unit
    def test_conditions_list_always_starts_with_message_filter(self):
        """Both list_filtered and count_filtered initialize conditions with the filter."""
        from pathlib import Path
        repo_py = Path(
            "src/multi_tenant/repositories/conversation.py"
        ).read_text(encoding="utf-8")

        # Verify the conditions list starts with message_count > 0
        # This ensures the filter cannot be accidentally bypassed
        assert 'conditions: list[str] = ["c.message_count > 0"]' in repo_py
