"""S157 KB updates — SPEC-1669 implementation + test artifacts.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "knowledge-db"))

from db import KnowledgeDB

db = KnowledgeDB()

# -- 1. Promote SPEC-1669 to implemented --

db.update_spec(
    "SPEC-1669",
    changed_by="claude",
    change_reason="S157: Implemented -- POST /api/superadmin/platform-admin/regenerate-key "
    "endpoint, PlatformAdminRepository.update_api_key_hash(), "
    "TenantContext platform_admin_id/email fields, audit logging. "
    "14 tests all PASS.",
    status="implemented",
    assertions=[{
        "type": "grep",
        "pattern": "regenerate_platform_admin_key",
        "file": "src/multi_tenant/superadmin_api.py",
    }],
)
print("[OK] SPEC-1669 -> implemented")

# -- 2. Resolve WI-1069 --

db.update_work_item(
    "WI-1069",
    changed_by="claude",
    change_reason="S157: SPEC-1669 implemented -- endpoint, repository, context fields, "
    "audit logging, 14 tests all PASS.",
    resolution_status="resolved",
    stage="resolved",
)
print("[OK] WI-1069 -> resolved")

# -- 3. Record test artifacts for the 14 new tests --

test_data = [
    ("TEST-8806", "SPEC-1669: Returns new ar_spa_* key on regeneration",
     "TestRegenerateKeyHappyPath", "test_returns_new_key"),
    ("TEST-8807", "SPEC-1669: Key hash updated in repository",
     "TestRegenerateKeyHappyPath", "test_key_hash_updated_in_repo"),
    ("TEST-8808", "SPEC-1669: Key format follows ar_spa_plat_{random}",
     "TestRegenerateKeyHappyPath", "test_key_format_correct"),
    ("TEST-8809", "SPEC-1669: Regenerated_at is valid ISO 8601 timestamp",
     "TestRegenerateKeyHappyPath", "test_regenerated_at_is_iso_timestamp"),
    ("TEST-8810", "SPEC-1669: Response warns key displayed once only",
     "TestRegenerateKeyHappyPath", "test_response_message_warns_about_single_display"),
    ("TEST-8811", "SPEC-1669: Audit SECURITY_EVENT logged on regeneration",
     "TestRegenerateKeyAudit", "test_audit_event_logged"),
    ("TEST-8812", "SPEC-1669: Audit failure does not block key regeneration",
     "TestRegenerateKeyAudit", "test_audit_failure_does_not_block_regeneration"),
    ("TEST-8813", "SPEC-1669: 503 when platform admin repo not initialized",
     "TestRegenerateKeyErrors", "test_repo_not_initialized_returns_503"),
    ("TEST-8814", "SPEC-1669: 500 when admin identity missing from context",
     "TestRegenerateKeyErrors", "test_missing_admin_id_returns_500"),
    ("TEST-8815", "SPEC-1669: 500 when Cosmos DB update fails",
     "TestRegenerateKeyErrors", "test_repo_update_failure_returns_500"),
    ("TEST-8816", "SPEC-1669: PlatformAdminRepository has update_api_key_hash",
     "TestUpdateApiKeyHash", "test_repository_has_update_method"),
    ("TEST-8817", "SPEC-1669: TenantContext has platform_admin_id field",
     "TestTenantContextPlatformAdminFields", "test_context_has_platform_admin_id"),
    ("TEST-8818", "SPEC-1669: TenantContext has platform_admin_email field",
     "TestTenantContextPlatformAdminFields", "test_context_has_platform_admin_email"),
    ("TEST-8819", "SPEC-1669: Platform admin fields default to None",
     "TestTenantContextPlatformAdminFields", "test_context_defaults_none"),
]

TEST_FILE = "tests/multi_tenant/test_superadmin_key_regeneration.py"

for test_id, title, test_class, test_function in test_data:
    db.insert_test(
        id=test_id,
        title=title,
        spec_id="SPEC-1669",
        test_type="unit",
        expected_outcome="PASS",
        test_file=TEST_FILE,
        test_class=test_class,
        test_function=test_function,
        description=title,
        last_result="PASS",
        changed_by="claude",
        change_reason="S157: Test for SPEC-1669 key regeneration implementation",
    )
    print(f"[OK] {test_id} created")

print("\nDone.")
