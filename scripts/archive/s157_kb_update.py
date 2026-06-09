"""S157 KB updates — SPEC-1667/1668 implementation + new spec + deployment docs.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "knowledge-db"))

from db import KnowledgeDB

db = KnowledgeDB()

# ── 1. Promote SPEC-1667 and SPEC-1668 to implemented ──

db.update_spec(
    "SPEC-1667",
    changed_by="claude",
    change_reason="S157: Fully implemented — PlatformAdminRepository, ar_spa_ prefix auth, "
    "require_platform_admin() router guard, reverse guard, seed script. "
    "Deployed to production (revision 0000093) and staging. Verified.",
    status="implemented",
    assertions=[
        {
            "type": "grep",
            "pattern": "require_platform_admin",
            "file": "src/multi_tenant/middleware.py",
        }
    ],
)
print("[OK] SPEC-1667 -> implemented")

db.update_spec(
    "SPEC-1668",
    changed_by="claude",
    change_reason="S157: Implemented — router-level require_platform_admin() replaces 55 "
    "per-endpoint require_role(SUPERADMIN) guards. Tenant keys get 403 on "
    "superadmin endpoints. SPA keys get blocked from tenant endpoints.",
    status="implemented",
    assertions=[
        {
            "type": "grep",
            "pattern": "is_platform_admin",
            "file": "src/multi_tenant/auth.py",
        }
    ],
)
print("[OK] SPEC-1668 -> implemented")

# ── 2. Record owner specification: SPA key regeneration ──

db.insert_spec(
    id="SPEC-1669",
    title="SPA Console MUST Allow Platform Admin to Regenerate Their API Key",
    description=(
        "The SPA log-in gate should allow the SPA (the service provider "
        "administrator) to request a new API key.\n\n"
        "**Context:** SPEC-1667 established isolated SPA authentication via "
        "ar_spa_* keys stored in the platform_admins collection. Currently, "
        "key generation requires running seed_platform_admin.py with CLI access. "
        "The SPA console needs a self-service mechanism to rotate keys.\n\n"
        "**Requirements:**\n"
        "1. The SPA console UI MUST provide a mechanism to request a new API key\n"
        "2. Key regeneration MUST invalidate the previous key immediately\n"
        "3. The new key MUST be displayed exactly once and never stored in plaintext\n"
        "4. Key regeneration MUST be auditable (logged with timestamp and admin_id)\n\n"
        "[Source: src/multi_tenant/repositories/platform_admin.py]"
    ),
    status="specified",
    changed_by="owner",
    change_reason="Owner specification: 'The SPA log-in gate should allow the SPA "
    "(me) to request a new API key.' Recorded per GOV-09.",
    priority="medium",
    scope="spa_console",
    section="authentication",
    tags=["spa", "authentication", "key-management", "SPEC-1667"],
)
print("[OK] SPEC-1669 created (SPA key regeneration)")

# ── 3. Create work item for SPEC-1669 ──

db.insert_work_item(
    id="WI-1069",
    title="Implement SPA API key regeneration endpoint + UI",
    origin="new",
    component="spa_console",
    resolution_status="open",
    changed_by="claude",
    change_reason="S157: Created from owner specification SPEC-1669",
    description=(
        "Add POST /api/superadmin/platform-admin/regenerate-key endpoint "
        "that generates a new ar_spa_* key, updates the platform_admins "
        "collection, and returns the new key once. Add corresponding UI "
        "in the SPA console to trigger key regeneration."
    ),
    source_spec_id="SPEC-1669",
    priority="medium",
)
print("[OK] WI-1069 created (SPA key regeneration work item)")

# ── 4. Create test for SPEC-1669 ──

db.insert_test(
    id="TEST-8805",
    title="SPEC-1669: SPA key regeneration replaces previous key",
    spec_id="SPEC-1669",
    test_type="unit",
    expected_outcome="PASS",
    description=(
        "1. Seed a platform admin with initial key K1.\n"
        "2. Call regeneration endpoint with K1.\n"
        "3. Verify response contains new key K2 (ar_spa_* prefix).\n"
        "4. Verify K1 returns 401 on superadmin endpoint.\n"
        "5. Verify K2 returns 200 on superadmin endpoint.\n"
        "6. Verify platform_admins document updated_at is recent."
    ),
    changed_by="claude",
    change_reason="S157: Test for SPEC-1669 (GOV-12: WI triggers test creation)",
)
print("[OK] TEST-8805 created")

# ── 5. Update DOC-141 deployment guide with v1.78.0 ──

db.insert_document(
    id="DOC-141",
    title="Agent Red Production Deployment Guide",
    category="operational",
    status="current",
    content=(
        "## Deployment History\n\n"
        "| Version | Date | ACR | Revision | Notes |\n"
        "|---------|------|-----|----------|-------|\n"
        "| v1.62.0 | 2026-03-01 | ca3n | 0000090 | S125 beta deploy |\n"
        "| v1.77.0 | 2026-03-07 | ca4j | 0000091 | S157 test mode + tenant names |\n"
        "| v1.78.0 | 2026-03-08 | ca4n | 0000093 | S157 SPEC-1667 SPA isolation |\n\n"
        "## Staging Deployment History\n\n"
        "| Version | Date | Revision | Notes |\n"
        "|---------|------|----------|-------|\n"
        "| v1.77.0 | 2026-03-07 | 0000026 | S157 |\n"
        "| v1.78.0 | 2026-03-08 | TBD | S157 SPEC-1667 |\n\n"
        "## SPEC-1667 SPA Authentication\n\n"
        "SPA platform admin credentials seeded in both environments.\n"
        "Production key stored in Key Vault: SPA-PLATFORM-ADMIN-KEY.\n"
        "Staging key: [REDACTED — stored in Key Vault as SPA-PLATFORM-ADMIN-KEY].\n\n"
        "## Known Issues\n\n"
        "- Production Cosmos has no seeded tenant API keys (pre-existing).\n"
        "- Git push blocked by .github/workflows/lint.yml OAuth scope.\n"
        "- azure-cosmos SDK >=4.14 removed enable_cross_partition_query param.\n"
    ),
    changed_by="claude",
    change_reason="S157: v4 — added v1.78.0 deployment, SPEC-1667 SPA auth notes",
)
print("[OK] DOC-141 v4 updated")

# ── 6. Resolve SPEC-1667/1668 work items if they exist ──

for wi_id in ["WI-1066", "WI-1067", "WI-1068"]:
    wi = db.get_work_item(wi_id)
    if wi and wi.get("source_spec_id") in ("SPEC-1667", "SPEC-1668"):
        if wi["resolution_status"] == "open":
            db.update_work_item(
                wi_id,
                changed_by="claude",
                change_reason="S157: SPEC-1667/1668 implemented and deployed",
                resolution_status="resolved",
                stage="resolved",
            )
            print(f"[OK] {wi_id} -> resolved")

print("\nDone.")
