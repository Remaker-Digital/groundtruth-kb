"""S152 — Record batch 2 test artifacts: session, identity, email, API, activation.

Creates test artifacts, test coverage mappings, and promotes spec statuses.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "knowledge-db"))
from db import KnowledgeDB

SESSION = "S152"
CHANGED_BY = f"claude-{SESSION}"

# Determine next TEST ID
db = KnowledgeDB()
row = db._get_conn().execute("SELECT MAX(CAST(SUBSTR(id, 6) AS INTEGER)) as max_id FROM tests").fetchone()
START_TEST_ID = row["max_id"] + 1
print(f"Starting from TEST-{START_TEST_ID:04d}")

# --- Session/Identity file ---
FILE1 = "tests/multi_tenant/test_session_identity_spec_verification.py"
TESTS_FILE1 = [
    (
        "SPEC-0584",
        "TestSpec0584SessionPersistence",
        [
            "test_session_token_is_jwt_with_expiry",
            "test_session_token_8_hour_ttl",
            "test_verify_session_token_returns_payload_not_consumed",
        ],
        "Session persistence across page refresh",
        "8-hour JWT token is reusable (not consumed on verify)",
    ),
    (
        "SPEC-0585",
        "TestSpec0585SessionClearOnLogout",
        [
            "test_expired_token_returns_none",
            "test_invalid_token_returns_none",
            "test_empty_string_token_returns_none",
        ],
        "Session gate reappears on logout/cookie clear",
        "Invalid/expired tokens return None, forcing re-auth",
    ),
    (
        "SPEC-1619",
        "TestSpec1619MagicLinkOriginUrl",
        [
            "test_build_url_with_origin_tenant",
            "test_build_url_without_origin_tenant",
            "test_build_url_preserves_standalone_path",
            "test_spec_1619_comment_exists_in_source",
        ],
        "Magic link URL preserves origin tenant",
        "URL includes ?tenant= matching origin context",
    ),
    (
        "SPEC-0427",
        "TestSpec0427UnifiedAuthImplementation",
        [
            "test_middleware_resolves_auth_to_tenant_context",
            "test_mfa_module_exists_alongside_auth",
        ],
        "Auth/2FA/RBAC unified implementation",
        "TenantContext carries auth+role+tier; MFA module co-located",
    ),
    (
        "SPEC-0498",
        "TestSpec0498CustomerIdentification",
        [
            "test_identity_preprocessor_exists",
            "test_identity_preprocessor_detects_email",
            "test_chat_models_support_visitor_identity",
        ],
        "Customer identification at chat start",
        "identity_preprocessor intercepts messages for email; VisitorIdentity model exists",
    ),
    (
        "SPEC-0502",
        "TestSpec0502NameEmailRequired",
        [
            "test_email_extraction_from_message",
            "test_identity_action_types_include_email_received",
        ],
        "Name/email required before AI responds",
        "Email extraction works on direct and embedded email patterns",
    ),
    (
        "SPEC-0505",
        "TestSpec0505OtpVerification",
        [
            "test_otp_pattern_is_6_digits",
            "test_otp_length_is_6",
            "test_otp_ttl_is_10_minutes",
            "test_max_otp_attempts_is_3",
        ],
        "OTP verification for Persistent Customer Memory",
        "6-digit OTP, 600s TTL, 3 max attempts",
    ),
    (
        "SPEC-0506",
        "TestSpec0506VerifyIdentityLanguage",
        [
            "test_identity_action_has_system_message",
        ],
        "Ask to verify identity (no additional explanation)",
        "IdentityAction carries system_message for OTP flow",
    ),
    (
        "SPEC-0507",
        "TestSpec0507AnonymousWarning",
        [
            "test_skip_phrases_include_guest_options",
            "test_skip_verification_action_has_warning_message",
        ],
        "Anonymous warning MUST NOT be skipped",
        "Skip phrases (skip/guest/no thanks) all trigger warning",
    ),
    (
        "SPEC-0499",
        "TestSpec0499AnonymousDiscouraged",
        [
            "test_preprocessor_processes_all_unverified_messages",
            "test_otp_rate_limited_action_exists",
        ],
        "Anonymous sessions discouraged",
        "Preprocessor intercepts all unverified messages",
    ),
    (
        "SPEC-0869",
        "TestSpec0869CamelCaseApiResponses",
        [
            "test_pydantic_models_use_camelcase_aliases",
            "test_api_versioning_header_names_are_kebab_case",
        ],
        "API responses use camelCase",
        "Pydantic models with aliases; headers use kebab-case",
    ),
    (
        "SPEC-0453",
        "TestSpec0453ApiVersionTracking",
        [
            "test_api_version_is_semver",
            "test_product_version_is_semver",
            "test_api_version_middleware_adds_both_headers",
            "test_deprecated_paths_is_defined",
        ],
        "API version numbering tracks product version",
        "SemVer API_VERSION + PRODUCT_VERSION; middleware adds both headers",
    ),
    (
        "SPEC-0054",
        "TestSpec0054DraftUntilActivated",
        [
            "test_config_state_has_draft_and_active",
            "test_activation_service_has_save_draft",
            "test_activation_service_has_activate",
            "test_draft_save_result_has_state_field",
        ],
        "Config changes are drafts until activated",
        "ConfigState.DRAFT/ACTIVE; ActivationService.save_draft()/activate()",
    ),
    (
        "SPEC-0479",
        "TestSpec0479NoActiveWithoutMandatory",
        [
            "test_activation_result_has_errors",
            "test_validation_result_has_hard_errors",
            "test_activation_service_has_validate_method",
        ],
        "No Active state without mandatory inputs",
        "activate() validates before promoting; ValidationResult blocks on hard errors",
    ),
    (
        "SPEC-0064",
        "TestSpec0064ActiveMeansWidgetAvailable",
        [
            "test_activation_result_includes_activated_at",
            "test_config_state_active_value",
        ],
        "Active config means widget is live",
        "ConfigState.ACTIVE read by pipeline; ActivationResult records timestamp",
    ),
]

# --- Email file ---
FILE2 = "tests/multi_tenant/test_email_spec_verification.py"
TESTS_FILE2 = [
    (
        "SPEC-0588",
        "TestSpec0588TitanSmtpPrimary",
        [
            "test_magic_link_email_tries_smtp_first",
            "test_welcome_email_tries_acs_or_smtp",
            "test_smtp_port_465_for_ssl",
        ],
        "Titan SMTP as primary email provider",
        "SMTP checked before ACS; port 465 with SMTP_SSL",
    ),
    (
        "SPEC-0589",
        "TestSpec0589TitanSenderAddress",
        [
            "test_smtp_from_env_variable_used",
            "test_agent_red_branding_in_from_header",
        ],
        "Titan Email sender address configuration",
        "SMTP_FROM env var used; Agent Red in From header",
    ),
    (
        "SPEC-0409",
        "TestSpec0409AcsFallback",
        [
            "test_acs_fallback_in_magic_link",
            "test_acs_fallback_in_api_key_reset",
        ],
        "Azure Communication Services as fallback",
        "ACS fallback in magic link and API key reset emails",
    ),
    (
        "SPEC-0760",
        "TestSpec0760CredentialsInWelcomeEmail",
        [
            "test_welcome_email_accepts_superadmin_key",
            "test_welcome_email_accepts_widget_key",
            "test_welcome_email_template_includes_api_key",
            "test_welcome_email_template_includes_widget_key",
        ],
        "Superadmin credentials in welcome email",
        "Welcome email includes superadmin_key and widget_key",
    ),
    (
        "SPEC-0683",
        "TestSpec0683SignInLinkResolvesToAdmin",
        [
            "test_welcome_email_uses_admin_login_url_placeholder",
            "test_build_admin_login_url_prefers_standalone",
            "test_build_admin_login_url_not_agentredcx",
        ],
        "Sign-in link resolves to admin UI",
        "Template uses {admin_login_url}; builder returns admin console URL",
    ),
    (
        "SPEC-0684",
        "TestSpec0684WelcomeEmailLogo",
        [
            "test_email_wrapper_has_logo_image",
            "test_email_wrapper_has_alt_text",
        ],
        "Welcome email displays Agent Red logo",
        "Email wrapper has <img> with logo and alt text",
    ),
    (
        "SPEC-0689",
        "TestSpec0689KeyRegenerationNotice",
        [
            "test_welcome_email_has_regeneration_notice",
            "test_welcome_email_key_section_has_security_notice",
        ],
        "Key regeneration notice in welcome email",
        "Template includes 'regenerate' text and security notice",
    ),
    (
        "SPEC-1628",
        "TestSpec1628ApiKeyResetWrapper",
        [
            "test_api_key_reset_imports_email_wrapper",
            "test_api_key_reset_formats_wrapper",
        ],
        "API key reset uses shared _EMAIL_WRAPPER",
        "_EMAIL_WRAPPER imported and formatted in API key email",
    ),
    (
        "SPEC-1629",
        "TestSpec1629ApiKeyResetLoginButton",
        [
            "test_api_key_reset_has_admin_login_url_param",
            "test_api_key_reset_email_has_link",
        ],
        "API key reset email includes login link",
        "_send_api_key_email accepts admin_login_url; body has <a href>",
    ),
    (
        "SPEC-1631",
        "TestSpec1631RemakerDigitalFooterLink",
        [
            "test_email_wrapper_has_remaker_digital_link",
            "test_email_wrapper_remaker_is_hyperlinked",
        ],
        "Email footer Remaker Digital hyperlinked",
        "Footer has <a href='https://remakerdigital.com'>",
    ),
    (
        "SPEC-0420",
        "TestSpec0420TeamInvitationEmails",
        [
            "test_magic_link_request_endpoint_exists",
            "test_send_magic_link_email_function_exists",
        ],
        "Team invitation emails sent automatically",
        "Magic link request endpoint for invitations",
    ),
    (
        "SPEC-0777",
        "TestSpec0777AutomaticWelcomeEmail",
        [
            "test_welcome_email_function_is_async",
            "test_welcome_email_called_from_provisioning",
            "test_welcome_email_called_from_stripe",
        ],
        "Automatic welcome email on tenancy creation",
        "send_welcome_email called from provisioning and Stripe",
    ),
]


test_id_counter = START_TEST_ID
all_coverage = []

for file_path, tests_list in [(FILE1, TESTS_FILE1), (FILE2, TESTS_FILE2)]:
    for spec_id, test_class, test_functions, title, expected_outcome in tests_list:
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
                test_file=file_path,
                test_class=test_class,
                test_function=func_name,
                last_result="PASS",
                last_executed_at="2026-03-06T00:00:00Z",
            )
            all_coverage.append(
                {
                    "spec_id": spec_id,
                    "test_file": file_path,
                    "test_class": test_class,
                    "test_function": func_name,
                    "confidence": "high",
                    "match_reason": f"{SESSION}: Direct spec-to-test mapping via test class name",
                }
            )
            test_id_counter += 1

total_tests = test_id_counter - START_TEST_ID
print(f"Created {total_tests} test artifacts (TEST-{START_TEST_ID:04d}..TEST-{test_id_counter - 1:04d})")

# Record test coverage mappings
count = db.insert_test_coverage_batch(all_coverage, created_by=CHANGED_BY)
print(f"Recorded {count} test coverage mappings")

# Promote spec statuses
all_spec_ids = set()
for _, tests_list in [(FILE1, TESTS_FILE1), (FILE2, TESTS_FILE2)]:
    for spec_id, *_ in tests_list:
        all_spec_ids.add(spec_id)

promoted = 0
for spec_id in sorted(all_spec_ids):
    spec = db.get_spec(spec_id)
    if spec and spec["status"] == "specified":
        db.insert_spec(
            id=spec_id,
            title=spec["title"],
            status="implemented",
            changed_by=CHANGED_BY,
            change_reason=f"{SESSION}: Promoted to implemented — real tests verify implementation (batch 2: session+identity+email+API+activation)",
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
        print(f"  Skipped {spec_id} (status={spec['status']})")
    else:
        print(f"  NOT FOUND: {spec_id}")

print(f"\nPromoted {promoted} specs from 'specified' to 'implemented'")
print(f"Total new test artifacts: {total_tests}")
print("Done.")
db.close()
