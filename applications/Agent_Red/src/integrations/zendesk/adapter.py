# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Zendesk Helpdesk Adapter (SPEC-1775).

Full HelpdeskAdapter + KnowledgeAdapter implementation for Zendesk.
Auth: OAuth2.  API: REST v2, cursor pagination, 700 req/min.

Status mapping (Zendesk → normalized):
  new, open       → OPEN
  pending         → PENDING
  hold            → WAITING_ON_AGENT
  solved          → RESOLVED
  closed          → CLOSED

Webhook events: ticket.created, ticket.updated
Signature: HMAC-SHA256 via x-zendesk-webhook-signature

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
from datetime import datetime
from typing import Any
from urllib.parse import urlencode

from src.integrations.models import (
    AuthenticationError,
    IntegrationError,
    MessageDirection,
    NormalizedArticle,
    NormalizedContact,
    NormalizedMessage,
    NormalizedTicket,
    RateLimitError,
    TicketPriority,
    TicketStatus,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

INTEGRATION_ID = "zendesk"

# Zendesk status → normalized status
STATUS_MAP: dict[str, TicketStatus] = {
    "new": TicketStatus.OPEN,
    "open": TicketStatus.OPEN,
    "pending": TicketStatus.PENDING,
    "hold": TicketStatus.WAITING_ON_AGENT,
    "solved": TicketStatus.RESOLVED,
    "closed": TicketStatus.CLOSED,
}

# Normalized status → Zendesk status (for writes)
REVERSE_STATUS_MAP: dict[str, str] = {
    TicketStatus.OPEN.value: "open",
    TicketStatus.PENDING.value: "pending",
    TicketStatus.WAITING_ON_AGENT.value: "hold",
    TicketStatus.RESOLVED.value: "solved",
    TicketStatus.CLOSED.value: "closed",
}

PRIORITY_MAP: dict[str, TicketPriority] = {
    "low": TicketPriority.LOW,
    "normal": TicketPriority.NORMAL,
    "high": TicketPriority.HIGH,
    "urgent": TicketPriority.URGENT,
}


# ---------------------------------------------------------------------------
# Adapter
# ---------------------------------------------------------------------------


class ZendeskAdapter:
    """Full helpdesk + knowledge adapter for Zendesk (SPEC-1775).

    All external API calls go through ``_request()`` which handles auth
    headers, error mapping, and rate limit detection.  In production this
    would use httpx; for testability the HTTP layer is injectable.
    """

    def __init__(
        self,
        tenant_id: str,
        *,
        subdomain: str = "",
        access_token: str = "",
        http_client: Any = None,
    ) -> None:
        self.tenant_id = tenant_id
        self.subdomain = subdomain
        self.access_token = access_token
        self._http = http_client  # injectable for testing
        self._base_url = f"https://{subdomain}.zendesk.com" if subdomain else ""

    # -- HTTP layer ---------------------------------------------------------

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Execute an authenticated Zendesk API request.

        Raises:
            AuthenticationError: on 401/403
            RateLimitError: on 429
            IntegrationError: on other failures
        """
        if not self._base_url or not self.access_token:
            raise AuthenticationError(
                "Zendesk not configured (missing subdomain or token)",
                integration_id=INTEGRATION_ID,
            )

        url = f"{self._base_url}/api/v2{path}"
        if params:
            url = f"{url}?{urlencode(params)}"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if self._http is not None:
            # Injected HTTP client (testing)
            response = await self._http.request(
                method, url, headers=headers, json=json_body
            )
        else:
            raise IntegrationError(
                "No HTTP client configured",
                integration_id=INTEGRATION_ID,
            )

        status = getattr(response, "status_code", getattr(response, "status", 0))

        if status == 401 or status == 403:
            raise AuthenticationError(
                f"Zendesk auth failed ({status})",
                integration_id=INTEGRATION_ID,
            )
        if status == 429:
            retry_after = float(
                getattr(response, "headers", {}).get("Retry-After", "60")
            )
            raise RateLimitError(
                "Zendesk rate limit exceeded",
                integration_id=INTEGRATION_ID,
                retry_after_seconds=retry_after,
            )
        if status >= 400:
            raise IntegrationError(
                f"Zendesk API error ({status}): {path}",
                integration_id=INTEGRATION_ID,
                status_code=status,
                retryable=status >= 500,
            )

        return getattr(response, "json", lambda: {})()

    # -- Normalization helpers -----------------------------------------------

    @staticmethod
    def _normalize_ticket(raw: dict[str, Any]) -> NormalizedTicket:
        """Convert a Zendesk ticket JSON to NormalizedTicket."""
        zd_status = raw.get("status", "new")
        zd_priority = raw.get("priority", "normal")

        requester = None
        if raw.get("requester"):
            req = raw["requester"]
            requester = NormalizedContact(
                external_id=str(req.get("id", "")),
                source=INTEGRATION_ID,
                email=req.get("email", ""),
                name=req.get("name", ""),
            )

        return NormalizedTicket(
            external_id=str(raw.get("id", "")),
            source=INTEGRATION_ID,
            subject=raw.get("subject", ""),
            status=STATUS_MAP.get(zd_status, TicketStatus.OPEN),
            priority=PRIORITY_MAP.get(zd_priority, TicketPriority.NORMAL),
            requester=requester,
            tags=raw.get("tags", []),
            custom_fields={
                cf["id"]: cf["value"]
                for cf in raw.get("custom_fields", [])
                if cf.get("value") is not None
            },
            created_at=_parse_dt(raw.get("created_at")),
            updated_at=_parse_dt(raw.get("updated_at")),
            raw=raw,
        )

    @staticmethod
    def _normalize_article(raw: dict[str, Any]) -> NormalizedArticle:
        """Convert a Zendesk Guide article to NormalizedArticle."""
        return NormalizedArticle(
            external_id=str(raw.get("id", "")),
            source=INTEGRATION_ID,
            title=raw.get("title", ""),
            body_text=raw.get("body", ""),
            body_html=raw.get("body", ""),
            url=raw.get("html_url", ""),
            category=str(raw.get("section_id", "")),
            labels=raw.get("label_names", []),
            last_modified=_parse_dt(raw.get("updated_at")),
        )

    @staticmethod
    def _normalize_comment(raw: dict[str, Any]) -> NormalizedMessage:
        """Convert a Zendesk ticket comment to NormalizedMessage."""
        is_public = raw.get("public", True)
        author_id = str(raw.get("author_id", ""))

        direction = MessageDirection.INTERNAL if not is_public else MessageDirection.INBOUND

        return NormalizedMessage(
            external_id=str(raw.get("id", "")),
            source=INTEGRATION_ID,
            direction=direction,
            body_text=raw.get("plain_body", raw.get("body", "")),
            body_html=raw.get("html_body", ""),
            sender=NormalizedContact(
                external_id=author_id,
                source=INTEGRATION_ID,
            ),
            timestamp=_parse_dt(raw.get("created_at")),
        )

    # -- HelpdeskAdapter protocol -------------------------------------------

    async def list_tickets(
        self,
        tenant_id: str,
        *,
        cursor: str | None = None,
        limit: int = 100,
        status: str | None = None,
    ) -> tuple[list[NormalizedTicket], str | None]:
        """List tickets with cursor pagination."""
        params: dict[str, str] = {"page[size]": str(min(limit, 100))}
        if cursor:
            params["page[after]"] = cursor
        if status:
            params["filter[status]"] = status

        data = await self._request("GET", "/tickets.json", params=params)
        tickets = [self._normalize_ticket(t) for t in data.get("tickets", [])]
        next_cursor = (
            data.get("meta", {}).get("after_cursor")
            if data.get("meta", {}).get("has_more")
            else None
        )
        return tickets, next_cursor

    async def get_ticket(
        self, tenant_id: str, ticket_id: str
    ) -> NormalizedTicket | None:
        """Get a single ticket by external ID."""
        try:
            data = await self._request("GET", f"/tickets/{ticket_id}.json")
            return self._normalize_ticket(data.get("ticket", {}))
        except IntegrationError as e:
            if e.status_code == 404:
                return None
            raise

    async def add_reply(
        self,
        tenant_id: str,
        ticket_id: str,
        body: str,
        *,
        html_body: str | None = None,
        internal: bool = False,
    ) -> NormalizedMessage:
        """Add a public or internal reply to a ticket."""
        comment: dict[str, Any] = {
            "body": body,
            "public": not internal,
        }
        if html_body:
            comment["html_body"] = html_body

        data = await self._request(
            "PUT",
            f"/tickets/{ticket_id}.json",
            json_body={"ticket": {"comment": comment}},
        )
        # Zendesk returns the updated ticket; extract the latest comment
        audit = data.get("audit", {})
        events = audit.get("events", [])
        comment_event = next(
            (e for e in events if e.get("type") == "Comment"), {}
        )
        return NormalizedMessage(
            external_id=str(comment_event.get("id", "")),
            source=INTEGRATION_ID,
            direction=MessageDirection.OUTBOUND,
            body_text=body,
            body_html=html_body or "",
        )

    async def update_status(
        self, tenant_id: str, ticket_id: str, status: str
    ) -> NormalizedTicket:
        """Update a ticket's status."""
        zd_status = REVERSE_STATUS_MAP.get(status, status)
        data = await self._request(
            "PUT",
            f"/tickets/{ticket_id}.json",
            json_body={"ticket": {"status": zd_status}},
        )
        return self._normalize_ticket(data.get("ticket", {}))

    async def add_tags(
        self, tenant_id: str, ticket_id: str, tags: list[str]
    ) -> NormalizedTicket:
        """Add tags to a ticket (non-destructive merge)."""
        await self._request(
            "PUT",
            f"/tickets/{ticket_id}/tags.json",
            json_body={"tags": tags},
        )
        # Refetch to get normalized view
        return await self.get_ticket(tenant_id, ticket_id) or NormalizedTicket(
            external_id=ticket_id, source=INTEGRATION_ID
        )

    async def assign_ticket(
        self, tenant_id: str, ticket_id: str, assignee_id: str
    ) -> NormalizedTicket:
        """Assign a ticket to an agent."""
        data = await self._request(
            "PUT",
            f"/tickets/{ticket_id}.json",
            json_body={"ticket": {"assignee_id": int(assignee_id)}},
        )
        return self._normalize_ticket(data.get("ticket", {}))

    async def create_ticket(
        self,
        tenant_id: str,
        subject: str,
        body: str,
        *,
        requester_email: str | None = None,
        priority: str = "normal",
        tags: list[str] | None = None,
    ) -> NormalizedTicket:
        """Create a new ticket."""
        ticket: dict[str, Any] = {
            "subject": subject,
            "comment": {"body": body},
            "priority": priority,
        }
        if requester_email:
            ticket["requester"] = {"email": requester_email}
        if tags:
            ticket["tags"] = tags

        data = await self._request(
            "POST",
            "/tickets.json",
            json_body={"ticket": ticket},
        )
        return self._normalize_ticket(data.get("ticket", {}))

    async def search_tickets(
        self, tenant_id: str, query: str, *, limit: int = 25
    ) -> list[NormalizedTicket]:
        """Search tickets by query string."""
        params = {
            "query": f"type:ticket {query}",
            "per_page": str(min(limit, 100)),
        }
        data = await self._request("GET", "/search.json", params=params)
        return [self._normalize_ticket(r) for r in data.get("results", [])]

    async def register_webhook(
        self, tenant_id: str, target_url: str, events: list[str]
    ) -> dict[str, Any]:
        """Register a webhook for ticket events."""
        data = await self._request(
            "POST",
            "/webhooks",
            json_body={
                "webhook": {
                    "name": f"agent-red-{tenant_id}",
                    "endpoint": target_url,
                    "http_method": "POST",
                    "request_format": "json",
                    "status": "active",
                    "subscriptions": [
                        {"type": event} for event in events
                    ],
                }
            },
        )
        return data.get("webhook", {})

    async def verify_webhook(
        self, headers: dict[str, str], body: bytes, secret: str
    ) -> bool:
        """Verify Zendesk webhook HMAC-SHA256 signature."""
        signature = headers.get("x-zendesk-webhook-signature", "")
        if not signature:
            return False
        expected = hmac.new(
            secret.encode(), body, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected)

    async def health_check(self, tenant_id: str) -> bool:
        """Check connectivity by hitting /api/v2/account.json."""
        try:
            await self._request("GET", "/account.json")
            return True
        except Exception:
            return False

    # -- KnowledgeAdapter protocol ------------------------------------------

    async def list_articles(
        self,
        tenant_id: str,
        *,
        cursor: str | None = None,
        limit: int = 100,
        category: str | None = None,
    ) -> tuple[list[NormalizedArticle], str | None]:
        """List Guide help center articles with pagination."""
        path = "/help_center/articles.json"
        if category:
            path = f"/help_center/sections/{category}/articles.json"

        params: dict[str, str] = {"per_page": str(min(limit, 100))}
        if cursor:
            params["page"] = cursor

        data = await self._request("GET", path, params=params)
        articles = [self._normalize_article(a) for a in data.get("articles", [])]
        next_page = data.get("next_page")
        next_cursor = str(int(cursor or "1") + 1) if next_page else None
        return articles, next_cursor

    async def get_article(
        self, tenant_id: str, article_id: str
    ) -> NormalizedArticle | None:
        """Get a single article by ID."""
        try:
            data = await self._request(
                "GET", f"/help_center/articles/{article_id}.json"
            )
            return self._normalize_article(data.get("article", {}))
        except IntegrationError as e:
            if e.status_code == 404:
                return None
            raise

    async def search_articles(
        self, tenant_id: str, query: str, *, limit: int = 25
    ) -> list[NormalizedArticle]:
        """Search Guide articles by query string."""
        params = {"query": query, "per_page": str(min(limit, 100))}
        data = await self._request(
            "GET", "/help_center/articles/search.json", params=params
        )
        return [self._normalize_article(r) for r in data.get("results", [])]

    # -- Customer lookup (EcommerceAdapter-style) ----------------------------

    async def lookup_customer(
        self, tenant_id: str, *, email: str | None = None
    ) -> NormalizedContact | None:
        """Look up a Zendesk user by email."""
        if not email:
            return None
        params = {"query": email}
        data = await self._request("GET", "/users/search.json", params=params)
        users = data.get("users", [])
        if not users:
            return None
        u = users[0]
        return NormalizedContact(
            external_id=str(u.get("id", "")),
            source=INTEGRATION_ID,
            email=u.get("email", ""),
            name=u.get("name", ""),
            phone=u.get("phone", ""),
            company=u.get("organization", {}).get("name", "") if u.get("organization") else "",
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_dt(value: str | None) -> datetime | None:
    """Parse an ISO 8601 datetime string, returning None on failure."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None
