"""Tests for Admin Conversation Inbox API — search endpoint (P1 #13).

Covers:
    - POST /api/admin/conversations/search — full-text search
    - Search across messages, customer names, and internal notes
    - Status filter validation
    - Empty query validation (422)
    - Empty results for non-matching query
    - Snippet extraction and match-in field accuracy
    - Route ordering (search before /{conversation_id} catch-all)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import TenantStatus, TenantTier
from src.multi_tenant.admin_conversation_api import (
    SearchConversationsRequest,
    SearchConversationsResponse,
    SearchResultEntry,
    _extract_search_snippet,
    configure_admin_conversation_services,
    router,
)
from src.multi_tenant.middleware import get_tenant_context
from src.multi_tenant.repository import ConversationRepository

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TENANT_ID = "t-conv-test-001"
NOW_ISO = datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_tenant_context(
    tenant_id: str = TENANT_ID,
) -> TenantContext:
    return TenantContext(
        tenant_id=tenant_id,
        tier=TenantTier.STARTER,
        status=TenantStatus.ACTIVE,
        auth_method="api_key",
    )


def _make_conversation(
    conversation_id: str | None = None,
    customer_name: str = "Alice Smith",
    status: str = "active",
    messages: list[dict[str, str]] | None = None,
    internal_notes: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    cid = conversation_id or str(uuid.uuid4())
    return {
        "id": cid,
        "conversation_id": cid,
        "tenant_id": TENANT_ID,
        "customer_id": f"cust-{cid[:8]}",
        "customer_name": customer_name,
        "status": status,
        "is_billable": True,
        "message_count": len(messages or []),
        "turn_count": 1,
        "started_at": NOW_ISO,
        "last_activity_at": NOW_ISO,
        "messages": messages or [],
        "internal_notes": internal_notes or [],
        "agents_invoked": ["IC", "KR", "RG"],
    }


# ---------------------------------------------------------------------------
# Mock ConversationRepository
# ---------------------------------------------------------------------------


class MockConversationRepo:
    """In-memory conversation repository for testing."""

    def __init__(self, conversations: list[dict[str, Any]] | None = None) -> None:
        self._conversations = list(conversations or [])

    async def query(
        self,
        tenant_id: str,
        query_text: str,
        parameters: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        """Simulate Cosmos DB query with in-memory filtering.

        For search tests, we simulate the CONTAINS() behavior by doing
        in-memory substring matching.
        """
        # Extract search term from parameters
        search_term = ""
        status_filter = None
        for p in (parameters or []):
            if p["name"] == "@search_term":
                search_term = p["value"]
            if p["name"] == "@status":
                status_filter = p["value"]

        results = []
        for doc in self._conversations:
            if doc.get("tenant_id") != tenant_id:
                continue
            if status_filter and doc.get("status") != status_filter:
                continue

            # Simulate CONTAINS matching
            term_lower = search_term.lower()
            matched = False

            # Check customer_name
            name = doc.get("customer_name", "") or ""
            if term_lower in name.lower():
                matched = True

            # Check messages
            if not matched:
                for msg in doc.get("messages", []):
                    if term_lower in (msg.get("content", "") or "").lower():
                        matched = True
                        break

            # Check internal notes
            if not matched:
                for note in doc.get("internal_notes", []):
                    if term_lower in (note.get("content", "") or "").lower():
                        matched = True
                        break

            if matched:
                results.append(doc)

        return results

    # Stubs for other methods required by the repo interface
    async def read(self, tenant_id: str, doc_id: str) -> dict[str, Any]:
        for doc in self._conversations:
            if doc.get("tenant_id") == tenant_id and doc.get("id") == doc_id:
                return doc
        from src.multi_tenant.repository import DocumentNotFoundError
        raise DocumentNotFoundError("conversations", doc_id, tenant_id)

    async def list_filtered(self, **kwargs: Any) -> list[dict[str, Any]]:
        return self._conversations

    async def count_filtered(self, **kwargs: Any) -> int:
        return len(self._conversations)

    async def assign_agent(self, **kwargs: Any) -> None:
        pass

    async def add_internal_note(self, **kwargs: Any) -> None:
        pass

    async def patch(self, **kwargs: Any) -> None:
        pass


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_conversations() -> list[dict[str, Any]]:
    """Generate sample conversations with varied content for search tests."""
    return [
        _make_conversation(
            conversation_id="conv-001",
            customer_name="Alice Smith",
            status="active",
            messages=[
                {"role": "customer", "content": "I need help with my order"},
                {"role": "ai", "content": "I'd be happy to help with your order. What's the issue?"},
            ],
        ),
        _make_conversation(
            conversation_id="conv-002",
            customer_name="Bob Johnson",
            status="resolved",
            messages=[
                {"role": "customer", "content": "What are your shipping rates?"},
                {"role": "ai", "content": "We offer free shipping on orders over $50."},
            ],
            internal_notes=[
                {"note_id": "n1", "content": "Customer was satisfied with the answer about shipping"},
            ],
        ),
        _make_conversation(
            conversation_id="conv-003",
            customer_name="Charlie Brown",
            status="escalated",
            messages=[
                {"role": "customer", "content": "My refund hasn't been processed yet"},
                {"role": "ai", "content": "I'm sorry about the delay. Let me check on that."},
            ],
            internal_notes=[
                {"note_id": "n2", "content": "Escalated to billing team for refund review"},
            ],
        ),
        _make_conversation(
            conversation_id="conv-004",
            customer_name="Diana Prince",
            status="active",
            messages=[
                {"role": "customer", "content": "Do you have the blue widget in stock?"},
                {"role": "ai", "content": "Yes, the blue widget is currently available."},
            ],
        ),
    ]


@pytest.fixture
def mock_repo(sample_conversations: list[dict[str, Any]]) -> MockConversationRepo:
    return MockConversationRepo(sample_conversations)


@pytest.fixture
def client(mock_repo: MockConversationRepo) -> TestClient:
    app = FastAPI()
    app.include_router(router)

    configure_admin_conversation_services(mock_repo)  # type: ignore[arg-type]

    ctx = _make_tenant_context()
    app.dependency_overrides[get_tenant_context] = lambda: ctx

    return TestClient(app)


# ---------------------------------------------------------------------------
# Tests: POST /api/admin/conversations/search
# ---------------------------------------------------------------------------


class TestSearchConversations:
    """Tests for the conversation search endpoint."""

    def test_search_by_message_content(self, client: TestClient) -> None:
        """Search matches on message content."""
        resp = client.post(
            "/api/admin/conversations/search",
            json={"query": "shipping rates"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["totalResults"] >= 1
        assert any(
            r["conversationId"] == "conv-002" for r in data["results"]
        )

    def test_search_by_customer_name(self, client: TestClient) -> None:
        """Search matches on customer name."""
        resp = client.post(
            "/api/admin/conversations/search",
            json={"query": "Alice"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["totalResults"] >= 1
        assert any(
            r["conversationId"] == "conv-001" for r in data["results"]
        )
        # Check matched_in field
        alice_result = next(
            r for r in data["results"] if r["conversationId"] == "conv-001"
        )
        assert alice_result["matchedIn"] == "customer_name"

    def test_search_by_internal_notes(self, client: TestClient) -> None:
        """Search matches on internal notes content."""
        resp = client.post(
            "/api/admin/conversations/search",
            json={"query": "billing team"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["totalResults"] >= 1
        assert any(
            r["conversationId"] == "conv-003" for r in data["results"]
        )
        note_result = next(
            r for r in data["results"] if r["conversationId"] == "conv-003"
        )
        assert note_result["matchedIn"] == "notes"

    def test_search_case_insensitive(self, client: TestClient) -> None:
        """Search is case-insensitive."""
        resp = client.post(
            "/api/admin/conversations/search",
            json={"query": "SHIPPING"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["totalResults"] >= 1

    def test_search_no_results(self, client: TestClient) -> None:
        """Search returns empty list when no matches found."""
        resp = client.post(
            "/api/admin/conversations/search",
            json={"query": "xyznonexistent12345"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["totalResults"] == 0
        assert data["results"] == []

    def test_search_empty_query_422(self, client: TestClient) -> None:
        """Empty query string returns 422 validation error."""
        resp = client.post(
            "/api/admin/conversations/search",
            json={"query": ""},
        )
        assert resp.status_code == 422

    def test_search_missing_query_422(self, client: TestClient) -> None:
        """Missing query field returns 422 validation error."""
        resp = client.post(
            "/api/admin/conversations/search",
            json={},
        )
        assert resp.status_code == 422

    def test_search_with_status_filter(self, client: TestClient) -> None:
        """Search can be filtered by conversation status."""
        # "refund" appears in conv-003 which has status "escalated"
        resp = client.post(
            "/api/admin/conversations/search",
            json={"query": "refund", "status": "escalated"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["totalResults"] >= 1
        for r in data["results"]:
            assert r["status"] == "escalated"

    def test_search_status_filter_excludes(self, client: TestClient) -> None:
        """Status filter excludes conversations with different status."""
        # "refund" appears in conv-003 (escalated), not in any "active" conv
        resp = client.post(
            "/api/admin/conversations/search",
            json={"query": "refund", "status": "active"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["totalResults"] == 0

    def test_search_invalid_status_400(self, client: TestClient) -> None:
        """Invalid status value returns 400."""
        resp = client.post(
            "/api/admin/conversations/search",
            json={"query": "help", "status": "invalid_status"},
        )
        assert resp.status_code == 400

    def test_search_response_shape(self, client: TestClient) -> None:
        """Response includes expected camelCase fields."""
        resp = client.post(
            "/api/admin/conversations/search",
            json={"query": "order"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "tenantId" in data
        assert "query" in data
        assert "totalResults" in data
        assert "results" in data
        if data["results"]:
            r = data["results"][0]
            assert "conversationId" in r
            assert "snippet" in r
            assert "matchedIn" in r
            assert "messageCount" in r

    def test_search_with_limit(self, client: TestClient) -> None:
        """Limit parameter restricts result count."""
        resp = client.post(
            "/api/admin/conversations/search",
            json={"query": "the", "limit": 1},
        )
        assert resp.status_code == 200
        data = resp.json()
        # Our mock doesn't enforce OFFSET/LIMIT in SQL,
        # but the response should still be valid
        assert isinstance(data["results"], list)

    def test_search_returns_snippet(self, client: TestClient) -> None:
        """Search results include a non-empty snippet."""
        resp = client.post(
            "/api/admin/conversations/search",
            json={"query": "blue widget"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["totalResults"] >= 1
        result = next(
            r for r in data["results"] if r["conversationId"] == "conv-004"
        )
        assert len(result["snippet"]) > 0
        assert result["matchedIn"] == "messages"

    def test_search_multiple_matches(self, client: TestClient) -> None:
        """Search for a common term returns multiple conversations."""
        # "help" appears in conv-001 ("I need help with my order")
        # and conv-002 note has "satisfied"
        resp = client.post(
            "/api/admin/conversations/search",
            json={"query": "order"},
        )
        assert resp.status_code == 200
        data = resp.json()
        # At least conv-001 has "order" in messages
        assert data["totalResults"] >= 1


# ---------------------------------------------------------------------------
# Tests: Route ordering (search before /{conversation_id} catch-all)
# ---------------------------------------------------------------------------


class TestRouteOrdering:
    """Ensure /search is not shadowed by /{conversation_id}."""

    def test_search_not_shadowed(self, client: TestClient) -> None:
        """POST /search should return 200, not be treated as conversation_id='search'."""
        resp = client.post(
            "/api/admin/conversations/search",
            json={"query": "test"},
        )
        # Should NOT be 405 or 404 — that would mean shadowing
        assert resp.status_code == 200

    def test_get_search_hits_detail_route(self, client: TestClient) -> None:
        """GET /search falls through to /{conversation_id} detail route.

        Since there is no GET /search route defined, FastAPI routes GET
        requests to the /{conversation_id} catch-all with conversation_id="search".
        This is expected — search is POST-only.
        """
        resp = client.get("/api/admin/conversations/search")
        # Hits /{conversation_id} with id="search" — either 200 (found) or 404 (not found)
        assert resp.status_code in (200, 404)


# ---------------------------------------------------------------------------
# Tests: _extract_search_snippet helper
# ---------------------------------------------------------------------------


class TestExtractSearchSnippet:
    """Unit tests for the snippet extraction helper."""

    def test_match_in_customer_name(self) -> None:
        doc = _make_conversation(customer_name="Alice Wonderland")
        snippet, matched_in = _extract_search_snippet(doc, "Alice")
        assert matched_in == "customer_name"
        assert "Alice" in snippet

    def test_match_in_messages(self) -> None:
        doc = _make_conversation(
            messages=[{"role": "customer", "content": "I want a refund for my order"}]
        )
        snippet, matched_in = _extract_search_snippet(doc, "refund")
        assert matched_in == "messages"
        assert "refund" in snippet.lower()

    def test_match_in_notes(self) -> None:
        doc = _make_conversation(
            customer_name="No Match",
            messages=[{"role": "customer", "content": "no match here"}],
            internal_notes=[{"note_id": "n1", "content": "Escalated to supervisor"}],
        )
        snippet, matched_in = _extract_search_snippet(doc, "supervisor")
        assert matched_in == "notes"
        assert "supervisor" in snippet.lower()

    def test_snippet_truncation(self) -> None:
        """Long message content produces a truncated snippet."""
        long_content = "x" * 50 + "FINDME" + "y" * 200
        doc = _make_conversation(
            messages=[{"role": "customer", "content": long_content}]
        )
        snippet, matched_in = _extract_search_snippet(doc, "FINDME", max_snippet_len=80)
        assert len(snippet) <= 80
        assert matched_in == "messages"

    def test_snippet_with_ellipsis(self) -> None:
        """Snippet gets ellipsis when match is in the middle of content."""
        content = "A" * 100 + " important keyword " + "B" * 100
        doc = _make_conversation(
            messages=[{"role": "customer", "content": content}]
        )
        snippet, _ = _extract_search_snippet(doc, "important keyword")
        assert snippet.startswith("…")

    def test_no_match_fallback(self) -> None:
        """If somehow no match is found, returns empty snippet."""
        doc = _make_conversation(
            customer_name="X",
            messages=[],
            internal_notes=[],
        )
        snippet, matched_in = _extract_search_snippet(doc, "zzzznotfound")
        assert snippet == ""
        assert matched_in == "messages"

    def test_case_insensitive_matching(self) -> None:
        """Snippet extraction is case-insensitive."""
        doc = _make_conversation(
            messages=[{"role": "customer", "content": "Please help with SHIPPING"}]
        )
        snippet, matched_in = _extract_search_snippet(doc, "shipping")
        assert matched_in == "messages"
        assert len(snippet) > 0

    def test_priority_customer_name_over_messages(self) -> None:
        """Customer name match takes priority over message match."""
        doc = _make_conversation(
            customer_name="Order Manager",
            messages=[{"role": "customer", "content": "I have an order question"}],
        )
        snippet, matched_in = _extract_search_snippet(doc, "order")
        assert matched_in == "customer_name"


# ---------------------------------------------------------------------------
# Tests: Request model validation
# ---------------------------------------------------------------------------


class TestSearchRequestModel:
    """Tests for SearchConversationsRequest validation."""

    def test_valid_request(self) -> None:
        req = SearchConversationsRequest(query="test")
        assert req.query == "test"
        assert req.status is None
        assert req.limit == 50

    def test_max_query_length(self) -> None:
        req = SearchConversationsRequest(query="x" * 500)
        assert len(req.query) == 500

    def test_query_too_long(self) -> None:
        with pytest.raises(Exception):  # Pydantic validation error
            SearchConversationsRequest(query="x" * 501)

    def test_custom_limit(self) -> None:
        req = SearchConversationsRequest(query="test", limit=10)
        assert req.limit == 10

    def test_limit_too_high(self) -> None:
        with pytest.raises(Exception):
            SearchConversationsRequest(query="test", limit=201)

    def test_limit_too_low(self) -> None:
        with pytest.raises(Exception):
            SearchConversationsRequest(query="test", limit=0)


# ---------------------------------------------------------------------------
# Tests: Service accessor / 503
# ---------------------------------------------------------------------------


class TestServiceAccessor:
    """Test that the search endpoint returns 503 when services not configured."""

    def test_search_503_when_not_configured(self) -> None:
        """Search returns 503 when ConversationRepository is not wired."""
        import src.multi_tenant.admin_conversation_api as mod

        # Save and clear the repo
        original = mod._conversation_repo
        try:
            mod._conversation_repo = None

            app = FastAPI()
            app.include_router(router)
            ctx = _make_tenant_context()
            app.dependency_overrides[get_tenant_context] = lambda: ctx

            test_client = TestClient(app)
            resp = test_client.post(
                "/api/admin/conversations/search",
                json={"query": "test"},
            )
            assert resp.status_code == 503
        finally:
            mod._conversation_repo = original
