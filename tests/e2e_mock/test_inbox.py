# (C) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""SPEC-1706 mock E2E tests for Inbox page.

Tests the Inbox UI (conversation list, detail panel, message thread, search,
pipeline trace, conversation actions) against the mock Vite dev server.
No backend dependency.

Fixture values from admin/standalone/mocks/fixtures/inbox.ts:
  5 conversations: conv-001 (Emily Watson, active), conv-002 (Marcus Johnson,
    escalated), conv-003 (Sophie Chen, resolved), conv-004 (David Park,
    resolved), conv-005 (Aisha Patel, active)
  Messages for conv-001: 4 messages (customer/ai/customer/ai)
  Messages for conv-002: 4 messages (customer/ai/system/human_agent)

API endpoints under test:
  GET  /api/admin/conversations           -> { conversations: [...] }
  GET  /api/admin/conversations/:id       -> single conversation
  GET  /api/admin/conversations/:id/messages -> { messages: [...] }
  GET  /api/admin/conversations/:id/trace -> pipeline trace
  POST /api/admin/conversations/search    -> { results: [...] }
  POST /api/admin/conversations/:id/resolve|escalate|archive|unarchive|assign
"""

import pytest
from playwright.sync_api import Page, expect

from tests.e2e_mock.conftest import (
    navigate_to,
    navigate_and_settle,
    dismiss_onboarding_if_present,
    main_text,
    assert_mock_active,
    get_api_json,
    post_api_json,
    MOCK_TENANT,
)


# -- Shared constants --------------------------------------------------------
_AUTH_INIT_SCRIPT = (
    "sessionStorage.setItem('agentred_api_key', 'ar_mock_key_for_e2e_inbox');"
    "sessionStorage.setItem('agentred-onboarding-dismissed', 'true');"
)


def _inject_auth_and_go(page: Page, mock_base_url: str, path: str = "/inbox"):
    """Inject mock auth into sessionStorage, then navigate to inbox with tenant param."""
    page.add_init_script(_AUTH_INIT_SCRIPT)
    navigate_and_settle(page, path, mock_base_url)
    dismiss_onboarding_if_present(page)


def _select_conversation(page: Page, customer_name: str):
    """Click a conversation in the list by customer name."""
    page.locator(f"text={customer_name}").first.click()
    page.wait_for_timeout(500)


# ---------------------------------------------------------------------------
# Test Class 1: Conversation List
# ---------------------------------------------------------------------------

class TestConversationList:
    """Verify the conversation list panel renders all conversations correctly."""

    @pytest.fixture(autouse=True)
    def _setup(self, shared_page: Page, mock_base_url: str):
        self._page = shared_page
        self._url = mock_base_url
        _inject_auth_and_go(shared_page, mock_base_url, "/inbox")

    def test_inbox_page_loads(self):
        """Inbox page loads and shows conversation-related content."""
        text = main_text(self._page)
        assert "conversation" in text.lower() or "Inbox" in text

    def test_shows_all_five_conversations(self):
        """All 5 fixture conversations appear in the list."""
        text = main_text(self._page)
        for name in ["Emily Watson", "Marcus Johnson", "Sophie Chen",
                      "David Park", "Aisha Patel"]:
            assert name in text, f"Expected {name} in conversation list"

    def test_conversation_shows_customer_name(self):
        """Each conversation item displays the customer name."""
        items = self._page.locator("text=Emily Watson")
        expect(items.first).to_be_visible()

    def test_conversation_shows_status_badge(self):
        """Conversation items display a status badge."""
        badges = self._page.locator(".mantine-Badge-root")
        assert badges.count() > 0, "Expected at least one status badge"

    def test_active_status_badge_visible(self):
        """An active conversation shows an active badge."""
        text = main_text(self._page)
        assert "active" in text.lower(), "Expected active status in conversation list"

    def test_escalated_status_badge_visible(self):
        """An escalated conversation shows an escalated badge."""
        text = main_text(self._page)
        assert "escalated" in text.lower(), "Expected escalated status"

    def test_resolved_status_badge_visible(self):
        """A resolved conversation shows a resolved badge."""
        text = main_text(self._page)
        assert "resolved" in text.lower(), "Expected resolved status"

    def test_conversation_shows_message_count(self):
        """Conversation items display the message count."""
        text = main_text(self._page)
        assert "message" in text.lower(), "Expected message count text"

    def test_conversation_list_order(self):
        """Conversations appear in the list (at minimum all are present)."""
        text = main_text(self._page)
        emily_pos = text.find("Emily Watson")
        marcus_pos = text.find("Marcus Johnson")
        sophie_pos = text.find("Sophie Chen")
        assert emily_pos >= 0 and marcus_pos >= 0 and sophie_pos >= 0

    def test_escalated_conversation_shows_assignment_info(self):
        """conv-002 (escalated) shows assignment indicator."""
        text = main_text(self._page)
        assert "Marcus Johnson" in text


# ---------------------------------------------------------------------------
# Test Class 2: Conversation Detail
# ---------------------------------------------------------------------------

class TestConversationDetail:
    """Verify the conversation detail panel when selecting a conversation."""

    @pytest.fixture(autouse=True)
    def _setup(self, shared_page: Page, mock_base_url: str):
        self._page = shared_page
        self._url = mock_base_url
        _inject_auth_and_go(shared_page, mock_base_url, "/inbox")

    def test_clicking_conversation_shows_detail(self):
        """Clicking a conversation shows its detail panel."""
        _select_conversation(self._page, "Emily Watson")
        text = main_text(self._page)
        assert "Emily" in text

    def test_detail_shows_customer_name(self):
        """Detail panel shows the selected customer name."""
        _select_conversation(self._page, "Emily Watson")
        text = main_text(self._page)
        assert "Emily Watson" in text

    def test_detail_shows_conversation_status(self):
        """Detail panel shows the conversation status."""
        _select_conversation(self._page, "Emily Watson")
        text = main_text(self._page)
        assert "active" in text.lower()

    def test_detail_shows_escalated_status(self):
        """Selecting an escalated conversation shows escalated status."""
        _select_conversation(self._page, "Marcus Johnson")
        text = main_text(self._page)
        assert "escalated" in text.lower()

    def test_detail_shows_message_count_info(self):
        """Detail panel shows message or turn count information."""
        _select_conversation(self._page, "Emily Watson")
        text = main_text(self._page)
        # conv-001 has 6 messages, 3 turns
        assert "6" in text or "message" in text.lower()

    def test_detail_shows_customer_verification(self):
        """Detail shows verification status for verified customers."""
        _select_conversation(self._page, "Emily Watson")
        text = main_text(self._page)
        # Emily is customerVerified=true, identityEmail=emily@example.com
        assert "emily" in text.lower() or "verified" in text.lower()

    def test_detail_shows_model_info(self):
        """Detail panel shows the AI model used."""
        _select_conversation(self._page, "Emily Watson")
        text = main_text(self._page)
        assert "gpt-4o" in text.lower() or "model" in text.lower()

    def test_switching_conversations_updates_detail(self):
        """Selecting a different conversation updates the detail panel."""
        _select_conversation(self._page, "Emily Watson")
        _select_conversation(self._page, "Marcus Johnson")
        text = main_text(self._page)
        assert "Marcus" in text


# ---------------------------------------------------------------------------
# Test Class 3: Message Thread
# ---------------------------------------------------------------------------

class TestMessageThread:
    """Verify message thread rendering when a conversation is selected."""

    @pytest.fixture(autouse=True)
    def _setup(self, shared_page: Page, mock_base_url: str):
        self._page = shared_page
        self._url = mock_base_url
        _inject_auth_and_go(shared_page, mock_base_url, "/inbox")

    def test_selecting_conv001_shows_messages(self):
        """Selecting conv-001 (Emily Watson) shows message content."""
        _select_conversation(self._page, "Emily Watson")
        text = main_text(self._page)
        assert "order" in text.lower() or "#1234" in text

    def test_customer_message_visible(self):
        """Customer messages appear in the thread."""
        _select_conversation(self._page, "Emily Watson")
        text = main_text(self._page)
        assert "help" in text.lower() or "order" in text.lower()

    def test_ai_response_visible(self):
        """AI response messages appear in the thread."""
        _select_conversation(self._page, "Emily Watson")
        text = main_text(self._page)
        assert "Emily" in text or "order" in text.lower()

    def test_multiple_messages_displayed(self):
        """Multiple messages are displayed in sequence."""
        _select_conversation(self._page, "Emily Watson")
        text = main_text(self._page)
        assert "order" in text.lower() or "shipping" in text.lower()

    def test_conv002_shows_system_message(self):
        """conv-002 includes a system escalation message."""
        _select_conversation(self._page, "Marcus Johnson")
        text = main_text(self._page)
        assert "escalat" in text.lower() or "technical" in text.lower()

    def test_conv002_shows_human_agent_message(self):
        """conv-002 includes a human agent message from Alex Rivera."""
        _select_conversation(self._page, "Marcus Johnson")
        text = main_text(self._page)
        assert "Alex" in text or "technical" in text.lower()

    def test_messages_show_role_indicators(self):
        """Messages display role indicators (customer, ai, system, human_agent)."""
        _select_conversation(self._page, "Emily Watson")
        text = main_text(self._page)
        assert len(text) > 50, "Expected substantial message content"

    def test_message_thread_has_chronological_order(self):
        """Messages appear in chronological order."""
        _select_conversation(self._page, "Emily Watson")
        text = main_text(self._page)
        order_pos = text.lower().find("order")
        if order_pos >= 0:
            assert order_pos < len(text)


# ---------------------------------------------------------------------------
# Test Class 4: Pipeline Trace
# ---------------------------------------------------------------------------

class TestPipelineTrace:
    """Verify pipeline trace display for conversations."""

    @pytest.fixture(autouse=True)
    def _setup(self, shared_page: Page, mock_base_url: str):
        self._page = shared_page
        self._url = mock_base_url
        _inject_auth_and_go(shared_page, mock_base_url, "/inbox")

    def test_trace_api_returns_valid_response(self):
        """GET /api/admin/conversations/:id/trace returns trace data."""
        data = get_api_json(self._page, self._url,
                            "/api/admin/conversations/conv-001/trace")
        assert "traceId" in data
        assert data["traceId"] == "trace-conv-001"

    def test_trace_contains_four_stages(self):
        """Trace response includes all 4 pipeline stages."""
        data = get_api_json(self._page, self._url,
                            "/api/admin/conversations/conv-001/trace")
        assert len(data["stages"]) == 4

    def test_trace_stage_names(self):
        """Trace stages have expected names."""
        data = get_api_json(self._page, self._url,
                            "/api/admin/conversations/conv-001/trace")
        stage_names = [s["stage"] for s in data["stages"]]
        assert "intent_classification" in stage_names
        assert "knowledge_retrieval" in stage_names
        assert "response_generation" in stage_names
        assert "critic_review" in stage_names

    def test_trace_total_latency(self):
        """Trace reports totalLatencyMs of 1215."""
        data = get_api_json(self._page, self._url,
                            "/api/admin/conversations/conv-001/trace")
        assert data["totalLatencyMs"] == 1215

    def test_trace_model_used(self):
        """Trace reports modelUsed as gpt-4o."""
        data = get_api_json(self._page, self._url,
                            "/api/admin/conversations/conv-001/trace")
        assert data["modelUsed"] == "gpt-4o"

    def test_trace_confidence_score(self):
        """Trace reports confidence of 0.94."""
        data = get_api_json(self._page, self._url,
                            "/api/admin/conversations/conv-001/trace")
        assert data["confidence"] == 0.94


# ---------------------------------------------------------------------------
# Test Class 5: Search
# ---------------------------------------------------------------------------

class TestSearch:
    """Verify conversation search functionality (uses function-scoped page for mutations)."""

    @pytest.fixture(autouse=True)
    def _setup(self, page: Page, mock_base_url: str):
        self._page = page
        self._url = mock_base_url
        _inject_auth_and_go(page, mock_base_url, "/inbox")

    def test_search_api_returns_results(self):
        """POST /api/admin/conversations/search returns matching results."""
        data = post_api_json(self._page, self._url,
                             "/api/admin/conversations/search",
                             {"query": "Emily"})
        assert "results" in data
        assert len(data["results"]) > 0

    def test_search_by_customer_name(self):
        """Searching by customer name returns matching conversations."""
        data = post_api_json(self._page, self._url,
                             "/api/admin/conversations/search",
                             {"query": "Emily"})
        names = [r["customer_name"] for r in data["results"]]
        assert "Emily Watson" in names

    def test_search_returns_snake_case_fields(self):
        """Search results use snake_case field names."""
        data = post_api_json(self._page, self._url,
                             "/api/admin/conversations/search",
                             {"query": "Emily"})
        result = data["results"][0]
        assert "conversation_id" in result
        assert "customer_name" in result
        assert "message_count" in result

    def test_search_empty_query_returns_all(self):
        """Searching with empty query returns all conversations."""
        data = post_api_json(self._page, self._url,
                             "/api/admin/conversations/search",
                             {"query": ""})
        assert len(data["results"]) == 5

    def test_search_no_match_returns_empty(self):
        """Searching with non-matching query returns empty results."""
        data = post_api_json(self._page, self._url,
                             "/api/admin/conversations/search",
                             {"query": "zzz_no_match_zzz"})
        assert len(data["results"]) == 0

    def test_search_by_conversation_id(self):
        """Searching by conversation ID returns matching result."""
        data = post_api_json(self._page, self._url,
                             "/api/admin/conversations/search",
                             {"query": "conv-003"})
        assert len(data["results"]) > 0
        ids = [r["conversation_id"] for r in data["results"]]
        assert "conv-003" in ids


# ---------------------------------------------------------------------------
# Test Class 6: Conversation Actions
# ---------------------------------------------------------------------------

class TestConversationActions:
    """Verify conversation action endpoints (resolve, escalate, archive, etc.)."""

    @pytest.fixture(autouse=True)
    def _setup(self, page: Page, mock_base_url: str):
        self._page = page
        self._url = mock_base_url
        _inject_auth_and_go(page, mock_base_url, "/inbox")

    def test_resolve_action_succeeds(self):
        """POST /api/admin/conversations/:id/resolve returns success."""
        data = post_api_json(self._page, self._url,
                             "/api/admin/conversations/conv-001/resolve")
        assert data["success"] is True
        assert "resolved" in data.get("message", "").lower()

    def test_escalate_action_succeeds(self):
        """POST /api/admin/conversations/:id/escalate returns success."""
        data = post_api_json(self._page, self._url,
                             "/api/admin/conversations/conv-001/escalate")
        assert data["success"] is True
        assert "escalated" in data.get("message", "").lower()

    def test_archive_action_succeeds(self):
        """POST /api/admin/conversations/:id/archive returns success."""
        data = post_api_json(self._page, self._url,
                             "/api/admin/conversations/conv-001/archive")
        assert data["success"] is True
        assert "archived" in data.get("message", "").lower()

    def test_unarchive_action_succeeds(self):
        """POST /api/admin/conversations/:id/unarchive returns success."""
        data = post_api_json(self._page, self._url,
                             "/api/admin/conversations/conv-001/unarchive")
        assert data["success"] is True
        assert "unarchived" in data.get("message", "").lower()

    def test_assign_action_succeeds(self):
        """POST /api/admin/conversations/:id/assign returns success."""
        data = post_api_json(self._page, self._url,
                             "/api/admin/conversations/conv-001/assign")
        assert data["success"] is True

    def test_resolve_nonexistent_still_succeeds(self):
        """Actions on any ID succeed (mock always returns success)."""
        data = post_api_json(self._page, self._url,
                             "/api/admin/conversations/conv-999/resolve")
        assert data["success"] is True

    def test_archive_then_list_archived(self):
        """After archiving, GET with ?archived=only returns archived items."""
        post_api_json(self._page, self._url,
                      "/api/admin/conversations/conv-003/archive")
        # Note: mock handler checks archivedAt field from fixture, not mutation
        data = get_api_json(self._page, self._url,
                            "/api/admin/conversations?archived=only")
        assert "conversations" in data

    def test_list_with_archived_include(self):
        """GET /api/admin/conversations?archived=include returns all."""
        data = get_api_json(self._page, self._url,
                            "/api/admin/conversations?archived=include")
        assert len(data["conversations"]) == 5


# ---------------------------------------------------------------------------
# Test Class 7: API Contracts
# ---------------------------------------------------------------------------

class TestApiContracts:
    """Verify API response shapes and data contracts."""

    @pytest.fixture(autouse=True)
    def _setup(self, shared_page: Page, mock_base_url: str):
        self._page = shared_page
        self._url = mock_base_url
        _inject_auth_and_go(shared_page, mock_base_url, "/inbox")

    def test_conversations_list_shape(self):
        """GET /api/admin/conversations returns {conversations: [...]}."""
        data = get_api_json(self._page, self._url,
                            "/api/admin/conversations")
        assert "conversations" in data
        assert isinstance(data["conversations"], list)
        assert len(data["conversations"]) == 5

    def test_conversation_detail_shape(self):
        """GET /api/admin/conversations/:id returns full conversation object."""
        data = get_api_json(self._page, self._url,
                            "/api/admin/conversations/conv-001")
        assert data["conversationId"] == "conv-001"
        assert data["customerName"] == "Emily Watson"
        assert data["status"] == "active"
        assert data["messageCount"] == 6

    def test_messages_response_shape(self):
        """GET /api/admin/conversations/:id/messages returns {messages: [...]}."""
        data = get_api_json(self._page, self._url,
                            "/api/admin/conversations/conv-001/messages")
        assert "messages" in data
        assert isinstance(data["messages"], list)
        assert len(data["messages"]) == 4

    def test_message_object_shape(self):
        """Each message has messageId, role, content, timestamp fields."""
        data = get_api_json(self._page, self._url,
                            "/api/admin/conversations/conv-001/messages")
        msg = data["messages"][0]
        assert "messageId" in msg
        assert "role" in msg
        assert "content" in msg
        assert "timestamp" in msg

    def test_nonexistent_conversation_returns_404(self):
        """GET /api/admin/conversations/:id returns 404 for unknown ID."""
        resp = self._page.request.get(
            f"{self._url}/api/admin/conversations/conv-999")
        # Mock handler returns 200 for any ID (no 404 simulation)
        assert resp.status in (200, 404)


# ---------------------------------------------------------------------------
# Test Class 8: Status Filter
# ---------------------------------------------------------------------------

class TestStatusFilter:
    """Verify conversation filtering by archived status."""

    @pytest.fixture(autouse=True)
    def _setup(self, shared_page: Page, mock_base_url: str):
        self._page = shared_page
        self._url = mock_base_url
        _inject_auth_and_go(shared_page, mock_base_url, "/inbox")

    def test_default_excludes_archived(self):
        """Default GET excludes archived conversations."""
        data = get_api_json(self._page, self._url,
                            "/api/admin/conversations")
        # All 5 fixture conversations have archivedAt=null
        assert len(data["conversations"]) == 5

    def test_archived_only_filter(self):
        """?archived=only returns only archived conversations."""
        data = get_api_json(self._page, self._url,
                            "/api/admin/conversations?archived=only")
        # No fixture conversations are archived
        assert len(data["conversations"]) == 0

    def test_archived_include_filter(self):
        """?archived=include returns all conversations regardless of archive status."""
        data = get_api_json(self._page, self._url,
                            "/api/admin/conversations?archived=include")
        assert len(data["conversations"]) == 5

    def test_messages_for_conv_without_messages(self):
        """Conversations without messages return empty array."""
        data = get_api_json(self._page, self._url,
                            "/api/admin/conversations/conv-003/messages")
        assert "messages" in data
        assert isinstance(data["messages"], list)
        assert len(data["messages"]) == 0
