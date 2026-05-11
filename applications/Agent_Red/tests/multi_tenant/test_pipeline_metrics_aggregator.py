"""Tests for PipelineMetricsAggregator (SPEC-1584).

Validates cross-tenant conversation trace aggregation with per-agent,
per-edge, and per-tenant metric computation. Time windowing and caching.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import time


from src.multi_tenant.pipeline_metrics import (
    AgentMetrics,
    EdgeMetrics,
    PipelineMetricsAggregator,
    TenantMetrics,
    get_pipeline_agents,
    get_pipeline_edges,
    _MetricsCache,
    _cutoff_timestamp,
    _period_to_seconds,
)


# ---------------------------------------------------------------------------
# Test data fixtures
# ---------------------------------------------------------------------------

def _make_conversation(
    conv_id: str = "conv-001",
    tenant_id: str = "tenant-001",
    stages: list[dict] | None = None,
    total_latency_ms: int = 500,
    intent: str = "product_inquiry",
    critic_passed: bool = True,
    ts: int = 0,
) -> dict:
    """Build a mock conversation document with pipeline_trace."""
    if stages is None:
        stages = [
            {"stage": "intent-classifier", "elapsed_ms": 50, "succeeded": True},
            {"stage": "knowledge-retrieval", "elapsed_ms": 150, "succeeded": True},
            {"stage": "response-generator", "elapsed_ms": 200, "succeeded": True},
            {"stage": "critic-supervisor", "elapsed_ms": 80, "succeeded": True},
            {"stage": "analytics-collector", "elapsed_ms": 20, "succeeded": True},
        ]
    return {
        "id": conv_id,
        "tenant_id": tenant_id,
        "pipeline_trace": {
            "trace_id": f"trace-{conv_id}",
            "stages": stages,
            "total_latency_ms": total_latency_ms,
            "intent": intent,
            "critic_passed": critic_passed,
            "model_used": "gpt-4",
        },
        "_ts": ts or int(time.time()),
    }


# ---------------------------------------------------------------------------
# Period helpers
# ---------------------------------------------------------------------------

class TestPeriodHelpers:
    """Test time window utility functions."""

    def test_period_to_seconds_24h(self):
        assert _period_to_seconds("24h") == 86400

    def test_period_to_seconds_7d(self):
        assert _period_to_seconds("7d") == 7 * 86400

    def test_period_to_seconds_1h(self):
        assert _period_to_seconds("1h") == 3600

    def test_period_to_seconds_unknown_defaults(self):
        assert _period_to_seconds("unknown") == 86400

    def test_cutoff_timestamp(self):
        now = int(time.time())
        cutoff = _cutoff_timestamp("24h")
        assert abs(cutoff - (now - 86400)) <= 2  # Allow 2s drift


# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------

class TestMetricsCache:
    """Tests for the in-memory TTL cache."""

    def test_set_and_get(self):
        cache = _MetricsCache(ttl_seconds=60)
        cache.set("key1", {"data": 42})
        assert cache.get("key1") == {"data": 42}

    def test_get_nonexistent_returns_none(self):
        cache = _MetricsCache(ttl_seconds=60)
        assert cache.get("missing") is None

    def test_expired_entry_returns_none(self):
        cache = _MetricsCache(ttl_seconds=0)  # Immediate expiry
        cache.set("key1", "value")
        # Entry expires immediately
        assert cache.get("key1") is None

    def test_clear(self):
        cache = _MetricsCache(ttl_seconds=60)
        cache.set("k1", "v1")
        cache.set("k2", "v2")
        cache.clear()
        assert cache.get("k1") is None
        assert cache.get("k2") is None


# ---------------------------------------------------------------------------
# Aggregation -- agent metrics
# ---------------------------------------------------------------------------

class TestAgentAggregation:
    """Tests for per-agent metrics aggregation (SPEC-1584)."""

    def test_agent_invocation_counts(self):
        """PipelineMetricsAggregator computes agent invocation counts (TEST-2767)."""
        agg = PipelineMetricsAggregator()
        conversations = [
            _make_conversation("c1", "t1"),
            _make_conversation("c2", "t1"),
            _make_conversation("c3", "t2"),
        ]
        agents, _, _ = agg.aggregate_conversations(conversations)

        # intent-classifier appears in all 3 conversations
        assert agents["intent-classifier"].invocation_count == 3
        assert agents["knowledge-retrieval"].invocation_count == 3
        assert agents["response-generator"].invocation_count == 3

    def test_latency_percentiles(self):
        """PipelineMetricsAggregator computes latency percentiles (TEST-2768)."""
        agg = PipelineMetricsAggregator()
        # Create conversations with varying latencies
        conversations = []
        for i in range(100):
            stages = [
                {"stage": "intent-classifier", "elapsed_ms": 10 + i, "succeeded": True},
                {"stage": "knowledge-retrieval", "elapsed_ms": 50 + i, "succeeded": True},
                {"stage": "response-generator", "elapsed_ms": 100 + i * 2, "succeeded": True},
            ]
            conversations.append(_make_conversation(f"c{i}", "t1", stages=stages))

        agents, _, _ = agg.aggregate_conversations(conversations)
        ic = agents["intent-classifier"]

        assert ic.invocation_count == 100
        assert ic.avg_latency_ms > 0
        assert ic.p50_latency_ms > 0
        assert ic.p95_latency_ms > ic.p50_latency_ms
        assert ic.p99_latency_ms >= ic.p95_latency_ms

    def test_empty_conversations(self):
        """PipelineMetricsAggregator handles empty conversation sets (TEST-2769)."""
        agg = PipelineMetricsAggregator()
        agents, edges, tenants = agg.aggregate_conversations([])

        assert len(agents) == len(get_pipeline_agents())
        for am in agents.values():
            assert am.invocation_count == 0
            assert am.avg_latency_ms == 0.0
            assert am.error_rate == 0.0

    def test_error_rate_computation(self):
        """Agent error rate is computed from failed stages."""
        agg = PipelineMetricsAggregator()
        stages_with_error = [
            {"stage": "intent-classifier", "elapsed_ms": 50, "succeeded": True},
            {"stage": "knowledge-retrieval", "elapsed_ms": 150, "succeeded": False},
            {"stage": "response-generator", "elapsed_ms": 200, "succeeded": True},
        ]
        conversations = [
            _make_conversation("c1", "t1"),  # All succeed
            _make_conversation("c2", "t1", stages=stages_with_error),  # KR fails
        ]
        agents, _, _ = agg.aggregate_conversations(conversations)

        assert agents["knowledge-retrieval"].error_count == 1
        assert agents["knowledge-retrieval"].error_rate == 0.5
        assert agents["intent-classifier"].error_rate == 0.0

    def test_error_log_populated(self):
        """Failed stages populate the error log."""
        agg = PipelineMetricsAggregator()
        stages_with_error = [
            {"stage": "intent-classifier", "elapsed_ms": 50, "succeeded": False},
        ]
        conversations = [_make_conversation("c1", "t1", stages=stages_with_error)]
        agents, _, _ = agg.aggregate_conversations(conversations)

        assert len(agents["intent-classifier"].error_log) == 1
        assert agents["intent-classifier"].error_log[0]["conversation_id"] == "c1"


# ---------------------------------------------------------------------------
# Aggregation -- edge metrics
# ---------------------------------------------------------------------------

class TestEdgeAggregation:
    """Tests for agent-to-agent edge metrics."""

    def test_edge_volume(self):
        """Edge volume counts transitions between agents."""
        agg = PipelineMetricsAggregator()
        conversations = [_make_conversation("c1", "t1"), _make_conversation("c2", "t1")]
        _, edges, _ = agg.aggregate_conversations(conversations)

        # intent-classifier → knowledge-retrieval should have 2 transitions
        key = ("intent-classifier", "knowledge-retrieval")
        assert edges[key].volume == 2

    def test_edge_metrics_structure(self):
        """All defined edges have EdgeMetrics objects."""
        agg = PipelineMetricsAggregator()
        _, edges, _ = agg.aggregate_conversations([])

        assert len(edges) == len(get_pipeline_edges())
        for (src, tgt), em in edges.items():
            assert em.source == src
            assert em.target == tgt

    def test_drop_off_rate(self):
        """Drop-off rate computed from source invocations vs edge volume."""
        agg = PipelineMetricsAggregator()
        # Intent classifier invoked 3 times, but only 2 route to KR
        conversations = [
            _make_conversation("c1", "t1"),  # Full pipeline
            _make_conversation("c2", "t1"),  # Full pipeline
            _make_conversation("c3", "t1", stages=[
                {"stage": "intent-classifier", "elapsed_ms": 50, "succeeded": True},
                {"stage": "escalation-handler", "elapsed_ms": 100, "succeeded": True},
                {"stage": "analytics-collector", "elapsed_ms": 20, "succeeded": True},
            ]),  # Escalation path
        ]
        _, edges, _ = agg.aggregate_conversations(conversations)

        ic_kr = edges[("intent-classifier", "knowledge-retrieval")]
        assert ic_kr.volume == 2
        # IC had 3 invocations, 2 routed to KR
        ic_esc = edges[("intent-classifier", "escalation-handler")]
        assert ic_esc.volume == 1


# ---------------------------------------------------------------------------
# Aggregation -- tenant metrics
# ---------------------------------------------------------------------------

class TestTenantAggregation:
    """Tests for per-tenant pipeline metrics."""

    def test_multi_tenant_aggregation(self):
        """Conversations are aggregated per tenant."""
        agg = PipelineMetricsAggregator()
        conversations = [
            _make_conversation("c1", "tenant-A"),
            _make_conversation("c2", "tenant-A"),
            _make_conversation("c3", "tenant-B"),
        ]
        _, _, tenants = agg.aggregate_conversations(conversations)

        assert len(tenants) == 2
        assert tenants["tenant-A"].total_conversations == 2
        assert tenants["tenant-B"].total_conversations == 1

    def test_tenant_latency_average(self):
        """Average latency computed across conversations."""
        agg = PipelineMetricsAggregator()
        conversations = [
            _make_conversation("c1", "t1", total_latency_ms=100),
            _make_conversation("c2", "t1", total_latency_ms=300),
        ]
        _, _, tenants = agg.aggregate_conversations(conversations)

        assert tenants["t1"].avg_latency_ms == 200.0

    def test_tenant_escalation_tracking(self):
        """Escalation intent is counted."""
        agg = PipelineMetricsAggregator()
        conversations = [
            _make_conversation("c1", "t1", intent="escalation"),
            _make_conversation("c2", "t1", intent="product_inquiry"),
            _make_conversation("c3", "t1", intent="human_handoff"),
        ]
        _, _, tenants = agg.aggregate_conversations(conversations)

        assert tenants["t1"].escalation_count == 2
        assert tenants["t1"].escalation_rate == 2 / 3

    def test_tenant_error_count(self):
        """Tenant error count from any stage failure."""
        agg = PipelineMetricsAggregator()
        conversations = [
            _make_conversation("c1", "t1"),  # All good
            _make_conversation("c2", "t1", stages=[
                {"stage": "intent-classifier", "elapsed_ms": 50, "succeeded": False},
            ]),  # Error
        ]
        _, _, tenants = agg.aggregate_conversations(conversations)

        assert tenants["t1"].error_count == 1
        assert tenants["t1"].error_rate == 0.5

    def test_recent_conversations_capped(self):
        """Recent conversations list capped at 20."""
        agg = PipelineMetricsAggregator()
        conversations = [
            _make_conversation(f"c{i}", "t1") for i in range(30)
        ]
        _, _, tenants = agg.aggregate_conversations(conversations)

        assert len(tenants["t1"].recent_conversations) == 20

    def test_conversations_without_trace_skipped(self):
        """Documents without pipeline_trace are skipped."""
        agg = PipelineMetricsAggregator()
        conversations = [
            {"id": "c1", "tenant_id": "t1"},  # No trace
            {"id": "c2", "tenant_id": "t1", "pipeline_trace": None},
            _make_conversation("c3", "t1"),  # Has trace
        ]
        _, _, tenants = agg.aggregate_conversations(conversations)

        assert tenants["t1"].total_conversations == 1


# ---------------------------------------------------------------------------
# Aggregation across time ranges (TEST-2770)
# ---------------------------------------------------------------------------

class TestTimeRangeAggregation:
    """Tests for time-windowed aggregation."""

    def test_aggregate_ignores_time_in_pure_mode(self):
        """Pure aggregate_conversations doesn't filter by time — that's the DB query's job."""
        agg = PipelineMetricsAggregator()
        old_conv = _make_conversation("c1", "t1", ts=1000)
        new_conv = _make_conversation("c2", "t1", ts=int(time.time()))

        agents, _, _ = agg.aggregate_conversations([old_conv, new_conv])
        assert agents["intent-classifier"].invocation_count == 2


# ---------------------------------------------------------------------------
# AgentMetrics property edge cases
# ---------------------------------------------------------------------------

class TestAgentMetricsProperties:
    """Edge case tests for AgentMetrics computed properties."""

    def test_zero_invocations(self):
        am = AgentMetrics(agent="test")
        assert am.avg_latency_ms == 0.0
        assert am.p50_latency_ms == 0.0
        assert am.p95_latency_ms == 0.0
        assert am.p99_latency_ms == 0.0
        assert am.error_rate == 0.0
        assert am.avg_tokens_in == 0.0
        assert am.avg_tokens_out == 0.0
        assert am.avg_cost == 0.0

    def test_single_invocation(self):
        am = AgentMetrics(agent="test", invocation_count=1, latencies=[100.0])
        assert am.avg_latency_ms == 100.0
        assert am.p50_latency_ms == 100.0
        assert am.p95_latency_ms == 100.0


class TestTenantMetricsProperties:
    """Edge case tests for TenantMetrics computed properties."""

    def test_zero_conversations(self):
        tm = TenantMetrics(tenant_id="test")
        assert tm.avg_latency_ms == 0.0
        assert tm.error_rate == 0.0
        assert tm.escalation_rate == 0.0
        assert tm.resolution_rate == 0.0


class TestEdgeMetricsProperties:
    """Edge case tests for EdgeMetrics."""

    def test_zero_volume(self):
        em = EdgeMetrics(source="a", target="b")
        assert em.avg_transition_latency_ms == 0.0
        assert em.drop_off_rate == 0.0
