"""Container failure resilience coverage for SPEC-1799 / WI-3203."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from src.agents.base import AgentRedBaseAgent
from src.agents.containers.agent_app import create_agent_app
from src.chat.pipeline import agent_dispatch
from src.chat.pipeline.agent_dispatch import AgentDispatchMixin


class _ResilienceAgent(AgentRedBaseAgent):
    """Minimal live agent used for container probe checks."""

    agent_type = "resilience-test"

    async def process(
        self,
        payload: dict[str, Any],
        headers: dict[str, str],
    ) -> dict[str, Any]:
        return {"payload": payload, "headers": headers}


class _FailingDispatch(AgentDispatchMixin):
    """Dispatch harness with exhausted transport and HTTP tiers."""

    def __init__(self) -> None:
        self.direct_called = False

    def _transport_available(self) -> bool:
        return False

    async def _call_intent_classifier_http(
        self,
        message: str,
        system_prompt: str,
    ) -> dict[str, Any]:
        raise RuntimeError("container unavailable")

    async def _call_intent_classifier_direct(
        self,
        message: str,
        system_prompt: str,
    ) -> dict[str, Any]:
        self.direct_called = True
        raise AssertionError("direct in-process dispatch must not be used")


def test_container_health_and_readiness_degrade_before_setup() -> None:
    app = create_agent_app(_ResilienceAgent)
    client = TestClient(app, raise_server_exceptions=False)

    health = client.get("/health")
    assert health.status_code == 503
    assert health.json() == {
        "agent": "resilience-test",
        "protocol": "A2A",
        "configured": False,
        "status": "not_configured",
    }

    ready = client.get("/ready")
    assert ready.status_code == 503
    assert ready.json() == {"ready": False, "agent": "resilience-test"}


def test_container_readiness_and_health_recover_after_setup() -> None:
    app = create_agent_app(_ResilienceAgent)
    asyncio.run(app.state.agent.setup())
    client = TestClient(app, raise_server_exceptions=False)

    ready = client.get("/ready")
    assert ready.status_code == 200
    assert ready.json() == {"ready": True, "agent": "resilience-test"}

    health = client.get("/health")
    assert health.status_code == 200
    body = health.json()
    assert body["agent"] == "resilience-test"
    assert body["configured"] is True
    assert body["status"] == "healthy"


def test_require_transport_or_fail_returns_503_with_tier_diagnostic() -> None:
    dispatch = AgentDispatchMixin()

    with pytest.raises(HTTPException) as exc_info:
        dispatch._require_transport_or_fail("intent-classifier")

    assert exc_info.value.status_code == 503
    assert "Agent dispatch unavailable: intent-classifier" in exc_info.value.detail
    assert "All transport tiers exhausted" in exc_info.value.detail


@pytest.mark.asyncio()
async def test_non_streaming_dispatch_503s_without_direct_fallback(monkeypatch) -> None:
    monkeypatch.setattr(agent_dispatch, "USE_AGENT_CONTAINERS", True)
    dispatch = _FailingDispatch()

    with pytest.raises(HTTPException) as exc_info:
        await dispatch._call_intent_classifier(
            "hello",
            "classify the customer message",
        )

    assert exc_info.value.status_code == 503
    assert "All transport tiers exhausted" in exc_info.value.detail
    assert dispatch.direct_called is False
