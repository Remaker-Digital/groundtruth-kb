"""S182: Record KB artifacts for WI-1107 self-provisioning refactoring.

Creates 1 spec (SPEC-1798), resolves WI-1107,
and records 26 test artifacts (TEST-10371..10396).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sys
sys.path.insert(0, "tools/knowledge-db")
import db

kdb = db.KnowledgeDB()

# ---------------------------------------------------------------------------
# Specification
# ---------------------------------------------------------------------------

kdb.insert_spec(
    id="SPEC-1798",
    title="Test provisioning endpoint returns keys in non-production (WI-1107)",
    description=(
        "POST /api/superadmin/test/provision-tenant creates a tenant and returns raw "
        "user_api_key and widget_key in the response. Blocked in production (returns 403). "
        "Available in staging/development. Uses same spa_provision_tenant() orchestrator "
        "as regular provisioning but wraps the result in TestProvisionResponse which "
        "includes key fields. Enables SPEC-1673 compliance — test automation self-provisions "
        "ephemeral tenants via SPA key instead of provider holding persistent tenant keys.\n"
        "Scripts refactored: test_pipeline.py (--self-provision flag, _self_provision_tenants, "
        "_cleanup_provisioned_tenants), seed_midflight.py (--self-provision flag, run_seed "
        "self_provision param). Shared helper: scripts/_self_provision.py.\n"
        "[Source: src/multi_tenant/superadmin_api/_tenants.py]"
    ),
    status="implemented",
    type="requirement",
    changed_by="claude",
    change_reason="S182: WI-1107 self-provisioning refactoring",
)
print("  Created SPEC-1798")

# ---------------------------------------------------------------------------
# Resolve WI-1107
# ---------------------------------------------------------------------------

kdb.insert_work_item(
    id="WI-1107",
    title="Refactor test_pipeline.py and seed_midflight.py to not require provider-held tenant keys",
    source_spec_id="SPEC-1798",
    resolution_status="resolved",
    origin="new",
    component="pipeline",
    changed_by="claude",
    change_reason="S182: Implemented self-provisioning via POST /api/superadmin/test/provision-tenant",
)
print("  Resolved WI-1107")

# ---------------------------------------------------------------------------
# Test Artifacts
# ---------------------------------------------------------------------------

test_file = "tests/integration/test_self_provisioning.py"
test_id_start = 10371

tests = [
    # TestProvisionEndpointExists (4 tests)
    ("test_endpoint_registered", "SPEC-1798", "Test provisioning endpoint registered"),
    ("test_endpoint_method_is_post", "SPEC-1798", "Test provisioning endpoint is POST"),
    ("test_response_model_has_key_fields", "SPEC-1798", "TestProvisionResponse has key fields"),
    ("test_response_model_keys_are_optional", "SPEC-1798", "TestProvisionResponse keys are optional"),
    # TestProductionGate (3 tests)
    ("test_production_returns_403", "SPEC-1798", "Production environment returns 403"),
    ("test_staging_does_not_return_403", "SPEC-1798", "Staging environment does not return 403"),
    ("test_development_does_not_return_403", "SPEC-1798", "Development environment does not return 403"),
    # TestProvisionedTenantModel (2 tests)
    ("test_dataclass_fields", "SPEC-1798", "ProvisionedTenant dataclass has required fields"),
    ("test_warnings_default_empty", "SPEC-1798", "ProvisionedTenant warnings default empty"),
    # TestProvisionTestTenant (5 tests)
    ("test_raises_on_403", "SPEC-1798", "provision_test_tenant raises on 403"),
    ("test_raises_on_non_201", "SPEC-1798", "provision_test_tenant raises on non-201"),
    ("test_raises_on_missing_key", "SPEC-1798", "provision_test_tenant raises on missing key"),
    ("test_success_returns_provisioned_tenant", "SPEC-1798", "provision_test_tenant returns keys on success"),
    ("test_auto_generates_email_and_name", "SPEC-1798", "provision_test_tenant auto-generates email"),
    # TestCleanupTestTenant (3 tests)
    ("test_cleanup_returns_true_on_success", "SPEC-1798", "cleanup_test_tenant returns True on success"),
    ("test_cleanup_returns_false_on_failure", "SPEC-1798", "cleanup_test_tenant returns False on failure"),
    ("test_cleanup_returns_false_on_exception", "SPEC-1798", "cleanup_test_tenant returns False on exception"),
    # TestPipelineSelfProvisionFlag (3 tests)
    ("test_argparser_accepts_self_provision", "SPEC-1798", "Pipeline has --self-provision flag"),
    ("test_self_provision_function_exists", "SPEC-1798", "Pipeline has _self_provision_tenants function"),
    ("test_cleanup_function_exists", "SPEC-1798", "Pipeline has _cleanup_provisioned_tenants function"),
    # TestSeedMidflightSelfProvision (2 tests)
    ("test_run_seed_accepts_self_provision", "SPEC-1798", "run_seed accepts self_provision param"),
    ("test_main_function_has_self_provision_arg", "SPEC-1798", "seed_midflight has --self-provision flag"),
    # TestSpec1673Compliance (4 tests)
    ("test_regular_create_tenant_has_no_key_fields", "SPEC-1798", "CreateTenantResponse has no key fields"),
    ("test_test_provision_has_key_fields", "SPEC-1798", "TestProvisionResponse has key fields"),
    ("test_endpoints_are_separate", "SPEC-1798", "Regular and test endpoints are separate"),
    ("test_helper_module_sends_to_test_endpoint", "SPEC-1798", "Helper uses /test/provision-tenant path"),
]

for i, (test_func, spec_id, title) in enumerate(tests):
    test_id = f"TEST-{test_id_start + i}"
    kdb.insert_test(
        id=test_id,
        title=title,
        spec_id=spec_id,
        test_type="behavioral",
        expected_outcome="pass",
        test_file=test_file,
        test_function=test_func,
        changed_by="claude",
        change_reason="S182: WI-1107 self-provisioning tests",
    )

print(f"  Created {len(tests)} test artifacts (TEST-{test_id_start}..TEST-{test_id_start + len(tests) - 1})")

kdb.close()
print("\nDone. 1 spec, 1 WI resolved, 26 test artifacts recorded.")
