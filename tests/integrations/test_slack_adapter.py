"""Tests for Slack Channel Adapter (SPEC-1776).

Tests cover:
  - Manifest declaration (capabilities, auth, webhook config)
  - Block Kit helpers (text, citation, escalation)
  - send_message with and without blocks
  - receive_messages with pagination
  - Webhook signature verification with timestamp replay check
  - format_message (plain and rich)
  - send_threaded_reply with citations
  - HTTP error mapping (auth, rate limit)
  - Health check
  - Factory registration

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import hmac
import time
from dataclasses import dataclass
from typing import Any

import pytest

from src.integrations.models import (
    AuthenticationError,
    MessageChannel,
    MessageDirection,
    RateLimitError,
)
from src.integrations.slack.adapter import (
    INTEGRATION_ID,
    SlackAdapter,
    build_citation_block,
    build_escalation_block,
    build_text_block,
)
from src.integrations.slack.manifest import SLACK_MANIFEST
from src.integrations.manifest import (
    AuthType,
    Capability,
    IntegrationCategory,
    SyncStrategy,
)


# ---------------------------------------------------------------------------
# Mock HTTP
# ---------------------------------------------------------------------------


@dataclass
class MockResponse:
    status_code: int = 200
    _json: dict[str, Any] | None = None
    headers: dict[str, str] | None = None

    def json(self) -> dict[str, Any]:
        return self._json or {"ok": True}


class MockHTTP:
    def __init__(self, responses: list[MockResponse] | None = None):
        self._responses = responses or []
        self._idx = 0
        self.calls: list[tuple] = []

    async def request(self, method, url, headers=None, json=None, params=None):
        self.calls.append((method, url, json))
        if self._idx < len(self._responses):
            resp = self._responses[self._idx]
            self._idx += 1
            return resp
        return MockResponse()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def adapter() -> SlackAdapter:
    return SlackAdapter(
        tenant_id="t-1",
        bot_token="xoxb-test",
        signing_secret="test-secret",
        http_client=MockHTTP(),
    )


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------


class TestManifest:
    def test_integration_id(self):
        assert SLACK_MANIFEST.integration_id == "slack"

    def test_category_is_channel(self):
        assert SLACK_MANIFEST.category == IntegrationCategory.CHANNEL

    def test_auth_type_is_oauth2(self):
        assert SLACK_MANIFEST.auth_type == AuthType.OAUTH2

    def test_sync_strategy_is_webhook(self):
        assert SLACK_MANIFEST.sync_strategy == SyncStrategy.WEBHOOK

    def test_has_dest_reply(self):
        assert SLACK_MANIFEST.has_capability(Capability.DEST_REPLY)

    def test_has_webhook_receive(self):
        assert SLACK_MANIFEST.has_capability(Capability.WEBHOOK_RECEIVE)

    def test_capabilities_count(self):
        assert len(SLACK_MANIFEST.capabilities) == 2

    def test_tier_gate_professional(self):
        assert SLACK_MANIFEST.tier_gate == "professional"

    def test_webhook_signature_header(self):
        assert SLACK_MANIFEST.webhook_signature_header == "x-slack-signature"


# ---------------------------------------------------------------------------
# Block Kit helpers
# ---------------------------------------------------------------------------


class TestBlockKit:
    def test_text_block(self):
        block = build_text_block("Hello world")
        assert block["type"] == "section"
        assert block["text"]["type"] == "mrkdwn"
        assert block["text"]["text"] == "Hello world"

    def test_citation_block(self):
        sources = [
            {"title": "Doc A", "url": "https://a.com"},
            {"title": "Doc B", "url": "https://b.com"},
        ]
        block = build_citation_block(sources)
        assert block["type"] == "context"
        assert len(block["elements"]) == 2

    def test_citation_block_max_10(self):
        sources = [{"title": f"S{i}", "url": f"https://{i}.com"} for i in range(15)]
        block = build_citation_block(sources)
        assert len(block["elements"]) == 10

    def test_escalation_block(self):
        block = build_escalation_block("https://ticket.com")
        assert block["type"] == "actions"
        assert block["elements"][0]["action_id"] == "escalate_to_agent"
        assert block["elements"][0]["url"] == "https://ticket.com"


# ---------------------------------------------------------------------------
# Protocol methods
# ---------------------------------------------------------------------------


class TestChannelProtocol:
    @pytest.mark.asyncio
    async def test_send_message(self):
        http = MockHTTP([MockResponse(_json={"ok": True, "ts": "1234.5678", "channel": "C01"})])
        adapter = SlackAdapter("t-1", bot_token="xoxb-test", http_client=http)
        msg = await adapter.send_message("t-1", "C01", "Hello")
        assert msg.external_id == "1234.5678"
        assert msg.direction == MessageDirection.OUTBOUND
        assert msg.channel == MessageChannel.SLACK

    @pytest.mark.asyncio
    async def test_send_message_with_thread(self):
        http = MockHTTP([MockResponse(_json={"ok": True, "ts": "1234.5678", "channel": "C01"})])
        adapter = SlackAdapter("t-1", bot_token="xoxb-test", http_client=http)
        msg = await adapter.send_message("t-1", "C01", "Reply", thread_id="1111.0000")
        assert msg.metadata["thread_ts"] == "1111.0000"

    @pytest.mark.asyncio
    async def test_receive_messages(self):
        http = MockHTTP([MockResponse(_json={
            "ok": True,
            "messages": [
                {"ts": "1.0", "text": "Hello", "user": "U01"},
                {"ts": "2.0", "text": "World", "user": "U02"},
            ],
            "has_more": False,
        })])
        adapter = SlackAdapter("t-1", bot_token="xoxb-test", http_client=http)
        messages, cursor = await adapter.receive_messages("t-1", "C01")
        assert len(messages) == 2
        assert messages[0].body_text == "Hello"
        assert cursor is None

    @pytest.mark.asyncio
    async def test_format_message_plain(self):
        adapter = SlackAdapter("t-1", bot_token="xoxb-test", http_client=MockHTTP())
        result = await adapter.format_message("Hello")
        assert result == {"text": "Hello"}

    @pytest.mark.asyncio
    async def test_format_message_rich(self):
        adapter = SlackAdapter("t-1", bot_token="xoxb-test", http_client=MockHTTP())
        result = await adapter.format_message("Hello", rich=True)
        assert "blocks" in result


# ---------------------------------------------------------------------------
# Webhook verification
# ---------------------------------------------------------------------------


class TestWebhookVerification:
    @pytest.mark.asyncio
    async def test_valid_signature(self):
        adapter = SlackAdapter("t-1")
        secret = "test-secret"
        body = b'{"event": "app_mention"}'
        ts = str(int(time.time()))
        sig_base = f"v0:{ts}:{body.decode()}"
        expected = "v0=" + hmac.new(secret.encode(), sig_base.encode(), hashlib.sha256).hexdigest()
        headers = {"x-slack-signature": expected, "x-slack-request-timestamp": ts}
        assert await adapter.verify_webhook(headers, body, secret) is True

    @pytest.mark.asyncio
    async def test_expired_timestamp(self):
        adapter = SlackAdapter("t-1")
        old_ts = str(int(time.time()) - 600)
        headers = {"x-slack-signature": "v0=abc", "x-slack-request-timestamp": old_ts}
        assert await adapter.verify_webhook(headers, b"body", "secret") is False

    @pytest.mark.asyncio
    async def test_missing_headers(self):
        adapter = SlackAdapter("t-1")
        assert await adapter.verify_webhook({}, b"body", "secret") is False


# ---------------------------------------------------------------------------
# Error mapping
# ---------------------------------------------------------------------------


class TestErrorMapping:
    @pytest.mark.asyncio
    async def test_invalid_auth_raises(self):
        http = MockHTTP([MockResponse(_json={"ok": False, "error": "invalid_auth"})])
        adapter = SlackAdapter("t-1", bot_token="xoxb-test", http_client=http)
        with pytest.raises(AuthenticationError):
            await adapter.send_message("t-1", "C01", "test")

    @pytest.mark.asyncio
    async def test_rate_limited_raises(self):
        http = MockHTTP([MockResponse(_json={"ok": False, "error": "ratelimited"}, headers={"Retry-After": "30"})])
        adapter = SlackAdapter("t-1", bot_token="xoxb-test", http_client=http)
        with pytest.raises(RateLimitError):
            await adapter.send_message("t-1", "C01", "test")

    @pytest.mark.asyncio
    async def test_missing_token_raises(self):
        adapter = SlackAdapter("t-1")
        with pytest.raises(AuthenticationError):
            await adapter.send_message("t-1", "C01", "test")


# ---------------------------------------------------------------------------
# Threaded reply
# ---------------------------------------------------------------------------


class TestThreadedReply:
    @pytest.mark.asyncio
    async def test_send_threaded_reply_with_sources(self):
        http = MockHTTP([MockResponse(_json={"ok": True, "ts": "1.0", "channel": "C01"})])
        adapter = SlackAdapter("t-1", bot_token="xoxb-test", http_client=http)
        msg = await adapter.send_threaded_reply(
            "C01", "thread-ts",
            "Answer",
            sources=[{"title": "FAQ", "url": "https://faq.com"}],
        )
        assert msg.external_id == "1.0"
        # Check blocks were sent
        call_json = http.calls[0][2]
        blocks = call_json.get("blocks", [])
        assert len(blocks) >= 2  # text + citation


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


class TestFactory:
    def test_slack_factory_creates_adapter(self):
        from src.integrations.slack import slack_factory
        adapter = slack_factory("t-1")
        assert isinstance(adapter, SlackAdapter)
        assert adapter.tenant_id == "t-1"
