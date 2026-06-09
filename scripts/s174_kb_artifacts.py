"""S174: Create KB artifacts for 680-tenant scale entitlements improvements.

9 specifications (SPEC-1745..SPEC-1753), 9 work items (WI-1265..WI-1273),
1 backlog snapshot (BL-012).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sqlite3
import json
from datetime import datetime

DB_PATH = "groundtruth.db"


def main():
    conn = sqlite3.connect(DB_PATH)
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    # ─── SPECIFICATIONS ───────────────────────────────────────────

    specs = [
        {
            "id": "SPEC-1745",
            "version": 1,
            "priority": "critical",
            "title": "Sharded Rate Limiting for 680-Tenant Scale",
            "description": (
                "Replace the single asyncio.Lock in RateLimitMiddleware with a sharded locking strategy. "
                "Current architecture serializes ALL tenant rate checks through one lock, creating a throughput "
                "ceiling of ~2,174 RPS. At 680 tenants with 500 RPM each, peak demand is ~5,667 RPS (2.61x oversubscribed).\n\n"
                "Implementation:\n"
                "1. Create ShardedRateLimitBackend wrapper with N shards (default 16)\n"
                "2. Each shard has its own asyncio.Lock + InMemoryRateLimitBackend instance\n"
                "3. Shard selection: hash(tenant_id) % num_shards\n"
                "4. 16 shards = ~42 tenants per shard, reducing contention 16x\n"
                "5. Theoretical ceiling: 16 x 2,174 = ~34,800 RPS (6.1x headroom)\n"
                "6. Maintain RateLimitBackend protocol compatibility\n"
                "7. Redis backend remains unsharded (Redis handles concurrency internally)\n\n"
                "[Source: src/multi_tenant/middleware.py]\n"
                "[Source: src/multi_tenant/rate_limit_backend.py]\n\n"
                "Scale target: SPEC-1516 (680 concurrent merchant tenants). Analysis: S174."
            ),
            "status": "specified",
            "type": "requirement",
            "scope": "backend",
            "section": "rate-limiting",
            "tags": json.dumps(["scale", "performance", "rate-limiting", "680-tenants"]),
            "assertions": json.dumps(
                [{"type": "grep", "file": "src/multi_tenant/rate_limit_backend.py", "pattern": "Shard|shard"}]
            ),
        },
        {
            "id": "SPEC-1746",
            "version": 1,
            "priority": "critical",
            "title": "Fix Trial Tier Level Mapping in require_tier()",
            "description": (
                "Trial tier is mapped to level 0 (same as Starter) in require_tier(). Trial users have "
                "Professional-grade entitlements in TIER_DEFAULTS (5,000 conversations, 3 memory layers, "
                "custom instructions) but are REJECTED by any endpoint gated with require_tier(PROFESSIONAL).\n\n"
                "Current mapping: Trial=0, Starter=0, Professional=1, Enterprise=2\n\n"
                "Fix: Map Trial to level 1 (same as Professional). Trial is explicitly designed as a "
                "Professional evaluation period.\n\n"
                "[Source: src/multi_tenant/middleware.py]\n"
                "[Source: src/multi_tenant/cosmos_schema.py]\n\n"
                "Impact: Trial-to-paid conversion funnel."
            ),
            "status": "specified",
            "type": "requirement",
            "scope": "backend",
            "section": "entitlements",
            "tags": json.dumps(["entitlements", "trial", "tier-mapping", "conversion"]),
            "assertions": json.dumps(
                [{"type": "grep", "file": "src/multi_tenant/middleware.py", "pattern": "TRIAL.*1|trial.*professional"}]
            ),
        },
        {
            "id": "SPEC-1747",
            "version": 1,
            "priority": "critical",
            "title": "Atomic Reservation for Tier Count Limits (TOCTOU Fix)",
            "description": (
                "Replace count-check-then-write pattern with atomic reservation for all tier-limited counts. "
                "Current implementation has TOCTOU race conditions.\n\n"
                "Affected resources:\n"
                "1. Quick actions: max_quick_actions per tier (5/20/50)\n"
                "2. Quick action assignments: max_quick_action_assignments per tier (10/50/200)\n"
                "3. Website crawl sources: count limit per tier\n"
                "4. Concurrent conversations: max_concurrent_conversations per tier (5/10/30)\n\n"
                "Fix: Use Cosmos DB conditional writes with ETags for atomic check-and-increment, "
                "or implement a reservation pattern with rollback.\n\n"
                "[Source: src/multi_tenant/admin_quick_action_api.py]\n"
                "[Source: src/multi_tenant/endpoints.py]\n"
                "[Source: src/multi_tenant/admin_knowledge_api.py]"
            ),
            "status": "specified",
            "type": "requirement",
            "scope": "backend",
            "section": "entitlements",
            "tags": json.dumps(["entitlements", "concurrency", "TOCTOU", "680-tenants"]),
            "assertions": json.dumps(
                [
                    {
                        "type": "grep",
                        "file": "src/multi_tenant/admin_quick_action_api.py",
                        "pattern": "atomic|reservation|etag|If-Match",
                    }
                ]
            ),
        },
        {
            "id": "SPEC-1748",
            "version": 1,
            "priority": "high",
            "title": "Tier Re-validation in ActivationService.activate()",
            "description": (
                "ActivationService.activate() deploys configuration without re-checking the tenant's current tier "
                "against the features being activated. A tenant downgraded mid-session could activate Professional-only "
                "features on a Starter plan.\n\n"
                "Fix: Add _validate_tier_entitlements(config, tenant.tier) check at the start of activate().\n\n"
                "[Source: src/multi_tenant/activation_service.py]"
            ),
            "status": "specified",
            "type": "requirement",
            "scope": "backend",
            "section": "entitlements",
            "tags": json.dumps(["entitlements", "activation", "defense-in-depth"]),
            "assertions": json.dumps(
                [
                    {
                        "type": "grep",
                        "file": "src/multi_tenant/activation_service.py",
                        "pattern": "validate_tier|tier_entitlement|tier_check",
                    }
                ]
            ),
        },
        {
            "id": "SPEC-1749",
            "version": 1,
            "priority": "high",
            "title": "Add Tier Gate to import_knowledge_from_url()",
            "description": (
                "The import_knowledge_from_url() endpoint has NO tier check. A Starter tenant could call the "
                "import endpoint directly to bypass the per-tier crawl source limit.\n\n"
                "Fix: Add require_tier() or explicit count validation to the import handler.\n\n"
                "[Source: src/multi_tenant/admin_knowledge_api.py]"
            ),
            "status": "specified",
            "type": "requirement",
            "scope": "backend",
            "section": "entitlements",
            "tags": json.dumps(["entitlements", "knowledge-base", "tier-gate"]),
            "assertions": json.dumps(
                [
                    {
                        "type": "grep",
                        "file": "src/multi_tenant/admin_knowledge_api.py",
                        "pattern": "require_tier|tier_gate|tier_check.*import",
                    }
                ]
            ),
        },
        {
            "id": "SPEC-1750",
            "version": 1,
            "priority": "high",
            "title": "Null Tier Guard for Admin Endpoints",
            "description": (
                "When ctx.tier is None (missing or corrupt Cosmos document), most admin endpoints silently "
                "proceed with no tier enforcement.\n\n"
                "Fix: Add tier_required() middleware guard that rejects None tier with 403. "
                "Apply to all /api/admin/* endpoints. Exempt widget-facing endpoints.\n\n"
                "[Source: src/multi_tenant/middleware.py]"
            ),
            "status": "specified",
            "type": "requirement",
            "scope": "backend",
            "section": "entitlements",
            "tags": json.dumps(["entitlements", "security", "null-safety"]),
            "assertions": json.dumps(
                [
                    {
                        "type": "grep",
                        "file": "src/multi_tenant/middleware.py",
                        "pattern": "tier.*None|tier_required|null.*tier",
                    }
                ]
            ),
        },
        {
            "id": "SPEC-1751",
            "version": 1,
            "priority": "medium",
            "title": "Extended Cache TTLs for 680-Tenant Scale",
            "description": (
                "Current cache TTLs cause unnecessary Cosmos DB load at 680 tenants:\n\n"
                "1. ConfigProcessor cache: 60s -> 300s (80% reduction in cache miss rate)\n"
                "2. Tenant metadata cache: None -> 120s LRU (1,000 entries, ~95% hit rate)\n"
                "3. Explicit invalidation on write operations\n\n"
                "[Source: src/multi_tenant/activation_service.py]\n"
                "[Source: src/multi_tenant/middleware.py]"
            ),
            "status": "specified",
            "type": "requirement",
            "scope": "backend",
            "section": "performance",
            "tags": json.dumps(["performance", "caching", "cosmos-db", "680-tenants"]),
            "assertions": json.dumps(
                [
                    {
                        "type": "grep",
                        "file": "src/multi_tenant/activation_service.py",
                        "pattern": "300|cache_ttl|lru_cache",
                    }
                ]
            ),
        },
        {
            "id": "SPEC-1752",
            "version": 1,
            "priority": "medium",
            "title": "Per-Tier Caps for KB Articles and Escalation Categories",
            "description": (
                "Three features have no per-tier caps:\n\n"
                "1. KB articles: Starter 50, Professional 200, Enterprise 1,000\n"
                "2. Escalation categories per member: Starter 3, Professional 10, Enterprise 25\n"
                "3. Team members: Starter 5, Professional 20, Enterprise 100\n\n"
                "Add caps to TIER_DEFAULTS and enforce in API handlers.\n\n"
                "[Source: src/multi_tenant/cosmos_schema.py]\n"
                "[Source: src/multi_tenant/admin_knowledge_api.py]"
            ),
            "status": "specified",
            "type": "requirement",
            "scope": "backend",
            "section": "entitlements",
            "tags": json.dumps(["entitlements", "tier-caps", "knowledge-base"]),
            "assertions": json.dumps(
                [
                    {
                        "type": "grep",
                        "file": "src/multi_tenant/cosmos_schema.py",
                        "pattern": "max_kb_articles|max_escalation_categories|max_team_members",
                    }
                ]
            ),
        },
        {
            "id": "SPEC-1753",
            "version": 1,
            "priority": "medium",
            "title": "Enforce History Depth at API Boundary",
            "description": (
                "Conversation history filtering happens only in DataRetentionService (daily sweep). "
                "The API endpoints return conversations beyond tier retention during the sweep window.\n\n"
                "Fix: Add history_depth_days filter to conversation list/detail API queries.\n\n"
                "[Source: src/multi_tenant/admin_inbox_api.py]\n"
                "[Source: src/multi_tenant/cosmos_schema.py]"
            ),
            "status": "specified",
            "type": "requirement",
            "scope": "backend",
            "section": "entitlements",
            "tags": json.dumps(["entitlements", "history", "data-retention", "defense-in-depth"]),
            "assertions": json.dumps(
                [
                    {
                        "type": "grep",
                        "file": "src/multi_tenant/admin_inbox_api.py",
                        "pattern": "history_retention|retention_days|date_filter",
                    }
                ]
            ),
        },
    ]

    for s in specs:
        conn.execute(
            """INSERT INTO specifications
            (id, version, title, description, status, type, changed_by, changed_at,
             change_reason, priority, scope, section, handle, tags, assertions)
            VALUES (?, ?, ?, ?, ?, ?, 'claude', ?,
             'S174: 680-tenant scale entitlements improvements', ?, ?, ?, NULL, ?, ?)""",
            (
                s["id"],
                s["version"],
                s["title"],
                s["description"],
                s["status"],
                s["type"],
                now,
                s["priority"],
                s["scope"],
                s["section"],
                s["tags"],
                s["assertions"],
            ),
        )
    print(f"Inserted {len(specs)} specifications (SPEC-1745..SPEC-1753)")

    # ─── WORK ITEMS ───────────────────────────────────────────────

    work_items = [
        (
            "WI-1265",
            "SPEC-1745",
            "Implement sharded rate limiting backend",
            "Replace single asyncio.Lock with 16-shard locking. Critical: 2.61x oversubscribed at 680 tenants.",
            "new",
            "rate-limiting",
            "critical",
        ),
        (
            "WI-1266",
            "SPEC-1746",
            "Fix Trial tier level mapping to Professional equivalent",
            "Map Trial to tier level 1 (Professional) in require_tier().",
            "defect",
            "entitlements",
            "critical",
        ),
        (
            "WI-1267",
            "SPEC-1747",
            "Implement atomic reservation for tier count limits",
            "Replace count-check-then-write with ETag-based atomic reservation.",
            "defect",
            "entitlements",
            "critical",
        ),
        (
            "WI-1268",
            "SPEC-1748",
            "Add tier re-validation to ActivationService.activate()",
            "Validate tenant tier against activated features before deployment.",
            "new",
            "activation",
            "high",
        ),
        (
            "WI-1269",
            "SPEC-1749",
            "Add tier gate to import_knowledge_from_url()",
            "Gate knowledge import endpoint with tier check.",
            "defect",
            "knowledge-base",
            "high",
        ),
        (
            "WI-1270",
            "SPEC-1750",
            "Add null tier guard to admin endpoints",
            "Reject requests with None tier at middleware level.",
            "new",
            "middleware",
            "high",
        ),
        (
            "WI-1271",
            "SPEC-1751",
            "Extend cache TTLs for 680-tenant scale",
            "ConfigProcessor 60s->300s, add 120s LRU tenant metadata cache.",
            "new",
            "performance",
            "medium",
        ),
        (
            "WI-1272",
            "SPEC-1752",
            "Add per-tier caps for KB articles, categories, team members",
            "Add max_kb_articles, max_escalation_categories, max_team_members to TIER_DEFAULTS.",
            "new",
            "entitlements",
            "medium",
        ),
        (
            "WI-1273",
            "SPEC-1753",
            "Enforce history retention at API boundary",
            "Add tier-based date filter to conversation list/detail endpoints.",
            "new",
            "entitlements",
            "medium",
        ),
    ]

    for wi_id, spec_id, title, desc, origin, component, priority in work_items:
        conn.execute(
            """INSERT INTO work_items
            (id, version, title, description, origin, component, source_spec_id,
             resolution_status, priority, changed_by, changed_at, change_reason, stage)
            VALUES (?, 1, ?, ?, ?, ?, ?, 'open', ?, 'claude', ?, 'S174: 680-tenant scale improvements', 'created')""",
            (wi_id, title, desc, origin, component, spec_id, priority, now),
        )
    print(f"Inserted {len(work_items)} work items (WI-1265..WI-1273)")

    # ─── BACKLOG SNAPSHOT ─────────────────────────────────────────

    backlog_items = [
        {"wi_id": "WI-1265", "position": 1, "notes": "CRITICAL: Single lock 2.61x oversubscribed at 680 tenants"},
        {"wi_id": "WI-1266", "position": 2, "notes": "CRITICAL: Trial conversion blocked"},
        {"wi_id": "WI-1267", "position": 3, "notes": "CRITICAL: TOCTOU races at concurrent scale"},
        {"wi_id": "WI-1270", "position": 4, "notes": "HIGH: Defensive null guard, low effort"},
        {"wi_id": "WI-1269", "position": 5, "notes": "HIGH: Knowledge import tier bypass"},
        {"wi_id": "WI-1268", "position": 6, "notes": "HIGH: Defense-in-depth for activation"},
        {"wi_id": "WI-1271", "position": 7, "notes": "MEDIUM: 80% Cosmos read reduction"},
        {"wi_id": "WI-1272", "position": 8, "notes": "MEDIUM: Uncapped resource creation"},
        {"wi_id": "WI-1273", "position": 9, "notes": "MEDIUM: History visibility gap"},
    ]

    wi_ids = [b["wi_id"] for b in backlog_items]
    by_origin = json.dumps({"new": 6, "defect": 3})
    by_component = json.dumps(
        {
            "rate-limiting": 1,
            "entitlements": 5,
            "activation": 1,
            "middleware": 1,
            "performance": 1,
            "knowledge-base": 1,
        }
    )
    conn.execute(
        """INSERT INTO backlog_snapshots
        (id, version, title, description, snapshot_at, work_item_ids,
         summary_by_origin, summary_by_component, changed_by, changed_at, change_reason)
        VALUES ('BL-012', 1, '680-Tenant Scale Entitlements Improvements',
        'S174: Rate limiting, tier mapping, TOCTOU, caching, and enforcement gaps for SPEC-1516 scale.',
        ?, ?, ?, ?, 'claude', ?, 'S174: 680-tenant scale improvements')""",
        (now, json.dumps(wi_ids), by_origin, by_component, now),
    )
    print("Inserted backlog BL-012")

    conn.commit()
    conn.close()
    print("\nAll KB artifacts created successfully.")


if __name__ == "__main__":
    main()
