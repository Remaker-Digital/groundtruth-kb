"""S175: Create KB artifacts for 680-tenant scaling proposals."""
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

import sys
sys.path.insert(0, "tools/knowledge-db")
from db import KnowledgeDB

kdb = KnowledgeDB()

# --- 7 Specifications ---

specs = [
    {
        "id": "SPEC-1754",
        "title": "Distributed rate limiting MUST use Redis backend when REDIS_URL is configured",
        "description": (
            "At 680-tenant scale with multiple replicas, in-memory rate limiting is per-process only. "
            "The existing RedisRateLimitBackend (security_hardening.py) and startup hook (lifecycle.py) "
            "MUST be activated by setting REDIS_URL. Additionally, the middleware rate limiter (sharded "
            "_RateLimitShard in middleware.py) currently does NOT use the shared RateLimitBackend. This "
            "MUST be bridged so that: (1) When REDIS_URL is set, the middleware rate limiter delegates to "
            "RedisRateLimitBackend instead of local shards. (2) The pre-auth rate limiter also delegates "
            "to Redis for distributed brute-force tracking. (3) Graceful fallback: if Redis becomes "
            "unavailable, fall back to in-memory silently. Infrastructure: Azure Cache for Redis "
            "(Basic C0 minimum, Standard C1 recommended). Extends SPEC-1626. "
            "[Source: src/multi_tenant/middleware.py, src/multi_tenant/security_hardening.py]"
        ),
        "type": "requirement",
    },
    {
        "id": "SPEC-1755",
        "title": "Container App replica scaling MUST support 680 concurrent tenants",
        "description": (
            "Production Container App MUST be configured for horizontal scaling: "
            "(1) Dockerfile: increase --workers from 1 to 4. "
            "(2) Production: min replicas 2, max replicas 8, scaling rule HTTP concurrent requests > 100. "
            "(3) Staging: min replicas 0, max replicas 3. "
            "(4) Requires distributed rate limiting (SPEC-1754) to be effective. "
            "Peak load: 680 tenants x 500 RPM / 60 = ~5,667 req/sec max. "
            "Realistic sustained: ~567 req/sec (10% active). "
            "[Source: Dockerfile]"
        ),
        "type": "requirement",
    },
    {
        "id": "SPEC-1756",
        "title": "SSE connection manager MUST enforce global connection limit per replica",
        "description": (
            "Add GLOBAL_SSE_MAX_CONNECTIONS constant (default 5000). can_connect() MUST check global "
            "count before per-tenant limit. When global limit reached, return HTTP 503 with Retry-After. "
            "Add global_connection_count property. Configurable via SSE_MAX_CONNECTIONS env var. "
            "At 680 tenants worst case: 680 x 30 (Enterprise) = 20,400 concurrent SSE connections. "
            "[Source: src/chat/sse_manager.py]"
        ),
        "type": "requirement",
    },
    {
        "id": "SPEC-1757",
        "title": "Tenant metadata cache MUST support cross-replica invalidation",
        "description": (
            "Align metadata cache TTL to 300s (currently 120s). When Redis is available (SPEC-1754), "
            "publish tenant invalidation events on channel agentred:cache:invalidate. Each replica "
            "subscribes and evicts matching entries. Without Redis, TTL-based expiry continues. "
            "Admin API tier-change and config-save endpoints MUST publish invalidation events. "
            "Modifies SPEC-1746. "
            "[Source: src/multi_tenant/middleware.py, src/multi_tenant/config/cache.py]"
        ),
        "type": "requirement",
    },
    {
        "id": "SPEC-1758",
        "title": "Pre-auth tracker MUST be bounded to prevent unbounded memory growth",
        "description": (
            "Cap _trackers at MAX_TRACKED_IPS (default 10000). LRU eviction when cap reached. "
            "Cleanup task continues for expired entries. Log warning when cap hit. "
            "Configurable via PRE_AUTH_MAX_TRACKED_IPS env var. "
            "At 680 tenants: potentially 50,000+ unique IPs daily. "
            "[Source: src/multi_tenant/security_hardening.py]"
        ),
        "type": "requirement",
    },
    {
        "id": "SPEC-1759",
        "title": "Per-tenant TOCTOU locks MUST be bounded with LRU eviction",
        "description": (
            "Cap _tenant_qa_locks at MAX_TENANT_LOCKS (default 1000). Use OrderedDict for LRU "
            "tracking. Evicted locks safe to discard. Modifies SPEC-1751. "
            "[Source: src/multi_tenant/admin_quick_action_api.py]"
        ),
        "type": "requirement",
    },
    {
        "id": "SPEC-1760",
        "title": "Health endpoint MUST expose scaling metrics for monitoring",
        "description": (
            "Add GET /health/metrics (platform-admin authenticated). Response: active_sse_connections, "
            "rate_limit_shard_sizes, tenant_meta_cache_size, cache_hit_rate, config_cache_size, "
            "pre_auth_tracker_count, tenant_lock_count, uptime_seconds, event_loop_lag_ms. "
            "Event loop lag via scheduled callback. Cache hit rate via counter. "
            "JSON response, no caching. "
            "[Source: src/multi_tenant/middleware.py, src/chat/sse_manager.py]"
        ),
        "type": "requirement",
    },
]

for s in specs:
    kdb.insert_spec(
        id=s["id"],
        title=s["title"],
        status="specified",
        changed_by="Claude",
        change_reason="S175: 680-tenant scaling assessment proposals",
        description=s["description"],
        type=s["type"],
    )
    print(f"  {s['id']}: {s['title'][:60]}")

print(f"\n{len(specs)} specs created.")

# --- 7 Work Items ---

wis = [
    ("WI-1274", "SPEC-1754", "Activate distributed rate limiting via Redis backend", "new", "infrastructure"),
    ("WI-1275", "SPEC-1755", "Configure Container App replica scaling for 680 tenants", "new", "infrastructure"),
    ("WI-1276", "SPEC-1756", "Add global SSE connection limit per replica", "new", "api"),
    ("WI-1277", "SPEC-1757", "Implement cross-replica cache invalidation via Redis pub/sub", "new", "api"),
    ("WI-1278", "SPEC-1758", "Bound pre-auth tracker dict with LRU eviction", "new", "api"),
    ("WI-1279", "SPEC-1759", "Bound per-tenant TOCTOU locks with LRU eviction", "new", "api"),
    ("WI-1280", "SPEC-1760", "Add /health/metrics endpoint with scaling indicators", "new", "api"),
]

for wi_id, spec_id, title, origin, component in wis:
    kdb.insert_work_item(
        id=wi_id,
        title=title,
        origin=origin,
        component=component,
        resolution_status="open",
        changed_by="Claude",
        change_reason="S175: 680-tenant scaling work items",
        source_spec_id=spec_id,
    )
    print(f"  {wi_id} -> {spec_id}: {title[:50]}")

print(f"\n{len(wis)} work items created.")

# --- Backlog Snapshot ---

backlog_wi_ids = [
    "WI-1274",  # P1: Redis provision + rate limit bridge
    "WI-1275",  # P2: Replica scaling (depends on WI-1274)
    "WI-1276",  # P3: Global SSE cap (independent)
    "WI-1278",  # P4: Pre-auth tracker memory cap (independent)
    "WI-1279",  # P5: Lock cleanup (independent)
    "WI-1277",  # P6: Cache invalidation (depends on WI-1274)
    "WI-1280",  # P7: Health metrics (independent)
]

kdb.insert_backlog_snapshot(
    id="BACKLOG-014",
    title="680-Tenant Horizontal Scaling Readiness",
    work_item_ids=backlog_wi_ids,
    changed_by="Claude",
    change_reason="S175: 680-tenant scaling backlog",
    description=(
        "Priority: infrastructure blockers first (Redis, replicas), then safety caps "
        "(SSE, memory), then cross-replica consistency, then monitoring."
    ),
)
print("\nBACKLOG-014 created with 7 items.")

kdb.close()
print("\nDone.")
