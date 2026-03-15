"""Mutation tests — Tenant Admin endpoints (team, quick actions, conversations, memory).

Tests: team CRUD, quick action management, conversation workflow, memory deletion.
All endpoints require tenant admin authentication.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.conftest import STARTER_TENANT_ID
from tests.multi_tenant.conftest import MutationTestBase
from src.multi_tenant.repository import DocumentNotFoundError


# ---------------------------------------------------------------------------
# Helpers — Team
# ---------------------------------------------------------------------------

TEAM_BASE = "/api/admin/team"


def _member_doc(
    member_id: str = "t-starter-001:alice@example.com",
    email: str = "alice@example.com",
    role: str = "admin",
    **overrides,
) -> dict:
    """Minimal team member Cosmos document."""
    doc = {
        "id": member_id,
        "tenant_id": STARTER_TENANT_ID,
        "email": email,
        "display_name": "Alice",
        "role": role,
        "is_active": True,
        "escalation_categories": [],
        "max_concurrent_conversations": 5,
        "user_api_key_prefix": "ar_user_t-st...",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    }
    doc.update(overrides)
    return doc


def _create_body(**overrides) -> dict:
    body = {
        "email": "bob@example.com",
        "display_name": "Bob",
        "role": "admin",
    }
    body.update(overrides)
    return body


# ---------------------------------------------------------------------------
# Helpers — Quick Actions
# ---------------------------------------------------------------------------

QA_BASE = "/api/admin/quick-actions"


def _qa_action(action_id: str = "qa-001", **overrides) -> dict:
    doc = {
        "id": action_id,
        "label": "Track order",
        "prompt_template": "I want to track my order.",
        "icon": None,
        "is_active": True,
        "sort_order": 0,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    }
    doc.update(overrides)
    return doc


# ---------------------------------------------------------------------------
# Helpers — Conversations
# ---------------------------------------------------------------------------

CONV_BASE = "/api/admin/conversations"


def _conv_doc(conv_id: str = "conv-001", status: str = "active", **overrides) -> dict:
    doc = {
        "id": conv_id,
        "conversation_id": conv_id,
        "tenant_id": STARTER_TENANT_ID,
        "status": status,
        "customer_id": "cust-001",
        "customer_name": "Jane Doe",
        "message_count": 3,
        "messages": [],
        "internal_notes": [],
        "started_at": "2026-01-01T00:00:00Z",
        "last_activity_at": "2026-01-01T01:00:00Z",
    }
    doc.update(overrides)
    return doc


# ---------------------------------------------------------------------------
# Helpers — Memory
# ---------------------------------------------------------------------------

MEMORY_BASE = "/api/admin/memory"


# ===========================================================================
# Team API — POST /api/admin/team (Create)
# ===========================================================================


class TestCreateTeamMember(MutationTestBase):
    """POST /api/admin/team — create team member."""

    def test_requires_auth(self, app_client, team_repos):
        self.assert_requires_auth(app_client, "post", TEAM_BASE, json=_create_body())

    def test_rejects_widget_key(self, widget_client, team_repos):
        self.assert_rejects_widget_key(widget_client, "post", TEAM_BASE, json=_create_body())

    @patch("src.multi_tenant.admin_team_api.generate_user_api_key", return_value="ar_user_test_key_123456")
    @patch("src.multi_tenant.admin_team_api.hash_api_key", return_value="hashed_key")
    def test_happy_path(self, _hash, _gen, starter_client, team_repos):
        team_repos["team_repo"].find_by_email = AsyncMock(return_value=None)
        team_repos["team_repo"].create = AsyncMock(return_value=None)
        resp = starter_client.post(TEAM_BASE, json=_create_body())
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "bob@example.com"
        assert data["role"] == "admin"
        assert data["userApiKey"] == "ar_user_test_key_123456"

    def test_409_duplicate_email(self, starter_client, team_repos):
        team_repos["team_repo"].find_by_email = AsyncMock(return_value=_member_doc())
        resp = starter_client.post(TEAM_BASE, json=_create_body())
        assert resp.status_code == 409

    def test_400_invalid_role(self, starter_client, team_repos):
        resp = starter_client.post(TEAM_BASE, json=_create_body(role="invalid_role"))
        assert resp.status_code == 400

    def test_400_protected_role(self, starter_client, team_repos):
        resp = starter_client.post(TEAM_BASE, json=_create_body(role="superadmin"))
        assert resp.status_code == 400

    def test_422_missing_email(self, starter_client, team_repos):
        body = {"display_name": "NoEmail", "role": "admin"}
        self.assert_validation_error(starter_client, "post", TEAM_BASE, json=body)


# ===========================================================================
# Team API — PUT /api/admin/team/{id} (Update)
# ===========================================================================


class TestUpdateTeamMember(MutationTestBase):
    """PUT /api/admin/team/{member_id} — update team member."""

    URL = f"{TEAM_BASE}/member-001"

    def test_requires_auth(self, app_client, team_repos):
        self.assert_requires_auth(app_client, "put", self.URL, json={"displayName": "New"})

    def test_rejects_widget_key(self, widget_client, team_repos):
        self.assert_rejects_widget_key(widget_client, "put", self.URL, json={"displayName": "New"})

    def test_happy_path(self, starter_client, team_repos):
        team_repos["team_repo"].read = AsyncMock(return_value=_member_doc(member_id="member-001"))
        team_repos["team_repo"].patch = AsyncMock(return_value=None)
        resp = starter_client.put(self.URL, json={"displayName": "Alice Updated"})
        assert resp.status_code == 200
        assert resp.json()["displayName"] == "Alice Updated"

    def test_404_not_found(self, starter_client, team_repos):
        team_repos["team_repo"].read = AsyncMock(side_effect=DocumentNotFoundError("team_members", "member-001", STARTER_TENANT_ID))
        resp = starter_client.put(self.URL, json={"displayName": "X"})
        assert resp.status_code == 404

    def test_400_invalid_role(self, starter_client, team_repos):
        team_repos["team_repo"].read = AsyncMock(return_value=_member_doc(member_id="member-001"))
        resp = starter_client.put(self.URL, json={"role": "nonexistent"})
        assert resp.status_code == 400


# ===========================================================================
# Team API — DELETE /api/admin/team/{id}
# ===========================================================================


class TestDeleteTeamMember(MutationTestBase):
    """DELETE /api/admin/team/{member_id} — hard delete."""

    URL = f"{TEAM_BASE}/member-001"

    def test_requires_auth(self, app_client, team_repos):
        self.assert_requires_auth(app_client, "delete", self.URL)

    def test_rejects_widget_key(self, widget_client, team_repos):
        self.assert_rejects_widget_key(widget_client, "delete", self.URL)

    def test_happy_path(self, starter_client, team_repos):
        team_repos["team_repo"].read = AsyncMock(return_value=_member_doc(member_id="member-001"))
        team_repos["team_repo"].delete = AsyncMock(return_value=None)
        resp = starter_client.delete(self.URL)
        assert resp.status_code == 200
        assert "deletedAt" in resp.json()

    def test_404_not_found(self, starter_client, team_repos):
        team_repos["team_repo"].read = AsyncMock(side_effect=DocumentNotFoundError("team_members", "member-001", STARTER_TENANT_ID))
        resp = starter_client.delete(self.URL)
        assert resp.status_code == 404

    def test_400_cannot_delete_superadmin(self, starter_client, team_repos):
        team_repos["team_repo"].read = AsyncMock(
            return_value=_member_doc(member_id="member-001", role="superadmin"),
        )
        # Non-superadmin caller sees 404 (hidden)
        resp = starter_client.delete(self.URL)
        assert resp.status_code == 404


# ===========================================================================
# Team API — POST /api/admin/team/{id}/rotate-key
# ===========================================================================


class TestRotateTeamKey(MutationTestBase):
    """POST /api/admin/team/{member_id}/rotate-key — rotate user API key."""

    URL = f"{TEAM_BASE}/member-001/rotate-key"

    def test_requires_auth(self, app_client, team_repos):
        self.assert_requires_auth(app_client, "post", self.URL)

    def test_rejects_widget_key(self, widget_client, team_repos):
        self.assert_rejects_widget_key(widget_client, "post", self.URL)

    @patch("src.multi_tenant.admin_team_api.generate_user_api_key", return_value="ar_user_new_key_rotated")
    @patch("src.multi_tenant.admin_team_api.hash_api_key", return_value="new_hash")
    def test_happy_path(self, _hash, _gen, starter_client, team_repos):
        team_repos["team_repo"].read = AsyncMock(return_value=_member_doc(member_id="member-001"))
        team_repos["team_repo"].patch = AsyncMock(return_value=None)
        resp = starter_client.post(self.URL)
        assert resp.status_code == 200
        data = resp.json()
        assert data["userApiKey"] == "ar_user_new_key_rotated"
        assert data["rotatedAt"] is not None

    def test_404_not_found(self, starter_client, team_repos):
        team_repos["team_repo"].read = AsyncMock(side_effect=DocumentNotFoundError("team_members", "member-001", STARTER_TENANT_ID))
        resp = starter_client.post(self.URL)
        assert resp.status_code == 404


# ===========================================================================
# Quick Actions — POST /api/admin/quick-actions (Create)
# ===========================================================================


class TestCreateQuickAction(MutationTestBase):
    """POST /api/admin/quick-actions — create quick action prompt."""

    def test_requires_auth(self, app_client, quick_action_repos):
        self.assert_requires_auth(app_client, "post", QA_BASE, json={"label": "X", "promptTemplate": "Y"})

    def test_rejects_widget_key(self, widget_client, quick_action_repos):
        self.assert_rejects_widget_key(widget_client, "post", QA_BASE, json={"label": "X", "promptTemplate": "Y"})

    @patch("src.multi_tenant.admin_quick_action_api._ensure_qa_draft", new_callable=AsyncMock)
    def test_happy_path(self, _draft, starter_client, quick_action_repos):
        quick_action_repos["prefs_repo"].get_quick_actions = AsyncMock(return_value=[])
        quick_action_repos["prefs_repo"].upsert_quick_action = AsyncMock(return_value=None)
        resp = starter_client.post(QA_BASE, json={"label": "Track order", "promptTemplate": "Track my order"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["label"] == "Track order"
        assert data["promptTemplate"] == "Track my order"
        assert data["id"]  # UUID generated

    def test_422_missing_label(self, starter_client, quick_action_repos):
        self.assert_validation_error(starter_client, "post", QA_BASE, json={"promptTemplate": "X"})

    def test_422_missing_prompt_template(self, starter_client, quick_action_repos):
        self.assert_validation_error(starter_client, "post", QA_BASE, json={"label": "X"})

    @patch("src.multi_tenant.admin_quick_action_api._ensure_qa_draft", new_callable=AsyncMock)
    def test_no_tier_limit_after_cap_removal(self, _draft, starter_client, quick_action_repos):
        # max_quick_actions removed from TIER_DEFAULTS — no cap enforcement.
        # Creating a quick action succeeds even with many existing actions.
        quick_action_repos["prefs_repo"].get_quick_actions = AsyncMock(
            return_value=[_qa_action(f"qa-{i}") for i in range(5)],
        )
        quick_action_repos["prefs_repo"].upsert_quick_action = AsyncMock(return_value=None)
        resp = starter_client.post(QA_BASE, json={"label": "New", "promptTemplate": "New prompt"})
        assert resp.status_code == 201


# ===========================================================================
# Quick Actions — PUT /api/admin/quick-actions/{id} (Update)
# ===========================================================================


class TestUpdateQuickAction(MutationTestBase):
    """PUT /api/admin/quick-actions/{action_id} — update quick action."""

    URL = f"{QA_BASE}/qa-001"

    def test_requires_auth(self, app_client, quick_action_repos):
        self.assert_requires_auth(app_client, "put", self.URL, json={"label": "Updated"})

    def test_rejects_widget_key(self, widget_client, quick_action_repos):
        self.assert_rejects_widget_key(widget_client, "put", self.URL, json={"label": "Updated"})

    @patch("src.multi_tenant.admin_quick_action_api._ensure_qa_draft", new_callable=AsyncMock)
    def test_happy_path(self, _draft, starter_client, quick_action_repos):
        quick_action_repos["prefs_repo"].get_quick_actions = AsyncMock(
            return_value=[_qa_action("qa-001")],
        )
        quick_action_repos["prefs_repo"].upsert_quick_action = AsyncMock(return_value=None)
        resp = starter_client.put(self.URL, json={"label": "Updated label"})
        assert resp.status_code == 200
        assert resp.json()["label"] == "Updated label"

    def test_404_not_found(self, starter_client, quick_action_repos):
        quick_action_repos["prefs_repo"].get_quick_actions = AsyncMock(return_value=[])
        resp = starter_client.put(self.URL, json={"label": "X"})
        assert resp.status_code == 404


# ===========================================================================
# Quick Actions — DELETE /api/admin/quick-actions/{id}
# ===========================================================================


class TestDeleteQuickAction(MutationTestBase):
    """DELETE /api/admin/quick-actions/{action_id} — delete prompt."""

    URL = f"{QA_BASE}/qa-001"

    def test_requires_auth(self, app_client, quick_action_repos):
        self.assert_requires_auth(app_client, "delete", self.URL)

    def test_rejects_widget_key(self, widget_client, quick_action_repos):
        self.assert_rejects_widget_key(widget_client, "delete", self.URL)

    @patch("src.multi_tenant.admin_quick_action_api._ensure_qa_draft", new_callable=AsyncMock)
    def test_happy_path(self, _draft, starter_client, quick_action_repos):
        quick_action_repos["prefs_repo"].delete_quick_action = AsyncMock(return_value=True)
        resp = starter_client.delete(self.URL)
        assert resp.status_code == 204

    @patch("src.multi_tenant.admin_quick_action_api._ensure_qa_draft", new_callable=AsyncMock)
    def test_404_not_found(self, _draft, starter_client, quick_action_repos):
        quick_action_repos["prefs_repo"].delete_quick_action = AsyncMock(return_value=False)
        resp = starter_client.delete(self.URL)
        assert resp.status_code == 404


# ===========================================================================
# Quick Actions — PUT /api/admin/quick-actions/assignments (Upsert)
# ===========================================================================


class TestUpsertPageAssignment(MutationTestBase):
    """PUT /api/admin/quick-actions/assignments — upsert page assignment."""

    URL = f"{QA_BASE}/assignments"

    def test_requires_auth(self, app_client, quick_action_repos):
        self.assert_requires_auth(app_client, "put", self.URL, json={"pageType": "home"})

    def test_rejects_widget_key(self, widget_client, quick_action_repos):
        self.assert_rejects_widget_key(widget_client, "put", self.URL, json={"pageType": "home"})

    @patch("src.multi_tenant.admin_quick_action_api._ensure_qa_draft", new_callable=AsyncMock)
    def test_happy_path(self, _draft, starter_client, quick_action_repos):
        quick_action_repos["prefs_repo"].get_quick_actions = AsyncMock(
            return_value=[_qa_action("qa-001")],
        )
        quick_action_repos["prefs_repo"].get_page_assignments = AsyncMock(return_value=[])
        quick_action_repos["prefs_repo"].upsert_page_assignment = AsyncMock(return_value=None)
        resp = starter_client.put(self.URL, json={
            "pageType": "home",
            "slot1ActionId": "qa-001",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["pageType"] == "home"

    @patch("src.multi_tenant.admin_quick_action_api._ensure_qa_draft", new_callable=AsyncMock)
    def test_400_invalid_page_type(self, _draft, starter_client, quick_action_repos):
        resp = starter_client.put(self.URL, json={"pageType": "nonexistent_page"})
        assert resp.status_code == 400

    @patch("src.multi_tenant.admin_quick_action_api._ensure_qa_draft", new_callable=AsyncMock)
    def test_404_referenced_action_not_found(self, _draft, starter_client, quick_action_repos):
        quick_action_repos["prefs_repo"].get_quick_actions = AsyncMock(return_value=[])
        resp = starter_client.put(self.URL, json={
            "pageType": "home",
            "slot1ActionId": "nonexistent-action",
        })
        assert resp.status_code == 404


# ===========================================================================
# Quick Actions — DELETE /api/admin/quick-actions/assignments/{page_type}
# ===========================================================================


class TestDeletePageAssignment(MutationTestBase):
    """DELETE /api/admin/quick-actions/assignments/{page_type} — delete assignment."""

    URL = f"{QA_BASE}/assignments/home"

    def test_requires_auth(self, app_client, quick_action_repos):
        self.assert_requires_auth(app_client, "delete", self.URL)

    def test_rejects_widget_key(self, widget_client, quick_action_repos):
        self.assert_rejects_widget_key(widget_client, "delete", self.URL)

    @patch("src.multi_tenant.admin_quick_action_api._ensure_qa_draft", new_callable=AsyncMock)
    def test_happy_path(self, _draft, starter_client, quick_action_repos):
        quick_action_repos["prefs_repo"].delete_page_assignment = AsyncMock(return_value=True)
        resp = starter_client.delete(self.URL)
        assert resp.status_code == 204

    @patch("src.multi_tenant.admin_quick_action_api._ensure_qa_draft", new_callable=AsyncMock)
    def test_404_not_found(self, _draft, starter_client, quick_action_repos):
        quick_action_repos["prefs_repo"].delete_page_assignment = AsyncMock(return_value=False)
        resp = starter_client.delete(self.URL)
        assert resp.status_code == 404


# ===========================================================================
# Quick Actions — POST /api/admin/quick-actions/seed
# ===========================================================================


class TestSeedQuickActions(MutationTestBase):
    """POST /api/admin/quick-actions/seed — seed starter actions."""

    URL = f"{QA_BASE}/seed"

    def test_requires_auth(self, app_client, quick_action_repos):
        self.assert_requires_auth(app_client, "post", self.URL)

    def test_rejects_widget_key(self, widget_client, quick_action_repos):
        self.assert_rejects_widget_key(widget_client, "post", self.URL)

    def test_happy_path_seeds_when_empty(self, starter_client, quick_action_repos):
        quick_action_repos["prefs_repo"].list_quick_actions = AsyncMock(return_value=[])
        quick_action_repos["prefs_repo"].upsert_quick_action = AsyncMock(return_value=None)
        resp = starter_client.post(self.URL)
        assert resp.status_code == 200
        data = resp.json()
        assert data["seeded"] == 4
        assert len(data["ids"]) == 4

    def test_idempotent_when_actions_exist(self, starter_client, quick_action_repos):
        quick_action_repos["prefs_repo"].list_quick_actions = AsyncMock(
            return_value=[_qa_action()],
        )
        resp = starter_client.post(self.URL)
        assert resp.status_code == 200
        assert resp.json()["seeded"] == 0


# ===========================================================================
# Conversations — POST /api/admin/conversations/{id}/assign
# ===========================================================================


class TestAssignConversation(MutationTestBase):
    """POST /api/admin/conversations/{id}/assign — assign agent."""

    URL = f"{CONV_BASE}/conv-001/assign"

    def test_requires_auth(self, app_client, conversation_repos):
        self.assert_requires_auth(app_client, "post", self.URL, json={"agentId": "agent-1"})

    def test_rejects_widget_key(self, widget_client, conversation_repos):
        self.assert_rejects_widget_key(widget_client, "post", self.URL, json={"agentId": "agent-1"})

    def test_happy_path(self, starter_client, conversation_repos):
        conversation_repos["conversation_repo"].assign_agent = AsyncMock(return_value=None)
        resp = starter_client.post(self.URL, json={"agentId": "agent-1"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["conversationId"] == "conv-001"
        assert data["assignedTo"] == "agent-1"
        assert data["assignedAt"] is not None

    def test_404_not_found(self, starter_client, conversation_repos):
        conversation_repos["conversation_repo"].assign_agent = AsyncMock(
            side_effect=DocumentNotFoundError("conversations", "conv-001", STARTER_TENANT_ID),
        )
        resp = starter_client.post(self.URL, json={"agentId": "agent-1"})
        assert resp.status_code == 404

    def test_422_missing_agent_id(self, starter_client, conversation_repos):
        self.assert_validation_error(starter_client, "post", self.URL, json={})


# ===========================================================================
# Conversations — POST /api/admin/conversations/{id}/escalate
# ===========================================================================


class TestEscalateConversation(MutationTestBase):
    """POST /api/admin/conversations/{id}/escalate — escalate to human."""

    URL = f"{CONV_BASE}/conv-001/escalate"

    def test_requires_auth(self, app_client, conversation_repos):
        self.assert_requires_auth(app_client, "post", self.URL)

    def test_rejects_widget_key(self, widget_client, conversation_repos):
        self.assert_rejects_widget_key(widget_client, "post", self.URL)

    @patch("src.multi_tenant.alert_delivery.send_escalation_alert", new_callable=AsyncMock)
    def test_happy_path(self, _alert, starter_client, conversation_repos):
        conversation_repos["conversation_repo"].read = AsyncMock(
            return_value=_conv_doc(status="active"),
        )
        conversation_repos["conversation_repo"].query = AsyncMock(return_value=[])
        conversation_repos["conversation_repo"].patch = AsyncMock(return_value=None)
        resp = starter_client.post(self.URL)
        assert resp.status_code == 200
        data = resp.json()
        assert data["conversationId"] == "conv-001"
        assert data["status"] == "escalated"

    def test_409_already_escalated(self, starter_client, conversation_repos):
        conversation_repos["conversation_repo"].read = AsyncMock(
            return_value=_conv_doc(status="escalated"),
        )
        conversation_repos["conversation_repo"].query = AsyncMock(return_value=[])
        resp = starter_client.post(self.URL)
        assert resp.status_code == 409


# ===========================================================================
# Conversations — POST /api/admin/conversations/{id}/resolve
# ===========================================================================


class TestResolveConversation(MutationTestBase):
    """POST /api/admin/conversations/{id}/resolve — mark resolved."""

    URL = f"{CONV_BASE}/conv-001/resolve"

    def test_requires_auth(self, app_client, conversation_repos):
        self.assert_requires_auth(app_client, "post", self.URL)

    def test_rejects_widget_key(self, widget_client, conversation_repos):
        self.assert_rejects_widget_key(widget_client, "post", self.URL)

    def test_happy_path(self, starter_client, conversation_repos):
        conversation_repos["conversation_repo"].read = AsyncMock(
            return_value=_conv_doc(status="active"),
        )
        conversation_repos["conversation_repo"].query = AsyncMock(return_value=[])
        conversation_repos["conversation_repo"].patch = AsyncMock(return_value=None)
        resp = starter_client.post(self.URL)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "resolved"
        assert data["resolvedAt"] is not None

    def test_409_already_resolved(self, starter_client, conversation_repos):
        conversation_repos["conversation_repo"].read = AsyncMock(
            return_value=_conv_doc(status="resolved"),
        )
        conversation_repos["conversation_repo"].query = AsyncMock(return_value=[])
        resp = starter_client.post(self.URL)
        assert resp.status_code == 409

    def test_404_not_found(self, starter_client, conversation_repos):
        conversation_repos["conversation_repo"].read = AsyncMock(
            side_effect=DocumentNotFoundError("conversations", "conv-001", STARTER_TENANT_ID),
        )
        conversation_repos["conversation_repo"].query = AsyncMock(return_value=[])
        resp = starter_client.post(self.URL)
        assert resp.status_code == 404


# ===========================================================================
# Conversations — POST /api/admin/conversations/{id}/notes
# ===========================================================================


class TestAddConversationNote(MutationTestBase):
    """POST /api/admin/conversations/{id}/notes — add internal note."""

    URL = f"{CONV_BASE}/conv-001/notes"

    def test_requires_auth(self, app_client, conversation_repos):
        self.assert_requires_auth(app_client, "post", self.URL, json={"content": "A note"})

    def test_rejects_widget_key(self, widget_client, conversation_repos):
        self.assert_rejects_widget_key(widget_client, "post", self.URL, json={"content": "A note"})

    def test_happy_path(self, starter_client, conversation_repos):
        conversation_repos["conversation_repo"].add_internal_note = AsyncMock(return_value=None)
        resp = starter_client.post(self.URL, json={"content": "Customer called back"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["conversationId"] == "conv-001"
        assert data["noteId"]
        assert data["createdAt"] is not None

    def test_404_not_found(self, starter_client, conversation_repos):
        conversation_repos["conversation_repo"].add_internal_note = AsyncMock(
            side_effect=DocumentNotFoundError("conversations", "conv-001", STARTER_TENANT_ID),
        )
        resp = starter_client.post(self.URL, json={"content": "A note"})
        assert resp.status_code == 404

    def test_422_missing_content(self, starter_client, conversation_repos):
        self.assert_validation_error(starter_client, "post", self.URL, json={})

    def test_422_empty_content(self, starter_client, conversation_repos):
        self.assert_validation_error(starter_client, "post", self.URL, json={"content": ""})


# ===========================================================================
# Conversations — POST /api/admin/conversations/search
# ===========================================================================


class TestSearchConversations(MutationTestBase):
    """POST /api/admin/conversations/search — full-text search."""

    URL = f"{CONV_BASE}/search"

    def test_requires_auth(self, app_client, conversation_repos):
        self.assert_requires_auth(app_client, "post", self.URL, json={"query": "hello"})

    def test_rejects_widget_key(self, widget_client, conversation_repos):
        self.assert_rejects_widget_key(widget_client, "post", self.URL, json={"query": "hello"})

    def test_happy_path(self, starter_client, conversation_repos):
        conversation_repos["conversation_repo"].query = AsyncMock(
            return_value=[
                {
                    "id": "conv-001",
                    "conversation_id": "conv-001",
                    "customer_name": "Jane hello Doe",
                    "status": "active",
                    "started_at": "2026-01-01T00:00:00Z",
                    "last_activity_at": "2026-01-01T01:00:00Z",
                    "message_count": 5,
                    "messages": [{"content": "hello world", "role": "user"}],
                    "internal_notes": [],
                },
            ],
        )
        resp = starter_client.post(self.URL, json={"query": "hello"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["totalResults"] >= 1
        assert data["results"][0]["conversationId"] == "conv-001"

    def test_422_missing_query(self, starter_client, conversation_repos):
        self.assert_validation_error(starter_client, "post", self.URL, json={})

    def test_422_empty_query(self, starter_client, conversation_repos):
        self.assert_validation_error(starter_client, "post", self.URL, json={"query": ""})


# ===========================================================================
# Memory — DELETE /api/admin/memory/customer/{customer_id}
# ===========================================================================


class TestDeleteCustomerMemory(MutationTestBase):
    """DELETE /api/admin/memory/customer/{customer_id} — GDPR erase."""

    URL = f"{MEMORY_BASE}/customer/cust-001"

    def test_requires_auth(self, app_client, memory_repos):
        self.assert_requires_auth(app_client, "delete", self.URL)

    def test_rejects_widget_key(self, widget_client, memory_repos):
        self.assert_rejects_widget_key(widget_client, "delete", self.URL)

    def test_happy_path(self, starter_client, memory_repos):
        memory_repos["memory_repo"].delete_by_customer = AsyncMock(return_value=12)
        resp = starter_client.delete(self.URL)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["customer_id"] == "cust-001"
        assert data["vectors_deleted"] == 12

    def test_503_when_service_not_configured(self, starter_client):
        """Memory repo is None — should return 503."""
        from src.multi_tenant.memory_dashboard import configure_memory_dashboard
        configure_memory_dashboard(memory_repo=None)
        try:
            resp = starter_client.delete(self.URL)
            assert resp.status_code == 503
        finally:
            configure_memory_dashboard(memory_repo=None)

    def test_500_on_repo_error(self, starter_client, memory_repos):
        memory_repos["memory_repo"].delete_by_customer = AsyncMock(
            side_effect=RuntimeError("Cosmos connection lost"),
        )
        resp = starter_client.delete(self.URL)
        assert resp.status_code == 500
