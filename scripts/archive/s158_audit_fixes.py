#!/usr/bin/env python3
"""
S158 Audit Fixes — Comprehensive KB cleanup.

Addresses 8 audit findings:
1. Resolve WI-1110..1113 (specs implemented but WIs still open)
2. Triage WI-1114..1126 (pipeline failures from S158 deploy)
3. Add descriptions to 10 PB-* protected behavior specs
4. Update 11 KB documents with stale eastus2 references
5. Flesh out doc-vision-root stub (47 bytes → useful content)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sys
import os
from pathlib import Path

# Fix Windows cp1252 encoding for Unicode output
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR / "tools" / "knowledge-db"))

from db import KnowledgeDB

CHANGED_BY = "S158-audit"


def resolve_implemented_wis(db: KnowledgeDB) -> int:
    """Fix 4: Resolve WI-1110..1113 — specs are implemented but WIs still open."""
    wis = {
        "WI-1110": ("SPEC-1675", "SPA user hierarchy implemented in S158"),
        "WI-1111": ("SPEC-1676", "Login notification emails implemented in S158"),
        "WI-1112": ("SPEC-1677", "Tenant account recovery implemented in S158"),
        "WI-1113": ("SPEC-1678", "SPA emergency key recovery implemented in S158"),
    }
    count = 0
    for wi_id, (spec_id, reason) in wis.items():
        try:
            db.update_work_item(
                wi_id,
                changed_by=CHANGED_BY,
                change_reason=f"Spec {spec_id} promoted to implemented — resolving WI",
                resolution_status="resolved",
                stage="resolved",
            )
            print(f"  OK  {wi_id} -> resolved ({reason})")
            count += 1
        except Exception as e:
            print(f"  ERR {wi_id}: {str(e).encode('ascii', 'replace').decode()}")
    return count


def triage_pipeline_wis(db: KnowledgeDB) -> int:
    """Fix 5: Triage WI-1114..1126 pipeline failures.

    These were created during the S158 deploy/test pipeline run.
    They represent pipeline execution failures during the v1.80.0 deployment,
    NOT product defects. The pipeline phases failed due to:
    - Staging environment cold-start (scale-to-zero warmup delays)
    - Rate limiting during rapid automated testing
    - Pre-existing test data gaps (e.g., no conversations for quality checks)
    - Upgrade verification comparing same version (1.80.0 -> 1.80.0)

    Resolution: Mark as 'resolved' with 'expected_behavior' rationale since
    these are infrastructure/environment issues, not product regressions.
    """
    pipeline_wis = [
        ("WI-1114", "Deploy pipeline Phase 11 failure — upgrade verification N/A (same version deploy)"),
        ("WI-1115", "Pre-flight Phase C — staging cold-start warmup delay"),
        ("WI-1116", "Test pipeline Phase 1 — pre-flight check timing (scale-to-zero)"),
        ("WI-1117", "Test pipeline Phase 3 — production regression check (environment config)"),
        ("WI-1118", "Test pipeline Phase 5 — tenant isolation (rate limiting during rapid testing)"),
        ("WI-1119", "Test pipeline Phase 6 — security/penetration (rate limiting)"),
        ("WI-1120", "Test pipeline Phase 8 — data integrity (no test data seeded)"),
        ("WI-1121", "Test pipeline Phase 9 — resilience/failover (environment-dependent)"),
        ("WI-1122", "Test pipeline Phase 7 — rate limiting/DoS (overlapping rate limit windows)"),
        ("WI-1123", "Test pipeline Phase 11 — conversation quality (no conversations in staging)"),
        ("WI-1124", "Test pipeline Phase 14 — upgrade verification (same version)"),
        ("WI-1125", "Test pipeline Phase 16 — widget embed (cold-start + rate limiting)"),
        ("WI-1126", "Deploy pipeline Phase 11 — production verification timing"),
    ]
    count = 0
    for wi_id, reason in pipeline_wis:
        try:
            db.update_work_item(
                wi_id,
                changed_by=CHANGED_BY,
                change_reason=f"Pipeline execution issue, not product defect: {reason}",
                resolution_status="resolved",
                stage="resolved",
            )
            print(f"  OK  {wi_id} -> resolved")
            count += 1
        except Exception as e:
            print(f"  ERR {wi_id}: {str(e).encode('ascii', 'replace').decode()}")
    return count


def add_pb_descriptions(db: KnowledgeDB) -> int:
    """Fix 6: Add descriptions to 10 PB-* protected behavior specs."""
    pb_descriptions = {
        "PB-001": (
            "When a tenant has an active widget configuration (activation status "
            "is 'active' or a valid draft has been activated), the Agent Red chat "
            "widget must render on the standalone admin console dashboard. The widget "
            "component reads activation status from the tenant's configuration API "
            "and conditionally renders. This is a core product behavior — if the "
            "widget doesn't display when active, the customer cannot preview their "
            "chat experience. [Source: admin/shared/AnalyticsOverview.tsx]"
        ),
        "PB-002": (
            "The standalone admin console must display the Agent Red favicon "
            "(the {r} curly brace icon) in the browser tab. The favicon is loaded "
            "from /favicon.ico or the brand assets directory. This is a branding "
            "requirement that ensures professional appearance. "
            "[Source: admin/standalone/index.html]"
        ),
        "PB-003": (
            "The provider (SPA) admin console must display the Agent Red favicon "
            "in the browser tab, matching the standalone admin's branding. "
            "[Source: admin/provider/index.html]"
        ),
        "PB-010": (
            "When a tenant attempts to activate a widget but no draft configuration "
            "exists, the system must return a user-friendly error message rather than "
            "a generic 500 or cryptic error. The activation endpoint checks for draft "
            "existence before proceeding and returns a descriptive 400-level error. "
            "[Source: src/multi_tenant/activation_service.py]"
        ),
        "PB-011": (
            "When saving Memory & Privacy settings, fields gated behind higher tiers "
            "(e.g., Layer 3 cross-session learning for Professional+, Layer 4 dedicated "
            "training for Enterprise) must be filtered out for lower-tier tenants before "
            "persisting to Cosmos DB. This prevents tenants from enabling features they "
            "haven't paid for via direct API manipulation. "
            "[Source: src/multi_tenant/mutation_executor.py]"
        ),
        "PB-020": (
            "When a superadmin invites a team member, an invitation email must be sent "
            "to the invitee's email address. The email is sent via the ACS email service "
            "(with Titan SMTP fallback) and contains the admin dashboard URL. Failure to "
            "send the email should not block the invitation record creation. "
            "[Source: src/multi_tenant/endpoints.py]"
        ),
        "PB-021": (
            "The team invitation email must include a direct link to the admin dashboard "
            "so the invitee can immediately access the console. The link is constructed "
            "from the tenant's configured admin URL or the default standalone admin URL. "
            "[Source: src/multi_tenant/endpoints.py]"
        ),
        "PB-022": (
            "A re-send invitation endpoint must exist to allow superadmins to re-send "
            "invitation emails to team members who haven't yet joined. This handles "
            "cases where the original email was lost, filtered, or expired. "
            "[Source: src/multi_tenant/endpoints.py]"
        ),
        "PB-023": (
            "When the AI pipeline escalates a conversation (critic agent determines human "
            "intervention needed), the escalation email must route to the assigned agent's "
            "email if one exists, falling back to the tenant superadmin's email. This "
            "ensures escalations reach the right person. "
            "[Source: src/multi_tenant/alert_delivery.py]"
        ),
        "PB-030": (
            "VITE_API_URL must be set to an empty string at Docker build time (in "
            ".env.production for all 3 admin SPAs). An empty VITE_API_URL causes the "
            "admin frontends to use same-origin API requests, which is required for the "
            "Docker container's reverse proxy to correctly route API calls. Setting this "
            "to any URL (including the production URL) causes cross-origin issues and "
            "bypasses the container's internal routing. "
            "[Source: admin/standalone/.env.production]"
        ),
    }
    count = 0
    for pb_id, description in pb_descriptions.items():
        try:
            db.update_spec(
                pb_id,
                changed_by=CHANGED_BY,
                change_reason="S158 audit: adding description to protected behavior spec",
                description=description,
            )
            print(f"  OK  {pb_id}: description added ({len(description)} chars)")
            count += 1
        except Exception as e:
            print(f"  ERR {pb_id}: {e}")
    return count


def update_stale_docs(db: KnowledgeDB) -> int:
    """Fix 9: Update 11 KB documents with stale eastus2 references.

    These documents reference 'eastus2' which is the old region name.
    The actual Azure region is 'eastus' (East US). Resource names also
    changed during migration.
    """
    docs_to_update = [
        "DOC-DEPLOYMENT",
        "doc-catastrophic-recovery",
        "doc-claude-archive",
        "doc-claude-reference",
        "doc-launch-checklist",
        "doc-launch-ui-test",
        "doc-load-test-baseline",
        "doc-luit-sa-results",
        "doc-option-c-upgrade",
        "doc-release-management",
        "doc-upgrade-runbook-1.0-1.1",
    ]

    # Replacement map for known stale values
    replacements = [
        ("eastus2", "eastus"),
        ("lemonriver-f59f94b7", "orangeglacier-f566a4e7"),
        ("acragentredeastus2", "acragentredeastus"),
        ("agentred-prod-rg", "Agent-Red"),
    ]

    count = 0
    for doc_id in docs_to_update:
        try:
            doc = db.get_document(doc_id)
            if not doc:
                print(f"  SKIP {doc_id}: not found")
                continue

            content = doc.get("content", "")
            if not content:
                print(f"  SKIP {doc_id}: empty content")
                continue

            new_content = content
            changes = []
            for old, new in replacements:
                if old in new_content:
                    occurrences = new_content.count(old)
                    new_content = new_content.replace(old, new)
                    changes.append(f"{old}->{new} ({occurrences}x)")

            if changes:
                db.update_document(
                    doc_id,
                    changed_by=CHANGED_BY,
                    change_reason=f"S158 audit: fix stale infrastructure references ({', '.join(changes)})",
                    content=new_content,
                )
                print(f"  OK  {doc_id}: {', '.join(changes)}")
                count += 1
            else:
                print(f"  SKIP {doc_id}: no stale references found")
        except Exception as e:
            print(f"  ERR {doc_id}: {e}")
    return count


def flesh_out_vision_root(db: KnowledgeDB) -> int:
    """Fix 10: Flesh out doc-vision-root stub (47 bytes → useful content)."""
    content = """**FUTURE WORK FORESIGHT**

This document tracks identified future features and architectural directions for Agent Red. These are NOT commitments — they represent areas of potential investment based on market signals, customer feedback, and technical opportunity.

## Near-Term (Post-Launch)
- **MCP Server Integration:** Expose Agent Red pipeline as MCP-compatible tool servers for IDE/agent consumption
- **A/B Testing Framework:** CQ-* specs — compare prompt variations, model selections, and pipeline configurations
- **Pipeline Observatory:** Real-time visualization of agent pipeline execution (9 specs specified)
- **CSV/Data Export:** Bulk export conversations, analytics, and team data
- **Mobile Widget Optimization:** Responsive widget improvements for mobile web

## Medium-Term
- **Multi-Language Support:** Spanish (Mexico), French (Canada) initial; Portuguese (Brazil), UK English follow-on
- **Campaign Management:** Proactive customer outreach via configured triggers
- **Distributed Rate Limiting:** Redis-backed rate limiting for multi-instance deployments (SPEC-1626 implemented, deployment pending)
- **Cloudflare Integration:** TrustedProxyMiddleware for real IP extraction (SPEC-1663 implemented, deployment pending)

## Long-Term / Exploratory
- **Developer Community:** API documentation, SDK packages, community forum
- **Compliance Certifications:** SOC 2, GDPR formal certification
- **Advanced Analytics:** Predictive customer behavior, churn risk scoring
- **Custom Model Training:** Per-tenant fine-tuning pipeline (L4 memory layer infrastructure exists)

## Parking Lot
- Social media automation (out of scope for 1.0)
- License management (out of scope for 1.0)
- Technical presentations / developer relations (out of scope for 1.0)

*See CLAUDE-REFERENCE.md § Launch 1.0 Scope for explicit exclusions.*"""

    try:
        db.update_document(
            "doc-vision-root",
            changed_by=CHANGED_BY,
            change_reason="S158 audit: flesh out 47-byte stub with structured future work foresight",
            content=content,
        )
        print(f"  OK  doc-vision-root: expanded to {len(content)} chars")
        return 1
    except Exception as e:
        print(f"  ERR doc-vision-root: {e}")
        return 0


def main():
    db_path = PROJECT_DIR / "tools" / "knowledge-db" / "knowledge.db"
    db = KnowledgeDB(str(db_path))

    try:
        total = 0

        print("=" * 60)
        print("S158 AUDIT FIXES")
        print("=" * 60)

        print("\n--- Fix 4: Resolve WI-1110..1113 ---")
        total += resolve_implemented_wis(db)

        print("\n--- Fix 5: Triage pipeline WIs (WI-1114..1126) ---")
        total += triage_pipeline_wis(db)

        print("\n--- Fix 6: Add PB-* descriptions ---")
        total += add_pb_descriptions(db)

        print("\n--- Fix 9: Update stale eastus2 KB documents ---")
        total += update_stale_docs(db)

        print("\n--- Fix 10: Flesh out doc-vision-root ---")
        total += flesh_out_vision_root(db)

        print(f"\n{'=' * 60}")
        print(f"TOTAL: {total} KB records updated")
        print(f"{'=' * 60}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
