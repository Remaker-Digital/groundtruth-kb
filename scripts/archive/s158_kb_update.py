"""S158 KB update — promote specs + record test artifacts.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sys
sys.path.insert(0, "tools/knowledge-db")
import db  # noqa: E402

kdb = db.KnowledgeDB()
conn = kdb._get_conn()

# -------------------------------------------------------------------
# Promote 4 specs to implemented
# -------------------------------------------------------------------

specs = [
    ("SPEC-1675", "SPA User Hierarchy and Lifecycle"),
    ("SPEC-1676", "Login Notification Emails"),
    ("SPEC-1677", "Tenant Account Recovery Address"),
    ("SPEC-1678", "SPA Emergency Key Recovery"),
]

for spec_id, title in specs:
    kdb.update_spec(
        id=spec_id,
        changed_by="S158",
        change_reason=(
            f"Implemented: {title}. Backend module, tests, frontend changes "
            "complete. 70/70 tests PASS. Full suite 6387 pass, 1 known fail."
        ),
        status="implemented",
    )
    print(f"Promoted {spec_id} to implemented")


# -------------------------------------------------------------------
# Record test artifacts
# -------------------------------------------------------------------

max_id = conn.execute(
    'SELECT MAX(CAST(SUBSTR(id, 6) AS INTEGER)) FROM tests WHERE id LIKE "TEST-%"'
).fetchone()[0]
next_id = (max_id or 0) + 1
print(f"Starting test IDs from TEST-{next_id}")

# SPEC-1675 tests (25) — test_spa_user_management.py
spec1675_tests = [
    ("test_superadmin_role_set", "TenantContext accepts superadmin role"),
    ("test_operator_role_set", "TenantContext accepts operator role"),
    ("test_role_default_none", "TenantContext role defaults to None"),
    ("test_guard_exists", "require_spa_superadmin guard function exists"),
    ("test_superadmin_passes", "Superadmin passes guard check"),
    ("test_operator_blocked", "Operator blocked by superadmin guard"),
    ("test_non_platform_admin_blocked", "Non-platform admin blocked by superadmin guard"),
    ("test_list_users_returns_admins", "List users returns platform admin list"),
    ("test_list_users_repo_not_initialized", "List users returns 503 when repo not configured"),
    ("test_create_operator_success", "Create operator returns new API key"),
    ("test_create_operator_blocked_for_operator", "Operator cannot create other operators"),
    ("test_create_operator_duplicate_email", "Duplicate email rejected for operator creation"),
    ("test_create_operator_audit_logged", "Operator creation audit logged"),
    ("test_deactivate_operator_success", "Deactivate operator succeeds"),
    ("test_cannot_deactivate_self", "Cannot deactivate self"),
    ("test_cannot_deactivate_superadmin", "Cannot deactivate superadmin"),
    ("test_operator_cannot_deactivate", "Operator cannot deactivate others"),
    ("test_deactivate_not_found", "Deactivate returns 404 for missing admin"),
    ("test_generate_backup_codes_returns_8", "Backup codes generation returns 8 codes"),
    ("test_backup_codes_stored_as_hashes", "Backup codes stored as SHA-256 hashes"),
    ("test_backup_codes_all_unique", "All backup codes are unique"),
    ("test_operator_can_generate_own_codes", "Operator can generate own backup codes"),
    ("test_set_notification_email", "Set notification email succeeds"),
    ("test_clear_notification_email", "Clear notification email succeeds"),
    ("test_operator_can_set_own_email", "Operator can set own notification email"),
]

for func, desc in spec1675_tests:
    kdb.insert_test(
        id=f"TEST-{next_id}",
        title=desc,
        spec_id="SPEC-1675",
        test_type="unit",
        expected_outcome="PASS",
        changed_by="S158",
        change_reason="SPEC-1675 SPA User Hierarchy — new test",
        test_file="tests/multi_tenant/test_spa_user_management.py",
        test_function=func,
    )
    next_id += 1

print("SPEC-1675: 25 tests recorded")

# SPEC-1678 tests (17 unique) — test_spa_recovery.py
spec1678_tests = [
    ("test_recovery_returns_200_with_valid_code", "Recovery returns 200 with valid backup code"),
    ("test_recovery_generates_new_key", "Recovery generates new SHA-256 API key hash"),
    ("test_recovery_consumes_backup_code", "Recovery consumes used backup code"),
    ("test_recovery_sends_email", "Recovery sends email with new ar_spa_plat_ key"),
    ("test_recovery_logs_audit_event", "Recovery logs SECURITY_EVENT audit"),
    ("test_invalid_email_returns_200", "Invalid email returns 200 (enumeration prevention)"),
    ("test_invalid_code_returns_200", "Invalid code returns 200 (enumeration prevention)"),
    ("test_same_message_for_valid_and_invalid", "Same response message for valid and invalid requests"),
    ("test_rate_limit_after_3_attempts", "Rate limited after 3 attempts from same IP"),
    ("test_different_ips_not_affected", "Different IPs not affected by rate limit"),
    ("test_rate_limit_function_directly", "Rate limit function works correctly"),
    ("test_rate_limit_window_expires", "Rate limit window expires after 15 minutes"),
    ("test_consumed_code_not_in_remaining", "Consumed code removed from remaining list"),
    ("test_other_codes_preserved", "Other backup codes preserved after consumption"),
    ("test_returns_200_when_repo_not_configured", "Returns 200 when repo not configured"),
    ("test_spa_recovery_path_is_auth_exempt", "/api/auth/spa-recovery in AUTH_EXEMPT_PREFIXES"),
    ("test_spa_recovery_router_exists", "SPA recovery router registered with correct prefix"),
]

for func, desc in spec1678_tests:
    kdb.insert_test(
        id=f"TEST-{next_id}",
        title=desc,
        spec_id="SPEC-1678",
        test_type="unit",
        expected_outcome="PASS",
        changed_by="S158",
        change_reason="SPEC-1678 SPA Emergency Key Recovery — new test",
        test_file="tests/multi_tenant/test_spa_recovery.py",
        test_function=func,
    )
    next_id += 1

print("SPEC-1678: 17 tests recorded")

# SPEC-1676 tests (10) — test_login_notification.py
spec1676_tests = [
    ("test_sends_email_on_login", "Login notification email sent on SPA auth"),
    ("test_email_contains_ip", "Email body contains client IP address"),
    ("test_email_contains_user_agent", "Email body contains user agent string"),
    ("test_notification_email_overrides_admin_email", "Notification email overrides admin email"),
    ("test_falls_back_to_admin_email_when_no_override", "Falls back to admin email when no override"),
    ("test_email_failure_does_not_raise", "Email failure does not raise exception"),
    ("test_no_acs_connection_string_skips_silently", "No ACS connection string skips silently"),
    ("test_notification_task_set_exists", "Notification task set exists in middleware"),
    ("test_tenant_context_has_notification_email_field", "TenantContext has notification email field"),
    ("test_notification_email_defaults_to_none", "Notification email defaults to None"),
]

for func, desc in spec1676_tests:
    kdb.insert_test(
        id=f"TEST-{next_id}",
        title=desc,
        spec_id="SPEC-1676",
        test_type="unit",
        expected_outcome="PASS",
        changed_by="S158",
        change_reason="SPEC-1676 Login Notification Emails — new test",
        test_file="tests/multi_tenant/test_login_notification.py",
        test_function=func,
    )
    next_id += 1

print("SPEC-1676: 10 tests recorded")

# SPEC-1677 tests (17) — test_tenant_recovery.py
spec1677_tests = [
    ("test_activate_sets_recovery_address", "Activate sets recovery address on tenant"),
    ("test_activate_audit_logged", "Activate recovery address audit logged"),
    ("test_activate_returns_503_when_not_configured", "Activate returns 503 when repos not configured"),
    ("test_send_auth_link_creates_token", "Send auth link creates verification token"),
    ("test_send_auth_link_sends_email", "Send auth link sends email with recovery URL"),
    ("test_send_auth_link_fails_when_no_recovery_address", "Send auth link fails when no recovery address"),
    ("test_send_auth_link_audit_logged", "Send auth link audit logged"),
    ("test_get_status_returns_recovery_info", "Get status returns recovery info"),
    ("test_get_status_tenant_not_found", "Get status returns 404 for unknown tenant"),
    ("test_verify_valid_token_returns_session_jwt", "Verify valid token returns session JWT"),
    ("test_verify_consumed_token_fails", "Verify consumed token returns 400"),
    ("test_verify_token_tenant_mismatch", "Verify token with tenant mismatch returns 400"),
    ("test_verify_audit_logged", "Verify token audit logged"),
    ("test_account_recovery_path_is_auth_exempt", "/api/auth/account-recovery in AUTH_EXEMPT_PREFIXES"),
    ("test_tenant_recovery_router_exists", "Tenant recovery router exists with correct prefix"),
    ("test_recovery_verify_router_exists", "Recovery verify router exists with correct prefix"),
    ("test_spa_facing_routes", "SPA-facing routes include activate, send-auth-link, status"),
]

for func, desc in spec1677_tests:
    kdb.insert_test(
        id=f"TEST-{next_id}",
        title=desc,
        spec_id="SPEC-1677",
        test_type="unit",
        expected_outcome="PASS",
        changed_by="S158",
        change_reason="SPEC-1677 Tenant Account Recovery — new test",
        test_file="tests/multi_tenant/test_tenant_recovery.py",
        test_function=func,
    )
    next_id += 1

print("SPEC-1677: 17 tests recorded")
print(f"\nTotal: {next_id - (max_id + 1)} test artifacts recorded (TEST-{max_id + 1}..TEST-{next_id - 1})")

# -------------------------------------------------------------------
# Summary
# -------------------------------------------------------------------

total_specs = conn.execute(
    "SELECT COUNT(DISTINCT id) FROM specifications"
).fetchone()[0]
impl = conn.execute(
    "SELECT COUNT(DISTINCT id) FROM specifications WHERE status = 'implemented'"
).fetchone()[0]
total_tests = conn.execute(
    "SELECT COUNT(DISTINCT id) FROM tests"
).fetchone()[0]

print(f"\nKB summary: {total_specs} specs ({impl} implemented), {total_tests} test artifacts")
