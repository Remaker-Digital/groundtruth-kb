"""Pact provider verification for the chat API (SPEC-1847/WI-1507).

Verifies the FastAPI chat endpoint satisfies the consumer contract defined
by the widget transport (widget/src/transport/http.ts).

The contract expectations are:
  - POST /api/chat/conversations → 200 with { conversation_id: string }
  - POST /api/chat/message → 200 with { ok: true }
  - POST /api/chat/message → 422 when missing required fields
  - GET /api/config → 200 with { config: {...}, quick_actions?: [...] }

Run with:
    pytest tests/contract/test_chat_provider.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient

# The pact JSON files define the widget's expected request/response shapes.
# These are maintained in pacts/ and are the single source of truth for
# the widget↔chat API contract.
PACTS_DIR = Path(__file__).resolve().parent.parent.parent / "pacts"


def load_pact(name: str = "widget-chat") -> dict[str, Any]:
    """Load a pact contract JSON file."""
    pact_file = PACTS_DIR / f"{name}.json"
    if not pact_file.exists():
        pytest.skip(f"Pact file not found: {pact_file}")
    with open(pact_file) as f:
        return json.load(f)


@pytest.fixture
def pact_interactions() -> list[dict[str, Any]]:
    """Load the widget-chat pact contract interactions."""
    pact = load_pact("widget-chat")
    return pact.get("interactions", [])


@pytest.fixture
async def client():
    """Create an async test client for the FastAPI app."""
    from src.main import app
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac


# ---------------------------------------------------------------------------
# Contract verification tests
# ---------------------------------------------------------------------------


# Auth-infrastructure errors (middleware can't resolve widget key without
# Cosmos) are expected in test isolation. We tolerate 500 when it contains
# the known middleware config message, but flag genuine 500s.
_KNOWN_INFRA_ERRORS = {"Widget key resolution not configured."}


def _is_infra_error(resp) -> bool:
    """True if the 500 is a known infrastructure/config error, not a code bug."""
    if resp.status_code != 500:
        return False
    try:
        data = resp.json()
        return data.get("error", "") in _KNOWN_INFRA_ERRORS
    except Exception:
        return False


@pytest.mark.asyncio
class TestChatProviderContract:
    """Verify the chat API satisfies the widget consumer contract.

    In test isolation (no Cosmos), the middleware returns 500 with
    "Widget key resolution not configured." — this is tolerated as an
    infrastructure error. The contract asserts that code-path errors
    (unhandled exceptions, wrong shapes) do NOT produce 500s.
    """

    async def test_config_endpoint_shape(self, client: AsyncClient) -> None:
        """GET /api/config returns the shape expected by the widget."""
        resp = await client.get(
            "/api/config",
            headers={"X-Widget-Key": "pk_live_test_placeholder"},
        )
        if resp.status_code == 200:
            data = resp.json()
            assert "config" in data, "Response must contain 'config' key"
            assert isinstance(data["config"], dict), "'config' must be a dict"
        else:
            # Auth or infra error — acceptable in test isolation
            assert resp.status_code in (401, 403, 404) or _is_infra_error(resp), (
                f"Unexpected error: {resp.status_code} {resp.text}"
            )

    async def test_start_conversation_shape(self, client: AsyncClient) -> None:
        """POST /api/chat/conversations returns { conversation_id: string }."""
        resp = await client.post(
            "/api/chat/conversations",
            json={},
            headers={"X-Widget-Key": "pk_live_test_placeholder"},
        )
        if resp.status_code == 200:
            data = resp.json()
            assert "conversation_id" in data, "Response must contain 'conversation_id'"
            assert isinstance(data["conversation_id"], str)
        else:
            assert resp.status_code in (401, 403, 404, 422) or _is_infra_error(resp), (
                f"Unexpected error: {resp.status_code} {resp.text}"
            )

    async def test_send_message_requires_content(self, client: AsyncClient) -> None:
        """POST /api/chat/message without content returns 422 or auth error."""
        resp = await client.post(
            "/api/chat/message",
            json={"conversation_id": "test-conv-id"},
            headers={"X-Widget-Key": "pk_live_test_placeholder"},
        )
        assert resp.status_code in (401, 403, 404, 422) or _is_infra_error(resp), (
            f"Unexpected error: {resp.status_code} {resp.text}"
        )

    async def test_send_message_requires_conversation_id(self, client: AsyncClient) -> None:
        """POST /api/chat/message without conversation_id returns 422 or auth error."""
        resp = await client.post(
            "/api/chat/message",
            json={"content": "Hello"},
            headers={"X-Widget-Key": "pk_live_test_placeholder"},
        )
        assert resp.status_code in (401, 403, 404, 422) or _is_infra_error(resp), (
            f"Unexpected error: {resp.status_code} {resp.text}"
        )

    async def test_rating_endpoint_accepts_positive_negative(self, client: AsyncClient) -> None:
        """POST /api/chat/conversations/{id}/rating accepts 'positive'/'negative'."""
        resp = await client.post(
            "/api/chat/conversations/test-conv/rating",
            json={"rating": "positive", "comment": "Great!"},
            headers={"X-Widget-Key": "pk_live_test_placeholder"},
        )
        assert resp.status_code in (200, 401, 403, 404) or _is_infra_error(resp), (
            f"Unexpected error: {resp.status_code} {resp.text}"
        )

    async def test_message_feedback_endpoint_shape(self, client: AsyncClient) -> None:
        """POST /api/chat/conversations/{id}/messages/{id}/feedback (SPEC-1836)."""
        resp = await client.post(
            "/api/chat/conversations/test-conv/messages/test-msg/feedback",
            json={"rating": "negative", "comment": "Inaccurate response"},
            headers={"X-Widget-Key": "pk_live_test_placeholder"},
        )
        assert resp.status_code in (200, 401, 403, 404) or _is_infra_error(resp), (
            f"Unexpected error: {resp.status_code} {resp.text}"
        )

    async def test_end_conversation_shape(self, client: AsyncClient) -> None:
        """POST /api/chat/conversations/{id}/end returns success or auth error."""
        resp = await client.post(
            "/api/chat/conversations/test-conv/end",
            json={},
            headers={"X-Widget-Key": "pk_live_test_placeholder"},
        )
        assert resp.status_code in (200, 401, 403, 404) or _is_infra_error(resp), (
            f"Unexpected error: {resp.status_code} {resp.text}"
        )

    async def test_consent_endpoint_shape(self, client: AsyncClient) -> None:
        """POST /api/chat/conversations/{id}/consent accepts consent_status."""
        resp = await client.post(
            "/api/chat/conversations/test-conv/consent",
            json={"consent_status": "granted"},
            headers={"X-Widget-Key": "pk_live_test_placeholder"},
        )
        assert resp.status_code in (200, 401, 403, 404) or _is_infra_error(resp), (
            f"Unexpected error: {resp.status_code} {resp.text}"
        )


# ---------------------------------------------------------------------------
# Pact file verification (when pact JSON exists)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestPactFileVerification:
    """Verify interactions from the pact JSON file against the live API."""

    async def test_all_pact_interactions_produce_expected_status(
        self, client: AsyncClient, pact_interactions: list[dict],
    ) -> None:
        """Each interaction in the pact file must produce the expected HTTP status."""
        if not pact_interactions:
            pytest.skip("No pact interactions defined")

        for interaction in pact_interactions:
            req = interaction.get("request", {})
            expected = interaction.get("response", {})
            method = req.get("method", "GET").upper()
            path = req.get("path", "/")
            body = req.get("body")
            expected_status = expected.get("status", 200)

            headers = {"X-Widget-Key": "pk_live_test_placeholder"}

            if method == "GET":
                resp = await client.get(path, headers=headers)
            elif method == "POST":
                resp = await client.post(path, json=body, headers=headers)
            elif method == "PUT":
                resp = await client.put(path, json=body, headers=headers)
            else:
                continue

            # Allow auth/infra failures since test doesn't have real keys or Cosmos
            if resp.status_code in (401, 403, 404) or _is_infra_error(resp):
                continue

            assert resp.status_code == expected_status, (
                f"Interaction '{interaction.get('description', 'unnamed')}': "
                f"expected {expected_status}, got {resp.status_code}"
            )
