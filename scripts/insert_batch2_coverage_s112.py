"""Insert test_coverage mappings for Batch 2 (91 specs): AUTH, INFRASTRUCTURE, CONFIG, EMAIL, AGENTS, TESTING.

Session S112 — Phase C coverage insertion.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "knowledge-db"))

from db import KnowledgeDB  # noqa: E402

db = KnowledgeDB()
c = db._get_conn()

CREATED_BY = "S112-batch2-coverage"
MAPPINGS: list[tuple[str, str, str | None, str, str, str]] = [
    # (spec_id, test_file, test_class, test_function, confidence, match_reason)

    # ── AGENTS (5 specs) ──────────────────────────────────────────────────
    ("SPEC-1396", "tests/agents/test_agent_class_specs.py", "TestAnalyticsCollectorAgent", "test_class_exists", "high", "Direct class existence test"),
    ("SPEC-1399", "tests/agents/test_agent_class_specs.py", "TestBaseAgentSpec", "test_process_method_abstract", "high", "Direct abstract method test"),
    ("SPEC-1407", "tests/agents/test_agent_class_specs.py", "TestIntentClassifierAgent", "test_azure_ic_model_env_default", "high", "Direct env var default test"),
    ("SPEC-1411", "tests/agents/test_agent_class_specs.py", "TestResponseGeneratorAgent", "test_class_exists", "high", "Direct class existence test"),
    ("SPEC-1414", "tests/agents/test_agent_class_specs.py", "TestResponseGeneratorAgent", "test_generate_stream_method_exists", "high", "Direct method existence test"),

    # ── AUTH (21 specs) ──────────────────────────────────────────────────
    ("SPEC-1228", "tests/multi_tenant/test_auth_specs.py", "TestSpec1228ShopifyJwtVerification", "test_spec1228_valid_jwt_decodes_successfully", "high", "JWT HS256 decode with leeway"),
    ("SPEC-1232", "tests/multi_tenant/test_auth_specs.py", "TestSpec1232UserApiKeyFormat", "test_spec1232_key_format_prefix_and_random", "high", "Key format validation"),
    ("SPEC-1243", "tests/multi_tenant/test_auth_specs.py", "TestSpec1243AccessExpiry", "test_spec1243_expired_tenant_raises_403", "high", "Access expiry blocking"),
    ("SPEC-1244", "tests/multi_tenant/test_auth_specs.py", "TestSpec1244RequireTier", "test_spec1244_matching_tier_passes", "high", "Tier gating dependency factory"),
    ("SPEC-1245", "tests/multi_tenant/test_auth_specs.py", "TestSpec1245RequireRole", "test_spec1245_matching_role_passes", "high", "Role gating dependency factory"),
    ("SPEC-1246", "tests/multi_tenant/test_security_middleware.py", "TestSpec1246BodyLimit", "test_spec1246_body_limit_is_1mb", "high", "1MB body limit constant"),
    ("SPEC-1248", "tests/multi_tenant/test_security_middleware.py", "TestSpec1248JsonDepthLimit", "test_spec1248_max_depth_is_50", "high", "50-level JSON depth constant"),
    ("SPEC-1252", "tests/multi_tenant/test_mfa_totp_specs.py", "TestSpec1252PendingJwt", "test_pending_jwt_has_type_claim", "high", "pending_2fa JWT issue"),
    ("SPEC-1257", "tests/multi_tenant/test_mfa_totp_specs.py", "TestSpec1257FullSessionJwt", "test_full_session_jwt_8hr_expiry", "high", "8-hour session JWT"),
    ("SPEC-1258", "tests/multi_tenant/test_mfa_totp_specs.py", "TestSpec1258TotpVerify", "test_valid_totp_code_returns_session", "high", "TOTP verify endpoint"),
    ("SPEC-1259", "tests/multi_tenant/test_mfa_totp_specs.py", "TestSpec1259BackupCodeVerify", "test_valid_backup_code_accepted", "high", "Backup code verify endpoint"),
    ("SPEC-1263", "tests/multi_tenant/test_mfa_totp_specs.py", "TestSpec1263BruteForce", "test_lockout_after_max_attempts", "high", "Brute-force tracking"),
    ("SPEC-1265", "tests/multi_tenant/test_mfa_totp_specs.py", "TestSpec1265SmsOtpHashing", "test_otp_stored_as_sha256_hash", "high", "SMS OTP SHA-256 hashing"),
    ("SPEC-1268", "tests/multi_tenant/test_mfa_totp_specs.py", "TestSpec1268AcsSmsFromDegradation", "test_missing_env_logs_warning", "high", "ACS_SMS_FROM graceful degradation"),
    ("SPEC-1272", "tests/multi_tenant/test_mfa_totp_specs.py", "TestSpec1272TotpParameters", "test_totp_6_digits_30sec_window1", "high", "TOTP 6-digit 30s parameters"),
    ("SPEC-1273", "tests/multi_tenant/test_mfa_totp_specs.py", "TestSpec1273BackupCodes", "test_generates_10_codes", "high", "10 backup codes generation"),
    ("SPEC-1276", "tests/multi_tenant/test_mfa_totp_specs.py", "TestSpec1276KeyVaultTotpSeeds", "test_seed_stored_in_keyvault", "high", "Key Vault TOTP seed storage"),
    ("SPEC-1281", "tests/multi_tenant/test_magic_link_auth.py", "TestSpec1281RateLimit", "test_rate_limit_blocks_4th_request_in_5_min", "high", "3-per-5-min rate limit"),
    ("SPEC-1282", "tests/multi_tenant/test_magic_link_auth.py", "TestSpec1282AntiEnumeration", "test_nonexistent_email_returns_200", "high", "Anti-enumeration 200 response"),
    ("SPEC-1286", "tests/multi_tenant/test_magic_link_auth.py", "TestSpec1286SingleUseTokens", "test_token_consumed_on_first_verify", "high", "Single-use token consumption"),
    ("SPEC-1289", "tests/multi_tenant/test_admin_mfa_auth.py", "TestSpec1289AvailableMfaMethods", "test_returns_three_mfa_methods", "high", "MFA methods enumeration"),

    # ── CONFIG (11 specs) ─────────────────────────────────────────────────
    ("SPEC-0953", "tests/multi_tenant/test_config_constants_and_models.py", "TestTtlConstants", "test_ttl_usage_period_35_days", "high", "TTL constant assertion"),
    ("SPEC-0956", "tests/multi_tenant/test_config_constants_and_models.py", "TestTtlConstants", "test_ttl_pack_balance_90_days", "high", "TTL constant assertion"),
    ("SPEC-0957", "tests/multi_tenant/test_config_constants_and_models.py", "TestTtlConstants", "test_ttl_sla_snapshots_90_days", "high", "TTL constant assertion"),
    ("SPEC-0958", "tests/multi_tenant/test_config_constants_and_models.py", "TestTtlConstants", "test_ttl_verification_token_10_min", "high", "TTL constant assertion"),
    ("SPEC-0959", "tests/multi_tenant/test_config_constants_and_models.py", "TestTtlConstants", "test_ttl_incidents_365_days", "high", "TTL constant assertion"),
    ("SPEC-0960", "tests/multi_tenant/test_config_constants_and_models.py", "TestTtlConstants", "test_ttl_alert_history_90_days", "high", "TTL constant assertion"),
    ("SPEC-0961", "tests/multi_tenant/test_config_constants_and_models.py", "TestTtlConstants", "test_ttl_ingestion_jobs_30_days", "high", "TTL constant assertion"),
    ("SPEC-1120", "tests/multi_tenant/test_config_constants_and_models.py", "TestConfigModels", "test_config_read_result_instantiation", "high", "Model class test"),
    ("SPEC-1121", "tests/multi_tenant/test_config_constants_and_models.py", "TestConfigModels", "test_config_version_info_instantiation", "high", "Model class test"),
    ("SPEC-1122", "tests/multi_tenant/test_config_constants_and_models.py", "TestConfigModels", "test_config_rollback_result_instantiation", "high", "Model class test"),
    ("SPEC-1124", "tests/multi_tenant/test_config_constants_and_models.py", "TestGateRank", "test_gate_rank_exists_and_has_entries", "high", "GATE_RANK ordering test"),

    # ── EMAIL (19 specs) ─────────────────────────────────────────────────
    ("SPEC-1293", "tests/multi_tenant/test_email_template_specs.py", "TestSpec1293VerificationToken", "test_token_uses_urlsafe_32", "high", "secrets.token_urlsafe(32)"),
    ("SPEC-1295", "tests/multi_tenant/test_email_template_specs.py", "TestSpec1295ConfirmationPage", "test_success_page_dark_theme", "high", "Branded confirmation page"),
    ("SPEC-1296", "tests/multi_tenant/test_email_template_specs.py", "TestSpec1296ErrorPage", "test_error_page_shows_reason", "high", "Branded error page"),
    ("SPEC-1299", "tests/multi_tenant/test_email_template_specs.py", "TestSpec1299SmtpConfig", "test_smtp_env_vars_exist", "high", "SMTP env var config"),
    ("SPEC-1300", "tests/multi_tenant/test_email_template_specs.py", "TestSpec1300SmtpSslStarttls", "test_ssl_for_port_465", "high", "SSL/STARTTLS selection"),
    ("SPEC-1302", "tests/multi_tenant/test_email_template_specs.py", "TestSpec1302FromAddress", "test_from_address_format", "high", "From address formatting"),
    ("SPEC-1304", "tests/multi_tenant/test_email_template_specs.py", "TestSpec1304VerificationSubject", "test_subject_line", "high", "Verification email subject"),
    ("SPEC-1306", "tests/multi_tenant/test_email_template_specs.py", "TestSpec1306SecurityNotice", "test_welcome_includes_security_notice", "high", "Security notice in welcome"),
    ("SPEC-1307", "tests/multi_tenant/test_email_template_specs.py", "TestSpec1307WelcomeFooter", "test_welcome_footer_has_tier_and_tenant", "high", "Welcome email footer"),
    ("SPEC-1309", "tests/multi_tenant/test_email_template_specs.py", "TestSpec1309WelcomeSubject", "test_subject_line", "high", "Welcome email subject"),
    ("SPEC-1313", "tests/multi_tenant/test_email_template_specs.py", "TestSpec1313TrialUrgencyStyling", "test_7day_blue_badge", "high", "Urgency badge styling"),
    ("SPEC-1314", "tests/multi_tenant/test_email_template_specs.py", "TestSpec1314EscalatingSubjects", "test_7day_subject", "high", "Escalating subject lines"),
    ("SPEC-1315", "tests/multi_tenant/test_email_template_specs.py", "TestSpec1315TrialEndBehavior", "test_body_mentions_widget_stops", "high", "Trial end behavior info"),
    ("SPEC-1316", "tests/multi_tenant/test_email_template_specs.py", "TestSpec1316AccessExpiryWarnings", "test_7day_access_expiry_email", "high", "Access expiry intervals"),
    ("SPEC-1317", "tests/multi_tenant/test_email_template_specs.py", "TestSpec1317AccessVsTrial", "test_access_expiry_mentions_provider", "high", "Provider contact reference"),
    ("SPEC-1318", "tests/multi_tenant/test_email_template_specs.py", "TestSpec1318AccessUrgencyStyling", "test_access_expiry_badge_styling", "high", "Access expiry badge styling"),
    ("SPEC-1319", "tests/multi_tenant/test_email_template_specs.py", "TestSpec1319MagicLinkSubject", "test_magic_link_subject", "high", "Magic link email subject"),
    ("SPEC-1320", "tests/multi_tenant/test_email_template_specs.py", "TestSpec1320MultiTenantMagicLink", "test_multi_tenant_magic_link_html", "high", "Multi-tenant sign-in buttons"),
    ("SPEC-1321", "tests/multi_tenant/test_email_template_specs.py", "TestSpec1321SafeToIgnore", "test_safe_to_ignore_disclaimer", "high", "Safe-to-ignore disclaimer"),

    # ── INFRASTRUCTURE (27 specs) ────────────────────────────────────────
    ("SPEC-1344", "tests/multi_tenant/test_repository_classes.py", "TestAlertRuleRepository", "test_get_rule_returns_optional_dict", "high", "Method return type"),
    ("SPEC-1357", "tests/multi_tenant/test_repository_classes.py", "TestCustomerProfileRepository", "test_class_exists_and_extends_base", "high", "Repository class existence"),
    ("SPEC-1358", "tests/multi_tenant/test_repository_classes.py", "TestIncidentRepository", "test_get_incident_returns_optional_dict", "high", "Method return type"),
    ("SPEC-1361", "tests/multi_tenant/test_repository_classes.py", "TestIncidentRepository", "test_list_all_returns_list", "high", "Method return type"),
    ("SPEC-1362", "tests/multi_tenant/test_repository_classes.py", "TestKnowledgeBaseRepository", "test_class_exists_and_extends_base", "high", "Repository class existence"),
    ("SPEC-1365", "tests/multi_tenant/test_repository_classes.py", "TestAuditLogRepository", "test_class_exists_and_extends_base", "high", "Repository class existence"),
    ("SPEC-1367", "tests/multi_tenant/test_repository_classes.py", "TestPreferencesRepository", "test_class_exists_and_extends_base", "high", "Repository class existence"),
    ("SPEC-1368", "tests/multi_tenant/test_repository_classes.py", "TestPreferencesRepository", "test_get_active_method", "high", "Method signature"),
    ("SPEC-1369", "tests/multi_tenant/test_repository_classes.py", "TestPreferencesRepository", "test_get_draft_method", "high", "Method signature"),
    ("SPEC-1370", "tests/multi_tenant/test_repository_classes.py", "TestPreferencesRepository", "test_get_previous_method", "high", "Method signature"),
    ("SPEC-1371", "tests/multi_tenant/test_repository_classes.py", "TestPreferencesRepository", "test_get_current_method", "high", "Method signature"),
    ("SPEC-1372", "tests/multi_tenant/test_repository_classes.py", "TestPreferencesRepository", "test_get_quick_actions_method", "high", "Method signature"),
    ("SPEC-1373", "tests/multi_tenant/test_repository_classes.py", "TestPreferencesRepository", "test_get_quick_actions_active_method", "high", "Method signature"),
    ("SPEC-1375", "tests/multi_tenant/test_repository_classes.py", "TestSlaSnapshotsRepository", "test_snapshot_type_daily_constant", "high", "Constant value"),
    ("SPEC-1377", "tests/multi_tenant/test_repository_classes.py", "TestTenantRepository", "test_class_exists_and_extends_base", "high", "Repository class existence"),
    ("SPEC-1380", "tests/multi_tenant/test_repository_classes.py", "TestTenantRepository", "test_list_expiring_trials_method", "high", "Method signature"),
    ("SPEC-1382", "tests/multi_tenant/test_repository_classes.py", "TestTenantRepository", "test_list_expiring_tenants_method", "high", "Method signature"),
    ("SPEC-1383", "tests/multi_tenant/test_repository_classes.py", "TestUsageRepository", "test_class_exists_and_extends_base", "high", "Repository class existence"),
    ("SPEC-1384", "tests/multi_tenant/test_auth_middleware_functions.py", "TestVerifyApiKey", "test_function_exists", "high", "Function existence"),
    ("SPEC-1385", "tests/multi_tenant/test_auth_middleware_functions.py", "TestVerifyUserApiKey", "test_function_exists", "high", "Function existence"),
    ("SPEC-1386", "tests/multi_tenant/test_auth_middleware_functions.py", "TestVerifyWidgetKey", "test_function_exists", "high", "Function existence"),
    ("SPEC-1389", "tests/multi_tenant/test_security_middleware_specs.py", "TestSizeLimitedReceive", "test_nested_function_exists", "high", "Nested function existence"),
    ("SPEC-1390", "tests/multi_tenant/test_security_middleware_specs.py", "TestJsonDepthDispatch", "test_dispatch_method_exists", "high", "Method existence"),
    ("SPEC-1391", "tests/multi_tenant/test_security_middleware_specs.py", "TestSecurityHeadersSend", "test_send_wrapper_exists", "high", "Wrapper function existence"),
    ("SPEC-1393", "tests/multi_tenant/test_security_middleware_specs.py", "TestSecurityHeaderValues", "test_x_frame_options_deny", "high", "Header value assertion"),
    ("SPEC-1394", "tests/multi_tenant/test_security_middleware_specs.py", "TestSecurityHeaderValues", "test_x_xss_protection_zero", "high", "Header value assertion"),
    ("SPEC-1395", "tests/multi_tenant/test_security_middleware_specs.py", "TestSecurityHeaderValues", "test_x_frame_options_in_headers_dict", "high", "Header dict presence"),

    # ── TESTING (8 specs) ─────────────────────────────────────────────────
    ("SPEC-1415", "tests/test_conftest_fixtures.py", "TestFixtureExistence", "test_reset_pre_auth_rate_limiter_fixture_exists", "high", "Fixture existence"),
    ("SPEC-1419", "tests/test_conftest_fixtures.py", "TestFixtureExistence", "test_mock_cosmos_fixture_exists", "high", "Fixture existence"),
    ("SPEC-1420", "tests/test_conftest_fixtures.py", "TestFixtureExistence", "test_mock_nats_fixture_exists", "high", "Fixture existence"),
    ("SPEC-1421", "tests/test_conftest_fixtures.py", "TestFixtureExistence", "test_mock_keyvault_fixture_exists", "high", "Fixture existence"),
    ("SPEC-1423", "tests/test_conftest_fixtures.py", "TestFixtureExistence", "test_app_client_fixture_exists", "high", "Fixture existence"),
    ("SPEC-1427", "tests/test_conftest_fixtures.py", "TestTenantConstants", "test_starter_tenant_id", "high", "Constant value"),
    ("SPEC-1428", "tests/test_conftest_fixtures.py", "TestTenantConstants", "test_pro_tenant_id", "high", "Constant value"),
    ("SPEC-1429", "tests/test_conftest_fixtures.py", "TestTenantConstants", "test_enterprise_tenant_id", "high", "Constant value"),
]


def main() -> None:
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()
    inserted = 0
    skipped = 0

    for spec_id, test_file, test_class, test_func, confidence, reason in MAPPINGS:
        # Check if mapping already exists
        existing = c.execute(
            "SELECT 1 FROM test_coverage WHERE spec_id = ? AND test_function = ?",
            (spec_id, test_func),
        ).fetchone()
        if existing:
            skipped += 1
            continue

        c.execute(
            """INSERT INTO test_coverage
               (spec_id, test_file, test_class, test_function, confidence, match_reason, created_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (spec_id, test_file, test_class, test_func, confidence, reason, now, CREATED_BY),
        )
        inserted += 1

    c.commit()

    # Report
    total_coverage = c.execute(
        "SELECT COUNT(DISTINCT spec_id) FROM test_coverage"
    ).fetchone()[0]
    total_specs = c.execute(
        "SELECT COUNT(DISTINCT id) FROM specifications WHERE status != 'retired'"
    ).fetchone()[0]

    print(f"Inserted: {inserted}, Skipped (already exist): {skipped}")
    print(f"Total coverage: {total_coverage}/{total_specs} specs ({100*total_coverage/total_specs:.1f}%)")


if __name__ == "__main__":
    main()
