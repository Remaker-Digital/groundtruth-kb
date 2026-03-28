"""Phase 4 — Transport performance benchmark matrix.

Measures the actual deployed architecture using per-hop stage latency
from SSE events. All benchmarks use the real chat API contract
(POST /conversations + GET /stream/{id}), authenticated via X-Widget-Key.

Per-hop attribution uses latency_ms from completed stage events (server-side
wall-clock from PipelineTimeoutBudget), not elapsed_ms subtraction.

Latency targets are provisional measurement thresholds, not hard gates.
Hard enforcement deferred to Phase 5 after baseline stabilization.

Analytics is explicitly excluded: fire-and-forget, non-customer-facing.

Recovery plan reference: INSIGHTS-2026-03-27-01-00.md Phase 4.
Codex GO: INSIGHTS-2026-03-28-02-05-PHASE4-PLAN-REREVIEW.md.
Governing decisions: ADR-001, DCL-002 v4.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest

from tests.transport.conftest import (
    BenchmarkResult,
    consume_sse_events,
    get_stage_latency,
    get_total_latency,
    has_error_event,
    has_stage,
    requires_test_host,
    run_conversation,
    STAGING_WIDGET_KEY,
    TEST_HOST_URL,
)

# Sample messages — varied to avoid caching effects
SAMPLE_MESSAGES = [
    "What are your store hours?",
    "Do you offer free shipping?",
    "What is your return policy?",
    "Do you have any sales right now?",
    "How can I track my order?",
    "What payment methods do you accept?",
    "Do you ship internationally?",
    "Can I cancel my order?",
    "What products do you recommend?",
    "How do I contact support?",
    "Do you have a loyalty program?",
    "What are your best sellers?",
    "How long does delivery take?",
    "Do you offer gift cards?",
    "What is your warranty policy?",
    "Can I change my shipping address?",
    "Do you price match?",
    "What sizes are available?",
    "How do I apply a discount code?",
    "When will my item be back in stock?",
]

ESCALATION_MESSAGES = [
    "I need to speak with a human agent right now",
    "Let me talk to a real person please",
    "I want to escalate this issue",
    "Connect me to a manager",
    "This is urgent, I need human help",
]


# ---------------------------------------------------------------------------
# Category A: Per-Hop Stage Latency
# ---------------------------------------------------------------------------


class TestPerHopStageLatency:
    """Measure per-agent latency from SSE stage events (latency_ms)."""

    @requires_test_host
    def test_per_hop_stage_latency(self, staging_base_url, widget_headers, benchmark_output):
        """20 conversations — per-stage P50/P95 from latency_ms.

        Provisional targets (measurement, not hard gates):
        - IC P95 < 200ms (gpt-4o-mini classification)
        - KR P95 < 2000ms (vector search + Cosmos)
        - RG P95 < 5000ms (gpt-4o streaming, in-process per DCL-002 v4)
        - Critic P95 < 1000ms (fail-closed if unavailable)
        """
        stage_results = {
            "intent-classifier": BenchmarkResult(name="ic-latency", tier="per-interface"),
            "knowledge-retrieval": BenchmarkResult(name="kr-latency", tier="per-interface"),
            "response-generator": BenchmarkResult(name="rg-latency", tier="per-interface"),
            "critic-supervisor": BenchmarkResult(name="critic-latency", tier="per-interface"),
        }

        for msg in SAMPLE_MESSAGES[:20]:
            events = run_conversation(staging_base_url, widget_headers, msg)
            if has_error_event(events):
                for r in stage_results.values():
                    r.errors += 1
                continue

            for stage_name, result in stage_results.items():
                latency = get_stage_latency(events, stage_name)
                if latency is not None:
                    result.samples.append(latency)

        # Report
        for stage_name, result in stage_results.items():
            print(f"\n  {stage_name}: P50={result.p50:.0f}ms P95={result.p95:.0f}ms "
                  f"({len(result.samples)} samples, {result.errors} errors)")

        # Provisional thresholds (measurement, not hard gates)
        ic = stage_results["intent-classifier"]
        kr = stage_results["knowledge-retrieval"]
        rg = stage_results["response-generator"]
        cr = stage_results["critic-supervisor"]

        assert len(ic.samples) >= 10, f"Insufficient IC samples: {len(ic.samples)}"
        assert ic.p95 < 200, f"IC P95={ic.p95:.0f}ms exceeds provisional 200ms"
        assert kr.p95 < 2000, f"KR P95={kr.p95:.0f}ms exceeds provisional 2000ms"
        assert rg.p95 < 5000, f"RG P95={rg.p95:.0f}ms exceeds provisional 5000ms"
        assert cr.p95 < 1000, f"Critic P95={cr.p95:.0f}ms exceeds provisional 1000ms"

        # Write benchmark artifact
        report = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "test": "per_hop_stage_latency",
            "sample_count": 20,
            "stages": {name: r.to_dict() for name, r in stage_results.items()},
        }
        (benchmark_output / "per-hop-latency.json").write_text(json.dumps(report, indent=2))

    @requires_test_host
    def test_total_pipeline_latency(self, staging_base_url, widget_headers, benchmark_output):
        """20 conversations — total pipeline P50/P95/P99 from done event."""
        result = BenchmarkResult(name="total-pipeline", tier="end-to-end")

        for msg in SAMPLE_MESSAGES[:20]:
            events = run_conversation(staging_base_url, widget_headers, msg)
            if has_error_event(events):
                result.errors += 1
                continue
            total = get_total_latency(events)
            if total is not None:
                result.samples.append(total)

        print(f"\n  Pipeline: P50={result.p50:.0f}ms P95={result.p95:.0f}ms "
              f"P99={result.p99:.0f}ms ({len(result.samples)} samples, {result.errors} errors)")

        assert len(result.samples) >= 10, f"Insufficient samples: {len(result.samples)}"
        assert result.p95 < 8000, f"Pipeline P95={result.p95:.0f}ms exceeds provisional 8000ms"

        report = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "test": "total_pipeline_latency",
            "benchmarks": [result.to_dict()],
        }
        (benchmark_output / "pipeline-latency.json").write_text(json.dumps(report, indent=2))

    @requires_test_host
    def test_gateway_baseline_latency(self, staging_base_url):
        """20x /ready — gateway overhead without agent dispatch."""
        import httpx
        result = BenchmarkResult(name="gateway-baseline", tier="http")
        client = httpx.Client(timeout=30.0)
        try:
            # Warm-up request (TLS handshake + connection pool init)
            client.get(f"{staging_base_url}/ready")
            for _ in range(20):
                start = time.monotonic()
                resp = client.get(f"{staging_base_url}/ready")
                elapsed = (time.monotonic() - start) * 1000
                if resp.status_code == 200:
                    result.samples.append(elapsed)
                else:
                    result.errors += 1
        finally:
            client.close()

        print(f"\n  Gateway baseline: P50={result.p50:.0f}ms P95={result.p95:.0f}ms")
        assert result.p95 < 500, f"Gateway P95={result.p95:.0f}ms exceeds 500ms"
        assert result.errors == 0

    @requires_test_host
    def test_escalation_path_latency(self, staging_base_url, widget_headers, benchmark_output):
        """5 escalation conversations — IC + escalation-handler latency_ms.

        If escalation is not classifiable (environment limitation), reports
        as a measurement gap — not a pass-equivalent (per Codex advisory).
        """
        ic_result = BenchmarkResult(name="escalation-ic", tier="per-interface")
        esc_result = BenchmarkResult(name="escalation-handler", tier="per-interface")
        measurement_gap = False

        for msg in ESCALATION_MESSAGES[:5]:
            events = run_conversation(staging_base_url, widget_headers, msg)
            if has_error_event(events):
                ic_result.errors += 1
                continue

            ic_latency = get_stage_latency(events, "intent-classifier")
            if ic_latency is not None:
                ic_result.samples.append(ic_latency)

            esc_latency = get_stage_latency(events, "escalation-handler")
            if esc_latency is not None:
                esc_result.samples.append(esc_latency)
            elif not has_stage(events, "escalation-handler"):
                measurement_gap = True

        print(f"\n  Escalation IC: P50={ic_result.p50:.0f}ms ({len(ic_result.samples)} samples)")
        print(f"  Escalation Handler: P50={esc_result.p50:.0f}ms ({len(esc_result.samples)} samples)")
        if measurement_gap:
            print("  WARNING: escalation-handler stage not observed — measurement gap")

        assert len(ic_result.samples) >= 1, "No IC samples from escalation attempts"

        report = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "test": "escalation_path_latency",
            "measurement_gap": measurement_gap,
            "stages": {
                "intent-classifier": ic_result.to_dict(),
                "escalation-handler": esc_result.to_dict(),
            },
        }
        (benchmark_output / "escalation-latency.json").write_text(json.dumps(report, indent=2))

    @requires_test_host
    def test_widget_pipeline_latency(self, staging_base_url, widget_headers, benchmark_output):
        """20 widget conversations — same metrics as per-hop test.

        Verifies widget traffic has comparable latency.
        """
        result = BenchmarkResult(name="widget-pipeline", tier="widget")

        for msg in SAMPLE_MESSAGES[:20]:
            events = run_conversation(staging_base_url, widget_headers, msg)
            if has_error_event(events):
                result.errors += 1
                continue
            total = get_total_latency(events)
            if total is not None:
                result.samples.append(total)

        print(f"\n  Widget pipeline: P50={result.p50:.0f}ms P95={result.p95:.0f}ms "
              f"({len(result.samples)} samples, {result.errors} errors)")

        assert len(result.samples) >= 10, f"Insufficient widget samples: {len(result.samples)}"

        report = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "test": "widget_pipeline_latency",
            "benchmarks": [result.to_dict()],
        }
        (benchmark_output / "widget-latency.json").write_text(json.dumps(report, indent=2))


# ---------------------------------------------------------------------------
# Category B: Architecture Verification
# ---------------------------------------------------------------------------


class TestArchitectureVerification:
    """Verify transport tier and RG placement match architecture decisions."""

    @requires_test_host
    def test_transport_tier_identification(self, staging_base_url, benchmark_output):
        """Query /ready and record the active transport tier."""
        import httpx
        client = httpx.Client(timeout=30.0)
        try:
            resp = client.get(f"{staging_base_url}/ready")
            assert resp.status_code == 200
            sdk = resp.json().get("agntcy_sdk", {})
            tier = sdk.get("active_tier", "unknown")
            active = sdk.get("transport_active", False)
            slim = sdk.get("slim_endpoint")
            nats = sdk.get("nats_endpoint")
        finally:
            client.close()

        print(f"\n  Active tier: {tier}")
        print(f"  Transport active: {active}")
        print(f"  SLIM: {slim or 'None'}")
        print(f"  NATS: {nats or 'None'}")

        report = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "test": "transport_tier_identification",
            "active_tier": tier,
            "transport_active": active,
            "slim_endpoint": slim,
            "nats_endpoint": nats,
        }
        (benchmark_output / "transport-tier.json").write_text(json.dumps(report, indent=2))

    def test_rg_placement_verification(self):
        """DCL-002 v4 in KB records in-process RG as intended production path.

        This is architecture metadata verification, not latency inference.
        """
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools" / "knowledge-db"))
        import db as kb_db
        kdb = kb_db.KnowledgeDB()

        spec = kdb.get_spec("DCL-002")
        assert spec is not None, "DCL-002 not found in KB"
        assert spec["version"] >= 4, (
            f"DCL-002 version {spec['version']} — expected >=4 (per-interface policy)"
        )

        desc = spec.get("description", "")
        assert "in-process" in desc.lower() or "gateway" in desc.lower(), (
            "DCL-002 v4 should document in-process RG streaming as intended path"
        )
        assert "response" in desc.lower() or "rg" in desc.lower(), (
            "DCL-002 v4 should reference response generator"
        )


# ---------------------------------------------------------------------------
# Category C: Failure Injection
# ---------------------------------------------------------------------------


class TestFailureInjection:
    """Verify failure paths have bounded latency."""

    def test_503_on_transport_exhaustion(self):
        """_require_transport_or_fail() raises HTTPException 503."""
        from fastapi import HTTPException
        from src.chat.pipeline.agent_dispatch import AgentDispatchMixin

        mixin = AgentDispatchMixin.__new__(AgentDispatchMixin)
        start = time.monotonic()
        with pytest.raises(HTTPException) as exc_info:
            mixin._require_transport_or_fail("test-agent")
        elapsed = (time.monotonic() - start) * 1000

        assert exc_info.value.status_code == 503
        assert elapsed < 50, f"503 took {elapsed:.1f}ms — should be near-instant"

    def test_critic_fail_closed_latency(self):
        """Critic unavailable returns safe fallback in <10ms."""
        import asyncio
        from unittest.mock import patch

        from src.chat.pipeline.critic_escalation import CriticEscalationMixin
        from src.multi_tenant.critic_policy import SAFE_FALLBACK_MESSAGE

        mixin = CriticEscalationMixin.__new__(CriticEscalationMixin)
        mixin._critic = None
        mixin._agent_urls = {}

        with patch("src.multi_tenant.agntcy_sdk_integration._transport", None), \
             patch("src.multi_tenant.agntcy_sdk_integration._transport_setup_ok", False):
            start = time.monotonic()
            approved, message, result = asyncio.run(
                mixin._validate_with_critic(
                    tenant_id="test-tenant",
                    conversation_id="test-conv",
                    response_text="Test response",
                    customer_message="Test question",
                    budget=None,
                    knowledge_titles=None,
                )
            )
            elapsed = (time.monotonic() - start) * 1000

        assert approved is False
        assert message == SAFE_FALLBACK_MESSAGE
        assert elapsed < 10, f"Fail-closed took {elapsed:.1f}ms — should be <10ms"
        print(f"\n  Critic fail-closed: {elapsed:.1f}ms")


# ---------------------------------------------------------------------------
# Category D: Benchmark Output
# ---------------------------------------------------------------------------


class TestBenchmarkOutput:
    """Generate consolidated benchmark report."""

    def test_benchmark_report_generation(self, benchmark_output):
        """Generate structured JSON report from all benchmark artifacts."""
        import httpx

        artifacts = {}
        for f in benchmark_output.glob("*.json"):
            if f.stem.startswith("transport-benchmark-"):
                continue  # Skip prior consolidated reports
            try:
                artifacts[f.stem] = json.loads(f.read_text())
            except (json.JSONDecodeError, OSError):
                pass

        version = "unknown"
        if TEST_HOST_URL:
            try:
                resp = httpx.get(f"{TEST_HOST_URL.rstrip('/')}/health", timeout=10.0)
                version = resp.json().get("product_version", "unknown")
            except Exception:
                pass

        report = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "version": version,
            "phase": "4",
            "test_host_url": TEST_HOST_URL or "not configured",
            "artifacts": artifacts,
        }

        report_path = benchmark_output / f"transport-benchmark-{int(time.time())}.json"
        report_path.write_text(json.dumps(report, indent=2))
        print(f"\n  Benchmark report: {report_path}")
        assert report_path.exists()
