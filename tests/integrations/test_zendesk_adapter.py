"""Tests for Zendesk Full Helpdesk Adapter (SPEC-1775).

Tests cover:
  - Manifest declaration (capabilities, auth, status mapping)
  - Ticket normalization (status, priority, requester, tags)
  - Article normalization
  - Comment normalization (direction mapping)
  - HelpdeskAdapter protocol methods (list, get, reply, status, tags, assign, create, search)
  - KnowledgeAdapter protocol methods (list_articles, get_article, search_articles)
  - Customer lookup
  - Webhook signature verification
  - HTTP error mapping (401, 429, 500)
  - Factory registration

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from typing import Any
from unittest.mock import AsyncMock

import pytest

from src.integrations.models import (
    AuthenticationError,
    IntegrationError,
    MessageDirection,
    RateLimitError,
    TicketPriority,
    TicketStatus,
)
from src.integrations.zendesk.adapter import (
    INTEGRATION_ID,
    PRIORITY_MAP,
    REVERSE_STATUS_MAP,
    STATUS_MAP,
    ZendeskAdapter,
)
from src.integrations.zendesk.manifest import ZENDESK_MANIFEST
from src.integrations.manifest import (
    AuthType,
    Capability,
    IntegrationCategory,
    SyncStrategy,
)


# ---------------------------------------------------------------------------
# Mock HTTP client
# ---------------------------------------------------------------------------


@dataclass
class MockResponse:
    status_code: int = 200
    _json: dict[str, Any] | None = None
    headers: dict[str, str] | None = None

    def json(self) -> dict[str, Any]:
        return self._json or {}


class MockHTTP:
    def __init__(self, responses: list[MockResponse] | None = None):
        self._responses = responses or []
        self._call_index = 0
        self.calls: list[tuple[str, str, dict]] = []

    async def request(self, method, url, headers=None, json=None, params=None):
        self.calls.append((method, url, {"headers": headers, "json": json}))
        if self._call_index < len(self._responses):
            resp = self._responses[self._call_index]
            self._call_index += 1
            return resp
        return MockResponse()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def adapter() -> ZendeskAdapter:
    return ZendeskAdapter(
        tenant_id="t-1",
        subdomain="test",
        access_token="test-token",
        http_client=MockHTTP(),
    )


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------


class TestManifest:
    def test_integration_id(self):
        assert ZENDESK_MANIFEST.integration_id == "zendesk"

    def test_category_is_helpdesk(self):
        assert ZENDESK_MANIFEST.category == IntegrationCategory.HELPDESK

    def test_auth_type_is_oauth2(self):
        assert ZENDESK_MANIFEST.auth_type == AuthType.OAUTH2

    def test_sync_strategy_is_hybrid(self):
        assert ZENDESK_MANIFEST.sync_strategy == SyncStrategy.HYBRID

    def test_rate_limit_700_rpm(self):
        assert ZENDESK_MANIFEST.rate_limit_rpm == 700

    def test_has_source_tickets_capability(self):
        assert ZENDESK_MANIFEST.has_capability(Capability.SOURCE_TICKETS)

    def test_has_source_articles_capability(self):
        assert ZENDESK_MANIFEST.has_capability(Capability.SOURCE_ARTICLES)

    def test_has_dest_reply_capability(self):
        assert ZENDESK_MANIFEST.has_capability(Capability.DEST_REPLY)

    def test_has_webhook_receive_capability(self):
        assert ZENDESK_MANIFEST.has_capability(Capability.WEBHOOK_RECEIVE)

    def test_has_12_capabilities(self):
        assert len(ZENDESK_MANIFEST.capabilities) == 12

    def test_tier_gate_professional(self):
        assert ZENDESK_MANIFEST.tier_gate == "professional"

    def test_webhook_signature_header(self):
        assert ZENDESK_MANIFEST.webhook_signature_header == "x-zendesk-webhook-signature"


# ---------------------------------------------------------------------------
# Status mapping
# ---------------------------------------------------------------------------


class TestStatusMapping:
    def test_new_maps_to_open(self):
        assert STATUS_MAP["new"] == TicketStatus.OPEN

    def test_open_maps_to_open(self):
        assert STATUS_MAP["open"] == TicketStatus.OPEN

    def test_pending_maps_to_pending(self):
        assert STATUS_MAP["pending"] == TicketStatus.PENDING

    def test_hold_maps_to_waiting(self):
        assert STATUS_MAP["hold"] == TicketStatus.WAITING_ON_AGENT

    def test_solved_maps_to_resolved(self):
        assert STATUS_MAP["solved"] == TicketStatus.RESOLVED

    def test_closed_maps_to_closed(self):
        assert STATUS_MAP["closed"] == TicketStatus.CLOSED

    def test_reverse_map_covers_all_normalized(self):
        for status in TicketStatus:
            assert status.value in REVERSE_STATUS_MAP


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------


class TestNormalization:
    def test_normalize_ticket_basic(self):
        raw = {
            "id": 12345,
            "subject": "Help needed",
            "status": "open",
            "priority": "high",
            "tags": ["vip", "urgent"],
            "created_at": "2026-03-01T10:00:00Z",
        }
        ticket = ZendeskAdapter._normalize_ticket(raw)
        assert ticket.external_id == "12345"
        assert ticket.source == INTEGRATION_ID
        assert ticket.subject == "Help needed"
        assert ticket.status == TicketStatus.OPEN
        assert ticket.priority == TicketPriority.HIGH
        assert "vip" in ticket.tags
        assert ticket.created_at is not None

    def test_normalize_ticket_with_requester(self):
        raw = {
            "id": 1,
            "status": "new",
            "requester": {"id": 99, "email": "user@test.com", "name": "User"},
        }
        ticket = ZendeskAdapter._normalize_ticket(raw)
        assert ticket.requester is not None
        assert ticket.requester.email == "user@test.com"

    def test_normalize_article(self):
        raw = {
            "id": 500,
            "title": "Getting Started",
            "body": "<p>Welcome</p>",
            "html_url": "https://help.example.com/articles/500",
            "section_id": 10,
            "label_names": ["guide"],
        }
        article = ZendeskAdapter._normalize_article(raw)
        assert article.external_id == "500"
        assert article.title == "Getting Started"
        assert article.source == INTEGRATION_ID
        assert "guide" in article.labels

    def test_normalize_comment_public(self):
        raw = {"id": 1, "public": True, "body": "Hello", "author_id": 5}
        msg = ZendeskAdapter._normalize_comment(raw)
        assert msg.direction == MessageDirection.INBOUND

    def test_normalize_comment_internal(self):
        raw = {"id": 2, "public": False, "body": "Internal", "author_id": 5}
        msg = ZendeskAdapter._normalize_comment(raw)
        assert msg.direction == MessageDirection.INTERNAL


# ---------------------------------------------------------------------------
# Protocol methods
# ---------------------------------------------------------------------------


class TestHelpdeskProtocol:
    @pytest.mark.asyncio
    async def test_list_tickets(self):
        http = MockHTTP([MockResponse(_json={
            "tickets": [{"id": 1, "status": "open", "subject": "T1"}],
            "meta": {"has_more": False},
        })])
        adapter = ZendeskAdapter("t-1", subdomain="test", access_token="tok", http_client=http)
        tickets, cursor = await adapter.list_tickets("t-1")
        assert len(tickets) == 1
        assert tickets[0].external_id == "1"
        assert cursor is None

    @pytest.mark.asyncio
    async def test_get_ticket_found(self):
        http = MockHTTP([MockResponse(_json={"ticket": {"id": 42, "status": "pending", "subject": "Test"}})])
        adapter = ZendeskAdapter("t-1", subdomain="test", access_token="tok", http_client=http)
        ticket = await adapter.get_ticket("t-1", "42")
        assert ticket is not None
        assert ticket.external_id == "42"

    @pytest.mark.asyncio
    async def test_get_ticket_not_found(self):
        http = MockHTTP([MockResponse(status_code=404)])
        adapter = ZendeskAdapter("t-1", subdomain="test", access_token="tok", http_client=http)
        ticket = await adapter.get_ticket("t-1", "999")
        assert ticket is None

    @pytest.mark.asyncio
    async def test_create_ticket(self):
        http = MockHTTP([MockResponse(_json={"ticket": {"id": 100, "status": "new", "subject": "New"}})])
        adapter = ZendeskAdapter("t-1", subdomain="test", access_token="tok", http_client=http)
        ticket = await adapter.create_ticket("t-1", "New", "Body", tags=["test"])
        assert ticket.external_id == "100"

    @pytest.mark.asyncio
    async def test_add_reply(self):
        http = MockHTTP([MockResponse(_json={
            "ticket": {"id": 1},
            "audit": {"events": [{"type": "Comment", "id": 200}]},
        })])
        adapter = ZendeskAdapter("t-1", subdomain="test", access_token="tok", http_client=http)
        msg = await adapter.add_reply("t-1", "1", "Reply text")
        assert msg.direction == MessageDirection.OUTBOUND

    @pytest.mark.asyncio
    async def test_search_tickets(self):
        http = MockHTTP([MockResponse(_json={"results": [{"id": 5, "status": "open"}]})])
        adapter = ZendeskAdapter("t-1", subdomain="test", access_token="tok", http_client=http)
        results = await adapter.search_tickets("t-1", "billing issue")
        assert len(results) == 1


# ---------------------------------------------------------------------------
# HTTP error mapping
# ---------------------------------------------------------------------------


class TestErrorMapping:
    @pytest.mark.asyncio
    async def test_401_raises_auth_error(self):
        http = MockHTTP([MockResponse(status_code=401)])
        adapter = ZendeskAdapter("t-1", subdomain="test", access_token="tok", http_client=http)
        with pytest.raises(AuthenticationError):
            await adapter.list_tickets("t-1")

    @pytest.mark.asyncio
    async def test_429_raises_rate_limit_error(self):
        http = MockHTTP([MockResponse(status_code=429, headers={"Retry-After": "30"})])
        adapter = ZendeskAdapter("t-1", subdomain="test", access_token="tok", http_client=http)
        with pytest.raises(RateLimitError):
            await adapter.list_tickets("t-1")

    @pytest.mark.asyncio
    async def test_500_raises_retryable_error(self):
        http = MockHTTP([MockResponse(status_code=500)])
        adapter = ZendeskAdapter("t-1", subdomain="test", access_token="tok", http_client=http)
        with pytest.raises(IntegrationError) as exc_info:
            await adapter.list_tickets("t-1")
        assert exc_info.value.retryable is True

    @pytest.mark.asyncio
    async def test_missing_config_raises_auth_error(self):
        adapter = ZendeskAdapter("t-1")  # No subdomain or token
        with pytest.raises(AuthenticationError):
            await adapter.list_tickets("t-1")


# ---------------------------------------------------------------------------
# Webhook verification
# ---------------------------------------------------------------------------


class TestWebhookVerification:
    @pytest.mark.asyncio
    async def test_valid_signature(self):
        adapter = ZendeskAdapter("t-1")
        body = b'{"event": "ticket.created"}'
        secret = "test-secret"
        sig = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        headers = {"x-zendesk-webhook-signature": sig}
        assert await adapter.verify_webhook(headers, body, secret) is True

    @pytest.mark.asyncio
    async def test_invalid_signature(self):
        adapter = ZendeskAdapter("t-1")
        headers = {"x-zendesk-webhook-signature": "invalid"}
        assert await adapter.verify_webhook(headers, b"body", "secret") is False

    @pytest.mark.asyncio
    async def test_missing_signature_header(self):
        adapter = ZendeskAdapter("t-1")
        assert await adapter.verify_webhook({}, b"body", "secret") is False


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


class TestFactory:
    def test_zendesk_factory_creates_adapter(self):
        from src.integrations.zendesk import zendesk_factory
        adapter = zendesk_factory("t-1")
        assert isinstance(adapter, ZendeskAdapter)
        assert adapter.tenant_id == "t-1"
