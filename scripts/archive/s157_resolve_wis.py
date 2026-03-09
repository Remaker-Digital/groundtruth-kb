"""S157 — Resolve remaining SPEC-1667 work items.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "knowledge-db"))

from db import KnowledgeDB

db = KnowledgeDB()

# -- WI-1065: platform_admins collection created --

db.update_work_item(
    "WI-1065",
    changed_by="claude",
    change_reason="S157: platform_admins collection created in both production and staging "
    "Cosmos databases. Collection config added to cosmos_schema.py (partition key "
    "/admin_id, unique key /email). Container auto-created at startup or via "
    "seed_platform_admin.py. SPA credentials seeded in both environments. "
    "Owner approved.",
    resolution_status="resolved",
    stage="resolved",
    owner_approved=True,
)
print("[OK] WI-1065 -> resolved")

# -- WI-1066: SPA auth refactored --

db.update_work_item(
    "WI-1066",
    changed_by="claude",
    change_reason="S157: Fully implemented -- PlatformAdminRepository, ar_spa_ prefix auth, "
    "require_platform_admin() router guard, reverse guard, SPA key dispatch in "
    "middleware. Deployed to production (revision 0000093) and staging. "
    "Verified: SPA key->superadmin 200, tenant key->superadmin 403. "
    "Owner approved.",
    resolution_status="resolved",
    stage="resolved",
    owner_approved=True,
)
print("[OK] WI-1066 -> resolved")

# -- WI-1067: auto_provision_superadmin -- wont_fix --
# This WI was based on a misunderstanding. auto_provision_superadmin() creates
# the TENANT's internal superadmin (highest tenant role), NOT the SPA identity.
# The plan's Key Design Decision #5 explicitly stated: "auto_provision_superadmin()
# unchanged -- it creates the tenant's internal superadmin, not the SPA identity."
# The tenant still needs its own superadmin for merchant dashboard access.
# The SPA and tenant superadmin are completely separate identities.

db.update_work_item(
    "WI-1067",
    changed_by="claude",
    change_reason="S157: wont_fix -- auto_provision_superadmin() creates the TENANT's "
    "internal superadmin (highest tenant role), not the SPA identity. The plan's "
    "Key Design Decision #5 explicitly kept this function unchanged. Tenants still "
    "need their own superadmin for merchant dashboard access. The SPA and tenant "
    "superadmin are completely separate, unrelated identities per SPEC-1667. "
    "Owner approved.",
    resolution_status="wont_fix",
    stage="resolved",
    owner_approved=True,
)
print("[OK] WI-1067 -> wont_fix")

# -- Verify no open WIs remain --
remaining = db.list_work_items(resolution_status="open")
print(f"\nOpen work items remaining: {len(remaining)}")
for wi in remaining:
    print(f"  {wi['id']}: {wi['title']}")

print("\nDone.")
