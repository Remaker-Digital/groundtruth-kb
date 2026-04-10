# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Slack Channel Adapter (SPEC-1776).

ChannelAdapter implementation for Slack.  Bot behavior: @mention trigger,
threaded responses, source citations, escalation, Block Kit formatting.

Auth: OAuth2 with bot token.
Webhooks: Events API with HMAC-SHA256 x-slack-signature + timestamp.
Rate limits: Tier 3 ≈ 50 req/min.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import time
from typing import Any

from src.integrations.models import (
    AuthenticationError,
    IntegrationError,
    MessageChannel,
    MessageDirection,
    NormalizedContact,
    NormalizedMessage,
    RateLimitError,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

INTEGRATION_ID = "slack"
SLACK_API_BASE = "https://slack.com/api"
TIMESTAMP_TOLERANCE = 300  # 5 minutes


# ---------------------------------------------------------------------------
# Block Kit helpers
# ---------------------------------------------------------------------------


def build_text_block(text: str) -> dict[str, Any]:
    """Build a simple mrkdwn text block."""
    return {
        "type": "section",
        "text": {"type": "mrkdwn", "text": text},
    }


def build_citation_block(sources: list[dict[str, str]]) -> dict[str, Any]:
    """Build a context block with source citations."""
    elements = []
    for src in sources[:10]:  # Slack limit: 10 context elements
        label = src.get("title", src.get("url", "Source"))
        url = src.get("url", "")
        text = f"<{url}|{label}>" if url else label
        elements.append({"type": "mrkdwn", "text": text})
    return {"type": "context", "elements": elements}


def build_escalation_block(ticket_url: str = "") -> dict[str, Any]:
    """Build an actions block with escalation button."""
    button: dict[str, Any] = {
        "type": "button",
        "text": {"type": "plain_text", "text": "Escalate to Agent"},
        "style": "danger",
        "action_id": "escalate_to_agent",
    }
    if ticket_url:
        button["url"] = ticket_url
    return {"type": "actions", "elements": [button]}


# ---------------------------------------------------------------------------
# Adapter
# ---------------------------------------------------------------------------


class SlackAdapter:
    """Channel adapter for Slack (SPEC-1776).

    Implements ChannelAdapter protocol.  All Slack Web API calls go
    through ``_api_call()`` which handles auth, rate limits, and errors.
    """

    def __init__(
        self,
        tenant_id: str,
        *,
        bot_token: str = "",
        signing_secret: str = "",
        http_client: Any = None,
    ) -> None:
        self.tenant_id = tenant_id
        self.bot_token = bot_token
        self.signing_secret = signing_secret
        self._http = http_client

    # -- HTTP layer ---------------------------------------------------------

    async def _api_call(
        self,
        method: str,
        *,
        json_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Call a Slack Web API method.

        Raises:
            AuthenticationError: on invalid_auth / token_revoked
            RateLimitError: on rate limit
            IntegrationError: on other failures
        """
        if not self.bot_token:
            raise AuthenticationError(
                "Slack bot token not configured",
                integration_id=INTEGRATION_ID,
            )

        url = f"{SLACK_API_BASE}/{method}"
        headers = {
            "Authorization": f"Bearer {self.bot_token}",
            "Content-Type": "application/json; charset=utf-8",
        }

        if self._http is not None:
            response = await self._http.request(
                "POST", url, headers=headers, json=json_body or {}
            )
        else:
            raise IntegrationError(
                "No HTTP client configured",
                integration_id=INTEGRATION_ID,
            )

        data = getattr(response, "json", lambda: {})()

        if not data.get("ok", False):
            error = data.get("error", "unknown_error")
            if error in ("invalid_auth", "token_revoked", "not_authed"):
                raise AuthenticationError(
                    f"Slack auth failed: {error}",
                    integration_id=INTEGRATION_ID,
                )
            if error == "ratelimited":
                retry_after = float(
                    getattr(response, "headers", {}).get("Retry-After", "30")
                )
                raise RateLimitError(
                    "Slack rate limit exceeded",
                    integration_id=INTEGRATION_ID,
                    retry_after_seconds=retry_after,
                )
            raise IntegrationError(
                f"Slack API error: {error} ({method})",
                integration_id=INTEGRATION_ID,
            )

        return data

    # -- ChannelAdapter protocol --------------------------------------------

    async def send_message(
        self,
        tenant_id: str,
        channel_id: str,
        body: str,
        *,
        thread_id: str | None = None,
        blocks: list[dict[str, Any]] | None = None,
    ) -> NormalizedMessage:
        """Send a message to a Slack channel or thread."""
        payload: dict[str, Any] = {
            "channel": channel_id,
            "text": body,  # Fallback for notifications
        }
        if thread_id:
            payload["thread_ts"] = thread_id
        if blocks:
            payload["blocks"] = blocks
        else:
            payload["blocks"] = [build_text_block(body)]

        data = await self._api_call("chat.postMessage", json_body=payload)

        return NormalizedMessage(
            external_id=data.get("ts", ""),
            source=INTEGRATION_ID,
            direction=MessageDirection.OUTBOUND,
            channel=MessageChannel.SLACK,
            body_text=body,
            metadata={
                "channel": data.get("channel", channel_id),
                "thread_ts": thread_id or "",
            },
        )

    async def receive_messages(
        self,
        tenant_id: str,
        channel_id: str,
        *,
        cursor: str | None = None,
        limit: int = 100,
    ) -> tuple[list[NormalizedMessage], str | None]:
        """Fetch recent messages from a channel via conversations.history."""
        payload: dict[str, Any] = {
            "channel": channel_id,
            "limit": min(limit, 200),
        }
        if cursor:
            payload["cursor"] = cursor

        data = await self._api_call("conversations.history", json_body=payload)

        messages = []
        for msg in data.get("messages", []):
            messages.append(
                NormalizedMessage(
                    external_id=msg.get("ts", ""),
                    source=INTEGRATION_ID,
                    direction=MessageDirection.INBOUND,
                    channel=MessageChannel.SLACK,
                    body_text=msg.get("text", ""),
                    sender=NormalizedContact(
                        external_id=msg.get("user", ""),
                        source=INTEGRATION_ID,
                    ),
                    metadata={"channel": channel_id},
                )
            )

        next_cursor = (
            data.get("response_metadata", {}).get("next_cursor")
            if data.get("has_more")
            else None
        )
        return messages, next_cursor

    async def register_webhook(
        self, tenant_id: str, target_url: str, events: list[str]
    ) -> dict[str, Any]:
        """Register an Events API subscription.

        Note: Slack Events API subscriptions are configured in the Slack app
        dashboard, not via API.  This returns configuration guidance.
        """
        return {
            "integration_id": INTEGRATION_ID,
            "note": "Configure Events API in Slack app dashboard",
            "target_url": target_url,
            "events": events,
            "required_scopes": [
                "app_mentions:read",
                "channels:history",
            ],
        }

    async def verify_webhook(
        self, headers: dict[str, str], body: bytes, secret: str
    ) -> bool:
        """Verify Slack Events API request signature.

        Validates x-slack-signature with timestamp replay protection.
        """
        timestamp_str = headers.get("x-slack-request-timestamp", "")
        signature = headers.get("x-slack-signature", "")

        if not timestamp_str or not signature:
            return False

        try:
            timestamp = int(timestamp_str)
        except ValueError:
            return False

        # Replay protection
        if abs(time.time() - timestamp) > TIMESTAMP_TOLERANCE:
            return False

        sig_basestring = f"v0:{timestamp}:{body.decode('utf-8')}"
        expected = (
            "v0="
            + hmac.new(
                secret.encode(), sig_basestring.encode(), hashlib.sha256
            ).hexdigest()
        )
        return hmac.compare_digest(signature, expected)

    async def format_message(
        self, text: str, *, rich: bool = False
    ) -> dict[str, Any]:
        """Format a message for Slack (Block Kit when rich=True)."""
        if rich:
            return {
                "text": text,
                "blocks": [build_text_block(text)],
            }
        return {"text": text}

    async def health_check(self, tenant_id: str) -> bool:
        """Check connectivity via auth.test."""
        try:
            await self._api_call("auth.test")
            return True
        except Exception:
            return False

    # -- Convenience methods ------------------------------------------------

    async def send_threaded_reply(
        self,
        channel_id: str,
        thread_ts: str,
        body: str,
        *,
        sources: list[dict[str, str]] | None = None,
        offer_escalation: bool = False,
    ) -> NormalizedMessage:
        """Send a threaded reply with optional citations and escalation."""
        blocks: list[dict[str, Any]] = [build_text_block(body)]
        if sources:
            blocks.append(build_citation_block(sources))
        if offer_escalation:
            blocks.append(build_escalation_block())

        return await self.send_message(
            self.tenant_id,
            channel_id,
            body,
            thread_id=thread_ts,
            blocks=blocks,
        )

    async def get_user_info(self, user_id: str) -> NormalizedContact | None:
        """Look up a Slack user by ID."""
        try:
            data = await self._api_call(
                "users.info", json_body={"user": user_id}
            )
            user = data.get("user", {})
            profile = user.get("profile", {})
            return NormalizedContact(
                external_id=user.get("id", user_id),
                source=INTEGRATION_ID,
                email=profile.get("email", ""),
                name=profile.get("real_name", user.get("name", "")),
            )
        except IntegrationError:
            return None
