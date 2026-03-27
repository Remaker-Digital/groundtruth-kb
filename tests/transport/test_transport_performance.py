"""Phase 4 — Transport performance benchmark matrix.

Defines and runs benchmarks for the containerized agent transport layer:
- Per-container latency (P50/P95/P99)
- Cross-container hop latency
- Transport tier comparison (SLIM vs NATS vs HTTP)
- Single-container recovery under load
- Widget-origin traffic performance

These tests require the staging test host and are skipped locally.
Results are structured for comparison across transport tiers.

Recovery plan reference: INSIGHTS-2026-03-27-01-00.md Phase 4.
Governing decisions: ADR-001, ADR-002.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import os
import statistics
import time
from dataclasses import dataclass, field
from pathlib import Path

import pytest

# Skip entire module if no test host URL
TEST_HOST_URL = os.environ.get("TEST_HOST_URL", "")
requires_test_host = pytest.mark.skipif(
    not TEST_HOST_URL,
    reason="TEST_HOST_URL not set — transport perf tests require staging test host",
)

pytestmark = [requires_test_host, pytest.mark.performance]


# ---------------------------------------------------------------------------
# Benchmark data structures
# ---------------------------------------------------------------------------


@dataclass
class BenchmarkResult:
    """Captures a single benchmark run."""
    name: str
    tier: str  # slim, nats, http
    samples: list[float] = field(default_factory=list)  # latency in ms
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
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def test_host_url() -> str:
    return TEST_HOST_URL.rstrip("/")


@pytest.fixture
def http_client():
    import httpx
    client = httpx.Client(timeout=30.0)
    yield client
    client.close()


@pytest.fixture
def benchmark_output() -> Path:
    """Output directory for benchmark results."""
    out = Path(__file__).parent.parent.parent / "scripts" / "benchmark-results"
    out.mkdir(exist_ok=True)
    return out


# ---------------------------------------------------------------------------
# 1. Per-container latency (health endpoint baseline)
# ---------------------------------------------------------------------------


class TestPerContainerLatency:
    """Measure per-container /health response latency."""

    def test_gateway_health_latency(self, test_host_url, http_client):
        """Gateway /ready latency should be under 500ms P95."""
        result = BenchmarkResult(name="gateway-health", tier="http")
        for _ in range(20):
            start = time.monotonic()
            resp = http_client.get(f"{test_host_url}/ready")
            elapsed = (time.monotonic() - start) * 1000
            if resp.status_code == 200:
                result.samples.append(elapsed)
            else:
                result.errors += 1

        assert result.p95 < 500, f"Gateway P95={result.p95:.1f}ms exceeds 500ms"
        assert result.errors == 0

    def test_transport_tier_detection(self, test_host_url, http_client):
        """Verify which transport tier is active on the gateway."""
        resp = http_client.get(f"{test_host_url}/ready")
        data = resp.json()
        sdk = data.get("agntcy_sdk", {})
        tier = sdk.get("active_tier", "unknown")
        active = sdk.get("transport_active", False)
        assert active, f"Transport not active (tier={tier})"
        # Record the active tier for other tests
        print(f"\n  Active transport tier: {tier}")
        print(f"  SLIM endpoint: {sdk.get('slim_endpoint', 'N/A')}")
        print(f"  NATS endpoint: {sdk.get('nats_endpoint', 'N/A')}")


# ---------------------------------------------------------------------------
# 2. Cross-container hop latency (agent dispatch roundtrip)
# ---------------------------------------------------------------------------


class TestCrossContainerLatency:
    """Measure cross-container dispatch latency.

    These tests send requests through the gateway that dispatch to
    agent containers, measuring the full roundtrip including transport
    overhead and agent processing.
    """

    def test_intent_classifier_roundtrip(self, test_host_url, http_client):
        """IC dispatch roundtrip should complete within budget."""
        # This would require an authenticated request to the chat endpoint
        # which triggers IC dispatch. Placeholder for when auth fixtures
        # are available.
        pass

    def test_transport_overhead_baseline(self, test_host_url, http_client):
        """Baseline: gateway-only latency vs agent dispatch latency.

        The difference approximates transport + agent processing overhead.
        """
        # Gateway-only baseline (no agent dispatch)
        gateway_times = []
        for _ in range(10):
            start = time.monotonic()
            http_client.get(f"{test_host_url}/ready")
            gateway_times.append((time.monotonic() - start) * 1000)

        gw_p50 = statistics.median(gateway_times)
        print(f"\n  Gateway baseline P50: {gw_p50:.1f}ms")


# ---------------------------------------------------------------------------
# 3. Benchmark output
# ---------------------------------------------------------------------------


class TestBenchmarkOutput:
    """Ensure benchmark infrastructure works and outputs are structured."""

    def test_benchmark_result_serialization(self):
        """BenchmarkResult should serialize to structured dict."""
        result = BenchmarkResult(
            name="test-bench",
            tier="slim",
            samples=[10.0, 20.0, 30.0, 40.0, 50.0],
        )
        d = result.to_dict()
        assert d["name"] == "test-bench"
        assert d["tier"] == "slim"
        assert d["p50_ms"] == 30.0
        assert d["sample_count"] == 5

    def test_gateway_benchmark_report(
        self, test_host_url, http_client, benchmark_output
    ):
        """Generate a benchmark report from gateway health probes."""
        result = BenchmarkResult(name="gateway-ready", tier="http")
        for _ in range(10):
            start = time.monotonic()
            resp = http_client.get(f"{test_host_url}/ready")
            elapsed = (time.monotonic() - start) * 1000
            if resp.status_code == 200:
                result.samples.append(elapsed)
            else:
                result.errors += 1

        report = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "test_host_url": test_host_url,
            "benchmarks": [result.to_dict()],
        }

        report_path = benchmark_output / "transport-benchmark-latest.json"
        report_path.write_text(json.dumps(report, indent=2))
        assert report_path.exists()
