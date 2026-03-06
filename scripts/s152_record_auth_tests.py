"""S152 — Record AUTH spec verification test artifacts in KB.

Creates test artifacts, test coverage mappings, and promotes spec statuses
for the 15 AUTH specs verified by real tests.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "knowledge-db"))
from db import KnowledgeDB

TEST_FILE = "tests/multi_tenant/test_auth_spec_verification.py"
SESSION = "S152"
CHANGED_BY = f"claude-{SESSION}"
START_TEST_ID = 7887  # Next available after TEST-7886

# Each entry: (spec_id, test_class, test_functions, title_summary, expected_outcome)
TESTS = [
    ("SPEC-0306", "TestSpec0306TrialExpiryMiddleware", [
        "test_check_trial_expiry_exists_in_middleware",
        "test_trial_expiry_passes_for_non_trial_tier",
        "test_trial_expiry_passes_for_future_expiry",
        "test_trial_expiry_blocks_expired_trial",
        "test_trial_expiry_passes_when_no_expiry_set",
    ], "Trial expiry enforced at middleware level", "Expired trials raise AuthenticationError, non-trial and valid-trial pass"),

    ("SPEC-0362", "TestSpec0362AdminFullAccess", [
        "test_admin_role_exists_in_enum",
        "test_admin_role_different_from_viewer",
        "test_admin_role_in_protected_check",
    ], "Admin role grants full access to configuration features", "ADMIN exists in TeamMemberRole enum and is in _ADMIN_ROLES set"),

    ("SPEC-0364", "TestSpec0364PerUserApiKeys", [
        "test_api_key_resolves_to_team_member",
        "test_tenant_context_has_team_member_fields",
    ], "Per-user API keys resolve to team member identity", "TenantContext carries team_member_id, team_member_email, team_member_role"),

    ("SPEC-0423", "TestSpec0423TwoFactorMethods", [
        "test_totp_verify_endpoint_exists",
        "test_sms_verify_endpoint_exists",
        "test_sms_request_endpoint_exists",
        "test_totp_backup_verify_endpoint_exists",
    ], "Multiple 2FA methods (TOTP, SMS, backup codes)", "MFA router has endpoints for TOTP, SMS, and backup code verification"),

    ("SPEC-0428", "TestSpec0428SuperadminMfaOptOut", [
        "test_requires_2fa_true_for_admin_with_mfa",
        "test_requires_2fa_false_with_opt_out",
        "test_requires_2fa_false_for_non_admin",
        "test_requires_2fa_false_when_mfa_not_enrolled",
    ], "Superadmin MFA opt-out", "requires_2fa returns False when mfa_opt_out flag is set"),

    ("SPEC-0429", "TestSpec0429MagicLinkThenTwoFa", [
        "test_admin_with_mfa_gets_pending_2fa_token",
        "test_non_admin_gets_direct_session",
    ], "Magic link verify triggers 2FA for admin with MFA", "Admin+MFA gets pending_2fa_token; non-admin gets direct session"),

    ("SPEC-0607", "TestSpec0607ApiKeyRegeneration", [
        "test_rotation_router_has_rotate_endpoint",
        "test_apikey_api_has_rotate_endpoint",
        "test_reset_via_email_endpoint_exists",
    ], "API key rotation and regeneration endpoints", "rotation_router and admin_apikey_api have rotate/reset endpoints"),

    ("SPEC-0758", "TestSpec0758SuperadminProtection", [
        "test_superadmin_role_exists",
        "test_superadmin_in_protected_roles",
        "test_protected_roles_is_a_set",
    ], "Superadmin protection from deletion/demotion", "SUPERADMIN in TeamMemberRole; 'superadmin' in PROTECTED_ROLES set"),

    ("SPEC-0868", "TestSpec0868TwoLayerAuth", [
        "test_middleware_accepts_api_key_header",
        "test_middleware_accepts_user_api_key",
        "test_tenant_context_supports_multiple_auth_methods",
    ], "Two-layer authentication (tenant + user)", "TenantContext supports api_key, user_api_key, shopify_session, widget_key auth methods"),

    ("SPEC-1618", "TestSpec1618SingleTenantEmail", [
        "test_single_member_gets_one_email",
        "test_multiple_members_get_separate_emails",
    ], "Single-tenant magic link emails (no combined multi-tenant)", "Each tenant_id+member gets separate email; no multi-tenant batching"),

    ("SPEC-1633", "TestSpec1633TenantScopedRequest", [
        "test_request_model_requires_tenant",
        "test_request_model_accepts_tenant",
        "test_lookup_uses_tenant_scoped_query",
    ], "Magic link request is tenant-scoped", "MagicLinkRequest requires tenant field; lookup calls find_by_email with tenant_id"),

    ("SPEC-1634", "TestSpec1634NoCrossTenantLookups", [
        "test_magic_link_does_not_call_find_all_by_email",
    ], "No cross-tenant email lookups", "find_all_by_email is never called in magic link flow"),

    ("SPEC-1635", "TestSpec1635NoOtherTenancyReferences", [
        "test_email_template_has_single_sign_in_link",
        "test_email_template_uses_single_magic_link_url",
    ], "Email contains no other-tenancy references", "Email template has exactly 1 link and 1 magic_link_url placeholder"),

    ("SPEC-1642", "TestSpec1642OneAdminUrl", [
        "test_url_includes_tenant_param",
        "test_url_is_deterministic",
    ], "One admin URL with tenant parameter", "Magic link URL includes ?tenant= and is deterministic"),

    ("SPEC-1644", "TestSpec1644UrlIdentifiesTenant", [
        "test_magic_link_request_requires_tenant_from_url",
        "test_magic_link_request_tenant_description_references_spec",
    ], "URL identifies tenant (SPEC-1644)", "MagicLinkRequest tenant field description references SPEC-1644"),
]

# Bonus class — not tied to a single spec, but adds coverage to MFA brute force
MFA_BRUTE_FORCE = ("SPEC-0423", "TestMfaBruteForceProtection", [
    "test_brute_force_limit_is_5",
    "test_check_brute_force_allows_under_limit",
    "test_check_brute_force_blocks_at_limit",
    "test_record_failed_attempt_increments",
    "test_clear_attempts_resets",
], "MFA brute force protection (5 attempt limit)", "_MAX_FAILED_ATTEMPTS=5, brute-force check/record/clear functions work correctly")


def main():
    db = KnowledgeDB()
    try:
        test_id_counter = START_TEST_ID
        all_coverage = []

        # --- Record test artifacts ---
        for spec_id, test_class, test_functions, title, expected_outcome in TESTS:
            for func_name in test_functions:
                test_id = f"TEST-{test_id_counter:04d}"
                db.insert_test(
                    id=test_id,
                    title=f"{spec_id}: {title} — {func_name}",
                    spec_id=spec_id,
                    test_type="multi_tenant",
                    expected_outcome=expected_outcome,
                    changed_by=CHANGED_BY,
                    change_reason=f"{SESSION}: Real test verifying {spec_id} against implementation",
                    test_file=TEST_FILE,
                    test_class=test_class,
                    test_function=func_name,
                    last_result="PASS",
                    last_executed_at="2026-03-06T00:00:00Z",
                )
                all_coverage.append({
                    "spec_id": spec_id,
                    "test_file": TEST_FILE,
                    "test_class": test_class,
                    "test_function": func_name,
                    "confidence": "high",
                    "match_reason": f"{SESSION}: Direct spec-to-test mapping via test class name",
                })
                test_id_counter += 1

        # MFA brute force tests (linked to SPEC-0423 since 2FA methods)
        spec_id, test_class, test_functions, title, expected_outcome = MFA_BRUTE_FORCE
        for func_name in test_functions:
            test_id = f"TEST-{test_id_counter:04d}"
            db.insert_test(
                id=test_id,
                title=f"{spec_id}: {title} — {func_name}",
                spec_id=spec_id,
                test_type="multi_tenant",
                expected_outcome=expected_outcome,
                changed_by=CHANGED_BY,
                change_reason=f"{SESSION}: Real test verifying MFA brute force protection",
                test_file=TEST_FILE,
                test_class=test_class,
                test_function=func_name,
                last_result="PASS",
                last_executed_at="2026-03-06T00:00:00Z",
            )
            all_coverage.append({
                "spec_id": spec_id,
                "test_file": TEST_FILE,
                "test_class": test_class,
                "test_function": func_name,
                "confidence": "high",
                "match_reason": f"{SESSION}: MFA brute force protection test — extends SPEC-0423 2FA coverage",
            })
            test_id_counter += 1

        print(f"Created {test_id_counter - START_TEST_ID} test artifacts (TEST-{START_TEST_ID:04d}..TEST-{test_id_counter-1:04d})")

        # --- Record test coverage mappings ---
        count = db.insert_test_coverage_batch(all_coverage, created_by=CHANGED_BY)
        print(f"Recorded {count} test coverage mappings")

        # --- Promote spec statuses to 'implemented' ---
        spec_ids = list(set(s[0] for s in TESTS))
        promoted = 0
        for spec_id in sorted(spec_ids):
            spec = db.get_spec(spec_id)
            if spec and spec["status"] == "specified":
                db.insert_spec(
                    id=spec_id,
                    title=spec["title"],
                    status="implemented",
                    changed_by=CHANGED_BY,
                    change_reason=f"{SESSION}: Promoted to implemented — real tests verify implementation against spec requirements (46 tests PASS in test_auth_spec_verification.py)",
                    description=spec.get("description"),
                    priority=spec.get("priority"),
                    scope=spec.get("scope"),
                    section=spec.get("section"),
                    handle=spec.get("handle"),
                    tags=json.loads(spec["tags"]) if spec.get("tags") else None,
                    assertions=json.loads(spec["assertions"]) if spec.get("assertions") else None,
                )
                promoted += 1
                print(f"  Promoted {spec_id}: {spec['title'][:60]}...")
            elif spec:
                print(f"  Skipped {spec_id} (status={spec['status']}, not 'specified')")
            else:
                print(f"  NOT FOUND: {spec_id}")

        print(f"\nPromoted {promoted} specs from 'specified' to 'implemented'")
        print(f"Total new test artifacts: {test_id_counter - START_TEST_ID}")
        print("Done.")

    finally:
        db.close()


if __name__ == "__main__":
    import json
    main()
