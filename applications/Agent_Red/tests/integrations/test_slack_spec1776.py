"""SPEC-1776 coverage for the Slack channel adapter."""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from typing import Any

import pytest

from src.integrations.manifest import (
    AuthType,
    Capability,
    IntegrationCategory,
    SyncStrategy,
)
from src.integrations.models import MessageChannel, MessageDirection
from src.integrations.slack import adapter as slack_adapter_module
from src.integrations.slack.adapter import (
    TIMESTAMP_TOLERANCE,
    SlackAdapter,
    build_citation_block,
    build_escalation_block,
    build_text_block,
)
from src.integrations.slack.manifest import SLACK_MANIFEST


@dataclass
class MockResponse:
    payload: dict[str, Any]
    headers: dict[str, str] | None = None

    def json(self) -> dict[str, Any]:
        return self.payload


@dataclass(frozen=True)
class RecordedCall:
    method: str
    url: str
    headers: dict[str, str]
    json: dict[str, Any]


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
        self.calls.append(RecordedCall(method, url, headers or {}, json or {}))
        if self._index >= len(self._responses):
            return MockResponse({"ok": True})
        response = self._responses[self._index]
        self._index += 1
        return response


def _adapter(http: RecordingHTTP) -> SlackAdapter:
    return SlackAdapter(
        "tenant-1",
        bot_token="unit-test-token",
        signing_secret="unit-test-signing-key",
        http_client=http,
    )


def test_spec1776_manifest_declares_slack_bot_setup_surface() -> None:
    assert SLACK_MANIFEST.integration_id == "slack"
    assert SLACK_MANIFEST.category == IntegrationCategory.CHANNEL
    assert SLACK_MANIFEST.auth_type == AuthType.OAUTH2
    assert set(SLACK_MANIFEST.auth_config.scopes) >= {
        "chat:write",
        "channels:history",
        "channels:read",
        "groups:read",
        "im:read",
        "im:write",
        "app_mentions:read",
        "users:read",
    }
    assert SLACK_MANIFEST.auth_config.authorize_url == ("https://slack.com/oauth/v2/authorize")
    assert SLACK_MANIFEST.auth_config.token_url == ("https://slack.com/api/oauth.v2.access")
    assert SLACK_MANIFEST.auth_config.client_id_env == "SLACK_CLIENT_ID"
    assert SLACK_MANIFEST.auth_config.client_secret_env == "SLACK_CLIENT_SECRET"
    assert SLACK_MANIFEST.has_capability(Capability.DEST_REPLY)
    assert SLACK_MANIFEST.has_capability(Capability.WEBHOOK_RECEIVE)
    assert SLACK_MANIFEST.sync_strategy == SyncStrategy.WEBHOOK
    assert SLACK_MANIFEST.webhook_signature_header == "x-slack-signature"
    assert SLACK_MANIFEST.webhook_signature_algo == "hmac-sha256"


def test_spec1776_block_kit_supports_text_citations_and_escalation() -> None:
    text_block = build_text_block("Here is the answer")
    citation_block = build_citation_block([{"title": "Returns FAQ", "url": "https://example.test/returns"}])
    escalation_block = build_escalation_block("https://example.test/tickets/123")

    assert text_block == {
        "type": "section",
        "text": {"type": "mrkdwn", "text": "Here is the answer"},
    }
    assert citation_block == {
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": "<https://example.test/returns|Returns FAQ>",
            }
        ],
    }
    assert escalation_block["type"] == "actions"
    assert escalation_block["elements"][0]["action_id"] == "escalate_to_agent"
    assert escalation_block["elements"][0]["url"] == "https://example.test/tickets/123"


@pytest.mark.asyncio
async def test_spec1776_threaded_reply_sends_block_kit_payload() -> None:
    http = RecordingHTTP([MockResponse({"ok": True, "ts": "1700000000.000200", "channel": "C123"})])

    message = await _adapter(http).send_threaded_reply(
        "C123",
        "1700000000.000100",
        "I found the policy.",
        sources=[{"title": "Returns FAQ", "url": "https://example.test/returns"}],
        offer_escalation=True,
    )

    assert message.external_id == "1700000000.000200"
    assert message.direction == MessageDirection.OUTBOUND
    assert message.channel == MessageChannel.SLACK
    assert message.metadata == {"channel": "C123", "thread_ts": "1700000000.000100"}
    assert http.calls[0].method == "POST"
    assert http.calls[0].url == "https://slack.com/api/chat.postMessage"
    assert http.calls[0].json["channel"] == "C123"
    assert http.calls[0].json["text"] == "I found the policy."
    assert http.calls[0].json["thread_ts"] == "1700000000.000100"
    assert [block["type"] for block in http.calls[0].json["blocks"]] == [
        "section",
        "context",
        "actions",
    ]


@pytest.mark.asyncio
async def test_spec1776_channel_history_normalizes_messages_and_cursor() -> None:
    http = RecordingHTTP(
        [
            MockResponse(
                {
                    "ok": True,
                    "messages": [
                        {"ts": "1700000000.1", "text": "<@BOT> help", "user": "U1"},
                        {"ts": "1700000000.2", "text": "More context", "user": "U2"},
                    ],
                    "has_more": True,
                    "response_metadata": {"next_cursor": "cursor-next"},
                }
            )
        ]
    )

    messages, cursor = await _adapter(http).receive_messages(
        "tenant-1",
        "C123",
        cursor="cursor-start",
        limit=500,
    )

    assert cursor == "cursor-next"
    assert [message.external_id for message in messages] == [
        "1700000000.1",
        "1700000000.2",
    ]
    assert messages[0].direction == MessageDirection.INBOUND
    assert messages[0].channel == MessageChannel.SLACK
    assert messages[0].body_text == "<@BOT> help"
    assert messages[0].sender.external_id == "U1"
    assert http.calls[0].url == "https://slack.com/api/conversations.history"
    assert http.calls[0].json == {
        "channel": "C123",
        "limit": 200,
        "cursor": "cursor-start",
    }


@pytest.mark.asyncio
async def test_spec1776_events_api_registration_guidance() -> None:
    guidance = await SlackAdapter("tenant-1").register_webhook(
        "tenant-1",
        "https://example.test/slack/events",
        ["app_mention", "message.channels"],
    )

    assert guidance["integration_id"] == "slack"
    assert guidance["target_url"] == "https://example.test/slack/events"
    assert guidance["events"] == ["app_mention", "message.channels"]
    assert set(guidance["required_scopes"]) >= {
        "app_mentions:read",
        "channels:history",
    }


@pytest.mark.asyncio
async def test_spec1776_webhook_signature_uses_timestamped_hmac(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixed_time = 1_700_000_000
    monkeypatch.setattr(slack_adapter_module.time, "time", lambda: fixed_time)
    body = b'{"event":{"type":"app_mention","text":"<@BOT> help"}}'
    timestamp = str(fixed_time)
    signing_key = "unit-test-signing-key"
    basestring = f"v0:{timestamp}:{body.decode('utf-8')}"
    signature = (
        "v0="
        + hmac.new(
            signing_key.encode(),
            basestring.encode(),
            hashlib.sha256,
        ).hexdigest()
    )

    adapter = SlackAdapter("tenant-1")
    assert await adapter.verify_webhook(
        {
            "x-slack-request-timestamp": timestamp,
            "x-slack-signature": signature,
        },
        body,
        signing_key,
    )
    assert not await adapter.verify_webhook(
        {
            "x-slack-request-timestamp": timestamp,
            "x-slack-signature": "v0=invalid",
        },
        body,
        signing_key,
    )
    assert not await adapter.verify_webhook(
        {
            "x-slack-request-timestamp": str(fixed_time - TIMESTAMP_TOLERANCE - 1),
            "x-slack-signature": signature,
        },
        body,
        signing_key,
    )
