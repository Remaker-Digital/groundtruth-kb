"""SPEC-1775 coverage for the Zendesk full helpdesk adapter."""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qs, urlparse

import pytest

from src.integrations.action_executor import ActionExecutor, ActionType, AIAction
from src.integrations.manifest import AuthType, Capability, SyncStrategy
from src.integrations.models import TicketStatus
from src.integrations.registry import IntegrationRegistry
from src.integrations.zendesk.adapter import (
    REVERSE_STATUS_MAP,
    STATUS_MAP,
    ZendeskAdapter,
)
from src.integrations.zendesk.manifest import ZENDESK_MANIFEST


@dataclass
class MockResponse:
    status_code: int = 200
    payload: dict[str, Any] | None = None
    headers: dict[str, str] | None = None

    def json(self) -> dict[str, Any]:
        return self.payload or {}


@dataclass(frozen=True)
class RecordedCall:
    method: str
    url: str
    headers: dict[str, str]
    json: dict[str, Any] | None


class RecordingHTTP:
    def __init__(self, responses: list[MockResponse]) -> None:
        self._responses = responses
        self._index = 0
        self.calls: list[RecordedCall] = []

    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
    ) -> MockResponse:
        self.calls.append(RecordedCall(method, url, headers or {}, json))
        if self._index >= len(self._responses):
            return MockResponse()
        response = self._responses[self._index]
        self._index += 1
        return response


def _adapter(http: RecordingHTTP) -> ZendeskAdapter:
    return ZendeskAdapter(
        "tenant-1",
        subdomain="example",
        access_token="test-token",
        http_client=http,
    )


def _path(call: RecordedCall) -> str:
    return urlparse(call.url).path


def _query(call: RecordedCall) -> dict[str, list[str]]:
    return parse_qs(urlparse(call.url).query)


def test_spec1775_manifest_declares_full_helpdesk_surface() -> None:
    assert ZENDESK_MANIFEST.integration_id == "zendesk"
    assert ZENDESK_MANIFEST.auth_type == AuthType.OAUTH2
    assert set(ZENDESK_MANIFEST.auth_config.scopes) >= {
        "read",
        "write",
        "tickets:read",
        "tickets:write",
    }
    assert ZENDESK_MANIFEST.sync_strategy == SyncStrategy.HYBRID
    assert ZENDESK_MANIFEST.rate_limit_rpm == 700
    assert ZENDESK_MANIFEST.webhook_signature_header == ("x-zendesk-webhook-signature")
    assert ZENDESK_MANIFEST.webhook_signature_algo == "hmac-sha256"
    assert {
        Capability.SOURCE_TICKETS,
        Capability.SOURCE_ARTICLES,
        Capability.SOURCE_CONTACTS,
        Capability.DEST_REPLY,
        Capability.DEST_DRAFT,
        Capability.DEST_NOTE,
        Capability.DEST_STATUS,
        Capability.DEST_TAG,
        Capability.DEST_ASSIGN,
        Capability.DEST_CREATE,
        Capability.ACTION_CUSTOMER_LOOKUP,
        Capability.WEBHOOK_RECEIVE,
    } <= ZENDESK_MANIFEST.capabilities


def test_spec1775_status_mapping_round_trips_supported_statuses() -> None:
    assert STATUS_MAP == {
        "new": TicketStatus.OPEN,
        "open": TicketStatus.OPEN,
        "pending": TicketStatus.PENDING,
        "hold": TicketStatus.WAITING_ON_AGENT,
        "solved": TicketStatus.RESOLVED,
        "closed": TicketStatus.CLOSED,
    }
    assert {
        TicketStatus.OPEN.value: "open",
        TicketStatus.PENDING.value: "pending",
        TicketStatus.WAITING_ON_AGENT.value: "hold",
        TicketStatus.RESOLVED.value: "solved",
        TicketStatus.CLOSED.value: "closed",
    } == REVERSE_STATUS_MAP


@pytest.mark.asyncio
async def test_spec1775_uses_rest_v2_cursor_ticket_pagination() -> None:
    http = RecordingHTTP(
        [
            MockResponse(
                payload={
                    "tickets": [{"id": 101, "status": "open", "subject": "Help"}],
                    "meta": {"has_more": True, "after_cursor": "cursor-next"},
                }
            )
        ]
    )
    tickets, cursor = await _adapter(http).list_tickets(
        "tenant-1",
        cursor="cursor-start",
        limit=500,
        status="open",
    )

    assert tickets[0].external_id == "101"
    assert cursor == "cursor-next"
    assert _path(http.calls[0]) == "/api/v2/tickets.json"
    assert _query(http.calls[0]) == {
        "page[size]": ["100"],
        "page[after]": ["cursor-start"],
        "filter[status]": ["open"],
    }


@pytest.mark.asyncio
async def test_spec1775_uses_guide_article_endpoints() -> None:
    http = RecordingHTTP(
        [
            MockResponse(
                payload={
                    "articles": [
                        {
                            "id": 501,
                            "title": "Returns",
                            "body": "Return policy",
                            "updated_at": "2026-01-01T00:00:00Z",
                        }
                    ],
                    "next_page": "https://example.zendesk.com/page/3",
                }
            ),
            MockResponse(
                payload={
                    "article": {
                        "id": 502,
                        "title": "Shipping",
                        "body": "Shipping policy",
                    }
                }
            ),
        ]
    )
    adapter = _adapter(http)

    articles, cursor = await adapter.list_articles(
        "tenant-1",
        category="200",
        cursor="2",
        limit=500,
    )
    article = await adapter.get_article("tenant-1", "502")

    assert articles[0].external_id == "501"
    assert cursor == "3"
    assert article is not None
    assert article.external_id == "502"
    assert _path(http.calls[0]) == "/api/v2/help_center/sections/200/articles.json"
    assert _query(http.calls[0]) == {"per_page": ["100"], "page": ["2"]}
    assert _path(http.calls[1]) == "/api/v2/help_center/articles/502.json"


@pytest.mark.asyncio
async def test_spec1775_customer_lookup_accepts_executor_signature() -> None:
    http = RecordingHTTP(
        [
            MockResponse(
                payload={
                    "users": [
                        {
                            "id": 9001,
                            "email": "jane@example.com",
                            "name": "Jane Customer",
                            "phone": "+15551234567",
                            "organization": {"name": "Acme"},
                        }
                    ]
                }
            )
        ]
    )

    contact = await _adapter(http).lookup_customer(
        "tenant-1",
        email="jane@example.com",
        customer_id="ignored-by-zendesk",
    )

    assert contact is not None
    assert contact.external_id == "9001"
    assert contact.email == "jane@example.com"
    assert contact.company == "Acme"
    assert _path(http.calls[0]) == "/api/v2/users/search.json"
    assert _query(http.calls[0]) == {"query": ["jane@example.com"]}


@pytest.mark.asyncio
async def test_spec1775_webhook_signature_uses_hmac_sha256_header() -> None:
    body = b'{"type":"ticket.updated","ticket_id":"101"}'
    secret = "webhook-secret"
    signature = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    headers = {ZENDESK_MANIFEST.webhook_signature_header: signature}

    assert await ZendeskAdapter("tenant-1").verify_webhook(headers, body, secret) is True


@pytest.mark.asyncio
async def test_spec1775_action_executor_routes_zendesk_destinations() -> None:
    http = RecordingHTTP(
        [
            MockResponse(payload={"audit": {"events": [{"type": "Comment", "id": 1}]}}),
            MockResponse(payload={"audit": {"events": [{"type": "Comment", "id": 2}]}}),
            MockResponse(payload={"audit": {"events": [{"type": "Comment", "id": 3}]}}),
            MockResponse(payload={"ticket": {"id": "101", "status": "solved"}}),
            MockResponse(),
            MockResponse(payload={"ticket": {"id": "101", "status": "open"}}),
            MockResponse(payload={"ticket": {"id": "101", "status": "open"}}),
            MockResponse(payload={"ticket": {"id": "202", "status": "new"}}),
            MockResponse(payload={"results": [{"id": "301", "title": "Refunds"}]}),
            MockResponse(
                payload={
                    "users": [
                        {
                            "id": "401",
                            "email": "jane@example.com",
                            "name": "Jane Customer",
                        }
                    ]
                }
            ),
        ]
    )
    adapter = _adapter(http)
    executor = ActionExecutor(IntegrationRegistry())

    async def dispatch(action_type: ActionType, params: dict[str, Any]) -> dict[str, Any]:
        return await executor._dispatch(
            adapter,
            AIAction(
                tenant_id="tenant-1",
                integration_id="zendesk",
                action_type=action_type,
                params=params,
            ),
        )

    await dispatch(
        ActionType.REPLY_SEND,
        {"ticket_id": "101", "body": "Public reply", "html_body": "<p>Reply</p>"},
    )
    await dispatch(ActionType.REPLY_DRAFT, {"ticket_id": "101", "body": "Draft"})
    await dispatch(ActionType.NOTE_ADD, {"ticket_id": "101", "body": "Internal"})
    await dispatch(
        ActionType.STATUS_UPDATE,
        {"ticket_id": "101", "status": TicketStatus.RESOLVED.value},
    )
    await dispatch(ActionType.TAG_ADD, {"ticket_id": "101", "tags": ["vip"]})
    await dispatch(
        ActionType.TICKET_ASSIGN,
        {"ticket_id": "101", "assignee_id": "123"},
    )
    await dispatch(
        ActionType.TICKET_CREATE,
        {
            "subject": "New issue",
            "body": "Please help",
            "requester_email": "jane@example.com",
            "priority": "high",
            "tags": ["new"],
        },
    )
    await dispatch(ActionType.ARTICLE_SEARCH, {"query": "refunds"})
    customer = await dispatch(
        ActionType.CUSTOMER_LOOKUP,
        {"email": "jane@example.com"},
    )

    assert customer["email"] == "jane@example.com"
    assert [_path(call) for call in http.calls] == [
        "/api/v2/tickets/101.json",
        "/api/v2/tickets/101.json",
        "/api/v2/tickets/101.json",
        "/api/v2/tickets/101.json",
        "/api/v2/tickets/101/tags.json",
        "/api/v2/tickets/101.json",
        "/api/v2/tickets/101.json",
        "/api/v2/tickets.json",
        "/api/v2/help_center/articles/search.json",
        "/api/v2/users/search.json",
    ]
    assert http.calls[0].json == {
        "ticket": {
            "comment": {
                "body": "Public reply",
                "public": True,
                "html_body": "<p>Reply</p>",
            }
        }
    }
    assert http.calls[1].json == {"ticket": {"comment": {"body": "Draft", "public": False}}}
    assert http.calls[2].json == {"ticket": {"comment": {"body": "Internal", "public": False}}}
    assert http.calls[3].json == {"ticket": {"status": "solved"}}
    assert http.calls[4].json == {"tags": ["vip"]}
    assert http.calls[6].json == {"ticket": {"assignee_id": 123}}
    assert http.calls[7].json == {
        "ticket": {
            "subject": "New issue",
            "comment": {"body": "Please help"},
            "priority": "high",
            "requester": {"email": "jane@example.com"},
            "tags": ["new"],
        }
    }
    assert _query(http.calls[8]) == {"query": ["refunds"], "per_page": ["25"]}
    assert _query(http.calls[9]) == {"query": ["jane@example.com"]}
