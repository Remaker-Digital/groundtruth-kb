# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Pipeline Metrics Aggregation Engine (SPEC-1584).

Queries conversation documents across all tenants and computes per-agent,
per-edge, and per-tenant aggregate metrics from pipeline_trace data.

Time windowing via since/until/period parameters. Results are cached with
configurable TTL for dashboard responsiveness.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import logging
import statistics
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Period helpers
# ---------------------------------------------------------------------------

PERIOD_SECONDS = {
    "1h": 3600,
    "6h": 6 * 3600,
    "24h": 24 * 3600,
    "7d": 7 * 86400,
    "30d": 30 * 86400,
}


def _period_to_seconds(period: str) -> int:
    """Convert a period string to seconds."""
    return PERIOD_SECONDS.get(period, 86400)


def _cutoff_timestamp(period: str) -> int:
    """Unix timestamp for the start of the given period window."""
    return int(time.time()) - _period_to_seconds(period)


# ---------------------------------------------------------------------------
# Data classes for aggregated results
# ---------------------------------------------------------------------------

@dataclass
class AgentMetrics:
    """Aggregated metrics for a single pipeline agent."""

    agent: str
    invocation_count: int = 0
    latencies: list[float] = field(default_factory=list)
    error_count: int = 0
    tokens_in: list[float] = field(default_factory=list)
    tokens_out: list[float] = field(default_factory=list)
    costs: list[float] = field(default_factory=list)
    # Trend data: list of {timestamp, value} dicts
    latency_trend: list[dict[str, Any]] = field(default_factory=list)
    token_usage_trend: list[dict[str, Any]] = field(default_factory=list)
    cost_trend: list[dict[str, Any]] = field(default_factory=list)
    error_log: list[dict[str, Any]] = field(default_factory=list)

    @property
    def avg_latency_ms(self) -> float:
        return statistics.mean(self.latencies) if self.latencies else 0.0

    @property
    def p50_latency_ms(self) -> float:
        return statistics.median(self.latencies) if self.latencies else 0.0

    @property
    def p95_latency_ms(self) -> float:
        if not self.latencies:
            return 0.0
        sorted_lat = sorted(self.latencies)
        idx = int(len(sorted_lat) * 0.95)
        return sorted_lat[min(idx, len(sorted_lat) - 1)]

    @property
    def p99_latency_ms(self) -> float:
        if not self.latencies:
            return 0.0
        sorted_lat = sorted(self.latencies)
        idx = int(len(sorted_lat) * 0.99)
        return sorted_lat[min(idx, len(sorted_lat) - 1)]

    @property
    def error_rate(self) -> float:
        return self.error_count / self.invocation_count if self.invocation_count else 0.0

    @property
    def avg_tokens_in(self) -> float:
        return statistics.mean(self.tokens_in) if self.tokens_in else 0.0

    @property
    def avg_tokens_out(self) -> float:
        return statistics.mean(self.tokens_out) if self.tokens_out else 0.0

    @property
    def avg_cost(self) -> float:
        return statistics.mean(self.costs) if self.costs else 0.0


@dataclass
class EdgeMetrics:
    """Aggregated metrics for an agent-to-agent transition."""

    source: str
    target: str
    volume: int = 0
    transition_latencies: list[float] = field(default_factory=list)
    drop_offs: int = 0
    total_source_invocations: int = 0

    @property
    def avg_transition_latency_ms(self) -> float:
        return (
            statistics.mean(self.transition_latencies)
            if self.transition_latencies
            else 0.0
        )

    @property
    def drop_off_rate(self) -> float:
        if self.total_source_invocations == 0:
            return 0.0
        return self.drop_offs / self.total_source_invocations


@dataclass
class TenantMetrics:
    """Aggregated pipeline metrics for a single tenant."""

    tenant_id: str
    display_name: str = ""
    tier: str | None = None
    total_conversations: int = 0
    billable_conversations: int = 0
    total_latency_sum: float = 0.0
    error_count: int = 0
    escalation_count: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    estimated_ru: float = 0.0
    resolved_count: int = 0
    # Trend data
    volume_trend: list[dict[str, Any]] = field(default_factory=list)
    cost_trend: list[dict[str, Any]] = field(default_factory=list)
    agent_breakdown: list[dict[str, Any]] = field(default_factory=list)
    intent_distribution: list[dict[str, Any]] = field(default_factory=list)
    recent_conversations: list[dict[str, Any]] = field(default_factory=list)

    @property
    def avg_latency_ms(self) -> float:
        return (
            self.total_latency_sum / self.total_conversations
            if self.total_conversations
            else 0.0
        )

    @property
    def error_rate(self) -> float:
        return (
            self.error_count / self.total_conversations
            if self.total_conversations
            else 0.0
        )

    @property
    def escalation_rate(self) -> float:
        return (
            self.escalation_count / self.total_conversations
            if self.total_conversations
            else 0.0
        )

    @property
    def resolution_rate(self) -> float:
        return (
            self.resolved_count / self.total_conversations
            if self.total_conversations
            else 0.0
        )

    @property
    def avg_conversation_length(self) -> float:
        return 0.0  # Requires message_count data


# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------

@dataclass
class _CacheEntry:
    """Cached aggregation result with TTL."""

    data: Any
    expires_at: float


class _MetricsCache:
    """Simple in-memory TTL cache for aggregated metrics."""

    def __init__(self, ttl_seconds: int = 60):
        self._ttl = ttl_seconds
        self._store: dict[str, _CacheEntry] = {}

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        if time.time() > entry.expires_at:
            del self._store[key]
            return None
        return entry.data

    def set(self, key: str, data: Any) -> None:
        self._store[key] = _CacheEntry(
            data=data,
            expires_at=time.time() + self._ttl,
        )

    def clear(self) -> None:
        self._store.clear()


# ---------------------------------------------------------------------------
# PipelineMetricsAggregator
# ---------------------------------------------------------------------------

# Pipeline agent list and edge topology sourced from registry (SPEC-1852).
# Lazy-loaded on first access to avoid import-time registry initialization.
_pipeline_agents_cache: list[str] | None = None
_pipeline_edges_cache: list[tuple[str, str]] | None = None


def get_pipeline_agents() -> list[str]:
    """Return core pipeline agent IDs from registry (replaces PIPELINE_AGENTS constant)."""
    global _pipeline_agents_cache
    if _pipeline_agents_cache is None:
        from src.agents.plugins.registry import PluginAgentRegistry
        _pipeline_agents_cache = PluginAgentRegistry.get_instance().get_core_agent_ids()
    return _pipeline_agents_cache


def get_pipeline_edges() -> list[tuple[str, str]]:
    """Return pipeline edge topology from registry (replaces PIPELINE_EDGES constant)."""
    global _pipeline_edges_cache
    if _pipeline_edges_cache is None:
        from src.agents.plugins.registry import PluginAgentRegistry
        _pipeline_edges_cache = PluginAgentRegistry.get_instance().get_pipeline_edges()
    return _pipeline_edges_cache

# Estimated RU cost per conversation document read
_ESTIMATED_RU_PER_READ = 3.5
# Estimated cost per 1K tokens (OpenAI GPT-4 ballpark)
_ESTIMATED_COST_PER_1K_TOKENS = 0.03


class PipelineMetricsAggregator:
    """Cross-tenant conversation trace aggregation engine (SPEC-1584).

    Queries Cosmos DB conversation documents with pipeline_trace data
    and computes per-agent, per-edge, and per-tenant metrics.
    """

    def __init__(
        self,
        cosmos_client: Any = None,
        cache_ttl: int = 60,
    ):
        self._cosmos = cosmos_client
        self._cache = _MetricsCache(ttl_seconds=cache_ttl)

    def set_cosmos_client(self, client: Any) -> None:
        """Set or replace the Cosmos client reference."""
        self._cosmos = client

    # -- Core aggregation from raw conversation docs --

    def aggregate_conversations(
        self,
        conversations: list[dict[str, Any]],
    ) -> tuple[
        dict[str, AgentMetrics],
        dict[tuple[str, str], EdgeMetrics],
        dict[str, TenantMetrics],
    ]:
        """Aggregate pipeline metrics from a list of conversation documents.

        Returns (agent_metrics, edge_metrics, tenant_metrics) dicts.
        This is a pure computation — no I/O.
        """
        agents: dict[str, AgentMetrics] = {
            name: AgentMetrics(agent=name) for name in get_pipeline_agents()
        }
        edges: dict[tuple[str, str], EdgeMetrics] = {
            (s, t): EdgeMetrics(source=s, target=t) for s, t in get_pipeline_edges()
        }
        tenants: dict[str, TenantMetrics] = {}

        for conv in conversations:
            tenant_id = conv.get("tenant_id", "unknown")
            trace = conv.get("pipeline_trace")
            if not trace or not isinstance(trace, dict):
                continue

            stages = trace.get("stages", [])
            total_latency = trace.get("total_latency_ms", 0)
            intent = trace.get("intent", "unknown")
            critic_passed = trace.get("critic_passed", True)
            conv_id = conv.get("id", "")
            ts = conv.get("_ts", 0)

            # Tenant aggregation
            if tenant_id not in tenants:
                tenants[tenant_id] = TenantMetrics(tenant_id=tenant_id)
            tm = tenants[tenant_id]
            tm.total_conversations += 1
            tm.total_latency_sum += total_latency

            # Count escalations (intent-based)
            if intent in ("escalation", "human_handoff"):
                tm.escalation_count += 1

            # Count errors (any stage failure)
            has_error = any(
                not s.get("succeeded", True) for s in stages
            )
            if has_error:
                tm.error_count += 1

            # Per-agent metrics from stages
            prev_stage_name = None
            prev_stage_end_ms = 0
            for stage_data in stages:
                stage_name = stage_data.get("stage", "")
                elapsed_ms = stage_data.get("elapsed_ms", 0)
                succeeded = stage_data.get("succeeded", True)

                if stage_name in agents:
                    am = agents[stage_name]
                    am.invocation_count += 1
                    am.latencies.append(elapsed_ms)
                    if not succeeded:
                        am.error_count += 1
                        am.error_log.append({
                            "conversation_id": conv_id,
                            "timestamp": ts,
                            "stage": stage_name,
                            "latency_ms": elapsed_ms,
                        })

                # Edge metrics: transition from prev to current
                if prev_stage_name and stage_name:
                    edge_key = (prev_stage_name, stage_name)
                    if edge_key in edges:
                        em = edges[edge_key]
                        em.volume += 1
                        # Transition latency = gap between stages
                        transition_lat = max(0, elapsed_ms - prev_stage_end_ms)
                        em.transition_latencies.append(transition_lat)

                prev_stage_name = stage_name
                prev_stage_end_ms = elapsed_ms

            # Estimate tokens and cost from total latency (heuristic)
            estimated_tokens = int(total_latency * 0.5)  # Rough heuristic
            tm.total_tokens += estimated_tokens
            tm.total_cost += estimated_tokens * _ESTIMATED_COST_PER_1K_TOKENS / 1000
            tm.estimated_ru += _ESTIMATED_RU_PER_READ

            # Track recent conversations for detail view
            if len(tm.recent_conversations) < 20:
                tm.recent_conversations.append({
                    "conversation_id": conv_id,
                    "timestamp": ts,
                    "intent": intent,
                    "latency_ms": total_latency,
                    "critic_passed": critic_passed,
                    "stages": len(stages),
                })

        # Compute edge drop-off rates
        for (src, _tgt), em in edges.items():
            if src in agents:
                em.total_source_invocations = agents[src].invocation_count

        return agents, edges, tenants

    # -- Cosmos DB query methods --

    async def _query_conversations(
        self,
        period: str = "24h",
        tenant_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Query conversation documents with pipeline_trace from Cosmos DB.

        Cross-partition query when tenant_id is None (all tenants).
        Partition-scoped when tenant_id is specified.
        """
        if self._cosmos is None:
            return []

        cutoff = _cutoff_timestamp(period)
        results: list[dict[str, Any]] = []

        try:
            from src.multi_tenant.cosmos_schema import COLLECTION_CONVERSATIONS

            container = self._cosmos.get_container(COLLECTION_CONVERSATIONS)

            if tenant_id:
                query = (
                    "SELECT c.id, c.tenant_id, c.pipeline_trace, c._ts, "
                    "c.message_count, c.status, c.billing_status "
                    "FROM c WHERE c.pipeline_trace != null "
                    "AND c._ts >= @cutoff AND c.tenant_id = @tid "
                    "ORDER BY c._ts DESC"
                )
                params = [
                    {"name": "@cutoff", "value": cutoff},
                    {"name": "@tid", "value": tenant_id},
                ]
            else:
                query = (
                    "SELECT c.id, c.tenant_id, c.pipeline_trace, c._ts, "
                    "c.message_count, c.status, c.billing_status "
                    "FROM c WHERE c.pipeline_trace != null "
                    "AND c._ts >= @cutoff "
                    "ORDER BY c._ts DESC"
                )
                params = [{"name": "@cutoff", "value": cutoff}]

            async for item in container.query_items(
                query=query,
                parameters=params,
                max_item_count=1000,
            ):
                results.append(item)

        except Exception as exc:
            logger.warning("Pipeline metrics query failed: %s", exc)

        return results

    # -- Public API --

    async def get_topology_metrics(
        self, period: str = "24h"
    ) -> tuple[dict[str, AgentMetrics], dict[tuple[str, str], EdgeMetrics], int]:
        """Get pipeline topology with agent and edge metrics.

        Returns (agent_metrics, edge_metrics, total_conversations).
        """
        cache_key = f"topology:{period}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        conversations = await self._query_conversations(period=period)
        agents, edges, tenants = self.aggregate_conversations(conversations)

        total = sum(t.total_conversations for t in tenants.values())
        result = (agents, edges, total)
        self._cache.set(cache_key, result)
        return result

    async def get_agent_detail(
        self, agent: str, period: str = "24h"
    ) -> AgentMetrics | None:
        """Get detailed metrics for a specific agent."""
        cache_key = f"agent:{agent}:{period}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        conversations = await self._query_conversations(period=period)
        agents, _, _ = self.aggregate_conversations(conversations)
        result = agents.get(agent)
        if result:
            self._cache.set(cache_key, result)
        return result

    async def get_tenant_comparison(
        self, period: str = "24h"
    ) -> dict[str, TenantMetrics]:
        """Get per-tenant pipeline metrics for comparison table."""
        cache_key = f"tenants:{period}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        conversations = await self._query_conversations(period=period)
        _, _, tenants = self.aggregate_conversations(conversations)
        self._cache.set(cache_key, tenants)
        return tenants

    async def get_tenant_detail(
        self, tenant_id: str, period: str = "24h"
    ) -> TenantMetrics | None:
        """Get detailed pipeline metrics for a single tenant."""
        cache_key = f"tenant:{tenant_id}:{period}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        conversations = await self._query_conversations(
            period=period, tenant_id=tenant_id
        )
        _, _, tenants = self.aggregate_conversations(conversations)
        result = tenants.get(tenant_id)
        if result:
            self._cache.set(cache_key, result)
        return result

    async def get_database_metrics(self) -> dict[str, Any]:
        """Get Cosmos DB operational metrics (SPEC-1583).

        Returns document counts, storage estimates, and RU trends
        per collection per tenant.
        """
        cache_key = "database_metrics"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        result: dict[str, Any] = {
            "collections": [],
            "total_documents": 0,
            "estimated_storage_mb": 0.0,
            "per_tenant": [],
            "ru_trend": [],
        }

        if self._cosmos is None:
            return result

        try:
            from src.multi_tenant.cosmos_schema import CollectionConfig

            for cc in CollectionConfig.all_configs():
                try:
                    container = self._cosmos.get_container(cc.name)
                    # Count documents (cross-partition)
                    count = 0
                    async for item in container.query_items(
                        query="SELECT VALUE COUNT(1) FROM c",
                        max_item_count=1,
                    ):
                        count = item
                    result["collections"].append({
                        "name": cc.name,
                        "document_count": count,
                        "partition_key": cc.partition_key,
                    })
                    result["total_documents"] += count
                except Exception as exc:
                    logger.debug("Skipping collection %s: %s", cc.name, exc)
                    result["collections"].append({
                        "name": cc.name,
                        "document_count": 0,
                        "error": str(exc),
                    })

            # Rough storage estimate: ~2KB per document average
            result["estimated_storage_mb"] = (
                result["total_documents"] * 2.0 / 1024
            )

        except Exception as exc:
            logger.warning("Database metrics collection failed: %s", exc)

        self._cache.set(cache_key, result)
        return result


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_aggregator: PipelineMetricsAggregator | None = None


def get_aggregator() -> PipelineMetricsAggregator:
    """Get or create the module-level aggregator singleton."""
    global _aggregator
    if _aggregator is None:
        _aggregator = PipelineMetricsAggregator()
    return _aggregator


def configure_aggregator(
    cosmos_client: Any = None,
    cache_ttl: int = 60,
) -> PipelineMetricsAggregator:
    """Configure the aggregator singleton with a Cosmos client."""
    global _aggregator
    _aggregator = PipelineMetricsAggregator(
        cosmos_client=cosmos_client,
        cache_ttl=cache_ttl,
    )
    return _aggregator
