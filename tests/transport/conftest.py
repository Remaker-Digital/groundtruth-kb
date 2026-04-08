"""Shared fixtures and helpers for transport tests.

Provides SSE event parsing, benchmark data structures, and staging
fixtures used across Phase 3 (E2E) and Phase 4 (performance) tests.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import os
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

TEST_HOST_URL = os.environ.get("TEST_HOST_URL", "")
STAGING_WIDGET_KEY = os.environ.get("STAGING_WIDGET_KEY", "")

requires_test_host = pytest.mark.skipif(
    not TEST_HOST_URL,
    reason="TEST_HOST_URL not set — requires staging test host",
)


# ---------------------------------------------------------------------------
# SSE event parsing (shared with Phase 3 E2E tests)
# ---------------------------------------------------------------------------


def consume_sse_events(raw_text: str) -> list[dict[str, Any]]:
    """Parse SSE text into a list of event dicts."""
    events: list[dict[str, Any]] = []
    for line in raw_text.split("\n"):
        line = line.strip()
        if line.startswith("data:"):
            payload = line[len("data:"):].strip()
            if payload:
                try:
                    events.append(json.loads(payload))
                except json.JSONDecodeError:
                    pass
    return events


def has_stage(events: list[dict], stage_name: str, state: str = "completed") -> bool:
    """Check if events contain a specific stage event."""
    return any(
        e.get("stage") == stage_name and e.get("status") == state
        for e in events
    )


def has_error_event(events: list[dict]) -> bool:
    """Check if events contain an error event."""
    return any(
        e.get("type") == "error"
        or (e.get("code") and e.get("recoverable") is not None)
        for e in events
    )


def get_stage_latency(events: list[dict], stage_name: str) -> float | None:
    """Extract latency_ms for a completed stage, or None if not found."""
    for e in events:
        if e.get("stage") == stage_name and e.get("status") == "completed":
            return e.get("latency_ms")
    return None


def get_total_latency(events: list[dict]) -> float | None:
    """Extract total_latency_ms from the done event, or None."""
    for e in events:
        if "total_latency_ms" in e and "conversation_id" in e and "stage" not in e:
            return e["total_latency_ms"]
    return None


# ---------------------------------------------------------------------------
# Benchmark data structures
# ---------------------------------------------------------------------------


@dataclass
class BenchmarkResult:
    """Captures a single benchmark run with percentile computation."""

    name: str
    tier: str
    samples: list[float] = field(default_factory=list)
    errors: int = 0

    @property
    def p50(self) -> float:
        return statistics.median(self.samples) if self.samples else 0

    @property
    def p95(self) -> float:
        if not self.samples:
            return 0
        idx = int(len(self.samples) * 0.95)
        return sorted(self.samples)[min(idx, len(self.samples) - 1)]

    @property
    def p99(self) -> float:
        if not self.samples:
            return 0
        idx = int(len(self.samples) * 0.99)
        return sorted(self.samples)[min(idx, len(self.samples) - 1)]

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "tier": self.tier,
            "sample_count": len(self.samples),
            "p50_ms": round(self.p50, 2),
            "p95_ms": round(self.p95, 2),
            "p99_ms": round(self.p99, 2),
            "errors": self.errors,
        }


# ---------------------------------------------------------------------------
# Staging fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def staging_base_url() -> str:
    """Staging gateway base URL (requires TEST_HOST_URL)."""
    if not TEST_HOST_URL:
        pytest.skip("TEST_HOST_URL not set")
    return TEST_HOST_URL.rstrip("/")


@pytest.fixture
def widget_headers() -> dict[str, str]:
    """Widget auth headers for chat API (requires STAGING_WIDGET_KEY)."""
    if not STAGING_WIDGET_KEY:
        pytest.skip("STAGING_WIDGET_KEY not set")
    return {
        "X-Widget-Key": STAGING_WIDGET_KEY,
        "Content-Type": "application/json",
        "X-Widget-Origin": "https://test-store.myshopify.com",
    }


@pytest.fixture
def benchmark_output() -> Path:
    """Output directory for benchmark results."""
    out = Path(__file__).parent.parent.parent / "scripts" / "benchmark-results"
    out.mkdir(exist_ok=True)
    return out


def run_conversation(base_url: str, headers: dict, message: str) -> list[dict]:
    """Create a conversation and consume SSE events. Returns parsed events."""
    import httpx

    client = httpx.Client(timeout=60.0)
    try:
        resp = client.post(
            f"{base_url}/api/chat/conversations",
            headers=headers,
            json={"initial_message": message},
        )
        if resp.status_code != 201:
            return []
        data = resp.json()
        stream_url = data.get("stream_url", f"/api/chat/stream/{data['conversation_id']}")
        stream = client.get(
            f"{base_url}{stream_url}",
            headers={**headers, "Accept": "text/event-stream"},
            timeout=60.0,
        )
        if stream.status_code != 200:
            return []
        return consume_sse_events(stream.text)
    finally:
        client.close()
